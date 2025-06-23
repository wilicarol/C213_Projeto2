import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QGridLayout
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

        self.init_ui()

        # Integração MQTT
        self.mqtt = MqttElevadorClient(self.iniciar_simulacao)
        self.mqtt.conectar()

    def init_ui(self):
        layout = QVBoxLayout()

        # Estilo visual claro
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
            QPushButton:hover {
                background-color: #e6f2ff;
            }
            QLabel {
                font-size: 15px;
                font-weight: bold;
            }
        """)

        self.label = QLabel("Selecione o andar de destino:")
        layout.addWidget(self.label)

        # Andares
        grid = QGridLayout()
        self.andares = {
            "Térreo": 4,
            "1º andar": 7,
            "2º andar": 10,
            "3º andar": 13,
            "4º andar": 16,
            "5º andar": 19,
            "6º andar": 22,
            "7º andar": 25,
            "8º andar": 28
        }

        for i, (nome, altura) in enumerate(reversed(self.andares.items())):
            btn = QPushButton(nome)
            btn.clicked.connect(lambda checked, h=altura: self.iniciar_simulacao(h))
            grid.addWidget(btn, i // 2, i % 2)

        layout.addLayout(grid)

        # Indicador de posição
        self.indicador_andar = QLabel("Posição atual: - m")
        layout.addWidget(self.indicador_andar)

        # Botão de reinício
        self.btn_reiniciar = QPushButton("Reiniciar gráfico")
        self.btn_reiniciar.clicked.connect(self.reiniciar_grafico)
        layout.addWidget(self.btn_reiniciar)

        # Gráfico
        self.plot_widget = pg.PlotWidget(title="Movimento da Cabine em Tempo Real")
        self.plot_widget.setBackground("w")
        self.plot_widget.setLabel('left', 'Altura', units='m')
        self.plot_widget.setLabel('bottom', 'Tempo', units='s')
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.enableAutoRange(x=False, y=False)

        self.curva = self.plot_widget.plot([], [], pen=pg.mkPen('b', width=2))
        layout.addWidget(self.plot_widget)

        self.setLayout(layout)

    def iniciar_simulacao(self, destino):
        self.simulador = SimuladorElevador(destino)

        # Limpa o gráfico completamente
        self.plot_widget.clear()

        # Cria nova curva limpa e reseta histórico
        self.curva = pg.PlotDataItem([], [], pen=pg.mkPen('b', width=2))
        self.plot_widget.addItem(self.curva)

        # Resetar histórico no simulador
        self.simulador.tempo = 0.0
        self.simulador.historico_tempo = [0.0]
        self.simulador.historico_posicao = [self.simulador.posicao_atual]

        # Faixa inicial
        self.plot_widget.setXRange(0, 30)
        ymin = min(self.simulador.posicao_atual, destino) - 2
        ymax = max(self.simulador.posicao_atual, destino) + 2
        self.plot_widget.setYRange(ymin, ymax)

        # Linha vermelha no setpoint
        self.plot_widget.addLine(y=destino, pen=pg.mkPen('r', style=pg.QtCore.Qt.DashLine))

        self.timer.start(int(self.simulador.Ts * 1000))

    def atualizar_simulacao(self):
        if self.simulador and self.simulador.passo():
            x = self.simulador.historico_tempo
            y = self.simulador.historico_posicao
            self.curva.setData(x, y, clear=False)

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
        self.plot_widget.clear()
        self.curva = pg.PlotDataItem(pen=pg.mkPen('b', width=2))
        self.plot_widget.addItem(self.curva)

        if self.simulador:
            y = self.simulador.posicao_atual
            self.plot_widget.setXRange(0, 30)
            self.plot_widget.setYRange(y - 2, y + 2)
            self.indicador_andar.setText(f"Gráfico reiniciado. Posição atual: {y:.2f} m")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = ElevadorWindow()
    janela.resize(850, 600)
    janela.show()
    sys.exit(app.exec_())
