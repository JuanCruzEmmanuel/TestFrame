"""
La idea de este driver es tener un selector de multimetros para todo aquellos que se puedan comunicar

Una vez esto, los comandos deben ser "los mismos" para todo los multimetros

"""

__autor__ = "Juan Cruz Noya"
__version__ = "1.0.3"
__propiedad__ = "Feas Electronica"


"""
VERSIONES REFERENCIAS

1.0.0 : Se inicia el driver para controlar osciloscopios tektronix

1.0.1 : Se agregan comandos para seteo de mediciones y obtencion de estas. Se testea lo realizado

1.0.2 : Se ha agregado la re para conexiones mas veloces

1.0.3 : Se han modificado ciertos parametros para que funcione con los TBS 2000
"""

#IMPORTS
import re
import pyvisa
import numpy as np
from time import sleep
"""
USB0::0x0699::0x03B0::C011519::INSTR
"""
class TEKTRONIX:
    def __init__(self):
        self.serial = None
        self.pattern = r"USB0::(.*?)::INSTR"  # Define el patrón
        self.min = 1
        self.max = 2500
        self.ch = 1
        self.MeasType = "PK2pk"
        self.posicionMedicion = 1
        self.conect()
        print("me conecte")
    def conect(self):
        rm = pyvisa.ResourceManager() #rm de resourceManager
        devices = rm.list_resources()
        #print(devices)
        matching_devices = [dev for dev in devices if re.match(self.pattern, dev)]
        #print(matching_devices)
        if not matching_devices:
            print("No se encontraron dispositivos TEKTRONIX.")
            return
        for add in matching_devices:
            try:
                device = rm.open_resource(add)
                infoDevice = device.query('*IDN?')
                # TBS 1062 = TEKTRONIX,TBS 1062,C011519,CF:91.1CT FV:v26.01
                if "TEKTRONIX" in infoDevice: #Hay que ver todo los string posibles para los osciloscopio
                    self.serial = device
                else:
                    pass
                
            except:
                pass


    def setVerticalScale(self,value):
        """
        Setea la escala del osciloscipio en el eje vertical

        :param:
            :value: valor del la escala
            :ch: Canal de trabajo
        :return:
            :None:
        """
        if "CH" in str(self.ch):
            CH = self.ch
        else:
            CH = "CH"+str(self.ch) #CONVIERTE EL VALOR QUE SE SETEO DE CANAL AL FORMATO OSCILOSCOPIO
        self.serial.write(f"{CH}:VOL {value}")
    
    def setVerticalPosition(self,value):
        """
        Setea la posicion del cursor del osciloscipio en el eje vertical

        :param:
            :value: valor del la escala
            :ch: Canal de trabajo
        :return:
            :None:
        """
        if "CH" in str(self.ch):
            CH = self.ch
        else:
            CH = "CH"+str(self.ch) #CONVIERTE EL VALOR QUE SE SETEO DE CANAL AL FORMATO OSCILOSCOPIO
        self.serial.write(f"{CH}:POS {value}")
    
    def setHorizontalScale(self,value):
        """
        Setea la escala del eje temporal
        """

        self.serial.write(f"HOR:MAI:SCA {value}")

    def setHorizontalPosition(self,value):
        """
        Setea la posicion horizontal del cursor
        """
        self.serial.write(f"HOR:MAI:POS {value}")

    def setChannel(self,value):

        self.ch = value

    def getCurve(self):
        
        """
        Devuelve la curva que se encuentra en pantalla en el canal correspondiente.
        """
        self.serial.write(f"DATa:SOUrce CH{self.ch}")
        self.serial.write(f"data:width 1;start {self.min};stop {self.max}")

        return self.serial.query("CURVE?")


    def setTriggerLevel(self,value):
        """
        Setea el nivel de trigger a un valor determinado por el usuario
        
        """
        self.serial.write(f"TRIGger:MAIn:LEVel {value}")


    def Info(self):

        return self.serial.query('*IDN?')
    

    def setON(self,value):
        value = str(value) #convierto en string solo para facilitar el debug
        if value == "1" or value == "2" or value =="3" or value == "4": #En caso que solo se especifique el canal por su valor numerico
            self.setChannel(value = value)
            self.serial.write(f"SELect:CH{self.ch} ON")
        else: #En caso que se escriba CH1, CH2, MATH o REFy
            self.serial.write(f"SELect:{value.upper()} ON")

    def setOFF(self,value):
        value = str(value) #convierto en string solo para facilitar el debug
        if value == "1" or value == "2" or value =="3" or value == "4": #En caso que solo se especifique el canal por su valor numerico
            self.setChannel(value = value)
            self.serial.write(f"SELect:CH{self.ch} OFF")
        else: #En caso que se escriba CH1, CH2, MATH o REFy
            self.serial.write(f"SELect:{value.upper()} OFF")
    def setMeasPos(self,value):
        """
        Setea el tipo de medicion en la posicion solicitada
        """
        try:
            self.serial.write(f"MEASU:MEAS{value}:SOU CH{self.ch}")
            self.serial.write(f"MEASUrement:MEAS{self.posicionMedicion}:STATE ON")     
            self.serial.write(f"MEASU:MEAS{value}:TYPE {self.MeasType}")
        except:
            self.serial.write(f"MEASU:MEAS{value}:SOU CH{self.ch}")
            self.serial.write(f"MEASU:MEAS{value}:TYPE {self.MeasType}")
    def setMeasType(self,value):
        """
        setea localmente la medicion deseada
        """
        DICTYPE = {
            "picoApico":"PK2pk",
            "PK2pk":"PK2pk",
            "VPP":"PK2pk",
            "P2P":"PK2pk",
            "PK2PK":"PK2pk",
            "pk2pk":"PK2pk",
            "max":"MAXI",
            "maximo":"MAXI",
            "MAX":"MAXI",
            "MAXIMO":"MAXI",
            "MIN":"MINI",
            "min":"MINI",
            "MINIMO":"MINI",
            "minimo":"MINI",
            "FREC":"FREQ",
            "frec":"FREQ",
            "frecuencia":"FREQ",
            "FRECUENCIA":"FREQ",
            "freq":"FREQ",
            "FREQ":"FREQ",
            "periodo":"PERI",
            "PERIODO":"PERI",
            "PER":"PERI",
            "per":"PERI",
            "PulsoPositivo":"PWIdth",
            "PULP":"PWIdth",
            "pulsopositivo":"PWIdth",
            "PULSOPOSITIVO":"PWIdth",
            "PulsoNegativo":"NWIdth",
            "PULN":"NWIdth",
            "pulsonegativo":"NWIdth",
            "PULSONEGATIVO":"NWIdth",
            "valorMedio":"MEAN",
            "MEDIO":"MEAN",
            "VALORMEDIO":"MEAN",
            "valormedio":"MEAN",
            "MEAN":"MEAN",
            "PROMEDIO":"MEAN",
            "vmed":"MEAN",
            "VMED":"MEAN"

        }

        self.MeasType = DICTYPE[value]

        self.setMeasPos(value = self.posicionMedicion)

    def getVoltPicoPico(self):
        pass

    def setMedicionPosicion(self,value):

        self.posicionMedicion = value

    def getFrecuency(self):
        pass

    def getPeriode(self):
        pass
    
    def getMEAS(self,val=1):
        m = self.serial.query("MEASUrement:MEAS5?").split(";") #Esto lo hago para que independiente de donde este pueda tomar la medicion
        self.serial.write(f"MEASU:MEAS5:TYPE {m[0]}")
        sleep(1)
        return self.serial.query(f"MEASU:MEAS{self.posicionMedicion}:VAL?")


if __name__=="__main__":
    osc = TEKTRONIX()
    #osc.setOFF(value = 2)  # Apago la señal 2
    #osc.setOFF(value = 3)  # Apago la señal 3
    #osc.setOFF(value = 4)  # Apago la señal 4
    osc.setON(value = 1)    #Enciendo la señal 1
    osc.setVerticalScale(value = 2.5)
    osc.setChannel(value = 1)
    osc.setMedicionPosicion(value = 1)
    osc.setMeasType(value="VPP")
    print(osc.getMEAS())
    osc.setON(value = 2)    #Enciendo la señal 2
    #osc.setVerticalPosition(-1)
    #osc.setHorizontalScale(value=2.5E-3)

    osc.setChannel(value = 2)
    osc.setMedicionPosicion(value = 2)
    osc.setMeasType(value="VPP")
    print(osc.getMEAS())


