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
    #VARIABLES Y AUXILIARES
    win.worker = None #Nuevamente creo el placeholder simplemente por una cuestion "etica" y mostrar que *aca* se usa
    win.protocolo_a_ejecutar = None #El protocolo que se va a ejecutar
    win._cantidadBloques = None #No recuerdo si lo utilizo en algo... tal vez es innecesaria
    win.Automatico.setCheckable(True) #Al iniciar creo la ejecucion automatica
    win.Manual.setCheckable(False) #Fuerzo de inicio a estar en automatico (manual=false)
    win.LISTA_PASOS_EN_EJECUCION =[]
    win.PASO = None
    win.paso_ejecucion = ""
    win.bloque_ejecucion = ""
    win.temp_msg = None
    win.lista_valores_temp =None
    win.FLAG_MANUAL_SALTO = False

    ###########
    win.NUMERICO_TEXTO = None

    #LAMBDAS DE ARRANQUE
    win.cargarDatos = lambda: cargarDatos(win)
    win.mostrar_bloques_protocolo = lambda: mostrar_bloques_protocolo(win) #PreCargo la funcion
    win.getProtocoloEjecutar = lambda: getProtocoloEjecutar(win)
    win.resetPasosEnEjecucion = lambda: resetPasosEnEjecucion(win)
    win.cambiar_automatico = lambda: cambiar_automatico(win)

    #FUNCION BOTONES
    win.Manual.clicked.connect(lambda: cambiar_manual(win))

    #SHORTCUTS (los nombres son meramente ilustrativos)
    shortcut_manual = QShortcut(QKeySequence("space"), win).activated.connect(lambda: cambiar_manual(win))
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
@pyqtSlot()
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

def getProtocoloEjecutar(win):
    return win.protocolo_a_ejecutar

def resetPasosEnEjecucion(win):
    win.LISTA_PASOS_EN_EJECUCION = []

def cambiar_automatico(win):
    win.worker.selectModo(modo="AUTOMATICO")

def cambiar_manual(win):
    win.worker.selectModo(modo="MANUAL")
    win.worker.pausarProtocolo() #Pausa la ejecucion
    win.worker.pausaSuperior()
    app = Ventana_Manual(protocolo=win.protocolo_a_ejecutar,MODO_FUNCIONAMIENTO="MANUAL")

    app.exec_()
    #print(app.i,app.j)
    if win.FLAG_MANUAL_SALTO:
        #print("Indicador_1")
        if app.i == None:
            #print("Indicador_5")
            if win.NUMERICO_TEXTO=="TEXTO": #En el caso que se haya saltado desde manual texto
                win.mostrarPopup(mensaje=win.temp_msg)
            else: #En caso que se haya saltado desde manual numerico
                win.mostrarPopupNumerico(lista_valores=win.lista_valores_temp)
            
            if app.MODO =="AUTOMATICO":
                win.cambiar_automatico()
        else:
            #print("Indicador_16")
            win.worker.setBloquePasoManual(i = app.i, j= app.j)
            win.worker.continuarSuperior()
            if app.MODO =="AUTOMATICO":
                win.cambiar_automatico()
        #print("Indicador_6")
        win.FLAG_MANUAL_SALTO=False #Debo desactivar la bandera
    else:
        #print("Indicador_2")
        win.worker.setBloquePasoManual(i = app.i, j= app.j)
        win.worker.continuarSuperior()
        if app.MODO =="AUTOMATICO":
            win.cambiar_automatico()
