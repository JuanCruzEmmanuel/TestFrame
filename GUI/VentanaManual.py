from PyQt5 import QtWidgets, uic
import sys
import os
import json
from PyQt5.QtWidgets import QTableWidgetItem
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
class Ventana_Manual(QtWidgets.QDialog):
    def __init__(self,protocolo = None):
        super().__init__()
        uic.loadUi("GUI/Manual.ui", self)  # Reemplaza con el nombre real del archivo .ui
        self.protocolo = protocolo
        #self.avanzar_paso_flag = False
        # Establecer la página inicial (por índice o nombre)
        self.stackedWidget.setCurrentWidget(self.principal)
        if self.protocolo == None:
            self.load_json()
        # Conectar el botón con la función para cambiar de página
        self.SELECCION_FILAS_COLUMNAS.clicked.connect(self.ir_a_seleccion)
        self.Retroceder.clicked.connect(self.ir_a_principal)

        self.Bloques.clicked.connect(self.show_pasos)
        self.Pasos.clicked.connect(self.get_indice_paso)
        self.Avanzar.clicked.connect(self.returned_value)
        self.PASO_AVANCE.clicked.connect(self.avanzar_paso)
        self.i = None
        self.j = None

    def avanzar_paso(self):
        self.reset_indices
        
        #self.avanzar_paso_flag = True
        self.close()  # Cierra la ventana
    def ir_a_seleccion(self):
        self.show_tabla()
        self.stackedWidget.setCurrentWidget(self.Seleccion)
    def ir_a_principal(self):
        self.stackedWidget.setCurrentWidget(self.principal)
        self.reset_indices()
    def reset_indices(self):
        self.i = None
        self.j = None
    def load_json(self):
        with open("_TEMPS_\protocolo_a_ejecutar.json","r") as file:
            self.protocolo = json.load(file)

    def show_tabla(self):
        self.Bloques.setRowCount(len(self.protocolo))
        for row, protocolo in enumerate(self.protocolo):
            self.Bloques.setItem(row, 0, QTableWidgetItem(str(protocolo["Nombre"])))
            self.Bloques.setItem(row, 1, QTableWidgetItem(str(protocolo["Resultado"])))
    def show_pasos(self):
        currentRow = self.Bloques.currentRow()
        self.i = currentRow
        pasos = self.protocolo[self.i]["Pasos"]
        self.Pasos.setRowCount(len(pasos))
        for row, paso in enumerate(pasos):

            self.Pasos.setItem(row, 0, QTableWidgetItem(str(paso["Nombre"])))
            self.Pasos.setItem(row, 1, QTableWidgetItem(str(paso["Resultado"])))
            self.Pasos.setItem(row, 2, QTableWidgetItem(str(paso["Comandos"])))
    def get_indice_paso(self):
        currentRow = self.Pasos.currentRow()
        self.j = currentRow

    def returned_value(self):
        if self.i !=None and self.j !=None:
            self.close()  # Cierra la ventana
if __name__ =="__main__":

    # Ejecutar la aplicación
    app = QtWidgets.QApplication(sys.argv)
    dialog = Ventana_Manual()
    dialog.exec_()
    print(dialog.i,dialog.j)

    dialog.reset_indices()

    print(dialog.i,dialog.j)

