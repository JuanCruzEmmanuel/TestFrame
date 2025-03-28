#Interfaz grafica para ingresar el numero de serie del equipo
import sys
import os
from PyQt5.QtWidgets import QMainWindow,QApplication,QDialog,QTableWidgetItem
from PyQt5.QtCore import pyqtSignal
import sys
from PyQt5 import uic
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from CONTROLADORES.BBDD import SMVA_DB

class IngresarNumeroSerie(QDialog):
    def __init__(self,bbdd=None,id_protocolos=1,id_protocolo=1):
        """
        Abre la UI para ingresar numero de serie

        """
        super().__init__() #Llamo a todas las funciones y metodos de la clase QDialog
        uic.loadUi(r'GUI\SeleccionarNumeroSerie.ui', self)  # Carga el archivo log.ui
        self.id_protocolos = id_protocolos
        self.id_protocolo = id_protocolo
        self.LASTID = None #Id que se crea
        self.bbdd = bbdd
        self.info_modulo = None #Auxiliar 1
        self.info_modulo_ns = None #Auxiliar para luego subir en caso de que se ingrese un nuevo valor
        self.showModulos()

        self.TablaConfig.clicked.connect(self.showModulosConNS)
        self.TablaNumeroSerie.clicked.connect(self.updateValues)
        self.NewSerialNumber.clicked.connect(self.updateNumeroSerie)
    def updateNumeroSerie(self):
        """
        Se encarga de actualizar self.info_modulo con el numero de serie para luego subirlo
        """
        if self.info_modulo != None:
            numeroSerie = self.SerialNumber.toPlainText() #Es el metodo que usa el QTextEdit para tener el valor que tiene la celda
            if len(self.info_modulo)==5:
                self.info_modulo.append(numeroSerie)
            elif len(self.info_modulo)>5:
                self.info_modulo[5]=numeroSerie
            
            self.info_modulo_ns[4]=numeroSerie
            if self.bbdd.checkIngresadoExiste(self.info_modulo_ns):
                self.showModulos()
            else:
                self.showModulos()
                #En caso que no exista se debe subir.....
                self.LASTID = self.bbdd.insertNuevoModulo(self.info_modulo_ns)
            
    def showModulos(self):
        """
        Muestra los valores de la tabla, con esta luego se seleccionara el codigo referente a los equipos/modulos
        """
        if self.info_modulo ==None:
            info_modulo = self.bbdd.getModuloFromIds(self.id_protocolos,self.id_protocolo) #Esto me devuelve: idmodulos_endisegno,Nombre,Codigo,protocolo_protocolos_idProtocolos,modulos_endisegno_idmodulos_endisegno
            self.TablaConfig.setRowCount(len(info_modulo))
            self.TablaConfig.setItem(0, 0, QTableWidgetItem(str(info_modulo[0])))
            self.TablaConfig.setItem(0, 1, QTableWidgetItem(str(info_modulo[1])))
            self.TablaConfig.setItem(0, 2, QTableWidgetItem(str(info_modulo[2])))
            self.TablaConfig.setItem(0, 3, QTableWidgetItem(""))

            self.info_modulo = info_modulo
        else:
            self.TablaConfig.setRowCount(len(self.info_modulo))
            self.TablaConfig.setItem(0, 0, QTableWidgetItem(str(self.info_modulo[0])))
            self.TablaConfig.setItem(0, 1, QTableWidgetItem(str(self.info_modulo[1])))
            self.TablaConfig.setItem(0, 2, QTableWidgetItem(str(self.info_modulo[2])))
            self.TablaConfig.setItem(0, 3, QTableWidgetItem(str(self.info_modulo[5])))

    def showModulosConNS(self):
        print(self.info_modulo)
        if self.info_modulo !=None:
            getInfoNS = self.bbdd.getModulosFromCodigo(self.id_protocolos,self.id_protocolo)
            self.TablaNumeroSerie.setRowCount(len(getInfoNS))
            for row, values in enumerate(getInfoNS):

                self.TablaNumeroSerie.setItem(row, 0, QTableWidgetItem(str(values[0])))
                self.TablaNumeroSerie.setItem(row, 1, QTableWidgetItem(str(values[1])))
                self.TablaNumeroSerie.setItem(row, 2, QTableWidgetItem(str(values[2])))
                self.TablaNumeroSerie.setItem(row, 3, QTableWidgetItem(str(values[4])))
                self.TablaNumeroSerie.setItem(row, 4, QTableWidgetItem(str(values[5])))
                self.TablaNumeroSerie.setItem(row, 5, QTableWidgetItem(str(values[3])))
                self.TablaNumeroSerie.setItem(row, 6, QTableWidgetItem(str(values[6])))

    def updateValues(self):
        currentRow = self.TablaNumeroSerie.currentRow() #Con esto selecciono el indice de la fila correspondiente desde 0 a N-1 
        if currentRow == -1:  # Verifica si no hay ninguna fila seleccionada
            print("No se ha seleccionado ninguna fila nabo.") #Este mensaje serie un easter egg, no deberia aparecer
            print("Created by Juan Cruz Noya 28/03/2025")
            return
        rowValue = [
            self.TablaNumeroSerie.item(currentRow, col).text()
            for col in range(self.TablaNumeroSerie.columnCount())
        ] #Me devuelve una lista con los valores seleccionado en ese indice
        print(rowValue)
        self.Nombre.setText(rowValue[2])
        self.Codigo.setText(rowValue[3])
        self.SerialNumber.setText(rowValue[4])

        self.info_modulo_ns = rowValue #id,categoria,nombre,codigo,ns,orden,Estado
if __name__ == "__main__":
    app = QApplication(sys.argv)
    bd = SMVA_DB()
    mw = IngresarNumeroSerie(bd,204381,16067)
    mw.show()
    sys.exit(app.exec_())