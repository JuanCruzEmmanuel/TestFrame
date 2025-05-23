from PyQt5.QtWidgets import QTableWidgetItem

def configurar_logica_agregar_config(win):
    
    win.TablaExistentes.clicked.connect(lambda: updateConfigSeleccionada(win))
    win.Avanzar.clicked.connect(lambda: setConfig(win))
    win.retroceder.clicked.connect(lambda: back_to_main(win))

def updateTablaConfig(win):
    BASEDEDATOS = win.database
    ID_PROTOCOLOS = win.id_protocolos
    configuracion =BASEDEDATOS.getConfigPuestoaPartirdeIdDelProtocolo(id =ID_PROTOCOLOS)
    tabla=win.TablaExistentes.setRowCount(len(configuracion))

    for row,config in enumerate(configuracion):   
        tabla.setItem(row, 0, QTableWidgetItem(str(config[0])))
        tabla.setItem(row, 1, QTableWidgetItem(str(config[1])))
        tabla.setItem(row, 2, QTableWidgetItem(str(config[4])))

def updateConfigSeleccionada(win):
    pass

def setConfig(win):
    pass

def back_to_main(win):
    """
    Se encarga de volver al main_windows del stack
    """
    win.stacks.setCurrentWidget(win.main)