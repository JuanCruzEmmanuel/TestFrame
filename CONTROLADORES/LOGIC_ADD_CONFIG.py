from PyQt5.QtWidgets import QTableWidgetItem
import time
def configurar_logica_agregar_config(win):
    """
    CONFIGURACIONES DE INICIO
    """
    win.TablaExistentes.clicked.connect(lambda: updateConfigSeleccionada(win))
    win.Avanzar.clicked.connect(lambda: setConfig(win))
    win.retroceder.clicked.connect(lambda: back_to_main(win))
    win.updateTablaConfig = lambda: updateTablaConfig(win) #Con esto puedo llamar cuando quiero a actualizar la tabla
    win.config_seleccionada = None
def updateTablaConfig(win):
    BASEDEDATOS = win.database
    ID_PROTOCOLOS = win.id_seleccionado
    configuracion =BASEDEDATOS.getConfigPuestoaPartirdeIdDelProtocolo(id =ID_PROTOCOLOS)
    win.TablaExistentes.setRowCount(len(configuracion))

    for row,config in enumerate(configuracion):   
        win.TablaExistentes.setItem(row, 0, QTableWidgetItem(str(config[0])))
        win.TablaExistentes.setItem(row, 1, QTableWidgetItem(str(config[1])))
        win.TablaExistentes.setItem(row, 2, QTableWidgetItem(str(config[4])))


def updateConfigSeleccionada(win):

    currentRow = win.TablaExistentes.currentRow() #Con esto selecciono el indice de la fila correspondiente desde 0 a N-1 
    if currentRow == -1:  # Verifica si no hay ninguna fila seleccionada
        print("No se ha seleccionado ninguna fila nabo, ¿otra vez por aca?.") #Este mensaje serie un easter egg, no deberia aparecer
        print("Created by Juan Cruz Noya 28/03/2025")
        return
    rowValue = [
        win.TablaExistentes.item(currentRow, col).text()
        for col in range(win.TablaExistentes.columnCount())
    ] #Me devuelve una lista con los valores seleccionado en ese indice
    #print(rowValue)

    win.config_seleccionada = rowValue

def setConfig(win):

    if win.config_seleccionada != None:
        idconfig = win.config_seleccionada[0]

        win.bbdd.setConfigEnProtocolo(id_config=idconfig,id_protocolo=win.id_seleccionado)
    else:
        pass
def back_to_main(win):
    """
    Se encarga de volver al main_windows del stack
    """
    win.stacks.setCurrentWidget(win.main)