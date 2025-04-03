# ui/main_window.py
from PyQt5.QtWidgets import QMainWindow, QPushButton,QTableWidget,QTableWidgetItem,QLineEdit
from PyQt5 import uic
import json
from GUI.RunProtocolo import run
from GUI.AsociarConfig import AsociarConfiguracionInstrumento
from GUI.IngresarNumeroSerie import IngresarNumeroSerie
from time import sleep
import sys
class MainWindow(QMainWindow):
    def __init__(self,database = None,version = "0.0.0"):
        super().__init__()
        self.database = database
        uic.loadUi('GUI/MAIN.ui', self)  # Carga el archivo log.ui
        self._vigencia = "Vigente"
        self._tipo = "Mostrar Todo"
        self.tablaProtocolo = self.findChild(QTableWidget, "tablaProtocolo") #No se si esto es necesario realmente
        self.nombreFiltro = self.findChild(QLineEdit, "nombreFiltro")
        self.apFiltroNombre = self.findChild(QPushButton, "apFiltroNombre")
        self.VERSION.setText(version)
        self.apFiltroNombre.clicked.connect(self.filtrar_tabla_por_nombre)
        self.UpdateBoton.clicked.connect(self.update)
        self.EjecutarBoton.clicked.connect(self.ejecutar_fila_seleccionada)
        # Cargar los datos iniciales
        self.datos = self.cargar_datos_json()  # Cargar el JSON en memoria
        self.mostrar_todos_los_datos()  # Mostrar todos los datos en la tabla
        self.runProtocolo = run(database=self.database)
    def cargar_datos_json(self):
        # Cargar el archivo JSON
        try:
            with open('_TEMPS_/protocolos.json', 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error al cargar el archivo JSON: {e}")
            return {}

    def mostrar_todos_los_datos(self):
        """Llena la tabla con todos los datos del JSON."""
        self.tablaProtocolo.setRowCount(len(self.datos))
        self.tablaProtocolo.setColumnCount(6)
        self.tablaProtocolo.setHorizontalHeaderLabels(["ID", "Nombre", "Ver","Tipo", "Vigente", "Comentario"])

        for row, (id_, values) in enumerate(self.datos.items()):
            self.tablaProtocolo.setItem(row, 0, QTableWidgetItem(id_))  # ID
            self.tablaProtocolo.setItem(row, 1, QTableWidgetItem(values[0]))  # Nombre
            self.tablaProtocolo.setItem(row, 2, QTableWidgetItem(values[1]))  # Versión
            self.tablaProtocolo.setItem(row, 3, QTableWidgetItem(values[3]))  # Tipo
            self.tablaProtocolo.setItem(row, 4, QTableWidgetItem(values[2]))  # Vigente
            self.tablaProtocolo.setItem(row, 5, QTableWidgetItem(values[4]))  # Comentario

    def filtrar_tabla_por_nombre(self):
        """Filtra la tabla con base en el texto ingresado en nombreFiltro."""
        texto_filtro = self.nombreFiltro.text().lower()  # Obtener el texto del filtro y convertirlo a minúsculas
        self._vigencia = self.tipoVigencia.currentText()
        self._tipo = self.tipoItem.currentText()
        dic_vigencia = {
            "Vigente": "SI",
            "No Vigente": "NO",
            "Mostrar Todo":""
        }

        tipo = "" if self._tipo =="Mostrar Todo" else self._tipo

        # Filtrar los datos
        datos_filtrados = {
            id_: values for id_, values in self.datos.items()
            if texto_filtro in values[0].lower() and dic_vigencia[self._vigencia].lower() in values[2].lower() and tipo.lower() in values[3].lower()  # Filtrar por nombre (posición 0)

        }

        # Actualizar la tabla con los datos filtrados
        self.tablaProtocolo.setRowCount(len(datos_filtrados))
        for row, (id_, values) in enumerate(datos_filtrados.items()):
            self.tablaProtocolo.setItem(row, 0, QTableWidgetItem(id_))  # ID
            self.tablaProtocolo.setItem(row, 1, QTableWidgetItem(values[0]))  # Nombre
            self.tablaProtocolo.setItem(row, 2, QTableWidgetItem(values[1]))  # Versión
            self.tablaProtocolo.setItem(row, 3, QTableWidgetItem(values[3]))  # Tipo
            self.tablaProtocolo.setItem(row, 4, QTableWidgetItem(values[2]))  # Vigente
            self.tablaProtocolo.setItem(row, 5, QTableWidgetItem(values[4]))  # Comentario

    def update(self):

        self.database.protocoloQuery()
        self.datos = self.cargar_datos_json()
        self.mostrar_todos_los_datos()

    def ejecutar_fila_seleccionada(self):
        """Obtiene los valores de la fila seleccionada y realiza acciones con ellos."""
        fila_seleccionada = self.tablaProtocolo.currentRow()  # Obtiene el índice de la fila seleccionada

        if fila_seleccionada == -1:  # Verifica si no hay ninguna fila seleccionada
            print("No se ha seleccionado ninguna fila.")
            return

        # Obtiene los valores de cada columna en la fila seleccionada
        valores_fila = [
            self.tablaProtocolo.item(fila_seleccionada, col).text()
            for col in range(self.tablaProtocolo.columnCount())
        ]

        # Realiza acciones con los valores obtenidos
        #print("Valores de la fila seleccionada:", valores_fila)

        #print("ID Del procolo: ", valores_fila[0])
        #print("Nombre del protocolo: ", valores_fila[1])
        if valores_fila[4].lower()=="si": #Significa que se encuentra vigente
            try:
                #print(valores_fila[0])
                print("se ingreso a configurar instrumento")
                app = AsociarConfiguracionInstrumento(bbdd=self.database,id_protocolos=valores_fila[0])
                app.exec_()
                print("se salio de configurar instrumentos")

                self.database.bloquePaso(id = valores_fila[0])
                print("Se ha copiado el Protocolo en un temporal")

                #######ASOCIAR NUMERO DE SERIE#################
                #Lo tengo que hacer aca, porque es el lugar donde ya se encuentra el nuevo protocolo creado, debo asociarle un Numero de Serie
                #Debido a esto, muy posiblemente haya un problema cuando se ingrese el numero de serie

                print(f"El id del protocolo es {self.database.ID_PROTOCOLO_CREADO[0]}")
                print(f"El primer id de bloque es {self.database.ID_PROTOCOLOS_BLOQUE_CREADO[0]}")

                app_serial = IngresarNumeroSerie(bbdd = self.database,
                                                 id_protocolo_modelo=valores_fila[0],
                                                 id_protocolos=str(self.database.ID_PROTOCOLO_CREADO[0]),
                                                 id_protocolo=str(self.database.ID_PROTOCOLOS_BLOQUE_CREADO[0])
                                                 )
                app_serial.exec_()


                self.runProtocolo.cargarDatos() #Le cargo los datos al run 
                #self.runProtocolo.cantidadBloques() #Le cargo la cantidad de bloques del protocolo
                #self.runProtocolo.show() #Muestro la pantalla
                self.runProtocolo.mostrar_bloques_protocolo()
                #self.runProtocolo.loop_ejecucion()
                self.runProtocolo.iniciarEjecucion() #Inicia la ejecucion del segundo hilo
                self.runProtocolo.exec_()
            except:
                raise("NO SE PUDO LEER EL PATH")
        else:
            #Se debe agregar interfaz grafica
            print("NO SE ENCUENTRA VIGENTE ESE PROTOCOLO")
