from PyQt5.QtWidgets import QMainWindow,QApplication
from PyQt5.QtCore import pyqtSignal
import sys
from PyQt5 import uic


class ingresoManual(QMainWindow):
    Mensaje_enviado = pyqtSignal(str)  # Señal personalizada
    def __init__(self, mensaje_protocolo = "NO HAY MENSAJE"):
        super().__init__()
        uic.loadUi(r'GUI\IngresoManual.ui', self)  # Carga el archivo log.ui
        self.texto = mensaje_protocolo
        self.InfoPaso.setText(self.texto)
        self.AutoOk.clicked.connect(self.enviarOk)
        self.Enviar.clicked.connect(self.sendMensaje)
        self.resultado = None

    def setMensaje(self,text):

        self.texto = text
    def sendMensaje(self):
        mensaje = self.Respuesta.text()
        if mensaje == "":
            pass
        else:
            self.resultado = mensaje
            self.Mensaje_enviado.emit(mensaje)
            self.close()
    def enviarOk(self):

        """
        devuelve un OK

        :return:
        """
        self.resultado = "OK"
        self.Mensaje_enviado.emit("OK")
        self.close()

    def getResultado(self):

        return self.resultado

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = ingresoManual()
    mw.show()
    sys.exit(app.exec_())