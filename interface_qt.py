import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel,
    QGridLayout, QHBoxLayout, QLineEdit
)
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
from simulador import SimuladorElevador
from mqtt_handler import MqttElevadorClient

class ElevadorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador de Elevador - PyQtGraph")
        self.simulador = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.atualizar_simulacao)
        self.botao_selecionado = None
        self.simulacao_ativa = False

        self.andares = {
            "Subsolo": 0,
            "Térreo": 4,
            "1º andar": 8,
            "2º andar": 11,
            "3º andar": 14,
            "4º andar": 17,
            "5º andar": 20,
            "6º andar": 23,
            "7º andar": 26,
            "8º andar": 29,
            "Técnico": 32
        }

        self.todos_tempos = []
        self.todas_posicoes = []

        self.init_ui()
        self.mqtt = MqttElevadorClient(self.iniciar_simulacao)
        self.mqtt.conectar()

    def init_ui(self):
        layout = QVBoxLayout()

        self.setStyleSheet("""
            QWidget {
                background-color: #f8f8f8;
                font-family: Segoe UI;
                font-size: 14px;
            }
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 6px;
            }
            QPushButton:disabled {
                background-color: #dddddd;
                color: #999999;
            }
            QPushButton:hover {
                background-color: #e6f2ff;
            }
            QLabel {
                font-size: 15px;
                font-weight: bold;
            }
        """)

        # 🔐 Campo de senha com feedback
        senha_layout = QHBoxLayout()
        senha_label = QLabel("Senha para Subsolo/Técnico:")

        self.senha_input = QLineEdit()
        self.senha_input.setEchoMode(QLineEdit.Password)
        self.senha_input.setPlaceholderText("Digite a senha...")
        self.senha_input.setFixedWidth(200)
        self.senha_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #aaa;
                border-radius: 4px;
                font-size: 14px;
            }
        """)

        self.senha_feedback = QLabel("")
        self.senha_feedback.setStyleSheet("color: gray; font-size: 12px;")

        senha_box = QVBoxLayout()
        senha_box.addWidget(self.senha_input)
        senha_box.addWidget(self.senha_feedback)

        senha_layout.addWidget(senha_label)
        senha_layout.addLayout(senha_box)
        layout.addLayout(senha_layout)

        label = QLabel("Selecione o andar de destino:")
        layout.addWidget(label)

        self.grid = QGridLayout()
        self.botoes_andar = {}
        self.criar_botoes()
        layout.addLayout(self.grid)

        self.indicador_andar = QLabel("Posição atual: - m")
        layout.addWidget(self.indicador_andar)

        botao_layout = QHBoxLayout()
        self.btn_reiniciar = QPushButton("Reiniciar gráfico")
        self.btn_reiniciar.setFixedSize(120, 40)
        self.btn_reiniciar.clicked.connect(self.reiniciar_grafico)

        self.btn_emergencia = QPushButton("STOP")
        self.btn_emergencia.setFixedSize(60, 60)
        self.btn_emergencia.clicked.connect(self.parar_emergencia)
        self.btn_emergencia.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 30px;
                border: 3px solid darkred;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
        """)

        botao_layout.addWidget(self.btn_reiniciar)
        botao_layout.addWidget(self.btn_emergencia)
        layout.addLayout(botao_layout)

        self.plot_widget = pg.PlotWidget(title="Movimento da Cabine em Tempo Real")
        self.plot_widget.setMinimumHeight(400)
        self.plot_widget.setBackground("w")
        self.plot_widget.setLabel('left', 'Altura', units='m')
        self.plot_widget.setLabel('bottom', 'Tempo', units='s')
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setXRange(0, 100)
        self.plot_widget.setYRange(0, 36)
        self.plot_widget.getPlotItem().getAxis('bottom').setTickSpacing(5, 5)
        self.curva = self.plot_widget.plot([], [], pen=pg.mkPen('b', width=2))
        layout.addWidget(self.plot_widget)

        self.setLayout(layout)

    def criar_botoes(self):
        for i, (nome, altura) in enumerate(reversed(self.andares.items())):
            btn = QPushButton(nome)
            btn.setFixedSize(100, 40)
            btn.clicked.connect(lambda checked, h=altura, n=nome, b=btn: self.tratar_botao_andar(h, n, b))
            self.grid.addWidget(btn, i // 2, i % 2)
            self.botoes_andar[nome] = btn

    def tratar_botao_andar(self, altura, nome_andar, botao):
        if nome_andar in ["Subsolo", "Técnico"]:
            senha = self.senha_input.text()
            if senha != "admin123":
                self.senha_feedback.setText("❌ Senha incorreta")
                self.senha_feedback.setStyleSheet("color: red; font-size: 12px;")
                return
            else:
                self.senha_feedback.setText("✅ Senha aceita")
                self.senha_feedback.setStyleSheet("color: green; font-size: 12px;")
        else:
            self.senha_feedback.setText("")

        if self.botao_selecionado:
            self.botao_selecionado.setStyleSheet("")
        botao.setStyleSheet("""
            background-color: #c8facc;
            border: 2px solid #4CAF50;
            font-weight: bold;
        """)
        self.botao_selecionado = botao
        self.iniciar_simulacao(altura)

    def iniciar_simulacao(self, destino):
        posicao_atual = self.simulador.posicao_atual if self.simulador else 0.0
        tempo_base = self.todos_tempos[-1] if self.todos_tempos else 0.0

        self.simulador = SimuladorElevador(destino, posicao_inicial=posicao_atual)
        self.simulador.tempo = tempo_base
        self.simulador.historico_tempo = [tempo_base]
        self.simulador.historico_posicao = [posicao_atual]

        self.simulacao_ativa = True
        self.plot_widget.addLine(y=destino, pen=pg.mkPen('r', style=pg.QtCore.Qt.DashLine))
        self.timer.start(int(self.simulador.Ts * 1000))

    def atualizar_simulacao(self):
        if self.simulador and self.simulacao_ativa:
            if self.simulador.passo():
                self.todos_tempos.append(self.simulador.historico_tempo[-1])
                self.todas_posicoes.append(self.simulador.historico_posicao[-1])
                self.curva.setData(self.todos_tempos, self.todas_posicoes, clear=True)

                pos = self.simulador.posicao_atual
                andar = self.altura_para_andar(pos)
                self.indicador_andar.setText(f"Posição atual: {pos:.2f} m  ({andar})")
        else:
            self.timer.stop()

    def parar_emergencia(self):
        self.simulacao_ativa = False
        self.timer.stop()
        if self.simulador:
            self.todos_tempos.append(self.simulador.tempo)
            self.todas_posicoes.append(self.simulador.posicao_atual)
            self.curva.setData(self.todos_tempos, self.todas_posicoes, clear=True)
            self.indicador_andar.setText("Movimento interrompido por STOP.")

    def altura_para_andar(self, altura):
        for nome, valor in self.andares.items():
            if abs(altura - valor) <= 1.0:
                return nome
        return "Entre andares"

    def reiniciar_grafico(self):
        self.timer.stop()
        self.simulacao_ativa = False
        self.todos_tempos = [0.0]
        self.todas_posicoes = [0.0]
        self.plot_widget.clear()
        self.plot_widget.setXRange(0, 100)
        self.plot_widget.setYRange(0, 36)
        self.plot_widget.getPlotItem().getAxis('bottom').setTickSpacing(5, 5)
        self.curva = pg.PlotDataItem(pen=pg.mkPen('b', width=2))
        self.curva.setData(self.todos_tempos, self.todas_posicoes)
        self.plot_widget.addItem(self.curva)
        self.simulador = None
        self.indicador_andar.setText("Gráfico reiniciado. Posição atual: 0.00 m")
        if self.botao_selecionado:
            self.botao_selecionado.setStyleSheet("")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = ElevadorWindow()
    janela.resize(900, 700)
    janela.show()
    sys.exit(app.exec_())
