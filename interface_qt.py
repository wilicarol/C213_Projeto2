import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel,
    QGridLayout, QComboBox
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

        self.usuario_tipo = "Morador"
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
                padding: 6px 12px;
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

        tipo_label = QLabel("Tipo de usuário:")
        self.combo_usuario = QComboBox()
        self.combo_usuario.addItems(["Morador", "Serviçal"])
        self.combo_usuario.currentTextChanged.connect(self.atualizar_botoes)
        layout.addWidget(tipo_label)
        layout.addWidget(self.combo_usuario)

        self.label = QLabel("Selecione o andar de destino:")
        layout.addWidget(self.label)

        self.grid = QGridLayout()
        self.botoes_andar = {}
        self.atualizar_botoes()
        layout.addLayout(self.grid)

        self.indicador_andar = QLabel("Posição atual: - m")
        layout.addWidget(self.indicador_andar)

        self.btn_reiniciar = QPushButton("Reiniciar gráfico")
        self.btn_reiniciar.clicked.connect(self.reiniciar_grafico)
        layout.addWidget(self.btn_reiniciar)

        self.plot_widget = pg.PlotWidget(title="Movimento da Cabine em Tempo Real")
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

    def atualizar_botoes(self):
        self.usuario_tipo = self.combo_usuario.currentText()
        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().setParent(None)

        self.botoes_andar.clear()
        acessivel = lambda nome: True if self.usuario_tipo == "Serviçal" else nome not in ["Subsolo", "Técnico"]

        for i, (nome, altura) in enumerate(reversed(self.andares.items())):
            btn = QPushButton(nome)
            btn.setEnabled(acessivel(nome))
            btn.clicked.connect(lambda checked, h=altura: self.iniciar_simulacao(h))
            self.grid.addWidget(btn, i // 2, i % 2)
            self.botoes_andar[nome] = btn

    def iniciar_simulacao(self, destino):
        posicao_atual = self.simulador.posicao_atual if self.simulador else 0.0
        tempo_base = self.todos_tempos[-1] if self.todos_tempos else 0.0

        self.simulador = SimuladorElevador(destino, posicao_inicial=posicao_atual)
        self.simulador.tempo = tempo_base
        self.simulador.historico_tempo = [tempo_base]
        self.simulador.historico_posicao = [posicao_atual]

        self.plot_widget.addLine(y=destino, pen=pg.mkPen('r', style=pg.QtCore.Qt.DashLine))
        self.timer.start(int(self.simulador.Ts * 1000))

    def atualizar_simulacao(self):
        if self.simulador and self.simulador.passo():
            self.todos_tempos.append(self.simulador.historico_tempo[-1])
            self.todas_posicoes.append(self.simulador.historico_posicao[-1])
            self.curva.setData(self.todos_tempos, self.todas_posicoes, clear=True)

            pos = self.simulador.posicao_atual
            andar = self.altura_para_andar(pos)
            self.indicador_andar.setText(f"Posição atual: {pos:.2f} m  ({andar})")
        else:
            self.timer.stop()

    def altura_para_andar(self, altura):
        for nome, valor in self.andares.items():
            if abs(altura - valor) <= 1.0:
                return nome
        return "Entre andares"

    def reiniciar_grafico(self):
        self.timer.stop()
        self.todos_tempos = []
        self.todas_posicoes = []
        self.plot_widget.clear()
        self.plot_widget.setXRange(0, 100)
        self.plot_widget.setYRange(0, 36)
        self.plot_widget.getPlotItem().getAxis('bottom').setTickSpacing(5, 5)
        self.curva = pg.PlotDataItem(pen=pg.mkPen('b', width=2))
        self.plot_widget.addItem(self.curva)

        if self.simulador:
            y = self.simulador.posicao_atual
            self.indicador_andar.setText(f"Gráfico reiniciado. Posição atual: {y:.2f} m")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = ElevadorWindow()
    janela.resize(850, 600)
    janela.show()
    sys.exit(app.exec_())
