import json
#from time import sleep
#from datetime import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from PyQt5.QtWidgets import QVBoxLayout, QDialog, QTableWidgetItem
from PyQt5.QtCore import QEventLoop, QThread, pyqtSignal, pyqtSlot,Qt
#from PyQt5.QtGui import QColor, QBrush
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
    win.tiempo_paso = 0 #Variable que controla para graficar tiempo entre paso
    win.tiempo_total = 0 #Variable que controla para graficar tiempo total
    win.DEVICES_POOL = {} # Variable que Controla los equipos encendidos
    ###########
    win.NUMERICO_TEXTO = None

    #LAMBDAS DE ARRANQUE
    win.cargarDatos = lambda: cargarDatos(win)
    win.mostrar_bloques_protocolo = lambda: mostrar_bloques_protocolo(win) #PreCargo la funcion
    win.getProtocoloEjecutar = lambda: getProtocoloEjecutar(win)
    win.resetPasosEnEjecucion = lambda: resetPasosEnEjecucion(win)
    win.cambiar_automatico = lambda: cambiar_automatico(win)
    win.cambiar_manual = lambda: cambiar_manual(win)
    win.detenerEjecucion = lambda: detenerEjecucion(win)
    win.condicional_manual = lambda: condicional_manual(win)
    
    win.actualizarLog = lambda mensaje: actualizarLog(win, mensaje)
    win.actualizarSecuenciaPaso = lambda mensaje: actualizarSecuenciaPaso(win, mensaje)
    win.actualizarSecuenciaBloque = lambda mensaje: actualizarSecuenciaBloque(win, mensaje)
    win.actualizarNombreBloque = lambda mensaje: actualizarNombreBloque(win, mensaje)
    win.finalizarEjecucion = lambda: finalizarEjecucion(win)
    win.protocoloDetenido = lambda: protocoloDetenido(win)
    win.mostrarPopup = lambda mensaje: mostrarPopup(win, mensaje)
    win.mostrarPopupNumerico = lambda lista: mostrarPopupNumerico(win, lista)
    win.procesarResultadoPopup = lambda valor: procesarResultadoPopup(win, valor)    

    win.set_tiempo = lambda tiempo_paso,tiempo_total : set_tiempo(win,tiempo_paso,tiempo_total)
    #FUNCION BOTONES
    win.Manual.clicked.connect(lambda: cambiar_manual(win))

    #SHORTCUTS (los nombres son meramente ilustrativos)
    win.shortcut_manual = QShortcut(QKeySequence("space"), win).activated.connect(lambda: cambiar_manual(win))
    
    #####CONTROL DE WIGDETS
    for widget in [win.imagen_progreso1, win.imagen_progreso2]: #Funcion que le agrega layout para muestrear luego los dashes
        layout = QVBoxLayout()
        widget.setLayout(layout)
    
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
        win.TablaBloques.setItem(row, 4, QTableWidgetItem(values["Operador"]))

def getProtocoloEjecutar(win):
    return win.protocolo_a_ejecutar

def resetPasosEnEjecucion(win):
    win.LISTA_PASOS_EN_EJECUCION = []

def cambiar_automatico(win):
    win.worker.selectModo(modo="AUTOMATICO")
    win.graph_auto = True
def cambiar_manual(win):
    win.graph_auto = False
    win.worker.selectModo(modo="MANUAL")
    win.worker.pausarProtocolo() #Pausa la ejecucion
    win.worker.pausaSuperior()
    app = Ventana_Manual(protocolo=win.protocolo_a_ejecutar,MODO_FUNCIONAMIENTO="MANUAL")

    app.exec_()
    win.update_graph() #En caso manual, que grafique despues
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
            
def condicional_manual(win):
    win.FLAG_MANUAL_SALTO = True
    win.cambiar_manual()
    
#mostrar_pasos_protocolo() la active en main_windows por una cuestion de facilidad

def detenerEjecucion(win):
    if win.worker is not None and win.worker.isRunning():
        win.worker.stop()
        win.descripcionPaso.setText("Deteniendo ejecución...")
        
@pyqtSlot(str)
def actualizarLog(win, mensaje):
    win.descripcionPaso.setText(mensaje)
@pyqtSlot(str)
def actualizarSecuenciaPaso(win, mensaje):
    win.nPasos.setText(mensaje)
@pyqtSlot(str)
def actualizarSecuenciaBloque(win, mensaje):
    win.nBloque.setText(mensaje)

@pyqtSlot(str)
def actualizarNombreBloque(win, mensaje):
    win.bloqueEjecucion.setText(mensaje)
@pyqtSlot()
def finalizarEjecucion(win):
    win.descripcionPaso.setText("Protocolo completado.")
    print("FIN PROTOCOLO") #ACA SE DEBE ENVIAR UNA SEÑAL

@pyqtSlot()
def protocoloDetenido(win):
    win.descripcionPaso.setText("Protocolo detenido.")

@pyqtSlot(str)
def mostrarPopup(win, mensaje):
    win.NUMERICO_TEXTO="TEXTO"
    win.temp_msg = mensaje
    win.worker.pausarProtocolo() #Pausa la ejecucion
    win.manual_window = ingresoManual(mensaje_protocolo=mensaje)
    win.manual_window.sgn_saltar.connect(win.condicional_manual)
    win.manual_window.Mensaje_enviado.connect(win.procesarResultadoPopup)
    win.manual_window.show()
    
@pyqtSlot(list)
def mostrarPopupNumerico(win,lista_valores):
    win.NUMERICO_TEXTO="NUMERICO"
    win.lista_valores_temp = lista_valores
    win.worker.pausarProtocolo() #Pausa la ejecucion
    win.manual_window_numerico = IngresoManualNumerico(texto=lista_valores[0],min=lista_valores[1],max=lista_valores[2])
    win.manual_window_numerico.sgn_saltar.connect(win.condicional_manual)
    win.manual_window_numerico.Mensaje_enviado.connect(win.procesarResultadoPopup)
    win.manual_window_numerico.show()


@pyqtSlot(str)
def procesarResultadoPopup(win, valor):
    print(f"Resultado recibido desde popup: {valor}")
    #self.loop.quit()
    win.worker.manejarResultado(valor)  # Pasar el resultado al hilo secundario
@pyqtSlot(list,list)
def set_tiempo(win,tiempo_paso,tiempo_total):
    win.tiempo_paso =tiempo_paso
    #print(win.tiempo_paso)
    win.tiempo_total = tiempo_total
    #print(win.tiempo_total)
    if win.graph_auto: #Para que no se lagge
        win.update_graph()