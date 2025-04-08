"""
Este driver es el encargado de reaccionar a los distintos comandos del SMVA diseñado
en python. Luego se debera adaptar todas las librerias realizadas para labview para este nuevo driver

"""
import json
from CONTROLADORES.ReleDriver import TorreRele
from CONTROLADORES.driver import DRIVER

class driverInstrumentos:
    def __init__(self,BASE_DATO = None):
        self.resultado = ""
        self.comando = ""
        self.torreRele = TorreRele() #Creo el objeto
        #self.SALTO_CONFICIONAL = SALTO_CONDICIONAL
        self.BASE_DATO = BASE_DATO
    def readComando(self,CMD,SALTO_CONDICIONAL = False,):
        """
        El SMVA en LabVIEW leia las primeras 3 letras y de ahi determinaba el instru\n
        :return: instrumeno, indice de bloque, indice de filas
        """
        instrumentos = {
            "TOR":self.torreRele.readComando
        }

        """
        Cuando el SMVA veia un ";" significaba que tenia que ejecutarlo primero
        """
        i="NO_SALTO"
        j = "NO_SALTO"
        if ";" in CMD: #hay ciertos comandos donde el ; se encuentra primero despues segundo, o pueden existir multiples EJEMPLO ;SALTARSI_FALSO:"ETIQUETA3"
            CMD_SPLITED = CMD.split(";")
            if len(CMD_SPLITED)==2: #Significa que hubo un solo comando
                #Como el comando que me interesa va a aparecer a la derecha del ";" tengo que evaluar si el valor a la izquierda es NO NULL
                if CMD_SPLITED[0]!="":
                    CMD = CMD_SPLITED[0]
                COMANDO = CMD_SPLITED[1]
                if "SALTARSI_FALSO" in COMANDO:
                    ETIQ = COMANDO.split('"')[1]
                    if SALTO_CONDICIONAL == False:
                        i = self.BASE_DATO[ETIQ]["i"]
                        j = self.BASE_DATO[ETIQ]["j"]
                    else:
                        i = "NO_SALTO"
                        j = "NO_SALTO"
                elif "SALTARSI_VERDADERO" in COMANDO:
                    ETIQ = COMANDO.split('"')[1]
                    if SALTO_CONDICIONAL == True:
                        i = self.BASE_DATO[ETIQ]["i"]
                        j = self.BASE_DATO[ETIQ]["j"]
                    else:
                        i = "NO_SALTO"
                        j = "NO_SALTO"
        if CMD !="": #En el caso que el comando siga, se debera analizar
            if i == "NO_SALTO": #Lo que me devuelva esto, debe ser coherente, por eso debe devolver la misma longitud
                if CMD[0]=="*":
                    return DRIVER(cmd = CMD[1:]),"NO_SALTO","NO_SALTO"
                else:
                    try:
                        print(CMD[4:])
                        INST = instrumentos[CMD[0:3]](CMD = CMD[4:])
                        return INST,"NO_SALTO","NO_SALTO"
                    except:
                        return "OK","NO_SALTO","NO_SALTO"
            else:
                if CMD[0]=="*":
                    return DRIVER(cmd = CMD[1:]),i,j
                else:
                    try:
                        print(CMD[4:])
                        INST = instrumentos[CMD[0:3]](CMD = CMD[4:])
                        return INST,i,j
                    except:
                        return "OK",i,j
        else: #En caso que no haya comando de CMD
            return "OK",i,j