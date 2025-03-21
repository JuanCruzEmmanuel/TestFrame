import pyodbc
import json
import time

class SMVA_DB():
    _DATABASE = "dbfeas_smva_2_0_v1"
    def __init__(self):
        
        self.cursor = self.connect()
        self.user = None
        self.vigente = "Vigente"
        self.protocoloLista = None
        self.filterName = ""

    def connect(self,test=True):
        """
        FUNCION QUE SE ENCARGA DE CONECTAR A LA BD y se puede trabajar directamente con CURSORES
        :RETURN cursor: Cursor de manejo BD
        """
        if test:
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
                SELECT idprotocolo, Name, ordenSecuencia 
                FROM {self._DATABASE}.protocolo
                WHERE protocolos_idProtocolos = {id};
                """
        
        self.cursor.execute(query)
        protocolos = self.cursor.fetchall()

        # Estructura para el JSON
        resultado_json = []

        # Procesar cada protocolo
        for protocolo in protocolos:
            protocolo_id, protocolo_name, ordenSecuencia = protocolo

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
                    "CriterioPass":""
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

    def ID_PROTOCOLO_COPIA(self,id="1"):

        self.cursor.execute("{CALL selectProtocolosFromId (?)}",(id))

        MODELO = self.cursor.fetchall()[0] #Protocolo modelo

        NOMBREPROTOCOLO = MODELO[1]
        VERSIONPROTOCOLO= MODELO[2]
        VIGENCIAPROTOCOLO = MODELO[3]
        TIPOPROTOCOLO = MODELO[4]
        COMENTARIOPROTOCOLO = MODELO[5]
        RESULTADOPROTOCOLO = "NUEVO"

        self.cursor.execute("{CALL insertProtocolosAndLastId_2_0 (?,?,?,?,?,?)}",(NOMBREPROTOCOLO,VERSIONPROTOCOLO,VIGENCIAPROTOCOLO,TIPOPROTOCOLO,COMENTARIOPROTOCOLO,RESULTADOPROTOCOLO))

        LASTID = self.cursor.fetchall()[0] #Hasta este punto ya tengo el nuevo protocolo. Ahora se debe crear los bloques y los pasos
        self.cursor.execute("{CALL GetprotocoloFromIdProtocolos (?)}",(id))

        BLOQUEMODELOS = self.cursor.fetchall() #Obtengo los bloques del protocolo modelo

        for BLOQUE in BLOQUEMODELOS:

            NOMBREBLOQUE = BLOQUE[1]
            EQUIPOBLOQUE = BLOQUE[2]
            REVISIONBLOQUE = BLOQUE[3]
            ESTADOBLOQUE = BLOQUE[4]
            IDBLOQUE = BLOQUE[0] #CON ESTO VAMOS A OBTENER LA INFO DE LOS INSTRUMENTOS "creo"
            #print(IDBLOQUE)
            IDCONFIG = BLOQUE[12]
            SECUENCIABLOQUE = BLOQUE[13]
            self.cursor.execute("{CALL insertprotocoloAndLastId (?,?,?,?,?,?,?,?,?,?,?,?,?)}",(NOMBREBLOQUE,EQUIPOBLOQUE,REVISIONBLOQUE,ESTADOBLOQUE,"","","","","NUEVO",int(str(LASTID[0])),0,0,SECUENCIABLOQUE))
            IDCAMBIO = self.cursor.fetchall()[0] #Obtengo el idea nuevo
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

        self.cursor.execute("{CALL CopiarProtocoloModelo (?,?)}",(id,str(LASTID[0]))) #Recibe el ID del protocolo nuevo, y el id del protocolo modelo
        #self.cursor.fetchall()
        
        self.cursor.execute("{CALL GetCantPasosyValueMedicion (?)}",(str(LASTID[0])))
        datos = self.cursor.fetchall()[0]
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
        for paso in pasos:
            id_paso = paso["id_paso"] #El id del paso
            estado_paso = paso["Estado"] #Estado de paso
            resultado_paso = paso["Resultado"] #Resultado de paso
            criterio_paso = paso["CriterioPass"]
            id_mediciones = paso["mediciones_idmediciones"]
            self.cursor.execute(f"""UPDATE {self._DATABASE}.pasos SET Estado = ?, CriterioPass = ? WHERE idpasos = ?""",(estado_paso,criterio_paso,id_paso)) #Actualizo el paso
            #Actualizar el valor medido
            #Para ello primero debo pedir el id que relaciona mediciones con su valor (totalmente ineficiente)
            self.cursor.execute(f"""SELECT valuemedicion_idvaluemedicion FROM {self._DATABASE}.mediciones WHERE idmediciones={id_mediciones}""")
            id_value_mediciones = self.cursor.fetchall()[0][0] #ID value mediciones
            self.cursor.execute(f"""UPDATE {self._DATABASE}.valuemedicion SET ValorMedido = ?, EstadoMedicion = ? WHERE idvaluemedicion = ?""",(resultado_paso,estado_paso,id_value_mediciones)) #Actualizo el paso
        #Una vez termine esto, se debe actualizar 
        if resultado_bloque=="ABORT":
            _PASADA_ = "INCOMPLETO"
        elif resultado_bloque!="ABORT":
            _PASADA_ = "COMPLETO"
        else:
            _PASADA_ = "INCOMPLETO"
        #Tambien se debe guardar info del operador, se debe agregar esa info
        self.cursor.execute(f"""UPDATE {self._DATABASE}.protocolo SET Resultado = ?, Pasadas = ? WHERE idprotocolo = ?""",(resultado_bloque,_PASADA_,id_protocolo))
        print("Se subio")
if __name__ == "__main__":
    bd = SMVA_DB()
    with open("_TEMPS_/protocolo_a_ejecutar.json", "r", encoding="utf-8", errors="ignore") as file:
        protocolo = json.load(file)
    #Esto me simula la ejecucion externa
    for p in protocolo:
        bd.subir_paso_protocolo_y_protocolo(id_protocolo = p["ProtocoloID"],resultado_bloque=p["Resultado"],pasos = p["Pasos"])