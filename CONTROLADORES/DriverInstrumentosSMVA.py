"""
Este driver es el encargado de reaccionar a los distintos comandos del SMVA diseñado
en python. Luego se debera adaptar todas las librerias realizadas para labview para este nuevo driver

"""
import json
from CONTROLADORES.ReleDriver import TorreRele
from CONTROLADORES.driver import DRIVER

class driverInstrumentos:
    def __init__(self):
        self.resultado = ""
        self.comando = ""
        self.torreRele = TorreRele() #Creo el objeto
    def readComando(self,CMD):
        """
        El SMVA en LabVIEW leia las primeras 3 letras y de ahi determinaba el instru
        """
        instrumentos = {
            "TOR":self.torreRele.readComando
        }


        if CMD[0]=="*":
            return DRIVER(cmd = CMD[1:])
        else:
            try:
                print(CMD[4:])
                INST = instrumentos[CMD[0:3]](CMD = CMD[4:])
                return INST
            except:
                return "OK"