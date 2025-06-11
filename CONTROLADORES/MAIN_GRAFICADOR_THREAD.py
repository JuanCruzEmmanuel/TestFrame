from matplotlib.figure import Figure
from numpy import array
from PyQt5.QtCore import QThread,pyqtSignal

class GraficadorThread(QThread):
    graficos_listos = pyqtSignal(Figure, Figure)  # Señal para devolver los gráficos

    def __init__(self, tiempo_paso, tiempo_total):
        super().__init__()
        self.tiempo_paso = tiempo_paso
        self.tiempo_total = tiempo_total

    def run(self):
        fig1 = self.generar_figura(self.tiempo_paso, "Tiempo entre pasos")
        fig2 = self.generar_figura(self.tiempo_total, "Tiempo total")
        self.graficos_listos.emit(fig1, fig2)  # Emitimos los gráficos listos

    def generar_figura(self, data, titulo):
        fig = Figure(figsize=(4, 3))
        fig.patch.set_alpha(0)
        ax = fig.add_subplot(111)
        ax.set_facecolor('none')
        X = range(len(data))
        Y = array(data) #Lo importo desde numpy
        ax.plot(X, Y)
        ax.set_title(titulo)
        ax.set_xlabel("Pasos")
        ax.set_ylabel("Tiempo")
        ax.grid(True)
        fig.tight_layout()
        return fig