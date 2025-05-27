# controllers/page_main_logic.py
from PyQt5.QtWidgets import QTableWidgetItem
#from GUI.AsociarConfig import AsociarConfiguracionInstrumento
#from GUI.IngresarNumeroSerie import IngresarNumeroSerie

def configurar_logica_pagina_principal(win):
    """
    Funcion encargada de configurar los botones y logica, lo que neceita en si mismo es el estado actual, por eso recibe un parametro "win" que refleja el self de la anterior
    """
    win.apFiltroNombre.clicked.connect(lambda: filtrar_tabla_por_nombre(win))
    win.UpdateBoton.clicked.connect(lambda: update(win))
    win.EjecutarBoton.clicked.connect(lambda: ejecutar_fila_seleccionada(win))
    win.command_btn.clicked.connect(lambda: ejecutar_comando(win))
    mostrar_todos_los_datos(win)

def mostrar_todos_los_datos(win):
    datos = win.datos
    tabla = win.tablaProtocolo
    tabla.setRowCount(len(datos))
    tabla.setColumnCount(6)
    tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Ver", "Tipo", "Vigente", "Comentario"])

    for row, (id_, values) in enumerate(datos.items()):

        tabla.setItem(row, 0, QTableWidgetItem(id_))  # ID
        tabla.setItem(row, 1, QTableWidgetItem(values[0]))  # Nombre
        tabla.setItem(row, 2, QTableWidgetItem(values[1]))  # Versión
        tabla.setItem(row, 3, QTableWidgetItem(values[3]))  # Tipo
        tabla.setItem(row, 4, QTableWidgetItem(values[2]))  # Vigente
        tabla.setItem(row, 5, QTableWidgetItem(values[4]))  # Comentario



def filtrar_tabla_por_nombre(win):
    filtro = win.nombreFiltro.text().lower()
    vigencia = win.tipoVigencia.currentText()
    tipo = win.tipoItem.currentText()
    dic_vig = {"Vigente": "SI", "No Vigente": "NO", "Mostrar Todo": ""}

    datos = {
        id_: v for id_, v in win.datos.items()
        if filtro in v[0].lower() and dic_vig[vigencia].lower() in v[2].lower()
        and ("" if tipo == "Mostrar Todo" else tipo.lower()) in v[3].lower()
    }

    tabla = win.tablaProtocolo
    tabla.setRowCount(len(datos))
    for row, (id_, values) in enumerate(datos.items()):
        tabla.setItem(row, 0, QTableWidgetItem(id_))  # ID
        tabla.setItem(row, 1, QTableWidgetItem(values[0]))  # Nombre
        tabla.setItem(row, 2, QTableWidgetItem(values[1]))  # Versión
        tabla.setItem(row, 3, QTableWidgetItem(values[3]))  # Tipo
        tabla.setItem(row, 4, QTableWidgetItem(values[2]))  # Vigente
        tabla.setItem(row, 5, QTableWidgetItem(values[4]))  # Comentario


def update(win):
    win.database.protocoloQuery()
    win.datos = win.cargar_datos_json()
    mostrar_todos_los_datos(win)

def ejecutar_fila_seleccionada(win):
    fila = win.tablaProtocolo.currentRow()
    if fila == -1:
        print("No hay fila seleccionada.")
        return

    valores = [
        win.tablaProtocolo.item(fila, col).text()
        for col in range(win.tablaProtocolo.columnCount())
    ]
    no_ignore=True
    if valores[4].lower() == "si":
        try:
            win.id_seleccionado = valores[0]
            #print(valores[0])
            win.stacks.setCurrentWidget(win.asoconfig)
            win.updateTablaConfig()
            #app = AsociarConfiguracionInstrumento(bbdd=win.database, id_protocolos=valores[0])
            if no_ignore:
                #app.exec_()
                """win.database.bloquePaso(id=valores[0]) #Crea temporal
                print("Se ha copiado el Protocolo en un temporal")
                #######ASOCIAR NUMERO DE SERIE#################
                #Lo tengo que hacer aca, porque es el lugar donde ya se encuentra el nuevo protocolo creado, debo asociarle un Numero de Serie
                #Debido a esto, muy posiblemente haya un problema cuando se ingrese el numero de serie
                win.id_protocolos_nuevo = win.database.ID_PROTOCOLO_CREADO[0]
                win.id_protocolo_nuevo = win.database.ID_PROTOCOLOS_BLOQUE_CREADO[0]
                win.updateModulosTable(win) #Actualizo la tabla de modulos"""
                """app_serial = IngresarNumeroSerie(
                    bbdd=win.database,
                    id_protocolo_modelo=valores[0],
                    id_protocolos=str(win.database.ID_PROTOCOLO_CREADO[0]),
                    id_protocolo=str(win.database.ID_PROTOCOLOS_BLOQUE_CREADO[0])
                )
                app_serial.exec_()"""

                """
                win.runProtocolo.cargarDatos()
                win.runProtocolo.mostrar_bloques_protocolo()
                win.runProtocolo.iniciarEjecucion()
                win.runProtocolo.show()"""
        except Exception as e:
            print(f"Error al ejecutar: {e}")
    else:
        print("Protocolo no vigente")

def ejecutar_comando(win):

    CMD = win.command_box.toPlainText()
    win.comand_translator.translate(CMD=CMD)