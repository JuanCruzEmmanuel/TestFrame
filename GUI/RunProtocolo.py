import json
from time import sleep
from datetime import datetime
import sys
from PyQt5.QtWidgets import QApplication, QDialog, QTableWidgetItem
from PyQt5.QtCore import QEventLoop, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QBrush
from PyQt5 import uic
from GUI.IngresoManual import ingresoManual
from GUI.IngresoManualNumerico import IngresoManualNumerico
from CONTROLADORES.DriverInstrumentosSMVA import driverInstrumentos

class run(QDialog):

    def __init__(self, database=None):
        super().__init__()
        uic.loadUi(r'GUI\RunProtocolo.ui', self)
        self.database = database
        self.protocolo_a_ejecutar = None
        self._cantidadBloques = None
        self.PASO = None
        self.paso_ejecucion = ""
        self.bloque_ejecucion = ""
        self.worker = None
        self.LISTA_PASOS_EN_EJECUCION = []
        self.abortar.clicked.connect(self.detenerEjecucion)
        self.manual_window = None #Creo variable por las dudas de errores
        self.manual_window_numerico = None #Creo variables por la duda de errores
        

    @pyqtSlot()
    def mostrar_bloques_protocolo(self):
        self.TablaBloques.setRowCount(len(self.protocolo_a_ejecutar))
        self.TablaBloques.setColumnCount(5)
        self.TablaBloques.setHorizontalHeaderLabels(["#COUNT", "ID", "NOMBRE", "RESULTADO", "APROBADOR"])
        for row, values in enumerate(self.protocolo_a_ejecutar):
            self.TablaBloques.setItem(row, 0, QTableWidgetItem(str(row)))
            self.TablaBloques.setItem(row, 1, QTableWidgetItem(str(values["ProtocoloID"])))
            self.TablaBloques.setItem(row, 2, QTableWidgetItem(values["Nombre"]))
            self.TablaBloques.setItem(row, 3, QTableWidgetItem(values["Resultado"]))
            self.TablaBloques.setItem(row, 4, QTableWidgetItem(" "))

    @pyqtSlot(list)
    def mostrar_pasos_protocolo(self, lista_pasos_ejecutados):
        self.TablaPasos.setRowCount(len(lista_pasos_ejecutados))

        for row, values in enumerate(lista_pasos_ejecutados):
            estado = values["Estado"]
            color = QColor(135, 226, 64) if estado == "OK" else QColor(226, 88, 64)

            for col, key in enumerate(["OrdenDeSecuencia", "Nombre", "Estado", "ResultadoMinimo", "ResultadoMaximo", "Resultado"]):
                item = QTableWidgetItem(str(values[key]))  # Crear el item
                item.setBackground(QBrush(color))  # Aplicar color
                self.TablaPasos.setItem(row, col, item)  # Insertar en la tabla

    def cargarDatos(self):
        with open("_TEMPS_/protocolo_a_ejecutar.json", "r", encoding="utf-8", errors="ignore") as file:
            self.protocolo_a_ejecutar = json.load(file)
            self._cantidadBloques = len(self.protocolo_a_ejecutar)
            self.mostrar_bloques_protocolo()


    def getProtocoloEjecutar(self):
        return self.protocolo_a_ejecutar

    def resetPasosEnEjecucion(self):
        self.LISTA_PASOS_EN_EJECUCION = []

    def iniciarEjecucion(self):
        if self.worker is not None and self.worker.isRunning():
            self.descripcionPaso.setText("Ya se está ejecutando un protocolo.")
            return
        self.worker = WorkerThread(self.protocolo_a_ejecutar,database=self.database)
        self.worker.progreso.connect(self.actualizarLog)
        self.worker.terminado.connect(self.finalizarEjecucion)
        self.worker.detenido.connect(self.protocoloDetenido)
        self.worker.abrirPopup.connect(self.mostrarPopup)  # Conectar nueva señal
        self.worker.secuenciaPaso.connect(self.actualizarSecuenciaPaso)
        self.worker.secuenciaBloque.connect(self.actualizarSecuenciaBloque)
        self.worker.bloqueNombre.connect(self.actualizarNombreBloque)
        self.worker.pasosUpdate.connect(self.mostrar_pasos_protocolo)
        self.worker.UpdateTablaBloque.connect(self.cargarDatos) #Conecta la señal a actualizar tabla
        self.worker.abrirPopupNumerico.connect(self.mostrarPopupNumerico)
        self.worker.start()
        self.descripcionPaso.setText("Ejecutando protocolo...")

    def detenerEjecucion(self):
        if self.worker is not None and self.worker.isRunning():
            self.worker.stop()
            self.descripcionPaso.setText("Deteniendo ejecución...")

    @pyqtSlot(str)
    def actualizarLog(self, mensaje):
        self.descripcionPaso.setText(mensaje)
    @pyqtSlot(str)
    def actualizarSecuenciaPaso(self, mensaje):
        self.nPasos.setText(mensaje)
    @pyqtSlot(str)
    def actualizarSecuenciaBloque(self, mensaje):
        self.nBloque.setText(mensaje)

    @pyqtSlot(str)
    def actualizarNombreBloque(self, mensaje):
        self.bloqueEjecucion.setText(mensaje)
    @pyqtSlot()
    def finalizarEjecucion(self):
        self.descripcionPaso.setText("Protocolo completado.")
        print("FIN PROTOCOLO")

    @pyqtSlot()
    def protocoloDetenido(self):
        self.descripcionPaso.setText("Protocolo detenido.")

    @pyqtSlot(str)
    def mostrarPopup(self, mensaje):
        self.worker.pausarProtocolo() #Pausa la ejecucion
        self.manual_window = ingresoManual(mensaje_protocolo=mensaje)
        self.manual_window.Mensaje_enviado.connect(self.procesarResultadoPopup)
        self.manual_window.show()

    @pyqtSlot(list)
    def mostrarPopupNumerico(self,lista_valores):
        self.worker.pausarProtocolo() #Pausa la ejecucion
        self.manual_window_numerico = IngresoManualNumerico(texto=lista_valores[0],min=lista_valores[1],max=lista_valores[2])
        self.manual_window_numerico.Mensaje_enviado.connect(self.procesarResultadoPopup)
        self.manual_window_numerico.show()


    @pyqtSlot(str)
    def procesarResultadoPopup(self, valor):
        print(f"Resultado recibido desde popup: {valor}")
        #self.loop.quit()
        self.worker.manejarResultado(valor)  # Pasar el resultado al hilo secundario


class WorkerThread(QThread):
    UpdateTablaBloque = pyqtSignal() #Señal para actualizar la tabla de bloques
    progreso = pyqtSignal(str)  # Señal para actualizar mensajes en la GUI
    terminado = pyqtSignal()    # Señal para indicar que el trabajo terminó
    detenido = pyqtSignal()     # Señal para avisar que se detuvo
    abrirPopup = pyqtSignal(str)
    secuenciaPaso = pyqtSignal(str) # Señal que control la secuencia de paso
    secuenciaBloque = pyqtSignal(str) # Señal que controla la secuencia de bloque
    bloqueNombre = pyqtSignal(str) # Señal que controla el nombre del bloque
    pasosUpdate = pyqtSignal(list) #Señal con la lista de pasos actualizada (lista de lista)
    abrirPopupNumerico = pyqtSignal(list) #Señal para control windows numerica

    def __init__(self, protocolo,N_PROTOCOLO_ID = 0,database = None):
        super().__init__()
        self.database = database # SE AGREGA UN AUX DE LA BASE DE DATOS POR LAS DUDAS
        self.N_PROTOCOLO_ID = N_PROTOCOLO_ID
        self.protocolo = protocolo # Recibo el Json cargado
        self.running = True  # Controlar si el hilo debe seguir corriendo
        self.PASO = None #Incializo la variable con un vacio
        self.Bloque = None #inicializo la variable con un vacio
        self.manual_window = None
        self.TIPO_ITEM = {
            "IngresoManual": self.ingresoManual,
            "ProgramacionInstrumento": self.programacionInstrumento,
            "Medicion": self.medicion,
            "Verificacion": self.verificacion,
            "Calibracion": self.calibracion,
            "ProgramacionDeInstrumento": self.programacionInstrumento,
        }

        self.listaPasos = []
        self.pausa = False
        self.driverInstrumento = driverInstrumentos()

        self.wait_until_response = False
    def pausarProtocolo(self):
        self.pausa = True


    def continuarProtocolo(self):
        # Continúa la ejecución del protocolo
        self.pausa = False

    def ejecutarPaso(self, paso):
        self.PASO = paso
        self.paso_ejecucion = paso["Nombre"]
        sleep(1)  # Pausa antes de ejecutar cada paso
        item = self.TIPO_ITEM[paso["Tipo_Item"]]()

    def ingresoManual(self):
        #print("INGRESO A MANUAL")
        # Emitir señal para abrir el popup en el hilo principal
        if self.PASO["Tipo_Item"]=="IngresoManual":
            if self.PASO["Tipo_Respuesta"]!="NUMERICO":
                self.abrirPopup.emit(self.paso_ejecucion)
            else:
                self.abrirPopupNumerico.emit([self.PASO["Nombre"],self.PASO["ResultadoMinimo"],self.PASO["ResultadoMaximo"]]) #Emito esta señal para ingreso numerico

    def manejarResultado(self, valor):
        #print(f"Resultado recibido en hilo secundario: {valor}")
        self.procesarResultado(valor)

    def procesarResultado(self, valor):

        if self.PASO["Validacion"].lower() =="si": #Si la validacion es positiva entonces tenemos que ver si el resultado es correcto
            if self.PASO["Tipo_Respuesta"].lower() != "texto": #Es decir es numerico
                maximo = float(self.PASO["ResultadoMaximo"])
                minimo = float(self.PASO["ResultadoMinimo"])
                if float(valor)>=minimo and float(valor) <=maximo: #Si se encuentra en los rangos inclusive
                    self.PASO["Resultado"]=valor
                    self.PASO["Estado"] = "OK"
                else:
                    self.PASO["Resultado"]=valor
                    self.PASO["Estado"] = "NO OK"
            else:
                if valor == self.PASO["Respuesta_Correcta"]:
                    self.PASO["Resultado"]=valor
                    self.PASO["Estado"] = "OK"
                else:
                    self.PASO["Resultado"]=valor
                    self.PASO["Estado"] = "NO OK"

        else: #Siempre que no se especifique que se debe validar, el self.PASO["Estado"] sera "OK"
            self.PASO["Resultado"]=valor
            self.PASO["Estado"] = "OK"
        #Le agrego el horario de ejecucion
        self.PASO["TimeStamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #Para completar con la hora de la medicion
        with open("_TEMPS_/protocolo_a_ejecutar.json", "w", encoding="utf-8") as file:
            json.dump(self.protocolo,file,indent=4)
            
        if self.PASO["Estado"] == "NO OK":
            self.BLOQUE["Resultado"] ="NO PASA"
        else:
            self.BLOQUE["Resultado"] ="PASA"

        self.listaPasos.append(self.PASO)
        self.pasosUpdate.emit(self.listaPasos) #manda la de lista
        self.running = True
        self.continuarProtocolo()
        self.wait_until_response = False #Variable que me va a controlar solo el envio de los datos

    def programacionInstrumento(self):
        t = float(self.PASO["Tiempo_Medicion"]) / 1000  # Para pasarlo a segundos
        sleep(t)
        #print("Ingreso a programación")
        
        valor = self.driverInstrumento.readComando(CMD=self.PASO["Comandos"])
        self.procesarResultado(valor=valor)

    def medicion(self):
        t = float(self.PASO["Tiempo_Medicion"]) / 1000  # Para pasarlo a segundos
        sleep(t)
        print("Ingreso a medición")
        valor = self.driverInstrumento.readComando(CMD=self.PASO["Comandos"])
        print(valor)
        self.procesarResultado(valor=valor)
        

    def calibracion(self):
        print("Ingreso a calibración")
        sleep(1)  # Pausa al ingresar a calibración

    def verificacion(self):
        print("Ingreso a verificación")
        sleep(1)  # Pausa al ingresar a verificación

    def run(self):
        for bloque_idx, bloque in enumerate(self.protocolo):
            self.BLOQUE = bloque #Me va a representar el bloque que estoy ejecutando para luego evaluar su estado
            if self.N_PROTOCOLO_ID == 0:
                self.N_PROTOCOLO_ID = 1 #para que genere problema
                #print("DEBUG: INGRESO CON BLOQUE 0")
                ID_BLOQUE_EJECUCION = bloque["ProtocoloID"] #En el caso que sea 0 toma como referencia el id de ese bloque
            else:
                if ID_BLOQUE_EJECUCION == bloque["ProtocoloID"]: #Tengo que comparar si el bloque actual es el mismo
                    pass #No hace nada
                else:#Debe enviarse la señal de la base de datos
                    aux = self.protocolo[bloque_idx-1]
                    self.database.subir_paso_protocolo_y_protocolo(id_protocolo = aux["ProtocoloID"],resultado_bloque = aux["Resultado"],pasos = aux["Pasos"]) #Se sube el archivo previo
                    ID_BLOQUE_EJECUCION = bloque["ProtocoloID"] #Debo actualizar el bloque ID ejecucion
                    
            self.UpdateTablaBloque.emit()
            while self.pausa:
                sleep(1)
            if not self.running:
                self.detenido.emit()
                return
            self.secuenciaBloque.emit(bloque["ordenSecuencia"])
            self.bloqueNombre.emit(bloque["Nombre"])
            self.progreso.emit(f"Ejecutando bloque {bloque_idx + 1} de {len(self.protocolo)}")
            for paso in bloque["Pasos"]:

                N = 0
                while self.pausa:
                    sleep(1)

                while not self.running:
                    if N == 0:
                        self.detenido.emit()

                self.progreso.emit(f"Ejecutando paso: {paso['Nombre']}")
                self.secuenciaPaso.emit(paso["OrdenDeSecuencia"])
                self.ejecutarPaso(paso)
                sleep(0.5)  # Simula el tiempo de ejecución del paso
        self.wait_until_response =True #Si no pongo una variable, en el ultimo paso sale del loop sin que yo lo permita


        while self.wait_until_response: #Si no agrego el loop nunca envia porque sale del protoloco
            if not self.wait_until_response:
                print("¿Confirmado por chayanne?")
                self.database.subir_paso_protocolo_y_protocolo(id_protocolo = self.BLOQUE["ProtocoloID"],resultado_bloque = self.BLOQUE["Resultado"],pasos = self.BLOQUE["Pasos"]) #Se sube el archivo previo
                self.terminado.emit()


    def stop(self):
        # Detiene la ejecución del hilo
        self.running = False
