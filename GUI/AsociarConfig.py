#Interfaz grafica para ingresar el numero de serie del equipo
import sys
import os
from PyQt5.QtWidgets import QMainWindow,QApplication,QDialog,QTableWidgetItem
from PyQt5.QtCore import pyqtSignal
import sys
from PyQt5 import uic
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
#from CONTROLADORES.BBDD import SMVA_DB

class AsociarConfiguracionInstrumento(QDialog):
    def __init__(self,bbdd=None,id_protocolos=1):
        """
        Abre la UI para ingresar configuracion, esta la obtiene a partir del id seleccionado

        """
        super().__init__() #Llamo a todas las funciones y metodos de la clase QDialog
        uic.loadUi(r'GUI\AsociarConfigInstrum.ui', self)  # Carga el archivo log.ui
        self.bbdd = bbdd
        self.ID_PROTOCOLOS = id_protocolos

        self.config_seleccionada = None

        self.updateTablaConfig()
        self.TablaExistentes.clicked.connect(self.updateConfigSeleccionada)
        self.Avanzar.clicked.connect(self.setConfig)
    def updateTablaConfig(self):
        """
        Actualiza la tabla principal
        """
        #Actualizo la configuracion
        configuracion =self.bbdd.getConfigPuestoaPartirdeIdDelProtocolo(id =self.ID_PROTOCOLOS)
        self.TablaExistentes.setRowCount(len(configuracion))
        for row,config in enumerate(configuracion):   
            self.TablaExistentes.setItem(row, 0, QTableWidgetItem(str(config[0])))
            self.TablaExistentes.setItem(row, 1, QTableWidgetItem(str(config[1])))
            self.TablaExistentes.setItem(row, 2, QTableWidgetItem(str(config[4])))
    
    def updateConfigSeleccionada(self):

        currentRow = self.TablaExistentes.currentRow() #Con esto selecciono el indice de la fila correspondiente desde 0 a N-1 
        if currentRow == -1:  # Verifica si no hay ninguna fila seleccionada
            print("No se ha seleccionado ninguna fila nabo, ¿otra vez por aca?.") #Este mensaje serie un easter egg, no deberia aparecer
            print("Created by Juan Cruz Noya 28/03/2025")
            return
        rowValue = [
            self.TablaExistentes.item(currentRow, col).text()
            for col in range(self.TablaExistentes.columnCount())
        ] #Me devuelve una lista con los valores seleccionado en ese indice
        print(rowValue)

        self.config_seleccionada = rowValue

    def setConfig(self):
        if self.config_seleccionada != None:
            idconfig = self.config_seleccionada[0]

            self.bbdd.setConfigEnProtocolo(id_config=idconfig,id_protocolo=self.ID_PROTOCOLOS)
            self.close()  # Cierra la ventana
        else:
            pass
if __name__ == "__main__":
    app = QApplication(sys.argv)
    #bd = SMVA_DB()
    #mw = AsociarConfiguracionInstrumento(bd,id_protocolos=25017)
    #mw.show()
    #sys.exit(app.exec_())