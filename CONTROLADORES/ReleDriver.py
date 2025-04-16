"""
Este driver intentara emular el control de la torre de rele como lo hace el driver diseñado en LabVIEW.

Condiciones minimas de funcionamiento:

1) Descifrar la estructura de comandos y convertirla en hexadecimal.
2) Descifrar las distintas conexiones que hacen que las placas se relacionen entre si
3) Mantener los reles cerrados/abiertos hasta que exista una instruccion de apertura o cierre
4) Envio de datos
---------------MEJORAS MEDIANTE ESTE DRIVER-----------------------------------
5) Control de fallos

"""

__autor__ = "Juan Cruz Noya"
__version__ = "1.0.3"
__propiertario__ = "Feas Electronica"

"""
version 1.0.0 : inicio, funcionamiento junto a los objetos rele
version 1.0.1 : Se agrega separacion de comandos cp, y mux
version 1.0.2 : Se agrega comando AT
version 1.0.3 : se agrega comandos up

"""
#IMPORTs
from CONTROLADORES.Rele import Rele #Cree esta libreria para poder trabajar con la informacion de los rele de manera comoda. Este es el que lee la info de los rele y me la devuelve en distinto formatos.
import serial
import json
#from Rele import Rele
class TorreRele:
    """
    Es importante entender el comportamiento de la torre antes de empezar a definir cosas.
    -Por un lado el control de la torre tiene que saber discrepar en todo momento si se trabaja con 8 o 16 placas
    -Cada una de estas placas tiene una estructura dividida en bancos. Esto si bien parece complicado la podemos entender de la siguiente forma:
    PLACA 1:
    0 1  2  3  4  5  6  7 X X X X X             ||BANCO 1
    8 9 10 11 12 13 14 15 X X X X X             ||BANCO 2
    16 17 18 ....... Y asi hasta llegar al 63. LAS X X X X X son valores reservados propio de la configuracion de la torre (matricial, mux, ETC)

    La dificulad de descifrar el comando yase en poder comprender esta estructura y luego convertirla en binario para finalmente en hexadecimal

    Por ejemplo si el primer banco todos sus reles se cierran (1,1,1,1,1,1,1,1) el resultado de ese banco en particular seria 0xff y eso es lo que debe trabajarse. Asi por cada banco por cada placa

    entonces la cadena final debera ser comprendida (BANCO 1, BANCO 2, ...., BANCO 8, CONFIG, CONFIG, CONFIG, CONFIG, CONFIG) esto por cada placa.

    Entonces este codigo DEBE poder saber si el comando es de configuracion o de cierre o apertura de los reles, a su vez, esta informacion es muy importante que la guarde todo el tiempo.
    """
    #Bajo mi interpretacion la torre de rele debe ser lo principal al crearse un objeto. Luego esta debe ir pasando como "señal" a los siguientes. Para eso debemos establecer todos los metodos para su control optimo
    def __init__(self):
        self.RELES = Rele() #Creo una instancia de rele
        self.port = "COM13"
        self.serial = None
        self.__CONFLAG = False
        self.__NPLACAS = 8
    def conect(self):
        """
        Establecer conexion con el puerto. Esto para poder crear el objeto muy temprano en la ejecucion. Pero Sin la necesidad de usarse.
        """
        self.serial = serial.Serial(port = self.port, baudrate=9600,timeout=1)
        self.__CONFLAG = True #creo una bandera de precaucion
        return "OK"
    def setPort(self,port):
        """
        Metodo que setea el puerto en caso de querer cambiarlo.
        
        """
        if "com" not in port.lower() and type(port) is int:
            self.port = f"COM{port}"
        elif "com" in port.lower():
            self.port = port.upper()
        else: #En caso que todo este mal, sigue en COM13
            self.port = "COM13"
    
    def write(self,debug=True):

        if not self.__CONFLAG and debug==False:
            self.conect()
            #Comando de precaucion
        if self.__NPLACAS ==8:
            SENDCOMAND = "69" #105
        else:
            SENDCOMAND="D1"
        #hay que ver como es 208 que equivale a 16 placas
        for values in self.RELES.getPlacasInfo().values():
            for val in values:
                if "0x" in str(val).lower():
                    _control_ = str(val).lower().split("x")[1].upper()
                    if len(_control_)==1: #Esto en el caso de tener 0xd (que seria equivalente a 0x0d)
                        SENDCOMAND  += f"0{_control_}" #Con esto me protejo de no cometer estos errores de sintaxis
                    else:
                        SENDCOMAND+=str(val).lower().split("x")[1].upper() #En caso que no sea 1, solo puede ser 2.
                else: #Uno podria pensar que 0 siempre puede estar presente, o que esta inclusive en el 0x; pero en este caso ingresaria primero al if mientras que al else lo ignoraria
                    if "0" in str(val):
                        SENDCOMAND+="00"
                    else:
                        SENDCOMAND+=str(val)
        if self.__NPLACAS==8:
            SENDCOMAND=SENDCOMAND[0:210] #En caso de 8 placas
        else:
            SENDCOMAND=SENDCOMAND[0:418] #En caso de 8 placas
        #print(SENDCOMAND)
        SENDCOMAND = bytes.fromhex(SENDCOMAND)
        try:
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
            self.serial.flush()
            self.serial.write(SENDCOMAND)
            #self.serial.close()

            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
            self.serial.flush()

            self.serial.write(bytes.fromhex("02C9"))
 
            #print(self.serial.read(105))
            
            self.serial.close()

        except:
            print("error")
    def readComando(self,CMD):
        print("ingreso")

        """
        Esta debe leer el comando e interpretar que se debe realizar

        """
        
        CONFIGBYTES = { #Los espacios entre la posicion 8 a la 12 estan reservado para el modo de configuracion de la torre
            "1B64X1":["0x54","0X4C","0x4C","0x4C","0x4C"],
            "JP1_1B32X1+JP2_1B32X1": ["0x50","0X4C","0x4C","0x4C","0x4C"],
            "JP1_2B16X1+JP2_2B16X1":[0,"0X4C","0x4C","0x4C","0x4C"],
            "JP1_4B8X1+JP2_4B8X1":[0,"0X44","0x44","0x44","0x44"],
            "JP1_8B4X1+JP2_8B4X1":[0,"0X11","0x11","0x11","0x11"],
            "JP1_1B32X1+JP2_2B16X1":["0x10","0X4C","0x4C","0x4C","0x4C"],
            "JP1_1B32X1+JP2_4B8X1":["0x10","0X4C","0x4C","0x44","0x44"],
            "JP1_1B32X1+JP2_8B4X1":["0x10","0X4C","0x4C","0x11","0x11"],
            "JP1_2B16X1+JP2_1B32X1":["0x40","0X4C","0x4C","0x4C","0x4C"],
            "JP1_4B8X1+JP2_1B32X1":["0x40","0X44","0x44","0x4C","0x4C"],
            "JP1_8B4X1+JP2_1B32X1":["0x40","0X11","0x11","0x4C","0x4C"]
            }

        if "mux" in CMD.lower():
            print("MUX")
            _config = CONFIGBYTES[CMD.lower().split("_mux_")[1].upper()] #es importante seperar y trabajar coherentemente los datos. En este caso filtro en minuscula y el resultado lo hago mayus
            
            _placa = self.RELES.getPlacaInfo(CMD.lower().split("_mux_")[0].upper()) #En este caso vamos a filtarar la placa con su configuracion

            for byte_pos in range(8,13): #La posicion 13 no la toma
                _placa[byte_pos] = _config[byte_pos-8] #Agrego el -8 ya que la configuracion tiene indexacion desde 0 a 4, mientras que en _placa la config se encuentra en la 8 a la 12

        

            
            self.RELES.setPlacaConfig(placa=CMD.lower().split("_mux_")[0].upper(),config=_placa)
            self.conect()
            self.write()
            return "OK"
        elif "cp" in CMD.lower(): #ejemplo CP8_P0-C04+P1-C16+P2+P3+P4+P5+P6+P7
            #print("CONFIG")
            if CMD[2]=="8":
                self.__NPLACAS = 8
            elif CMD[3]=="6":
                self.__NPLACAS = 16
            else:
                raise TypeError("ERROR DE NUMERO DE PLACAS")
            _CMD = CMD.split("_") #ME DIVIDE EN [CP8,P0-C04+P1-C16+P2+P3+P4+P5+P6+P7]
            _PLACAS = _CMD[1].split("+") #ESTO ME DIVIDE EN [P0-C04,P1-C16,P2,P3,P4,P5,P6,P7]
            for __PLACA in _PLACAS:  #hay que reecorrer cada una de las placas
                if "-" in __PLACA: #Vemos que el - indica que se ha realizado algun comando de cierre o apertura
                    __PLACA = __PLACA.split("-")
                    _placa = self.RELES.getPlacaInfoBinary(str(__PLACA[0])) #El primer elemento dela lista es la placa que se va a trabajar, con esta funcion ya me devuelve la informacion en binario
                    _CONFIG = __PLACA[1].split(",") #Me quedo con la lista en este caso [C04] para la P0
                    for _CONF_RELE in _CONFIG:
                        if _CONF_RELE[0].lower() =="c":# Lo que indicaria que el rele se debe cerrar, entonces el valor a setear debe ser 1
                            value_set = 1
                        elif _CONF_RELE[1].lower()=="a":#lo que indicaria que el rele se debe abrir, entonces el valor se debe setear en 0
                            value_set = 0
                        else: #En caso de que exista algun error, se debe agregar un log para tenerlo en consideracion.
                            value_set = 0
                        
                        RELE_POS = _CONF_RELE[1:] #Tomo los elementos luego de la letra ej: SI es C01, solo me quedo con 01
                        if RELE_POS[0]=="0":
                            RELE_POS_NUM = int(RELE_POS[1]) #EN CASO QUE SEA 01, me quedo solo con el 1
                        else:
                            RELE_POS_NUM = int(RELE_POS) #En caso que sea 10, me quedo el numero completo
                            
                        N = RELE_POS_NUM//8 #Esto me va a dar un valor numerico entero
                        _placa[N][RELE_POS_NUM-N*8] = value_set #Me selecciona la lista N y coloca en la posicion RELE_POS_NUM - N*8 el valor 0 o 1. A esto debemos convertirlo en hexadecimal
                        
                    ###Para convetir a hexadecimal lo que debemos hacer es lo siguiente:
                    _placa_hex = [hex(int("".join(map(str, sublist)), 2)) for sublist in _placa]
                    #print(__PLACA[0])
                    #print(_placa_hex)
                    self.RELES.setPlacaConfig(placa=__PLACA[0], config=_placa_hex) #Se debe cargar la configuracion al diccionario
                
                else:
                    pass

            self.conect()
            self.write()
            return "OK"
        elif "ATRPXGXRX" in CMD:
            for i in range(16):#No toma el 16
                _placa = self.RELES.getPlacaInfo(placa =f"P{i}") #Con estro traigo la informacion de la placa

                for j in range(8):
                    _placa[j] = "0x0" #Completo los primero 8 espacios con 0

                self.RELES.setPlacaConfig(placa = f"P{i}", config = _placa)
            self.conect()
            self.write()
            return "OK"
        
        elif "UP" in CMD: #pj: UP8_P0-ASCOM11+P1+P2+P3+P4+P5+P6+P7
            DICPOS = { #LOS NUMEROS DE LA TUPLA REPRESENTA BANCO Y POSICION DENTRO DEL BANCO
                "P19":(8,7),
                "P812":(8,6),
                "P913":(8,5),
                "P04":(8,4),
                "P15":(8,3),
                "P08":(8,2),
                "P13":(9,7),
                "P23":(9,6),
                "PREF23":(9,5),
                "SCOM3":(9,4),
                "P02":(9,3),
                "P01":(9,2),
                "PREF01":(9,1),
                "SCOM1":(9,0),
                "P57":(10,7),
                "P67":(10,6),
                "PREF57":(10,5),
                "SCOM7":(10,4),
                "P46":(10,3),
                "P45":(10,2),
                "PREF45":(10,1),
                "SCOM5":(10,0),
                "P911":(11,7),
                "P1011":(11,6),
                "PREF1011":(11,5),
                "SCOM11":(11,4),
                "P810":(11,3),
                "P89":(11,2),
                "PREF89":(11,1),
                "SCOM9":(11,0),
                "P1315":(12,7),
                "P1415":(12,6),
                "PREF1415":(12,5),
                "SCOM15":(12,4),
                "P1214":(12,3),
                "P1213":(12,2),
                "PREF1213":(12,1),
                "SCOM13":(12,0)

            }
            if CMD[2]=="8":
                self.__NPLACAS = 8
            elif CMD[3]=="6":
                self.__NPLACAS = 16
            else:
                raise TypeError("ERROR DE NUMERO DE PLACAS")
            _CMD = CMD.split("_") #ME DIVIDE EN [UP8,P0-ASCOM11+P1+P2+P3+P4+P5+P6+P7]
            _PLACAS = _CMD[1].split("+") #ESTO ME DIVIDE EN [P0-ASCOM11,P1,P2,P3,P4,P5,P6,P7]
            for PLACAi in _PLACAS:  #hay que reecorrer cada una de las placas
                if "-" in PLACAi: #Vemos que el - indica que se ha realizado algun comando de cierre o apertura
                    PLACAi = PLACAi.split("-") #La convierto en una lista [P0,ASCOM11]
                    PLACAiBIN = self.RELES.getPlacaInfoBinary(str(PLACAi[0])) #El primer elemento dela lista es la placa que se va a trabajar, con esta funcion ya me devuelve la informacion en binario
                    #PLACAiBIN TIENE UNA ESTRUCTURA DE LISTA (banco_0,banco_1,......,banco_N-1) cada uno de estos bancos estan dividido en bloque de 8 bits banco_0 = [0,0,0,0,0,0,0,0]
                    CONFIGi = PLACAi[1].split(",") #Me quedo con la lista en este caso [ASCOM11,] para la P0
                    for _CONF_RELE in CONFIGi:
                        if _CONF_RELE[0].lower() =="c":# Lo que indicaria que el rele se debe cerrar, entonces el valor a setear debe ser 1
                            value_set = 1
                        elif _CONF_RELE[1].lower()=="a":#lo que indicaria que el rele se debe abrir, entonces el valor se debe setear en 0
                            value_set = 0
                        else: #En caso de que exista algun error, se debe agregar un log para tenerlo en consideracion.
                            value_set = 0
                    
                        RELE_POS = _CONF_RELE[1:] #Tomo los elementos luego de la letra ej: SI es C01, solo me quedo con 01
                        RELE_POS_VALUADO = DICPOS[RELE_POS] #Esto me va a devolver la posicion del banco y de la posicion del bit dentro de esta misma
                        PLACAiBIN[RELE_POS_VALUADO[0]][RELE_POS_VALUADO[1]] = value_set
                    
                    PLACAiHEX = [hex(int("".join(map(str, sublist)), 2)) for sublist in PLACAiBIN] #Convierte la lista en hexadecimal
                    self.RELES.setPlacaConfig(placa=PLACAi[0], config=PLACAiHEX) #Se debe cargar la configuracion al diccionario
                
                else: #En caso que la placa no tenga config:
                    pass

            try:
                self.conect()
                self.write()
                return "OK"
            except:
                print("ERROR")
                return "NO OK"

        else:
            print("OTROS")
            #En caso de no tener nada para hacer por ejemplo que solo reciba P3
            pass
if __name__ =="__main__":
    torre = TorreRele()
    #torre.conect()
    #torre.readComando("CP8_P0-A00+P1+P2+P3+P4+P5+P6+P7")
    #torre.readComando("ATRPXGXRX")
    #torre.write()
    
    
"""
EJEMPLO DE LA IMPLEMENTACION

SUPONGAMOS QUE TENEMOS LA PLACA 0


P0 = |00000000|00000000|00000000|00000000|00000000|00000000|00000000|00000000|00000000|00000000|00000000|00000000|00000000|

Viene un comando MUX para trabajar 1x64

MUX_P0-1B64X1

Como vemos en el diccionario este pone el banco 8 al 12 siguiendo estos valores en HEXADECIMAL "1B64X1":["0x54","0X4C","0x4C","0x4C","0x4C"]

P0 = |00000000|00000000|00000000|00000000|00000000|00000000|00000000|00000000|01010100|01001100|01001100|01001100|01001100|

Ahora viene un comando para cerrar los reles

CP8_P0-C04,C08,C63+P1+P2+P3+P4+P5+P6+P7

Cierran los reles 4,8 y 63, cerrar significa poner en 1 el bit correspondiente.

Cada banco tiene 8 posiciones. Son 8 posiciones por 8 bancos. Es decir, hay 64 posiciones que inicia en 0 y termina en 63

la posicion en los bancos van en orden creciente [0,1,2,3,4,5,6,7] [8,9,10,11,..][.....] y asi hasta el 63

Entonces:
El rele 4 se ubica en la posicion 5 del banco 0
El rele 8 se ubica en la posicion 1 del banco 1
El rele 63 se ubica en la posicion 7 del banco 7

P0 = |00001000|10000000|00000000|00000000|00000000|00000000|00000000|00000001|01010100|01001100|01001100|01001100|01001100|


Cada uno de estos valores antes de enviarlos se convierten en hexadecimal nuevamente.

Este proceso se repite con las 16 placas.

##JUAN CRUZ EMMANUEL NOYA 2024-2025
"""