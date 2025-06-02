import pyodbc
import json
import time

class SMVA_DB():
    _DATABASE = "dbfeas_smva_2_0_v1"
    def __init__(self):
        
        self.user = None
        self.vigente = "Vigente"
        self.protocoloLista = None
        self.filterName = ""
        self.ID_MODELO = None
        self.ID_BLOQUE_MODELO = None
        self.ID_PROTOCOLO_CREADO = None
        self.ID_PROTOCOLOS_BLOQUE_CREADO = None
        self.saltos_protocolo = {}
        self.SALTOS_CONDICIONALES = {}
        self.test = False
        self.cursor = self.connect()
        self.USUARIO_SMVA = None
    def close(self):
        self.cursor.close()

    def setUser(self,usuario):
        """
        Funcion que setea el usuario
        """
        self.USUARIO_SMVA=usuario
    def connect(self):
        """
        FUNCION QUE SE ENCARGA DE CONECTAR A LA BD y se puede trabajar directamente con CURSORES
        :RETURN cursor: Cursor de manejo BD
        """
        if self.test:
            IP = "192.168.0.141"
        else:
            IP = "192.168.0.4"
        cnxn = pyodbc.connect(
        r'DRIVER=MySQL ODBC 3.51 Driver;'
        rf'Server={IP};' #Para trabajar con el test
        r'Database=dbfeas_smva_2_0_v1;'
        r'Port=3306;'
        r'UID=remoto;'
        r'Password=remoto'
        )   

        cnxn.autocommit = True  # Desactivar múltiples conjuntos de resultados
        cursor = cnxn.cursor()

        return cursor

    def set_test(self):
        """
        Inicia el modo testeo
        """
        self.test=True

    def userQuery(self):

        query = f"""
            SELECT * FROM {self._DATABASE}.user;
            """
        self.cursor.execute(query)

        response = self.cursor.fetchall()

        self.user = response #Devuelve la lista de usuarios es importante que aca esta en forma de lista, luego nosotros debemos convertirla en un diccionario para su facil utilizacion

        return response

    def protocoloQuery(self):

        """
        Metodo que actualiza la lista de protocolos que luego se debe utilizar para seleccionar

        :seen_combinations: Utiliza un conjunto para llevar un registro de las combinaciones de Name y Version ya procesadas.
        :Filtrar duplicados: Recorre la lista de resultados (self.protocoloLista) y agrega a filtered_protocols solo los registros cuya combinación de Name y Version no se haya visto antes.
        :Diccionario final: Usa los registros filtrados para crear el diccionario dic_protocolos con idProtocolos como clave.

        :return: Devuelve el protocolo en _TEMPS_




        """
        dic_vigente = {
            "Vigente": "SI",
            "No Vigente": "NO"
        }
        disable = True
        if not disable:
            if self.vigente !="Mostrar Todo":
                query = f"""
                SELECT idProtocolos, Name, Version, Vigente, Tipo, Comentario 
                FROM {self._DATABASE}.protocolos 
                WHERE Vigente='{dic_vigente[self.vigente]}' AND Resultado = "MODELO";
                """

            else:
                query = f"""
                SELECT idProtocolos, Name, Version, Vigente, Tipo, Comentario 
                FROM {self._DATABASE}.protocolos 
                WHERE Resultado = "MODELO";
                """
        else:
            query = f"""
            SELECT idProtocolos, Name, Version, Vigente, Tipo, Comentario 
            FROM {self._DATABASE}.protocolos 
            WHERE Resultado = "MODELO";
            """
        self.cursor.execute(query)
        self.protocoloLista = self.cursor.fetchall() #Lista con todos los reultados de mi consulta

        # Filtrar solo el primer resultado para cada combinación de Name y Version
        seen_combinations = set()
        filtered_protocols = []
        for record in self.protocoloLista:
            name_version = (record[1], record[2])  # (Name, Version)
            if name_version not in seen_combinations:
                filtered_protocols.append(record)
                seen_combinations.add(name_version)

        # Crear un diccionario por idProtocolos
        dic_protocolos = {str(data[0]): list(data[1:]) for data in filtered_protocols}

        # Guardar el resultado en un archivo JSON
        with open("_TEMPS_/protocolos.json", "w") as file:
            json.dump(dic_protocolos, file)


    def bloquePaso(self, id):

        """
        Esta función arma un protocolo a ejecutar en base al ID seleccionado.
        :param id: ID del protocolo recibido desde main_window al presionar ejecutar.
        :return: Guarda en _TEMPS_ un JSON con el protocolo a ejecutarse.
        """
        id = self.ID_PROTOCOLO_COPIA(id = id) #OBTENGO EL NUEVO ID

        #Este paso demora aproximadamente 20 segundos de cronometro. Se deberia ver la forma de hacerlo mas eficiente, aunque para ser realista tiene que copiar varias cosas en simultaneo

        # Consulta para obtener el protocolo principal
        query = f"""
                SELECT idprotocolo, Name, ordenSecuencia, configuracion_idConfiguracion
                FROM {self._DATABASE}.protocolo
                WHERE protocolos_idProtocolos = {id};
                """
        
        self.cursor.execute(query)
        protocolos = self.cursor.fetchall()

        # Estructura para el JSON
        resultado_json = []

        # Procesar cada protocolo
        for protocolo in protocolos:
            protocolo_id, protocolo_name, ordenSecuencia, configuracion_idConfiguracion = protocolo

            # Consulta para obtener los pasos del protocolo
            query = f"""
                    SELECT Name, Tipo, ResultadoTipico, ResultadoMaximo, ResultadoMinimo, 
                           FactorConversion, Unidad, Tipo_Item, Validacion, 
                           Respuesta_Correcta, Comandos, OrdenDeSecuencia,Tiempo_Medicion,
                           Tipo_Respuesta,protocolo_idprotocolo,protocolo_protocolos_idProtocolos,mediciones_idmediciones,idpasos
                    FROM {self._DATABASE}.pasos
                    WHERE protocolo_idprotocolo = {protocolo_id};
                    """
            self.cursor.execute(query)
            pasos = self.cursor.fetchall()
            # Formatear los pasos
            pasos_json = [
                {
                    "Nombre": paso[0],
                    "Tipo": paso[1],
                    "ResultadoTipico": paso[2],
                    "ResultadoMaximo": paso[3],
                    "ResultadoMinimo": paso[4],
                    "FactorConversion": paso[5],
                    "Unidad": paso[6],
                    "Tipo_Item": paso[7],
                    "Validacion": paso[8],
                    "Respuesta_Correcta": paso[9],
                    "Comandos": paso[10],
                    "OrdenDeSecuencia": paso[11],
                    "Tiempo_Medicion":paso[12],
                    "Tipo_Respuesta":paso[13],
                    "Resultado":"",
                    "Estado":"",
                    "protocolo_idprotocolo":paso[14],
                    "protocolo_protocolos_idProtocolos":paso[15],
                    "mediciones_idmediciones":paso[16],
                    "id_paso":paso[17],
                    "CriterioPass":"",
                    "TimeStamp":""
                }
                for paso in pasos
            ]

            # Agregar protocolo con sus pasos al JSON
            resultado_json.append({
                "ProtocoloID": protocolo_id,
                "Nombre": protocolo_name,
                "Pasos": pasos_json,
                "ordenSecuencia":ordenSecuencia,
                "Resultado":"",
                "Operador":""
            })

        # Guardar en un archivo JSON
        with open('_TEMPS_/protocolo_a_ejecutar.json', 'w', encoding='utf-8') as json_file:
            json.dump(resultado_json, json_file, ensure_ascii=False, indent=4)

        print(f"Archivo JSON guardado correctamente en '_TEMPS_/protocolo_a_ejecutar.json'.")
        #DECIDI AGREGAR ESTA SECCION PARA QUE LOS SALTOS CONDICIONALES YA ESTEN DISPONIBLES DESDE EL MOMENTO 0
        for i, bloque in enumerate(resultado_json):
            for j, paso in enumerate(bloque["Pasos"]):
                comandos = paso.get("Comandos", "")
                if "ETIQ:" in comandos:
                    partes = comandos.split('ETIQ:') #cAMBIO ESTA SINTAXIS PARA SER MAS EFICIENTE
                    if len(partes) > 1:
                        etiqueta = partes[1]
                        if ";" in etiqueta:
                            etiqueta = etiqueta.split(";")[0]
                        try:
                            etiqueta = etiqueta.split('"')[1] #aGREGO QUE LUEGO DEL ETIQ BUSQUE LO SIGUIENTE A LAS COMILLAS
                        except:
                            pass
                        self.SALTOS_CONDICIONALES[etiqueta.strip()] = {"i": i, "j": j} #VARIABLE QUE CONTROLA LOS SALTOS CONDICIONALES

    def ID_PROTOCOLO_COPIA(self,id="1"):
        self.cursor.execute("{CALL selectProtocolosFromId (?)}",(id))

        MODELO = self.cursor.fetchall()[0] #Protocolo modelo

        NOMBREPROTOCOLO = MODELO[1]
        VERSIONPROTOCOLO= MODELO[2]
        VIGENCIAPROTOCOLO = MODELO[3]
        TIPOPROTOCOLO = MODELO[4]
        COMENTARIOPROTOCOLO = MODELO[5]
        RESULTADOPROTOCOLO = "NUEVO"
        #Creo un nuevo protocolo con los datos del modelo, y obtengo su ID
        self.cursor.execute("{CALL insertProtocolosAndLastId_2_0 (?,?,?,?,?,?)}",(NOMBREPROTOCOLO,VERSIONPROTOCOLO,VIGENCIAPROTOCOLO,TIPOPROTOCOLO,COMENTARIOPROTOCOLO,RESULTADOPROTOCOLO))


        self.ID_MODELO = id
        
        LASTID = self.cursor.fetchall()[0] #Hasta este punto ya tengo el nuevo protocolo. Ahora se debe crear los bloques y los pasos
        self.ID_PROTOCOLO_CREADO = LASTID #Me guardo el ID copiado
        self.cursor.execute("{CALL GetprotocoloFromIdProtocolos (?)}",(id))

        BLOQUEMODELOS = self.cursor.fetchall() #Obtengo los bloques del protocolo modelo
        
        #self.cursor.execute("{CALL GetprotocoloFromIdProtocolos (?)}",(LASTID[0])) #Necesito el primer ID bloque del nuevo protocolo

        #self.ID_PROTOCOLOS_BLOQUE_CREADO = self.cursor.fetchall()[0] #Necesito el primer ID bloque del nuevo protocolo

        for index, BLOQUE in enumerate(BLOQUEMODELOS):
            NOMBREBLOQUE = BLOQUE[1]
            EQUIPOBLOQUE = BLOQUE[2]
            REVISIONBLOQUE = BLOQUE[3]
            ESTADOBLOQUE = BLOQUE[4]
            IDBLOQUE = BLOQUE[0] #CON ESTO VAMOS A OBTENER LA INFO DE LOS INSTRUMENTOS "creo"
            #print(IDBLOQUE)
            if index == 0:
                self.ID_BLOQUE_MODELO =IDBLOQUE #Obtengo el primer valor del id bloque protocolo
            CONFIG_IDCONFIG = BLOQUE[11]
            IDCONFIG = BLOQUE[12]
            SECUENCIABLOQUE = BLOQUE[13]
            self.cursor.execute("{CALL insertprotocoloAndLastId (?,?,?,?,?,?,?,?,?,?,?,?,?)}",(NOMBREBLOQUE,EQUIPOBLOQUE,REVISIONBLOQUE,ESTADOBLOQUE,"","","","","NUEVO",int(str(LASTID[0])),CONFIG_IDCONFIG,0,SECUENCIABLOQUE))
            
            IDCAMBIO = self.cursor.fetchall()[0] #Obtengo el id nuevo
            if index == 0:
                self.ID_PROTOCOLOS_BLOQUE_CREADO = IDCAMBIO
            #En este punto empiza a hacer varias cosas en paralelo el SMVA voy a intentar replicarlas toda
            #---------------------ASOCIAR EQUIPO Y PROTOCOLO EN DISEÑO-----------------------------------------------#
            self.cursor.execute("{CALL GetEquipoFromIdprotocoloAndProtocolo_endisegno (?,?)}",(IDBLOQUE,id))
            DATA = self.cursor.fetchall() #cREO QUE SIEMPRE ES UN ELEMENTO VACIO POR LO QUE SE PUEDE EVALUAR ELIMINARLO DIRECTAMENTE Y REDUCIR TIEMPOS INNECESARIOS

            #---------------------ASOCIAR MODULO y PROTOCOLO EN DISEÑO-----------------------------------------------#
            self.cursor.execute("{CALL GetModuloFromIdprotocoloAndProtocolo_endisegno (?,?)}",(IDBLOQUE,id))
            try:
                DATA = self.cursor.fetchall()[0]
                IDCOMPONENTEDISEÑO = DATA[0] #OBTENGO EL VALOR DEL ID
                #CUANDO DATA SEA EMPTY esto se anula
                self.cursor.execute("{CALL AsocModuloAndprotoc_endisegno (?,?,?)}",(int(str(IDCAMBIO[0])),LASTID,IDCOMPONENTEDISEÑO)) #Asocio al nuevo bloque los valores obtenidos del modelo #Al parecer solo al primer bloque

            except:
                pass
            #--------------------ASOCIAR COMPONENTE y PROTOCOLO EN DISEÑO--------------------------------------------#
            self.cursor.execute("{CALL GetComponenteFromIdprotocoloAndProtocolo_endisegno (?,?)}",(IDBLOQUE,id))
            try:
                DATA = self.cursor.fetchall()[0]
                IDCOMPONENTEDISEÑO = DATA[0] #OBTENGO EL VALOR DEL ID
                #SI DA EMPTY ESTO SE ANULA
                self.cursor.execute("{CALL AsocComponenteAndprotoc_endisegno (?,?,?)}",(int(str(IDCAMBIO[0])),int(str(LASTID[0])),IDCOMPONENTEDISEÑO))
            except:
                pass
            
            #--------------------------------UPDATE CONFIG ----------------------------------------------------------#
            self.cursor.execute("{CALL updateConfigEnprotocolo_endisegno (?,?,?)}",(IDCONFIG,int(str(IDCAMBIO[0])),int(str(LASTID[0]))))
            #self.cursor.fetchall()
        #-----------------------------------COPIAR LOS PASOS--------------------------------------------------------#
        ### ESTO ES LO QUE PIERDE TIEEEEEEEMPO SE DEBE ACTUALIZAR URGENTE ESTA
        #print(id,str(LASTID[0]))
        #self.cursor.execute("{CALL CopiarProtocoloModelo_2 (?,?)}",(id,str(LASTID[0]))) #Recibe el ID del protocolo nuevo, y el id del protocolo modelo
        self.copiar_protocolo_modelo(val1 = int(id),val2 = int(LASTID[0])) #Replica del metodo anterior
        #self.cursor.fetchall()
        ### ESTO ES LO QUE PIERDE TIEEEEEEEMPO SE DEBE ACTUALIZAR URGENTE ESTA
        #self.cursor.execute("{CALL GetCantPasosyValueMedicion (?)}",(str(LASTID[0])))
        #datos = self.cursor.fetchall()[0]
        datos = self.getCantidadPasos(id=str(LASTID[0]))
        if datos[0]==datos[1]:
            pass
        else:
            "ERROR_0XXX"
        #self.cursor.execute("{CALL DEBUG_CorreccionValueMediciones (?)}",(int(str(LASTID[0]))))
        #self.cursor.fetchall()
        return str(LASTID[0])

    def subir_paso_protocolo_y_protocolo(self,id_protocolo,resultado_bloque,pasos):
        """
        FUNCION QUE SE ENCARGA DE SUBIR EL PROTOCOLO LOCAL A LA BASE DE DATOS \n
        :id_protocolo: El ID del bloque\n
        :resultado_bloque: Resultado del bloque\n
        :pasos: json de los pasos\n
        
        """


        print("Se inicializa la subida de archivos")
        #print(resultado_bloque)
        #print(pasos)
        N=0
        T_INICIO =""
        T_FIN = ""
        for paso in pasos:
            id_paso = paso["id_paso"] #El id del paso
            estado_paso = paso["Estado"] #Estado de paso
            resultado_paso = paso["Resultado"] #Resultado de paso
            criterio_paso = paso["CriterioPass"]
            id_mediciones = paso["mediciones_idmediciones"]
            timestamp = paso["TimeStamp"]
            if N==0:
                T_INICIO=paso["TimeStamp"] #Tiempo de inicio
            self.cursor.execute(f"""UPDATE {self._DATABASE}.pasos SET CriterioPass = ?, Estado = ?, CriterioPass = ?, TimeStamp = ? WHERE idpasos = ?""",(estado_paso, estado_paso,criterio_paso,timestamp,id_paso)) #Actualizo el paso
            #Actualizar el valor medido
            #Para ello primero debo pedir el id que relaciona mediciones con su valor (totalmente ineficiente)
            self.cursor.execute(f"""SELECT valuemedicion_idvaluemedicion FROM {self._DATABASE}.mediciones WHERE idmediciones={id_mediciones}""")
            id_value_mediciones = self.cursor.fetchall()[0][0] #ID value mediciones
            self.cursor.execute(f"""UPDATE {self._DATABASE}.valuemedicion SET ValorMedido = ?, EstadoMedicion = ?, TimeStamp = ? WHERE idvaluemedicion = ?""",(resultado_paso,estado_paso,timestamp,id_value_mediciones)) #Actualizo el paso
            N+=1
        #Una vez termine esto, se debe actualizar 
        T_FIN=paso["TimeStamp"] #Tiempo de fin
        if resultado_bloque=="ABORT":
            _PASADA_ = "INCOMPLETO"
        elif resultado_bloque!="ABORT":
            _PASADA_ = "COMPLETO"
        else:
            _PASADA_ = "INCOMPLETO"
        #Tambien se debe guardar info del operador, se debe agregar esa info
        self.cursor.execute(f"""UPDATE {self._DATABASE}.protocolo SET StartTime = ?, EndTime=  ?, Resultado = ?, Pasadas = ?, Aprobador =? WHERE idprotocolo = ?""",(T_INICIO,T_FIN,resultado_bloque,_PASADA_,self.USUARIO_SMVA,id_protocolo))
        print("Se subio")


    
    def copiar_protocolo_modelo(self, val1:int, val2:int):
        """
        Replica la lógica del procedimiento almacenado CopiarProtocoloModelo en Python.\n
        No maneja la conexión a la base de datos, ya que trabaja con el cursor\n
        Se reduce de 30 segundos a menos de 2 segundos\n
        :val1: ID del protocolo "MODELO"\n
        :val2: ID del nuevo protocolo\n
        """
        self.cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
        self.cursor.execute("SET sql_mode = '';")
        
        # Realizo la consulta que realiza CopiarProtocoloModelo pero modifico algunos metodos de consulta. Mas abajo voy a enumerar que es cada consulta
        query = f"""
            SELECT idpasos, pasos.Name as Name_Pasos, CriterioPass, Tipo, pasos.Estado as Estado_P, Observacion, 
                ResultadoTipico, ResultadoMaximo, ResultadoMinimo, pasos.TimeStamp as Tiempo_P, Ajustar, 
                pasos.Unidad as Unidad_P, Comandos, Saltar, FactorConversion, Imprimible, Habilitado, OrdenDeSecuencia, 
                Tipo_Item, Titulo, Inicio_Bloque, Validacion, Tipo_Respuesta, Respuesta_Correcta, Offset, 
                Tiempo_Medicion, Simular, Medir_o_Conectar, idmediciones, mediciones.Name as Name_M, Descripcion, 
                Escala, mediciones.Unidad as Unidad_M, Rango, SerialNumber, Codigo, Version, listainstrumentos_idListaInstrumentos, 
                idvaluemedicion, ValorMedido, EstadoMedicion, valuemedicion.TimeStamp as Tiempo_V, idprotocolo, 
                protocolo.Name as Name_Protocolo, Equipo, Revision, protocolo.Estado as Estado_Protocolo, 
                Resultado, Aprobador, StartTime, EndTime, Pasadas, protocolos_idProtocolos, 
                configuracion_idConfiguracion, config_endisegno_idConfig, ordenSecuencia
            FROM {self._DATABASE}.pasos
            INNER JOIN {self._DATABASE}.mediciones ON mediciones_idmediciones = idmediciones
            INNER JOIN {self._DATABASE}.valuemedicion ON valuemedicion_idvaluemedicion = idvaluemedicion
            INNER JOIN {self._DATABASE}.protocolo ON protocolo_idprotocolo = idprotocolo
            WHERE protocolo_idprotocolo IN (
                SELECT idprotocolo FROM {self._DATABASE}.protocolo WHERE protocolos_idProtocolos = ?
            )
            ORDER BY CAST(ordenSecuencia AS DECIMAL) ASC, CAST(ordenDeSecuencia AS DECIMAL) ASC;
        """
        self.cursor.execute(query, val1)
        todas_las_tablas = self.cursor.fetchall() #Confirmado por chayanne que funciona
        """
        todas_las_tablas contine:
        0 idpasos
        1 Name (Name_Pasos)
        2 Criterio de paso (CriterioPass)
        3 Tipo
        4 Estado (Estado_P)
        5 Observacion
        6 ResultadoTipico
        7 ResultadoMaximo
        8 ResultadoMinimo
        9 Tiempo timestamp (Tiempo_P)
        10 Ajustar
        11 Unidad_P
        12 Comandos
        13 Saltar
        14 FactorConversion
        15 Imprimible
        16 Habilitado
        17 OrdenSecuencia
        18 Tipo de Item
        19 Titulo
        20 Inicio de Bloque
        21 Validacion
        22 Tipo de respuesta
        23 Respuesta Correcta
        24 Offset
        25 Tiempo de medicion
        26 Simular
        27 Medio o Conectar
        28 idmediciones
        29 Name medicion (Name_M)
        30 Descripcion (supongo que de medicion)
        31 Escala
        32 Unidad Medicion
        33 Rango
        34 Serial Number
        35 Codigo
        36 Version
        37 listainstrumentos_idListaIntrusmentos
        38 idvaluemediciones
        39 ValorMedido
        40 EstadoMedicion
        41 Tiempo_V
        42 idprotocolo
        43 Name_Protocolo (nombre del bloque)
        44 Equipo
        45 Revision
        46 Estado Protocolo
        47 Resultado
        48 Aprobador
        49 StartTime
        50 EndTime
        51 Pasadas
        52 protocolos_idProtocolos
        53 configuracion_idConfiguracion
        54 config_endisegno_idConfig
        55 ordenSecuencia
        """
        #for fila in todas_las_tablas:
            #print(fila[0])
        # Contar bloques en Python
        print("\n")
        protocolos_unicos = {fila[42] for fila in todas_las_tablas} #42 = idprotocolo
        cant_bloques = len(protocolos_unicos)
        print(f"La cantidad de bloques distintos es de {cant_bloques}")
        for iterador_bloques in range(cant_bloques):
            #print(f"Nos encontramos en el bloque {iterador_bloques}")
            pasos_bloque = [fila for fila in todas_las_tablas if fila[55] == str(iterador_bloques)] #55 = ordenSecuencia
            resta_aux = len(pasos_bloque)-1
            #print(resta_aux)
            #cant_pasos_bloque = len(pasos_bloque)
            #print(pasos_bloque)
            # Obtener Aux_protocolo en Python
            self.cursor.execute(
                f"SELECT idprotocolo FROM {self._DATABASE}.protocolo WHERE protocolos_idProtocolos = ? AND OrdenSecuencia = ?",
                (val2, iterador_bloques)
            )
            aux_protocolo = self.cursor.fetchone()[0] #Obtento el IdProtocolo auxiliar aun no se bien si lo uso en algo.... pero lo vero, tampoco me gusta el nombre que le di
            #print(f"##Se ha obtenido el siguiente idprotocolo {aux_protocolo} de la tabla protocolo##")
            # Insertar en valuemedicion en lotes
            valuemedicion_data = [(p[39], p[40], p[41]) for p in pasos_bloque] #39 = ValorMedido, 40=EstadoMedicion y 41 = Tiempo_V
            self.cursor.executemany(
                f"INSERT INTO {self._DATABASE}.valuemedicion (ValorMedido, EstadoMedicion, TimeStamp) VALUES (?, ?, ?)",
                valuemedicion_data
            )
            self.cursor.execute("SELECT LAST_INSERT_ID()")  # Obtiene el último ID insertado
            aux_valuemedicion = int(self.cursor.fetchone()[0]) - resta_aux
            
            
            
            #print(f"el primer id de valuemedicion es {aux_valuemedicion}")
            # Insertar en mediciones en lotes
            mediciones_data = [
                (p[29], p[30], p[31], p[32], p[33], p[34], 
                p[35], p[36], p[37], aux_valuemedicion + i)
                for i, p in enumerate(pasos_bloque)
            ]
            self.cursor.executemany(
                f"""
                INSERT INTO {self._DATABASE}.mediciones (Name, Descripcion, Escala, Unidad, Rango, SerialNumber, Codigo, Version, 
                                        listainstrumentos_idListaInstrumentos, valuemedicion_idvaluemedicion) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                mediciones_data
            )
            self.cursor.execute("SELECT LAST_INSERT_ID()")  # Obtiene el último ID insertado
            aux_mediciones = int(self.cursor.fetchone()[0])-resta_aux
            
            
            #print(f"el primer id de mediciones es {aux_mediciones}")
            
            # Insertar en pasos en lotes
            pasos_data = [
                (p[1], p[2], p[3], p[4], p[5], p[6],
                p[7], p[8], p[9], p[10], p[11], p[12],
                p[13], p[14], p[15], p[16], p[17], 
                p[18], p[19], p[20], p[21], p[22], 
                p[23], p[24], p[25], p[26], p[27],
                aux_protocolo, val2, aux_mediciones + i)
                for i, p in enumerate(pasos_bloque)
            ]
            self.cursor.executemany(
                f"""
                INSERT INTO {self._DATABASE}.pasos (Name, CriterioPass, Tipo, Estado, Observacion, ResultadoTipico, ResultadoMaximo, ResultadoMinimo, 
                                TimeStamp, Ajustar, Unidad, Comandos, Saltar, FactorConversion, Imprimible, Habilitado, 
                                OrdenDeSecuencia, Tipo_Item, Titulo, Inicio_Bloque, Validacion, Tipo_Respuesta, Respuesta_Correcta, 
                                Offset, Tiempo_Medicion, Simular, Medir_o_Conectar, protocolo_idprotocolo, 
                                protocolo_protocolos_idProtocolos, mediciones_idmediciones) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                pasos_data
            )
        
        self.cursor.execute("SET FOREIGN_KEY_CHECKS=1;")

        #print("fin")

    ######## Asiciados al numero de serie ###################
    def getModulosFromCodigo(self,id_protocolo,id_protocolos):
        """
        #CABE DECIR QUE ESTA FUNCIONA PARA EL PROTOCOLO MODELO
        Se va a encargar de llamar las configuraciones asociadas al codigo\n
        :id_protocolo: ID del primer bloque(supongo) del protocolo\n
        :id_protocolos: ID del protocolo\n
        :return: *list* Lista con todos los numeros de serie que aparecen en el codigo
        """

        codigo = str(self.getModuloFromIds(id_protocolo=id_protocolo,id_protocolos=id_protocolos)[2]) #El elemento 2 es el codigo

        #Utilizo el metodo ya creado en la base de datos aunque nos podriamos independizar de esta
        """
        El procedimiento hace lo siguiente:
        BEGIN
        SELECT *
        FROM modulos
        WHERE Codigo = val1;
        END
        Lo que es muy facil de hacer en una simple consulta
        """
        self.cursor.execute("{Call GetModulosFromCodigo(?)}",str(codigo))

        values = self.cursor.fetchall()

        return values


    def getModuloFromIds(self,id_protocolo,id_protocolos):
        """
        Funcion que a partir de los id de los bloques(si raro) y el id del protocolo obtiene la configuracion....\n
        :id_protocolo: ID del primer bloque(supongo) del protocolo\n
        :id_protocolos: ID del protocolo\n
        :return: Datos referidos a partir de los id's
        """

        #Voy a usar un stored procedures aunque se puede replicar tranquilamente en codigo

        self.cursor.execute("{Call GetModuloFromIdprotocoloAndProtocolo_endisegno(?,?)}",(id_protocolo,id_protocolos))
        #Esto me devuelve: idmodulos_endisegno,Nombre,Codigo,Codigo,protocolo_protocolos_idProtocolos,modulos_endisegno_idmodulos_endisegno
        #En la posicion 3 se va a encontrar el codigo.... creo que lo correcto seria usar un fetchone
        datos_modulo = self.cursor.fetchone()

        return datos_modulo
    

    def checkIngresadoExiste(self,values):
        """
        Chequea lo que se vaya ingresar como numero de serie no se encuentre ya subido. En caso negativo lo sube\n
        :values: La fila seleccionada, puede modificarse el ns\n
        :return: True or False
        """
        #valeus = #id,categoria,nombre,codigo,ns,orden,Estado
        #print(values[4])
        self.cursor.execute(f"""SELECT * FROM {self._DATABASE}.modulos WHERE Categoria= ? AND Nombre= ? AND Orden= ? AND Codigo=? AND SerialNumber = ? AND Estado = ? """,(values[1],values[2],values[5],values[3],values[4],values[6]))

        r = self.cursor.fetchall()

        if len(r)>0:
            return True
        else:
            return False
        
    def insertNuevoModulo(self,values):
        """
        Crea un nuevo modulo con los valores seleccionados\n
        :values: La fila seleccionada, puede modificarse el ns\n
        :return: *LastID*
         """
        self.cursor.execute(f"""INSERT INTO {self._DATABASE}.modulos (Categoria, Nombre, Orden, Codigo, SerialNumber, Estado) VALUES (?,?,?,?,?,?) """,(values[1],values[2],values[5],values[3],values[4],values[6]))

        self.cursor.execute("SELECT LAST_INSERT_ID()")  # Obtiene el último ID insertado
        LASTID = int(self.cursor.fetchone()[0])
        return LASTID
    

    def asociarModuloaProtocolo(self,id_protocolo,id_protocolos,LASTID):
        """
        #Hace referencia al nuevo protocolo, ya que inserta una nueva fila
        Funcion que debe asociar el protocolo a un modulo con NS
        """
        #####SE deben actualizar todoooos los bloques, no solo el primer.....
        self.cursor.execute("{CALL GetprotocoloFromIdProtocolos (?)}",(id_protocolos))
        L = len(self.cursor.fetchall())
        self.cursor.execute("SET FOREIGN_KEY_CHECKS=0;") #Seteo las claves externas en 0
        if L >1:
            BLOQUES_ID = [int(id_protocolo) + i for i in range(L)]
            data = [(BLOQUES_ID[i], id_protocolos, LASTID) for i in range(len(BLOQUES_ID))]
            #Se tiene que crear un arreglo con todos los id, y luego usar un executemany
            self.cursor.executemany(f"INSERT INTO {self._DATABASE}.protocolo_has_modulos (protocolo_idprotocolo, protocolo_protocolos_idProtocolos, modulos_idModulos) VALUES (?,?,?)",data)
            self.cursor.execute("SELECT LAST_INSERT_ID()")
            LASTID = int(self.cursor.fetchone()[0])
        else:
            self.cursor.execute(f"INSERT INTO {self._DATABASE}.protocolo_has_modulos (protocolo_idprotocolo, protocolo_protocolos_idProtocolos, modulos_idModulos) VALUES (?,?,?)",(id_protocolo,id_protocolos,LASTID))

            self.cursor.execute("SELECT LAST_INSERT_ID()")
            LASTID = int(self.cursor.fetchone()[0])

        self.cursor.execute("SET FOREIGN_KEY_CHECKS=1;") #Seteo las claves externas en 1

        return LASTID
    
    #######ASOCIADO A CAMBIAR LA CONFIGURACION##############################

    def getConfigPuestoaPartirdeIdDelProtocolo(self,id):
        """
        Devuelve la configuracion del puesto a partir del id del protocolo, asi diferente versiones pueden mantener la configuracion\n

        :id: Id del protoclo seleccionado
        :return: Lista con configuraciones asociadas al id + nombre
        """

        nombre = self.getNameFromId(id=id) #Obtengo el nombre para no crear una nueva configuracion cada vez que se crea una nueva version de prtocolo
        self.cursor.execute(f'SELECT * FROM {self._DATABASE}.configuracion WHERE idConfiguracion IN (SELECT configuracion_idConfiguracion FROM {self._DATABASE}.protocolo where protocolos_idProtocolos in (SELECT idProtocolos FROM {self._DATABASE}.protocolos where Name = ?))',nombre)

        CONFIG = self.cursor.fetchall()
        return CONFIG
    

    def getNameFromId(self,id):
        """
        Devuelve el nombre del protoclo a partir del ID\n
        :ID: id del protocolo
        :return: Nombre del protocolo
        """

        self.cursor.execute(f"SELECT Name from {self._DATABASE}.protocolos WHERE idProtocolos = ?",id)

        NAME = self.cursor.fetchone()[0]

        return NAME
    
    def setConfigEnProtocolo(self,id_protocolo,id_config):
        """
        Setea la configuracion al protoclo que luego se va a copiar
        """
        self.cursor.execute("SET FOREIGN_KEY_CHECKS=0;") #Seteo las claves externas en 0
        self.cursor.execute(f"UPDATE {self._DATABASE}.protocolo SET configuracion_idConfiguracion = ? WHERE protocolos_idProtocolos = ?",(id_config,id_protocolo))
        self.cursor.execute("SET FOREIGN_KEY_CHECKS=1;") #Seteo las claves externas en 1
        print("Se Ha seteado la nueva configuracion")


    def getCantidadPasos(self,id):
        """
        Funcion que simula el metodo almacenado en la base de datos para consultar pasos y mediciones.\n
        :id: ID protocolo creado
        """
        query_pasos = """
            SELECT count(*) 
            FROM dbfeas_smva_2_0_v1.pasos 
            WHERE protocolo_idprotocolo IN (
                SELECT idprotocolo 
                FROM dbfeas_smva_2_0_v1.protocolo 
                WHERE protocolos_idProtocolos = ?
            )
        """
        query_mediciones = """
            SELECT count(valuemedicion_idvaluemedicion) 
            FROM dbfeas_smva_2_0_v1.mediciones 
            WHERE idmediciones IN (
                SELECT mediciones_idmediciones 
                FROM dbfeas_smva_2_0_v1.pasos 
                WHERE protocolo_idprotocolo IN (
                    SELECT idprotocolo 
                    FROM dbfeas_smva_2_0_v1.protocolo 
                    WHERE protocolos_idProtocolos = ?
                )
            )
        """

        self.cursor.execute(query_pasos, (id,))
        pasos_count = self.cursor.fetchone()[0]
        self.cursor.execute(query_mediciones, (id,))
        mediciones_count = self.cursor.fetchone()[0]
        return pasos_count, mediciones_count
if __name__ == "__main__":
    bd = SMVA_DB()
    bd.asociarModuloaProtocolo(415424,29901,16963)