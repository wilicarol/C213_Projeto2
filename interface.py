import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from simulador import SimuladorElevador

class ElevadorApp:
    def __init__(self, master):
        self.master = master
        master.title("Simulador de Elevador em Tempo Real")
        self.simulador = None
        self.canvas = None

        self.label = tk.Label(master, text="Selecione o andar de destino:", font=("Arial", 14))
        self.label.pack(pady=10)

        self.buttons_frame = tk.Frame(master)
        self.buttons_frame.pack()

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

        for andar, altura in reversed(self.andares.items()):
            btn = tk.Button(self.buttons_frame, text=andar, width=15,
                            command=lambda h=altura: self.iniciar_simulacao(h))
            btn.pack(pady=2)

        self.canvas_frame = tk.Frame(master)
        self.canvas_frame.pack(pady=20)

    def iniciar_simulacao(self, destino):
        self.simulador = SimuladorElevador(destino)

        self.fig, self.ax = plt.subplots(figsize=(7, 4))
        self.ax.set_title('Movimento da Cabine em Tempo Real')
        self.ax.set_xlabel('Tempo [s]')
        self.ax.set_ylabel('Altura [m]')
        self.ax.axhline(y=destino, linestyle='--', color='red', label='SetPoint')
        self.line, = self.ax.plot([], [], 'b-', label='Posição da Cabine')
        self.ax.legend()
        self.ax.grid()

        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

        self.atualizar_grafico()

    def atualizar_grafico(self):
        if self.simulador and self.simulador.passo():
            self.line.set_data(self.simulador.historico_tempo, self.simulador.historico_posicao)
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()
            self.master.after(int(self.simulador.Ts * 1000), self.atualizar_grafico)
        else:
            print("Simulação finalizada.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ElevadorApp(root)
    root.mainloop()
