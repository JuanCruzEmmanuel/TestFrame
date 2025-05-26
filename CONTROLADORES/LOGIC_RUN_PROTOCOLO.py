import json
from time import sleep
from datetime import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from PyQt5.QtWidgets import QApplication, QDialog, QTableWidgetItem
from PyQt5.QtCore import QEventLoop, QThread, pyqtSignal, pyqtSlot,Qt
from PyQt5.QtGui import QColor, QBrush
from PyQt5 import uic
from GUI.IngresoManual import ingresoManual
from GUI.IngresoManualNumerico import IngresoManualNumerico
from CONTROLADORES.DriverInstrumentosSMVA import driverInstrumentos
from GUI.VentanaManual import Ventana_Manual
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut

def configurar_logica_run_protocolo(win):
    win.protocolo_a_ejecutar = None #El protocolo que se va a ejecutar
    win._cantidadBloques = None #No recuerdo si lo utilizo en algo... tal vez es innecesaria
    win.Automatico.setCheckable(True) #Al iniciar creo la ejecucion automatica
    win.Manual.setCheckable(False) #Fuerzo de inicio a estar en automatico (manual=false)

    win.cargarDatos = lambda: cargarDatos(win)
    win.mostrar_bloques_protocolo = lambda: mostrar_bloques_protocolo(win) #PreCargo la funcion
def cargarDatos(win):
    with open("_TEMPS_/protocolo_a_ejecutar.json", "r", encoding="utf-8", errors="ignore") as file:
        N = 0 #He visto que en la PC endurancia existe un error "raro" y creo que esta podria solucionar ese error
        while N==0:
            try:
                win.protocolo_a_ejecutar = json.load(file)
                win._cantidadBloques = len(win.protocolo_a_ejecutar)
                win.mostrar_bloques_protocolo()
                N+=1
            except:
                N=0
#@pyqtSlot()
def mostrar_bloques_protocolo(win):
    win.TablaBloques.setRowCount(len(win.protocolo_a_ejecutar))
    win.TablaBloques.setColumnCount(5)
    win.TablaBloques.setHorizontalHeaderLabels(["#COUNT", "ID", "NOMBRE", "RESULTADO", "APROBADOR"])
    for row, values in enumerate(win.protocolo_a_ejecutar):
        win.TablaBloques.setItem(row, 0, QTableWidgetItem(str(row)))
        win.TablaBloques.setItem(row, 1, QTableWidgetItem(str(values["ProtocoloID"])))
        win.TablaBloques.setItem(row, 2, QTableWidgetItem(values["Nombre"]))
        win.TablaBloques.setItem(row, 3, QTableWidgetItem(values["Resultado"]))
        win.TablaBloques.setItem(row, 4, QTableWidgetItem(" "))

if __name__ =="__main__":
    with open("_TEMPS_/protocolo_a_ejecutar.json", "r", encoding="utf-8", errors="ignore") as file:
        N = 0 #He visto que en la PC endurancia existe un error "raro" y creo que esta podria solucionar ese error
        while N==0:
            try:
                protocolo_a_ejecutar = json.load(file)
                _cantidadBloques = len(protocolo_a_ejecutar)
                N+=1
            except:
                N=0
