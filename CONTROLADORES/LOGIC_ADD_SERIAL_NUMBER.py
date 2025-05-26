from PyQt5.QtWidgets import QTableWidgetItem
import time

def configurar_logica_agregar_serial_number(win):
    #CONFIGURACIONES DE INICIO
    win.info_modulo = None #Auxiliar 1, la debo crear para poder accederla al main
    win.info_modulo_ns = None #Auxiliar para luego subir en caso de que se ingrese un nuevo valor
    win.LASTID = None #Id que se crea
    win.TablaConfig.clicked.connect(lambda: showModulosConNS(win))
    win.TablaNumeroSerie.clicked.connect(lambda: updateValues(win))
    win.newSerialNumber.clicked.connect(lambda: updateNumeroSerie(win))
    win.avanzarRunProtocolo.clicked.connect(lambda: asociarNumeroSerie(win))
    win.updateModulosTable = lambda: updateModulosTable(win) #Antes llamado showModulo

def updateModulosTable(win):

    """
    Muestra los valores de la tabla, con esta luego se seleccionara el codigo referente a los equipos/modulos
    """
    if win.info_modulo ==None: #En caso que el auxiliar se mantenga en none (primer iteracion)
        #Tengo que usar los valores de protocolo modelo para llamar la funcion
        info_modulo = win.database.getModuloFromIds(win.database.ID_BLOQUE_MODELO,win.database.ID_MODELO) #Esto me devuelve: idmodulos_endisegno,Nombre,Codigo,protocolo_protocolos_idProtocolos,modulos_endisegno_idmodulos_endisegno
        win.TablaConfig.setRowCount(len(info_modulo))
        win.TablaConfig.setItem(0, 0, QTableWidgetItem(str(info_modulo[0])))
        win.TablaConfig.setItem(0, 1, QTableWidgetItem(str(info_modulo[1])))
        win.TablaConfig.setItem(0, 2, QTableWidgetItem(str(info_modulo[2])))
        win.TablaConfig.setItem(0, 3, QTableWidgetItem(""))
        win.info_modulo = info_modulo
    else:
        win.TablaConfig.setRowCount(len(win.info_modulo))
        win.TablaConfig.setItem(0, 0, QTableWidgetItem(str(win.info_modulo[0])))
        win.TablaConfig.setItem(0, 1, QTableWidgetItem(str(win.info_modulo[1])))
        win.TablaConfig.setItem(0, 2, QTableWidgetItem(str(win.info_modulo[2])))
        win.TablaConfig.setItem(0, 3, QTableWidgetItem(str(win.info_modulo[5])))
def showModulosConNS(win):

    print(win.info_modulo)
    if win.info_modulo !=None:
        getInfoNS = win.database.getModulosFromCodigo(win.database.ID_BLOQUE_MODELO,win.database.ID_MODELO)
        win.TablaNumeroSerie.setRowCount(len(getInfoNS))
        for row, values in enumerate(getInfoNS):

            win.TablaNumeroSerie.setItem(row, 0, QTableWidgetItem(str(values[0])))
            win.TablaNumeroSerie.setItem(row, 1, QTableWidgetItem(str(values[1])))
            win.TablaNumeroSerie.setItem(row, 2, QTableWidgetItem(str(values[2])))
            win.TablaNumeroSerie.setItem(row, 3, QTableWidgetItem(str(values[4])))
            win.TablaNumeroSerie.setItem(row, 4, QTableWidgetItem(str(values[5])))
            win.TablaNumeroSerie.setItem(row, 5, QTableWidgetItem(str(values[3])))
            win.TablaNumeroSerie.setItem(row, 6, QTableWidgetItem(str(values[6])))

def asociarNumeroSerie(win):
    """
    Funcion que incrusta al Numero de serie al nuevo protocolo creado
    """
    if win.LASTID != None:
        print(win.id_protocolos_nuevo,win.id_protocolo_nuevo,win.LASTID)
        win.database.asociarModuloaProtocolo(id_protocolos = win.id_protocolos_nuevo,id_protocolo=win.id_protocolo_nuevo,LASTID=win.LASTID)
        #self.close()  # Cierra la ventana

def updateNumeroSerie(win):
    """
    Se encarga de actualizar self.info_modulo con el numero de serie para luego subirlo
    """
    if win.info_modulo != None:
        numeroSerie = win.SerialNumber.toPlainText() #Es el metodo que usa el QTextEdit para tener el valor que tiene la celda
        if len(win.info_modulo)==5:
            win.info_modulo.append(numeroSerie)
        elif len(win.info_modulo)>5:
            win.info_modulo[5]=numeroSerie
        
        win.info_modulo_ns[4]=numeroSerie
        if win.database.checkIngresadoExiste(win.info_modulo_ns):
            win.updateModulosTable()
        else:
            win.updateModulosTable()
            #En caso que no exista se debe subir.....
            win.LASTID = win.database.insertNuevoModulo(win.info_modulo_ns)

def updateValues(win):
    currentRow = win.TablaNumeroSerie.currentRow() #Con esto selecciono el indice de la fila correspondiente desde 0 a N-1 
    if currentRow == -1:  # Verifica si no hay ninguna fila seleccionada
        print("No se ha seleccionado ninguna fila nabo.") #Este mensaje serie un easter egg, no deberia aparecer
        print("Created by Juan Cruz Noya 28/03/2025")
        return
    rowValue = [
        win.TablaNumeroSerie.item(currentRow, col).text()
        for col in range(win.TablaNumeroSerie.columnCount())
    ] #Me devuelve una lista con los valores seleccionado en ese indice
    print(rowValue)
    win.Nombre.setText(rowValue[2])
    win.Codigo.setText(rowValue[3])
    win.SerialNumber.setText(rowValue[4])
    win.LASTID = rowValue[0] #Selecciono el ID en caso de cargarlo.....
    win.info_modulo_ns = rowValue #id,categoria,nombre,codigo,ns,orden,Estado