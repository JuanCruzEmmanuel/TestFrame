######## SE va a encargar de controlar al PROSIM 8 INSTRUMENTO TRONCAL, seguiremos con la misma logica creada hasta el momento
import serial
import numpy
from INSTRUCONTRACT import instru_contract

class PROSIM8(instru_contract):
    def __init__(self,port,baudare=115200):
        self.port = port
        self.baudrate = baudare
        self.con = None
    def connect(self):
        """
        CONECTA PROSIM8 CON PUERTO SERIE\n
        DATOS:\n
        serial.STOPBITS_ONE = 1\n
        serial.PARITY_NONE = 'None'\n
        """
        self.con = serial.Serial(port=self.port,baudrate=self.baudrate,stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE,bytesize=8,xonxoff=True)

    def disconnect(self):
        """
        DESCONECTA PROSIM8 CON PUERTO SERIE\n
        """
        self.con.close()

    def readcommand(self):
        pass
    
    def writecommand(self):
        pass