######## SE va a encargar de controlar al PROSIM 8 INSTRUMENTO TRONCAL, seguiremos con la misma logica creada hasta el momento
import serial
import numpy
from INSTRUCONTRACT import instru_contract

class PROSIM8(instru_contract):
    def __init__(self,port,baudare=9600):
        self.port = port
        self.baudrate = baudare
    
    def connect(self):
        pass

    def disconnect(self):
        pass

    def readcommand(self):
        pass
    
    def writecommand(self):
        pass