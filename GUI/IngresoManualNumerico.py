from PyQt5.QtWidgets import QMainWindow,QApplication,QDialog
from PyQt5.QtCore import pyqtSignal
import sys
from PyQt5 import uic

class IngresoManualNumerico(QDialog):
    Mensaje_enviado = pyqtSignal(str) #Señal que se encarga de emitir el resultado correcto
    def __init__(self,texto="EMPTY",min=0,max=0):
        super().__init__() #Llamo a todas las funciones y metodos de la clase QDialog
        uic.loadUi(r'GUI\IngresoManualNumerico.ui', self)  # Carga el archivo log.ui
        self.__TEXTO__PANTALLA = texto #Seteo estos atributos de manera "oculta"
        self.__VAL_MIN = min #Seteo estos atributos de manera "oculta"
        self.__VAL_MAX = max #Seteo estos atributos de manera "oculta"
        self.resultado = None
        self.InfoPaso.setText(self.__TEXTO__PANTALLA)
        self.ValMin.setText(str(self.__VAL_MIN))
        self.ValMax.setText(str(self.__VAL_MAX))
        self.Enviar.clicked.connect(self.sendMensaje)


    def setMensaje(self,text,min,max):
        """
        Setea los parametros que van a verse en pantalla
        :text: Mensaje que se observara en pantalla
        :min: 
        """
        self.__TEXTO__PANTALLA = text
        self.__VAL_MIN = min 
        self.__VAL_MAX = max 

    def sendMensaje(self):
        """
        Se encarga de emitir el mensaje a la main root
        """
        mensaje = self.Val.text()
        if mensaje == "":
            pass
        else:
            self.resultado = mensaje
            self.Mensaje_enviado.emit(mensaje)
            self.close()

    def getResultado(self):

        return self.resultado
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = IngresoManualNumerico()
    mw.show()
    sys.exit(app.exec_())