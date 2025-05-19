import serial

"""
  ____  ____  _____     _______ ____     ____ _   _ ___    _      ____  _____   ____  ____  _____ ____ ___ ___  _   _ 
 |  _ \|  _ \|_ _\ \   / / ____|  _ \   / ___| | | |_ _|  / \    |  _ \| ____| |  _ \|  _ \| ____/ ___|_ _/ _ \| \ | |
 | | | | |_) || | \ \ / /|  _| | |_) | | |  _| | | || |  / _ \   | | | |  _|   | |_) | |_) |  _| \___ \| | | | |  \| |
 | |_| |  _ < | |  \ V / | |___|  _ <  | |_| | |_| || | / ___ \  | |_| | |___  |  __/|  _ <| |___ ___) | | |_| | |\  |
 |____/|_| \_\___|  \_/  |_____|_| \_\  \____|\___/|___/_/   \_\ |____/|_____| |_|   |_| \_\_____|____/___\___/|_| \_|
                                                                                                                      
"""
"""
Controla la guia de presion

"""
__author__ = "Juan Cruz Noya"
__company__ ="Feas Electronica"
class GUIAPRESION:

    def __init__(self, port="COM24", baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.con = None
        self.VALUE = 0

    def connection(self):
        self.con = serial.Serial(port=self.port, baudrate=self.baudrate)

    def disconnection(self):
        if self.con and self.con.is_open:
            self.con.close()

    def setValue(self,value):
        value = int(value)
        self.VALUE = value



    def entero_binario_16b(self,numero):
        if not (0<=numero<=0xFFFF): #pregunta si se encuentra entre 0 y 65535
            print("ERROR numerico")
        else:
            binario_16b = format(numero,'016b')
            return binario_16b
        
    def return_bytes(self,numero_b):

        MSB = numero_b[0:8]
        LSB = numero_b[8:]
        print(f"Los bytes mas significativos son {MSB} y los menos significativos {LSB}")
        print("\nLa nomenclatura es |7-6-5-4-3-2-1-0|\n")
        print("Manual indica que el bit 7 siempre debe ser 1, y su valor real se debe almacenar en POSICION_BITS7")
        MSB_7 = MSB[0] #Guardo el valor real para luego armar mi variable aux
        LSB_7 = LSB[0]#Guardo el valor real para luego armar mi variable aux
        # Forzamos que el primer carácter sea "1"
        MSB = "1" + MSB[1:]
        LSB = "1" + LSB[1:]

        POSICION_BIT7 = "00000000"


        # Convertimos la cadena a lista para modificarla fácilmente
        POSICION_BIT7 = list(POSICION_BIT7)
        POSICION_BIT7[0] = "1"
        POSICION_BIT7[-1] = LSB_7
        POSICION_BIT7[-2] = MSB_7

        # Volvemos a convertir la lista en cadena
        POSICION_BIT7 = "".join(POSICION_BIT7)

        print(f"La variable POSICION_BIT7 es {POSICION_BIT7}")

        return MSB,LSB,POSICION_BIT7

    def bin_to_hexa(self,bin):

        entero = int(bin,2)
        hexa = hex(entero)

        hexa_sin_prefijo = hexa[2:].upper()

        return hexa


    def checksum(self,ID, MSB, LSB, POS7):
        # Convertir todo a enteros si vienen como strings hexadecimales
        if isinstance(ID, str): ID = int(ID, 16)
        if isinstance(MSB, str): MSB = int(MSB, 16)
        if isinstance(LSB, str): LSB = int(LSB, 16)
        if isinstance(POS7, str): POS7 = int(POS7, 16)

        suma = ID + MSB + LSB + POS7
        suma_8bits = suma & 0xFF
        cs = (~suma_8bits + 1) & 0xFF  # Complemento a dos

        cs |= 0x80  # Forzar bit 7 a 1 ya que uso un or

        return hex(cs)
    
    def posicionamiento(self):
        ID =0x54
        self.send_paquete(ID=ID)
        return "OK"
    def ganancia(self):
        ID =0x4A
        self.send_paquete(ID=ID)
        return "OK"
    def send_paquete(self,ID):
        numero = self.VALUE
        numero_b = self.entero_binario_16b(numero)
        STX = 0x02
        ID = ID
        ETX = 0x03
        MSB,LSB,POSICION_BIT7 = self.return_bytes(numero_b)
        MSB_HEX=self.bin_to_hexa(MSB)
        LSB_HEX=self.bin_to_hexa(LSB)
        POS7_HEX=self.bin_to_hexa(POSICION_BIT7)
        CHKS = self.checksum(ID=ID,MSB=MSB_HEX,LSB=LSB_HEX,POS7=POS7_HEX)
        print(CHKS)
        #Ahora convierto todo a numeros entero, lo de arriba puede servir para debugear
        if self.con != None:
            MSB_HEX = int(self.bin_to_hexa(MSB), 16)
            LSB_HEX = int(self.bin_to_hexa(LSB), 16)
            POS7_HEX = int(self.bin_to_hexa(POSICION_BIT7), 16)
            CHKS = int(CHKS, 16)
            paquete_datos = bytes([STX, ID, MSB_HEX, LSB_HEX, POS7_HEX, CHKS, ETX])
        
            self.con.write(paquete_datos)
            return "OK"
        else:
            print(hex(STX),hex(ID),MSB_HEX,LSB_HEX,POS7_HEX,CHKS,hex(ETX))
if __name__ =="__main__":
    instru = GUIAPRESION()
    instru.setValue(value=33761)
    instru.ganancia()
"""    print("\n")
    numero = 33761
    numero_b = entero_binario_16b(numero)
    ID= 0x4A
    print(f"La representacion binaria 16b del numero {numero} es {numero_b}")

    MSB,LSB,POSICION_BIT7 = return_bytes(numero_b)

    MSB_HEX = bin_to_hexa(MSB)
    LSB_HEX = bin_to_hexa(LSB)
    POSICION_BIT7_HEX = bin_to_hexa(POSICION_BIT7)
    print("0x02")
    print(hex(ID))
    print(MSB_HEX)
    print(LSB_HEX)
    print(POSICION_BIT7_HEX)
    print(checksum(ID,MSB_HEX,LSB_HEX,POSICION_BIT7_HEX))
    print("0x03")"""