from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime

class DashboardWorker(QThread):
    finished = pyqtSignal(list, list, dict, dict)  # tiempo, operadores, resultados

    def __init__(self, cursor, base_de_datos, placa, version,nombre_equipo,tipo):
        super().__init__()
        self.cursor = cursor
        self.db = base_de_datos
        self.placa = placa
        self.version = version
        self.nombre_equipo = nombre_equipo
        self.tipo = tipo
    def run(self):
        # Acá hacés lo que estaba en actualizar_dashboard
        tiempo = []
        operadores = []
        resultado = {"PASA": 0, "NO PASA": 0, "INCOMPLETO": 0}
        if self.tipo != "PSA":
            distinct_protocolo =f"""SELECT idProtocolos FROM {self.db}.protocolos where name like '%{self.placa}%' and Version like '%{self.version}%' and Resultado != 'MODELO' """
            self.cursor.execute(distinct_protocolo)
            protocolo = self.cursor.fetchall()
            ID_PROTOCOLO = [p[0] for p in protocolo]
        else:
            dic_ = {
                "DESFIBRILADOR 3850":"DEFI3850",
                "MONITOR PM9000":"PM9000",
                "MULTIPAR":"MULTIPAR"
            }
            distinct_protocolo = f"""SELECT idProtocolos FROM {self.db}.protocolos where name like '%{dic_[self.nombre_equipo]}%' and Tipo ='PSA' and Version like '%{self.version}%' and Resultado != 'MODELO'"""
            self.cursor.execute(distinct_protocolo)
            protocolo = self.cursor.fetchall()
            ID_PROTOCOLO = [p[0] for p in protocolo]
        for id in ID_PROTOCOLO: #Es mas facil separar los protocolos asi
            query_ejecucion_protocolos = f"""SELECT * FROM {self.db}.protocolo where protocolos_idProtocolos={id}"""
            self.cursor.execute(query_ejecucion_protocolos)
            BLOQUES = protocolo = self.cursor.fetchall() #(id,Name,Equipo,Revision,Estado,Resultado,Aprobador,Start,End,Pasadas,)
            #Aca inicio el analisis del operador
            operador = []
            tiempo_incio = []
            tiempo_final = []
            estado = []
            t_i = 0
            for bloque in BLOQUES:
                operador.append(bloque[6])
                try:
                    delta = datetime.strptime(bloque[8], "%Y-%m-%d %H:%M:%S") - datetime.strptime(bloque[7], "%Y-%m-%d %H:%M:%S")
                    duracion_en_minutos = delta.total_seconds() / 60
                except:
                    duracion_en_minutos = 0
                #tiempo_incio.append(bloque[7]) #formato 2020-05-07 12:22:55
                #tiempo_final.append(bloque[8])  #formato 2020-05-07 12:22:55
                estado.append(bloque[5])
                t_i+=duracion_en_minutos
            operador_=set(operador)
            for operador_distinto in operador_:
                operadores.append(operador_distinto)
            try:

                #delta = datetime.strptime(tiempo_final[-1], "%Y-%m-%d %H:%M:%S") - datetime.strptime(tiempo_incio[0], "%Y-%m-%d %H:%M:%S")
                #duracion_en_minutos = delta.total_seconds() / 3600
                tiempo.append(t_i)

            except:
                tiempo.append(0)
            if any("NO PASS" in e for e in estado):
                resultado["NO PASA"] += 1
            elif any("ABORT" in e for e in estado):
                resultado["INCOMPLETO"] += 1
            elif any("INCOMPLETO" in e for e in estado):
                resultado["INCOMPLETO"] += 1
            else:
                resultado["PASA"] += 1
        # Lógica que ya tenés...
        # al final:
        #print(tiempo)

        #VOY A CALCULAR LOS EJECUTADOS HOY

        hoy = datetime.today()
        hoy_formateado = hoy.strftime("%Y-%m-%d")  # Esto es un string
        query_today = f"""SELECT distinct protocolos_idProtocolos FROM {self.db}.protocolo where StartTime like '%{hoy_formateado}%'"""
        self.cursor.execute(query_today)
        id_hoy = self.cursor.fetchall()
        id_hoy = [id[0] for id in id_hoy]
        lista_ejecutados_hoy = {
            "PASA":0,
            "NO PASA":0,
            "INCOMPLETO":0
        }
        for id in id_hoy:
            query_today = f"""SELECT Resultado FROM {self.db}.protocolo where protocolos_idProtocolos = {id}"""
            self.cursor.execute(query_today)
            estado = self.cursor.fetchall()
            estado = [e[0] for e in estado]
            if any("NO PASS" in e for e in estado):
                lista_ejecutados_hoy["NO PASA"] += 1
            elif any("ABORT" in e for e in estado):
                lista_ejecutados_hoy["INCOMPLETO"] += 1
            elif any("INCOMPLETO" in e for e in estado):
                lista_ejecutados_hoy["INCOMPLETO"] += 1
            elif any(e == "" for e in estado): #En caso que haya elementos vacio
                lista_ejecutados_hoy["INCOMPLETO"] += 1
            else:
                lista_ejecutados_hoy["PASA"] += 1
        self.finished.emit(tiempo, operadores, resultado,lista_ejecutados_hoy)