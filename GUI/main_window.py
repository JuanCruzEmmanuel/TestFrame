# ui/main_window.py
from PyQt5.QtWidgets import QMainWindow, QPushButton,QTableWidget,QTableWidgetItem,QLineEdit
from PyQt5 import uic
import json
from GUI.RunProtocolo import run
from GUI.AsociarConfig import AsociarConfiguracionInstrumento
from GUI.IngresarNumeroSerie import IngresarNumeroSerie
from CONTROLADORES.LOGIC_MAIN_WINDOWS import configurar_logica_pagina_principal
from CONTROLADORES.LOGIC_ADD_CONFIG import configurar_logica_agregar_config
from time import sleep
import sys

class MainWindow(QMainWindow):
    def __init__(self,database = None,version = "0.0.0"):
        super().__init__()
        self.database = database
        uic.loadUi('gui/main_2.ui', self)

        self.id_seleccionado = None  # Lo inicializás acá

        self.VERSION.setText(version)
        self.stacks.setCurrentWidget(self.main)
        self._vigencia = "Vigente"
        self._tipo = "Mostrar Todo"

        self.datos = self.cargar_datos_json()

        # Lógica separada
        configurar_logica_pagina_principal(self) #Botones de la main_windows
        configurar_logica_agregar_config(self) #Botones de asociar config
        #configurar_logica_run_page(self.run_protocolo, self.stacks, self.database)
        self.runProtocolo = run(database=self.database)
        #self.stacks.setCurrentWidget(self.run_protocolo) #StackedWidget
        #configurar_logica_pagina2(self.run_protocolo,self.stacks)
    def cargar_datos_json(self):
        # Cargar el archivo JSON
        try:
            with open('_TEMPS_/protocolos.json', 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error al cargar el archivo JSON: {e}")
            return {}

        print("ready")