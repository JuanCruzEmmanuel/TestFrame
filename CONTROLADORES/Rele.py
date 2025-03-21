"""
Esta a diferencia de ReleDriver controlara el flujo de informacion de cada rele
"""

import json

class Rele:

    def __init__(self):
        self.__PLACAS = ""


        self.load()

    def load(self):
        """Se encarga de cargar la informacion de las placas en Hexadecimal"""

        with open("_TEMPS_/Placas.JSON", "r") as jsonFile:
            self.__PLACAS = json.load(jsonFile)

    def getPlacasInfo(self):
        """
        Devuelve la informacion de las palcas en haxadecimal
        """
        return self.__PLACAS

    def getPlacaInfo(self,placa):

        """
        Devuelve la informacion en hexadecimal de la placa en cuestion
        """
        return self.__PLACAS[placa]
    
    def getPlacaInfoBinary(self,placa):
        """
        Convierte la lista hex en una lista binaria

        :param placa: P0 a P15
        """

        hex_list = self.__PLACAS[placa]

        binary_list = []
        for value in hex_list:
            if isinstance(value, str) and value.lower().startswith('0x'):  # Es un valor hexadecimal
                binary_list.append(list(map(int, f"{int(value, 16):08b}")))
            else:  # Es un valor entero
                binary_list.append(list(map(int, f"{value:08b}")))
        return binary_list

    def setPlacaConfig(self,placa,config):
        """
        Funcion que setea en el JSON los valores para no perder la configuraciones
        :param placa: Placa donde se va a setear la configuracion
        :param config: Configuracion de esa placa particular
        """

        self.__PLACAS[placa] = config

        try:
            with open("_TEMPS_/Placas.JSON","w") as jsonFile:
                json.dump(self.__PLACAS,jsonFile,indent=3)
        except:
            print("Error al cargar")


if __name__ =="__main__":
    r = Rele()
    print(r.getPlacaInfoBinary("P0"))