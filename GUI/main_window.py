# ui/main_window.py
from PyQt5.QtWidgets import QMainWindow, QPushButton,QTableWidget,QTableWidgetItem,QLineEdit
from PyQt5 import uic
import json
from GUI.RunProtocolo import run
from GUI.AsociarConfig import AsociarConfiguracionInstrumento
from GUI.IngresarNumeroSerie import IngresarNumeroSerie
from CONTROLADORES.LOGIC_MAIN_WINDOWS import configurar_logica_pagina_principal
from CONTROLADORES.LOGIC_ADD_CONFIG import configurar_logica_agregar_config
from CONTROLADORES.LOGIC_ADD_SERIAL_NUMBER import configurar_logica_agregar_serial_number
from CONTROLADORES.LOGIC_RUN_PROTOCOLO import configurar_logica_run_protocolo
from time import sleep
import sys

class MainWindow(QMainWindow):
    def __init__(self,database = None,version = "0.0.0"):
        super().__init__()
        self.database = database
        uic.loadUi('gui/main_2.ui', self)

        #No se si me conviene inicializar las cosas(como para ilustrar o simplemente comentarlas)
        #FUNCIONES QUE SE CARGAN EN configurar_logica_pagina_principal() para los siguientes botones:

        #self.tablaProtocoolo
        #self.updateBoton(update)
        #self.apFiltroNombre(filtrar_tabla_por_nombre) ----> self.tipoVigencia || self.tipoItem
        #self.EjecutarBoton(ejecutar_fila_seleccionada)
        #self.mostrar_todos_los_datos(self) -----> self.tablaProtocoolo

        self.id_seleccionado = None  #El ID del protocolo que se utilizara
        self.config_seleccionada = None # Se utiliza en LOGIC_ADD_CONFIG
        self.id_protocolos_nuevo = None # Va a ser util a la hora de cargar el numero de serie
        self.id_protocolo_nuevo = None # Va a ser util a la hora de cargar el numero de serie
        self.VERSION.setText(version)
        self.stacks.setCurrentWidget(self.main)
        self._vigencia = "Vigente"
        self._tipo = "Mostrar Todo"

        self.datos = self.cargar_datos_json()

        self.protocolo_a_ejecutar=None #La creo para que sea mas visible desde el main, aunque el importante esta luego
        # Lógica separada
        configurar_logica_pagina_principal(self) #Botones de la main_windows
        configurar_logica_agregar_config(self) #Botones de asociar config
        configurar_logica_agregar_serial_number(self) #Botones asociados a la configuracion del numero de serie
        configurar_logica_run_protocolo(self) #Botones asociados a run Protocolo
        #configurar_logica_run_page(self.run_protocolo, self.stacks, self.database)
        #self.runProtocolo = run(database=self.database)

    def cargar_datos_json(self):
        # Cargar el archivo JSON
        try:
            with open('_TEMPS_/protocolos.json', 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error al cargar el archivo JSON: {e}")
            return {}

        print("ready")