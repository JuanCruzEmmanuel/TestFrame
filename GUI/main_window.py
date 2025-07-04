# ui/main_window.py
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot,Qt,QObject
import json
import sys
import os
from time import sleep
from datetime import datetime
##GRAFICOS

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

#IMPORTO CALCULOS MATEMATICOS
#import numpy as np
from numpy import array
#IMPORTO LIBRERIAS EN CASO DE AGREGAR SHORTCUTS Y SECUENCIAS
from PyQt5.QtGui import QKeySequence,QColor, QBrush
from PyQt5.QtWidgets import QShortcut, QTableWidgetItem,QFileDialog

#IMPORTO CONTROLADORES DE INSTRUMENTO
from CONTROLADORES.DriverInstrumentosSMVA import driverInstrumentos


#####IMPORTO LOS BOTONES Y FUNCIONES ASOCIADAS#######################
from CONTROLADORES.LOGIC_MAIN_WINDOWS import configurar_logica_pagina_principal
from CONTROLADORES.LOGIC_ADD_CONFIG import configurar_logica_agregar_config
from CONTROLADORES.LOGIC_ADD_SERIAL_NUMBER import configurar_logica_agregar_serial_number
from CONTROLADORES.LOGIC_RUN_PROTOCOLO import configurar_logica_run_protocolo
from CONTROLADORES.LOGIC_DASHBOARD2 import configurar_logica_dashboard2
from CONTROLADORES.LIGHT_DARK_MODE_TOGGLE import ToggleSwitch
#from CONTROLADORES.MAIN_GRAFICADOR_THREAD import GraficadorThread
#OTROS IMPORTS
from CONTROLADORES.COMMAND_TRANSLATOR_DRIVER import COMMAND_TRANSLATOR
from CONTROLADORES.styles import LIGHT_STYLE, DARK_STYLE  # Si lo pones en un archivo externo

class MainWindow(QMainWindow):
    def __init__(self,database = None,version = "0.0.0"):
        super().__init__()
        self.database = database
        uic.loadUi('gui/main_responsive.ui', self)
        self.HIDE_COMMAND = True
        self.hide_or_show_commnad_pallet()
        #No se si me conviene inicializar las cosas(como para ilustrar o simplemente comentarlas)
        #FUNCIONES QUE SE CARGAN EN configurar_logica_pagina_principal() para los siguientes botones:

        self.id_seleccionado = None  #El ID del protocolo que se utilizara
        self.config_seleccionada = None # Se utiliza en LOGIC_ADD_CONFIG
        self.id_protocolos_nuevo = None # Va a ser util a la hora de cargar el numero de serie
        self.id_protocolo_nuevo = None # Va a ser util a la hora de cargar el numero de serie
        self.VERSION.setText(version)
        self.stacks.setCurrentWidget(self.main)
        self._vigencia = "Vigente"
        self._tipo = "Mostrar Todo"
        self.toggle = ToggleSwitch(on_toggle=self.toggle_theme, parent=self)
        self.TOGGLE.addWidget(self.toggle, alignment=Qt.AlignRight)
        self.datos = self.cargar_datos_json()

        self.protocolo_a_ejecutar=None #La creo para que sea mas visible desde el main, aunque el importante esta luego
        
        self.worker = None # Creo el placeholder del hilo de run protocolo, que es basicamente lo principal en ejecutar aca
        # Lógica separada
        configurar_logica_pagina_principal(self) #Botones de la main_windows
        configurar_logica_agregar_config(self) #Botones de asociar config
        configurar_logica_agregar_serial_number(self) #Botones asociados a la configuracion del numero de serie
        configurar_logica_run_protocolo(self) #Botones asociados a run Protocolo
        configurar_logica_dashboard2(self)


        #SHORTCUTS
        self.show_command = QShortcut(QKeySequence("Ctrl+Ñ"), self).activated.connect(self.hide_or_show_commnad_pallet)
        self.main_menu = QShortcut(QKeySequence("Ctrl+M"), self).activated.connect(self.move_to_main)

        #OTROS
        self.comand_translator = COMMAND_TRANSLATOR(win=self)
        self.graph_auto = True
        # Tema
        self.dark_mode = False
        self.setStyleSheet(LIGHT_STYLE) #Por defecto modo claro
        self.test_btn.clicked.connect(self.abrir_buscador_archivo)

    def toggle_theme(self, dark: bool):
        if dark:
            self.setStyleSheet(DARK_STYLE)
            self.dark_mode = True
        else:
            self.setStyleSheet(LIGHT_STYLE)
            self.dark_mode = False
    def abrir_buscador_archivo(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo", "", "Todos los archivos (*.SMVA)")
        if archivo:
            print("Archivo seleccionado:", archivo)
            CMD = f"load,smva,{archivo}"
            self.comand_translator.translate(CMD=CMD)
    def move_to_main(self):
        self.stacks.setCurrentWidget(self.main)
    
    def hide_or_show_commnad_pallet(self):
        if self.HIDE_COMMAND:
            self.command_box.hide()
            self.command_btn.hide()
            self.HIDE_COMMAND = not self.HIDE_COMMAND
        else:
            self.command_box.show()
            self.command_btn.show()
            self.HIDE_COMMAND = not self.HIDE_COMMAND
    def cargar_datos_json(self):
        # Cargar el archivo JSON
        try:
            with open('_TEMPS_/protocolos.json', 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error al cargar el archivo JSON: {e}")
            return {}

        print("ready")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            # Ignorar la tecla Escape para que no detenga la ejecucion.....
            event.ignore()
        else:
            # Procesar otras teclas normalmente
            super().keyPressEvent(event)

    @pyqtSlot(list)
    def mostrar_pasos_protocolo(self, lista_pasos_ejecutados):
        self.TablaPasos.setRowCount(len(lista_pasos_ejecutados))
        self.TablaPasos.setHorizontalHeaderLabels(["Orden", "Nombre", "Estado", "Rango Minimo", "Rango Maximo","Resultado"])
        for row, values in enumerate(lista_pasos_ejecutados):
            estado = values["Estado"]
            color = QColor(135, 226, 64) if estado == "OK" else QColor(226, 88, 64)

            for col, key in enumerate(["OrdenDeSecuencia", "Nombre", "Estado", "ResultadoMinimo", "ResultadoMaximo", "Resultado"]):
                item = QTableWidgetItem(str(values[key]))  # Crear el item
                item.setBackground(QBrush(color))  # Aplicar color
                self.TablaPasos.setItem(row, col, item)  # Insertar en la tabla
        self.TablaPasos.scrollToBottom()#Creo que esto me mueve hacia abajo el scroll

    def update_graph(self):
        # Lanzamos el hilo sin bloquear la GUI
        self.graficador_thread = GraficadorThread(self.tiempo_paso, self.tiempo_total)
        self.graficador_thread.graficos_listos.connect(self.mostrar_graficos)
        self.graficador_thread.start()

    def mostrar_graficos(self, fig1, fig2):
        # Ya estás en el hilo principal acá, así que podés actualizar los widgets
        self.mostrar_grafico_en_widget(self.imagen_progreso1, fig1)
        self.mostrar_grafico_en_widget(self.imagen_progreso2, fig2)
            

    def mostrar_grafico_en_widget(self, widget, figura: Figure):
        """
        Actualiza los graficos en el widget seleccionado
        """
        for i in reversed(range(widget.layout().count())):
            widget.layout().itemAt(i).widget().setParent(None)

        canvas = FigureCanvas(figura)
        widget.layout().addWidget(canvas)
        canvas.draw()
###########################PONOGO EL INICIAR EJECUCION ACA POR UNA CUESTION DE FACILIDAD###################################
    def iniciarEjecucion(self):
        if self.worker is not None and self.worker.isRunning():
            self.descripcionPaso.setText("Ya se está ejecutando un protocolo.")
            return
        self.worker = WorkerThread(self.protocolo_a_ejecutar,database=self.database,DEVICE_POOL=self.DEVICE_POOL)
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
        self.worker.abrirManual.connect(self.cambiar_manual)
        self.worker.tiempos_signal.connect(self.set_tiempo)
        self.worker.start()
        self.descripcionPaso.setText("Ejecutando protocolo...")


############################TAL VEZ NO ES LO CORRECTO######################################
##########################PERO POR UNA CUESTION DE FACILIDAD###############################
##########################VOY A CARGAR EL HILO ACA#########################################
#######################################XD##################################################

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
    abrirManual = pyqtSignal() #Abre la ventana de avanzar manual o saltar paso
    tiempos_signal = pyqtSignal(list,list) #Emite tiempo paso, tiempo  total
    def __init__(self, protocolo,N_PROTOCOLO_ID = 0,database = None, DEVICE_POOL={}):
        super().__init__()
        self.DEVICE_POOL = DEVICE_POOL # VARIABLE QUE CONTROLA
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
        self.PAUSE_SUPERIOR = False
        self.pausa = False
        self.driverInstrumento = driverInstrumentos(BASE_DATO=self.database,DEVICE_POOL=self.DEVICE_POOL)
        #FLAG GLOBALES Y AUXILIARES
        self.wait_until_response = False
        self.VERIFICACION_FLAG = False #bandera para controlar la verificacion
        self.FLAG_MANUAL_SALTO = False #Flag que controla el cambio de posiciones en caso de de estar en manual y elegir la opcion saltar

        self.MODO = "AUTOMATICO"
        #POSICIONES AUXILIARES
        self.I_BLOQUE = "NO_SALTO"
        self.J_BLOQUE = "NO_SALTO"
        self.I_MANUAL = None
        self.J_MANUAL = None

        self._smva_archivo = False
        
        #CONTROLES DE TIEMPO
        
        self.tiempo_incial = 0
        self.tiempo_previo = 0 #controla la medicion anterior
        self.tiempo_paso= [] #Guarda la variable que mide el tiempo entre pasos
        self.tiempo_total = [] #Guarda las variables que mide con respecto al incial
    def setsmvafile(self):
                
        # Cargar Archivo
        self._smva_archivo = True


    def pausarProtocolo(self):
        self.pausa = True
    def pausaSuperior(self):
        """
        Pausa un nivel superior el protocolo
        """
        self.PAUSE_SUPERIOR = True

    def continuarSuperior(self):
        """
        Continua el protocolo
        """
        self.PAUSE_SUPERIOR = False

        self.pausa = False #agrego para que no se quede en loop infinito
    def setBloquePasoManual(self,i,j):
        """
        Setea la posicion de trabajo\n
        :i: Indice de bloque\n
        :j: Indice de fila\n
        :return: Posicion deseada
        """
        self.I_MANUAL = i
        self.J_MANUAL = j
    def continuarProtocolo(self):
        # Continúa la ejecución del protocolo
        self.pausa = False

    def ejecutarPaso(self, paso):
        self.PASO = paso #Configuro el self.PASO
        self.paso_ejecucion = paso["Nombre"]
        sleep(0.3)  # Pausa antes de ejecutar cada paso
        self.TIPO_ITEM[paso["Tipo_Item"]]()

    def ingresoManual(self):
        #print("Indicador_11")
        FLAG_PAUSA_SUPERIOR = False
        #print("INGRESO A MANUAL")
        # Emitir señal para abrir el popup en el hilo principal
        if not self.PAUSE_SUPERIOR: 
            #print("Indicador_12")
            if self.PASO["Tipo_Item"]=="IngresoManual":
                if self.PASO["Tipo_Respuesta"]!="NUMERICO":
                    self.abrirPopup.emit(self.paso_ejecucion)
                else:
                    self.abrirPopupNumerico.emit([self.PASO["Nombre"],self.PASO["ResultadoMinimo"],self.PASO["ResultadoMaximo"]]) #Emito esta señal para ingreso numerico
        else: #En caso que si exista la pausa superior
            FLAG_PAUSA_SUPERIOR=True
            while FLAG_PAUSA_SUPERIOR: #Mientra este activo, se va a mantener aca
                #print("Indicador_3")
                if not self.PAUSE_SUPERIOR: #Pero no quiero que muestre nada hasta que se salga de la seleccion
                    #print("Indicador_4")
                    if self.I_MANUAL == None: #Solo me interesa evaluar si se ha seleccionado algun valor distinto de None
                        #print("Se continua al siguiente paso....")
                        if self.PASO["Tipo_Item"]=="IngresoManual":
                            #print("Indicador_14")
                            if self.PASO["Tipo_Respuesta"]!="NUMERICO":
                                #print("Indicador_15")
                                self.abrirPopup.emit(self.paso_ejecucion)
                                FLAG_PAUSA_SUPERIOR =False
                            else:
                                #print("Indicador_13")
                                self.abrirPopupNumerico.emit([self.PASO["Nombre"],self.PASO["ResultadoMinimo"],self.PASO["ResultadoMaximo"]]) #Emito esta señal para ingreso numerico
                                FLAG_PAUSA_SUPERIOR=False
                    else: #Se ha seleccionado saltar.....
                        #print("Se ha seleccionado saltar a otro paso....")
                        FLAG_PAUSA_SUPERIOR=False
                        self.FLAG_MANUAL_SALTO = True #Activa esta variable de estado para poder avisarle al run que existe un salto obligado
                        
                else:
                    #print("Reposo")
                    sleep(1.5) #Descanso 1 segundo para no consumir recursos innecesariamente.

                                       

    def manejarResultado(self, valor):
        #print(f"Resultado recibido en hilo secundario: {valor}")
        self.procesarResultado(valor)

    def procesarResultado(self, valor):

        if self.PASO["Validacion"].lower() =="si": #Si la validacion es positiva entonces tenemos que ver si el resultado es correcto
            if self.PASO["Tipo_Respuesta"].lower() != "texto": #Es decir es numerico
                maximo = float(self.PASO["ResultadoMaximo"])
                minimo = float(self.PASO["ResultadoMinimo"])
                try: #En caso que exista un fallo
                    if float(valor)>=minimo and float(valor) <=maximo: #Si se encuentra en los rangos inclusive
                        self.PASO["Resultado"]=valor
                        self.PASO["Estado"] = "OK"
                    else:
                        self.PASO["Resultado"]=valor
                        self.PASO["Estado"] = "NO OK"
                except: #Respuesta en caso de fallo seguimiento de fallo
                    self.PASO["Estado"] = "NO OK"
                    self.PASO["Resultado"] = -101 #Se envia respuesta texto a un resultado numerico
            else:#Esto significa que la respuesta es tipo texto
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
        tiempo_mecion = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #Para completar con la hora de la medicion
        self.PASO["TimeStamp"] = tiempo_mecion
        with open("_TEMPS_/protocolo_a_ejecutar.json", "w", encoding="utf-8") as file:
            json.dump(self.protocolo,file,indent=4)
            
        if self.PASO["Estado"] == "NO OK":
            self.BLOQUE["Resultado"] ="NO PASS"
        else:
            self.BLOQUE["Resultado"] ="PASS"
        if self.tiempo_incial == 0: #Para hacer comparaciones
            self.tiempo_incial=datetime.strptime(tiempo_mecion,"%Y-%m-%d %H:%M:%S").timestamp() / 60  # tiempo en minutos
            self.tiempo_paso.append(0) #inicio con cero
            self.tiempo_total.append(0) #inicio con cero
            self.tiempo_previo = self.tiempo_incial
        else:
            tiempo_actual = datetime.strptime(tiempo_mecion,"%Y-%m-%d %H:%M:%S").timestamp() / 60  # tiempo en minutos
            delta_paso = tiempo_actual - self.tiempo_previo
            delta_total = tiempo_actual-self.tiempo_incial
            self.tiempo_previo = tiempo_actual #actualizo la variable
            self.tiempo_paso.append(delta_paso) #actualizo la variable
            self.tiempo_total.append(delta_total) #actualizo la variable

        self.listaPasos.append(self.PASO)
        self.pasosUpdate.emit(self.listaPasos) #manda la de lista
        self.tiempos_signal.emit(self.tiempo_paso, self.tiempo_total) #Emito la señal de tiempo
        self.running = True
        if self.MODO == "MANUAL": #En caso que sea manual, es decir no hubo un cambio de estado, no debe seguir ejecutando pasos
            pass
        else:
            #En caso que haya alguna bandera de continuar, si.....
            self.continuarProtocolo()
            self.continuarSuperior()
        self.wait_until_response = False #Variable que me va a controlar solo el envio de los datos

    def programacionInstrumento(self):
        t = float(self.PASO["Tiempo_Medicion"]) / 1000  # Para pasarlo a segundos
        sleep(t)
        #print("Ingreso a programación")
        
        valor,i_bloque,j_pasos = self.driverInstrumento.readComando(CMD=self.PASO["Comandos"],SALTO_CONDICIONAL=self.VERIFICACION_FLAG)
        self.procesarResultado(valor=valor)
        self.I_BLOQUE = i_bloque
        self.J_BLOQUE = j_pasos
    def medicion(self):
        t = float(self.PASO["Tiempo_Medicion"]) / 1000  # Para pasarlo a segundos
        sleep(t)
        variable_flag = False #Variable para controlar si entron una variable *mister obvio*
        #print("Ingreso a medición")
        if "<<" in self.PASO["Comandos"]:
            variable_flag = True
            #Tiene que guardar el dato en un xml
            CMD = self.PASO["Comandos"].split("<<")
            varieble_nombre = CMD[0]
            CMD = CMD[1]
        else:
            CMD = self.PASO["Comandos"]
        valor,i_bloque,j_pasos = self.driverInstrumento.readComando(CMD=CMD,SALTO_CONDICIONAL=self.VERIFICACION_FLAG)

        if variable_flag:
            #Aca debemos agregar el control del nombre de variable
            if os.path.exists(r"_TEMPS_\variables.json"): #Se debe preguntar si el arhcivo existe, esto con el fin de facilitar la logica futura
                with open(r"_TEMPS_\variables.json","r") as file:
                    VARIABLES = json.load(file) #Cargo el json con todas las variables locales
            else:
                VARIABLES = {} #Si no existe entonces debo crear un dic vacio como le gusta a eia

            VARIABLES[varieble_nombre]=str(valor) #par cable-valor (key-value), no me gusta solo admitir str, pero bueno por el momento
            with open(r"_TEMPS_\variables.json","w") as file:
                json.dump(VARIABLES,file,indent=4)
                
        print(valor)
        self.procesarResultado(valor=valor)
        
    def selectModo(self,modo):
        """
        Selecciona el modo MANUAL o AUTOMATICO
        """
        self.MODO = modo

    def calibracion(self):
        print("Ingreso a calibración")
        #sleep(1)  # Pausa al ingresar a calibración

    def verificacion(self):
        COMANDO_SPLIT = self.PASO["Comandos"].split("-") #separo por los guiones P.E. ;VERIFICAR:BLOQUE"32"-PASO"2"-"PROSIM8"
        COMANDO_DIC = {} #Es necesario trabajar los datos de manera eficiente
        for splited in COMANDO_SPLIT:
            if "bloque" in splited.lower():
                valor = splited.split('"')[1]
                COMANDO_DIC["Bloque"] = int(valor)
            elif "paso" in splited.lower():
                valor = splited.split('"')[1]
                COMANDO_DIC["Paso"] = int(valor)
            else:
                if ";" in splited: #aveces viene con una etiqueta, por lo que es necesario eliminarla
                    splited = splited.split(";")[0]
                splited_busqueda =splited.split('"')[1]
                COMANDO_DIC["Valor"] = splited_busqueda

        """
        Hasta este punto vengo de un str:VERIFICAR:BLOQUE"32"-PASO"2"-"PROSIM8"
        y lo transformo en el siguiente diccionario:
        {
        "Bloque":int->32,
        "Paso":int->2,
        "Valor":str->PROSIM8
        }
        """
        #Parte logica de la busqueda, hace una pasada Rapida a todos los pasos del protocolo hasta encontrar las indicaciones.
        _N_BLOQUE_ = 0
        for bloque in self.protocolo:
            if _N_BLOQUE_ == COMANDO_DIC["Bloque"]:
                _N_PASOS_ = 0
                for paso in bloque["Pasos"]:
                    if _N_PASOS_ == COMANDO_DIC["Paso"]:
                        if str(paso["Resultado"]) == str(COMANDO_DIC["Valor"]):
                            self.VERIFICACION_FLAG = True
                            break
                        else:
                            self.VERIFICACION_FLAG = False
                            break
                    _N_PASOS_ +=1
            _N_BLOQUE_ +=1
                
        #sleep(1)  # Pausa al ingresar a verificación

    def run(self):

        """
        El run se venia ejecutando mediante un ciclo for, el problema que he notado
        es que de este modo ejecuciones hacia delante y hacia atras se volverian muy complicadas
        de trabajar, ya que for es una estructura puramente secuancial.
        for 0, for 1, for 2, ..... ,for N; en el caso de adelantar secuencia seria "facil"
        pero el problema existe cuando se quiere saltar de manera manual o se realiza un salto condicional hacia atras
        por esta razon he decidido cambiar el ciclo por un while controlados por indices "i" y "j"
        indice i--->Controla los bloques
        indice j--->Controla los pasos
        """
        i = 0 #Indice de bloque
        #for bloque_idx, bloque in enumerate(self.protocolo):
        while i < len(self.protocolo):
            self.protocolo[i]["Operador"]=self.database.USUARIO_SMVA #Cargo al inicio de cada bloque
            if self.FLAG_MANUAL_SALTO:#Se ha activado la variable de estado desde manual
                i = self.I_MANUAL
                j = self.J_MANUAL
                #self.FLAG_MANUAL_SALTO = False #Desactivo, esto tal vez no es lo mejor aca
            while self.PAUSE_SUPERIOR:
                if self.I_MANUAL !=None:
                    i = self.I_MANUAL
                    j = self.J_MANUAL
                sleep(1)

            while self.pausa:
                if self.PAUSE_SUPERIOR: #En el caso que ya se encuentre en pausa y se pida saltar...... debo asegurarme de ir a donde he solicitado
                    while self.PAUSE_SUPERIOR:
                        if self.I_MANUAL !=None:
                            i = self.I_MANUAL
                            j = self.J_MANUAL
                sleep(1)
            self.I_MANUAL = None
            self.J_MANUAL = None
            j = 0 #indice de paso
            self.BLOQUE = self.protocolo[i] #Me va a representar el bloque que estoy ejecutando para luego evaluar su estado
            if self.N_PROTOCOLO_ID == 0:
                self.N_PROTOCOLO_ID = 1 #para que genere problema
                #print("DEBUG: INGRESO CON BLOQUE 0")
                ID_BLOQUE_EJECUCION = self.protocolo[i]["ProtocoloID"] #En el caso que sea 0 toma como referencia el id de ese bloque
            else:
                if ID_BLOQUE_EJECUCION == self.protocolo[i]["ProtocoloID"]: #Tengo que comparar si el bloque actual es el mismo
                    pass #No hace nada
                else:#Debe enviarse la señal de la base de datos
                    aux = self.protocolo[i-1]
                    if not self._smva_archivo: #En caso de ser el testeo no subir nada
                        self.database.subir_paso_protocolo_y_protocolo(id_protocolo = aux["ProtocoloID"],resultado_bloque = aux["Resultado"],pasos = aux["Pasos"]) #Se sube el archivo previo
                    ID_BLOQUE_EJECUCION = self.protocolo[i]["ProtocoloID"] #Debo actualizar el bloque ID ejecucion
                    
            self.UpdateTablaBloque.emit()
            while self.pausa:
                #print("Debo ingresar¡?")
                sleep(0.5)
            if not self.running:
                self.detenido.emit()
                return
            self.secuenciaBloque.emit(str(self.protocolo[i]["ordenSecuencia"]))
            self.bloqueNombre.emit(self.protocolo[i]["Nombre"])
            self.progreso.emit(f"Ejecutando bloque {i + 1} de {len(self.protocolo)}")
            #for paso in self.protocolo[i]["Pasos"]:
            while j < len(self.protocolo[i]["Pasos"]):
                #print("Indicador_7")
                if self.FLAG_MANUAL_SALTO:#Se ha activado la variable de estado desde manual
                    #print("Indicador_8")
                    i = self.I_MANUAL
                    j = self.J_MANUAL
                    self.FLAG_MANUAL_SALTO = True #desactivo la variable para que el protocolo continue de manera normal

                while self.PAUSE_SUPERIOR:
                    #print("Indicador_9")
                    if self.I_MANUAL !=None:
                        i = self.I_MANUAL
                        j = self.J_MANUAL
                        sleep(1)

                while self.pausa:
                    #print("Indicador_10")
                    if self.PAUSE_SUPERIOR: #En el caso que ya se encuentre en pausa y se pida saltar...... debo asegurarme de ir a donde he solicitado
                        while self.PAUSE_SUPERIOR:
                            if self.I_MANUAL !=None:
                                i = self.I_MANUAL
                                j = self.J_MANUAL
                    sleep(1)
                if self.MODO == "MANUAL": #Nunca hemos salido del modo manual, por lo que nuevamente se debe re ingresar; esto a su vez debe nuevamente preguntar si se ha o no realizado una accion
                    self.abrirManual.emit()
                while self.PAUSE_SUPERIOR:
                    #print("Ingrese debido a que seguimos en modo manual")
                    if self.I_MANUAL !=None:
                        i = self.I_MANUAL
                        j = self.J_MANUAL
                        sleep(1)

                self.I_MANUAL = None
                self.J_MANUAL = None  
                if self.I_BLOQUE !="NO_SALTO" and self.J_BLOQUE !="NO_SALTO":
                    if int(self.I_BLOQUE)>i:
                        #Aca debo actualizar y agregar NC y OK a los pasos en caso que se salte hacia delante
                        #Puedo tener una funcion que se encargue solo de hacer eso
                        self.completarConNC(i=i,j=j) #Funcion que se encarga de completarlo solo
                    i = int(self.I_BLOQUE)
                    j = int(self.J_BLOQUE)
                    self.BLOQUE = self.protocolo[i] #Tengo que actualizar la variable que me controla los bloques
                    self.J_BLOQUE = "NO_SALTO"
                    self.I_BLOQUE = "NO_SALTO"
                    self.VERIFICACION_FLAG = False # Esto tal vez deba ser un arreglo tupla (False, False)
                    self.UpdateTablaBloque.emit() # Veo de hacer un emit.... puede salir mal

                N = 0
                while self.pausa:
                    #print("INGRESEEE")
                    sleep(1)

                while not self.running:
                    if N == 0:
                        self.detenido.emit()
                
                self.progreso.emit(f"Ejecutando paso: {self.protocolo[i]['Pasos'][j]['Nombre']}") #Cambie las comillas dobles por comillas simples para evitar errores del f-string
                self.secuenciaPaso.emit(self.protocolo[i]["Pasos"][j]["OrdenDeSecuencia"])
                self.ejecutarPaso(self.protocolo[i]["Pasos"][j])
                j+=1 #Incremento el indice
                sleep(0.1)  # Simula el tiempo de ejecución del paso
                
            i+=1 #incremento el indice del bloque
            self.listaPasos = [] #Reinicia la lista para no entorpecer la vista
        self.wait_until_response =True #Si no pongo una variable, en el ultimo paso sale del loop sin que yo lo permita


        while self.wait_until_response: #Si no agrego el loop nunca envia porque sale del protoloco
            if not self.wait_until_response:
                print("¿Confirmado por chayanne?")
                if not self._smva_archivo: #En caso de ser el testeo no subir nada
                    self.database.subir_paso_protocolo_y_protocolo(id_protocolo = self.BLOQUE["ProtocoloID"],resultado_bloque = self.BLOQUE["Resultado"],pasos = self.BLOQUE["Pasos"]) #Se sube el archivo previo
                self.terminado.emit()

        self._smva_archivo = False #Cuando termine debo cerrar
    def completarConNC(self,i,j):
        """
        Esta funcion se encarga de completar el protocolo local con NC y OK\n
        :i: Indice de bloque\n
        :j: Indice de paso
        """
        n=0 #Indica inicio
        if j!=0:
            j-=1 #Hay que fijarse si esto funciona.....
        while i <=self.I_BLOQUE: #Tengo que recorrer desde el i ingresado hasta I_BLOQUE de salto
            """Esto quiere decir que si estoy en el bloque 6 y tengo que ir hasta el bloque 7, va a recorrer inclusive hasta ese valor"""
            self.protocolo[i]["Operador"]=self.database.USUARIO_SMVA #Cargo al inicio de cada bloque
            self.bloqueNombre.emit(self.protocolo[i]["Nombre"]) #Para que muestre el nombre del bloque actual
            if n!=0:
                #En caso que se cambie el bloque......
                self.listaPasos = [] #Reinicia la lista para no entorpecer la vista
                self.pasosUpdate.emit(self.listaPasos) #manda la de lista
                self.UpdateTablaBloque.emit()
                #self.tiempos_signal.emit(self.tiempo_paso, self.tiempo_total) #Emito la señal de tiempo
                #j=0 #Reincio la variable
            while j < len(self.protocolo[i]["Pasos"]):
                self.protocolo[i]["Pasos"][j]["Resultado"]="NC"
                self.protocolo[i]["Pasos"][j]["Estado"]="OK"
                self.protocolo[i]["Pasos"][j]["CriterioPass"]="NC"
                self.protocolo[i]["Pasos"][j]["TimeStamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #Para completar con la hora de la medicion
                self.listaPasos.append(self.protocolo[i]["Pasos"][j]) #Esto puede salir muy mal, voy a updatear este paso
                self.pasosUpdate.emit(self.listaPasos) #para que se grafique
                if self.protocolo[i]["Resultado"]=="":
                    self.protocolo[i]["Resultado"]="PASS"
                sleep(0.1)
                j+=1#Incremento indice paso

            if "NO PASS" in self.BLOQUE["Resultado"]:
                self.BLOQUE["Resultado"] ="NO PASS"
            elif "PASS" in self.BLOQUE["Resultado"]:
                self.BLOQUE["Resultado"] ="PASS" #Debo agregar que el resultado del bloque sea PASA ya que se ha completado con 
            else:
                self.BLOQUE["Resultado"] ="PASS"
            if not self._smva_archivo: #En caso de ser el testeo no subir nada
                self.database.subir_paso_protocolo_y_protocolo(id_protocolo = self.protocolo[i]["ProtocoloID"],resultado_bloque = self.protocolo[i]["Resultado"],pasos = self.protocolo[i]["Pasos"]) #Se sube el archivo previo
            i+=1#Incremento indice bloque
        with open("_TEMPS_/protocolo_a_ejecutar.json", "w", encoding="utf-8") as file:
            json.dump(self.protocolo,file,indent=4)

    def stop(self):
        # Detiene la ejecución del hilo
        self.running = False
        
#Grafico en otro hilo para que funcione todo mejor! lo debo pasar a otro script para que sea mas ordenado
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