import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel,
    QGridLayout, QHBoxLayout, QLineEdit, QSizePolicy, QInputDialog, QMessageBox
)
from PyQt5.QtCore import QTimer, Qt
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
        self.parada_timer = QTimer()
        self.parada_timer.setSingleShot(True)
        self.parada_timer.timeout.connect(self.finalizar_parada)
        self.em_parada_final = False
        self.botao_selecionado = None
        self.simulacao_ativa = False

        self.andares = {
            "-1": 0,
            "T": 4,
            "1": 8,
            "2": 11,
            "3": 14,
            "4": 17,
            "5": 20,
            "6": 23,
            "7": 26,
            "8": 29,
            "TÉC": 32
        }

        self.todos_tempos = []
        self.todas_posicoes = []

        self.init_ui()
        self.mqtt = MqttElevadorClient(self.iniciar_simulacao)
        self.mqtt.conectar()

    def init_ui(self):
        layout = QVBoxLayout()

        self.visor_numero = QLabel("—")
        self.visor_direcao = QLabel("—")

        for lbl in (self.visor_numero, self.visor_direcao):
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFixedSize(60, 60)
            lbl.setStyleSheet("""
                QLabel {
                    background-color: black;
                    color: orange;
                    font-size: 32px;
                    font-weight: bold;
                    border-radius: 12px;
                }
            """)

        visor_layout = QHBoxLayout()
        visor_layout.setAlignment(Qt.AlignCenter)
        visor_layout.addWidget(self.visor_numero)
        visor_layout.addWidget(self.visor_direcao)
        layout.addLayout(visor_layout)


        self.setStyleSheet("""
            QWidget {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                stop:0 #dce1e3, stop:1 #f6f8f9);
                font-family: 'Segoe UI';
                font-size: 14px;
            }

            QLabel {
                font-size: 15px;
                font-weight: bold;
                color: #333;
            }

            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                stop:0 #f0f0f0, stop:1 #d9d9d9);
                border: 2px solid #a0a0a0;
                border-radius: 20px;
                min-width: 60px;
                min-height: 40px;
                font-weight: bold;
                color: #333;
            }

            QPushButton:hover {
                background-color: #e0f7fa;
                border: 2px solid #4fc3f7;
            }

            QPushButton:pressed {
                background-color: #b3e5fc;
                border: 2px solid #0288d1;
                color: black;
            }

            QPushButton:disabled {
                background-color: #eeeeee;
                color: #999999;
                border: 2px solid #cccccc;
            }

            QLineEdit {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #fff;
            }
        """)

        '''# 🔐 Campo de senha com feedback
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


        self.direcao_label = QLabel("-")  # inicializado com traço
        self.direcao_label.setAlignment(Qt.AlignCenter)
        self.direcao_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: orange;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.direcao_label)'''


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
                background-color: #ff3b30;
                color: white;
                font-weight: bold;
                font-size: 18px;
                border-radius: 30px;
                border: 3px solid #b71c1c;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #ff6f61;
            }
        """)


        botao_layout.addWidget(self.btn_reiniciar)
        botao_layout.addWidget(self.btn_emergencia)
        layout.addLayout(botao_layout)

        self.plot_widget = pg.PlotWidget(title="Movimento da Cabine em Tempo Real")
        self.plot_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plot_widget.setBackground("w")
        self.plot_widget.setLabel('left', 'Altura', units='m')
        self.plot_widget.setLabel('bottom', 'Tempo', units='s')
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setXRange(0, 100)
        self.plot_widget.setYRange(0, 36)
        self.plot_widget.getPlotItem().getAxis('bottom').setTickSpacing(5, 5)
        self.plot_widget.setBackground("#f4f4f4")
        self.plot_widget.getPlotItem().getAxis('left').setPen(pg.mkPen(color=(50,50,50)))
        self.plot_widget.getPlotItem().getAxis('bottom').setPen(pg.mkPen(color=(50,50,50)))

        self.curva = self.plot_widget.plot([], [], pen=pg.mkPen('b', width=2))
        layout.addWidget(self.plot_widget)

        container = QWidget()
        container.setLayout(layout)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(container)
        main_layout.setStretchFactor(container, 1)


    def criar_botoes(self):
        for i, (nome, altura) in enumerate(reversed(self.andares.items())):
            btn = QPushButton(nome)
            btn.setFixedSize(100, 40)
            btn.clicked.connect(lambda checked, h=altura, n=nome, b=btn: self.tratar_botao_andar(h, n, b))
            self.grid.addWidget(btn, i // 2, i % 2)
            self.botoes_andar[nome] = btn

    def tratar_botao_andar(self, altura, nome_andar, botao):
        # Verifica se é necessário solicitar senha
        if nome_andar in ["-1", "TÉC"]:
            senha, ok = QInputDialog.getText(self, "Acesso Restrito", "Digite a senha:", QLineEdit.Password)
            if not ok or senha != "admin123":
                QMessageBox.warning(self, "Acesso Negado", "❌ Senha incorreta ou cancelada.")
                return

        if self.botao_selecionado:
            self.botao_selecionado.setStyleSheet("")

        botao.setStyleSheet("""
            background-color: qradialgradient(cx:0.5, cy:0.5, radius:1,
                                            fx:0.5, fy:0.5,
                                            stop:0 #a5d6a7, stop:1 #81c784);
            border: 2px solid #388e3c;
            font-weight: bold;
            color: white;
        """)

        self.botao_selecionado = botao
        # Atualiza a seta de direção no visor
        pos_atual = self.simulador.posicao_atual if self.simulador else 0
        if altura > pos_atual:
            self.visor_direcao.setText("▲")
        elif altura < pos_atual:
            self.visor_direcao.setText("▼")
        else:
            self.visor_direcao.setText("-")
        
        self.iniciar_simulacao(altura)



    def iniciar_simulacao(self, sp):
        posicao_atual = self.simulador.posicao_atual if self.simulador else 0.0
        tempo_base = self.todos_tempos[-1] if self.todos_tempos else 0.0

        self.simulador = SimuladorElevador(sp, posicao_inicial=posicao_atual)
        self.simulador.tempo = tempo_base
        self.simulador.historico_tempo = [tempo_base]
        self.simulador.historico_posicao = [posicao_atual]

        self.simulacao_ativa = True
        self.plot_widget.addLine(y=sp, pen=pg.mkPen('r', style=pg.QtCore.Qt.DashLine))
        self.timer.start(int(self.simulador.Ts * 1000))

    def atualizar_simulacao(self):
        if self.simulador and self.simulacao_ativa:
            terminou = not self.simulador.passo()
            self.todos_tempos.append(self.simulador.historico_tempo[-1])
            self.todas_posicoes.append(self.simulador.historico_posicao[-1])
            self.curva.setData(self.todos_tempos, self.todas_posicoes, clear=True)

            pos = self.simulador.posicao_atual
            andar = self.altura_para_andar(pos)
            self.indicador_andar.setText(f"Posição atual: {pos:.2f} m  ({andar})")

            self.visor_numero.setText(andar)

            if not terminou:
                if not self.em_parada_final:
                    if self.simulador.sp > pos:
                        self.visor_direcao.setText("▲")
                    elif self.simulador.sp < pos:
                        self.visor_direcao.setText("▼")
                    else:
                        self.visor_direcao.setText("-")
            else:
                self.em_parada_final = True
                self.visor_direcao.setText("-")
                self.timer.stop()
                self.parada_timer.start(500)


    def finalizar_parada(self):
        self.simulacao_ativa = False
        self.em_parada_final = False
        self.timer.stop()
        self.visor_direcao.setText("-")

    def parar_emergencia(self):
        self.simulacao_ativa = False
        self.timer.stop()
        if self.simulador:
            self.todos_tempos.append(self.simulador.tempo)
            self.todas_posicoes.append(self.simulador.posicao_atual)
            self.curva.setData(self.todos_tempos, self.todas_posicoes, clear=True)
            self.indicador_andar.setText("Movimento interrompido por STOP.")

    def altura_para_andar(self, altura):
        mais_proximo = min(self.andares.items(), key=lambda x: abs(x[1] - altura))
        return mais_proximo[0]

    def reiniciar_grafico(self):
        self.timer.stop()
        self.simulacao_ativa = False
        self.todos_tempos = [0.0]
        self.todas_posicoes = [0.0]
        self.plot_widget.clear()
        self.plot_widget.setXRange(0, 100)
        self.plot_widget.setYRange(0, 36)
        self.plot_widget.getPlotItem().getAxis('bottom').setTickSpacing(5, 5)
        self.curva = self.plot_widget.plot(self.todos_tempos, self.todas_posicoes, pen=pg.mkPen('b', width=2))
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
