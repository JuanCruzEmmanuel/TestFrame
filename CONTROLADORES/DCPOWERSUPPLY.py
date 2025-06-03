import serial
import struct
import binascii
import time
import sys,os
import serial
import json

__version__ = "1.0"
__author__ = 'Juan Cruz Noya'
__license__ = 'GPL'
__email__ = "juancruznoya@mi.unc.edu.ar"

"""
Special thanks to Joe Sachers and Benoit Frigon
"""



class PSU:

    """
    PSU is an object for controlling an Array/Protek power supply. This class allows setting the voltage, reading current, and controlling the power state of the PSU.\n
    Import notation is that PSU always send three parameters such us power limit, volt limit, current limit and setter volt

    :param address: (0-255) Local address for controlling multiple PSUs on the same port.
    :param port: Serial port to connect to the PSU (e.g., "COM1", "/dev/ttyUSB0").
    :param baudrate: Baudrate for serial communication, typically between 9600 and 19200.

    :func set_voltage: Set the output voltage of the PSU in volts (e.g., set_voltage(5.0) for 5 volts).
    :func get_voltage: Retrieve the current output voltage of the PSU in volts.
    :func get_current: Retrieve the current output of the PSU in amperes.
    :func get_power: Retrieve the current power output of the PSU in watts.
    :func power_on: Turn on the PSU output.
    :func power_off: Turn off the PSU output.
    :func close: Close the serial communication with the PSU.
    """

    DEBUG_MODE = False
    HEADER = 0xAA  # bit 1
    ADDRESS = 0x00  # bit 2

    SET_CMD = 0x80  # bit 3
    READ_CMD = 0x81  # bit 3
    INFO_CMD = 0x8C # Bit 3
    STRUCT_FRONT = struct.Struct(b'< 3B 23x')
    STRUCT_SET_PARAMETERS = struct.Struct(b'<HIHIB')
    FRAME_LENGHT = 26
    OFFSET_CHECKSUM = 25
    OFSET_PAYLOAD = 3
    GLOBAL_VARIABLES = "_TEMPS_\PSU_GLOBAL.json"

    def __init__(self, address, port, baudrate, error=False):
        """
        :param address: PSU address (0x00-0xFF)
        :param port: Serial connection port for serial.Serial()
        :return: None
        """
        try:
            with open(self.GLOBAL_VARIABLES, 'r') as file:
                self.datos = json.load(file)
        except:
            self.datos = {}
        self.address = address
        self.serial = serial.Serial(port=port, baudrate=baudrate)
        self._max_current = 0  # in mA
        self._max_power = 10800  # in mW
        self._max_voltage = 0 #in mV
        try:
            self._voltage = float(self.datos["VOLT"])*1000
        except:
            self._voltage = 0

        try:
            self._max_current = self.datos["CURRENT"]
        except:
            self._max_current = 0

        try:
                self.on = self.datos["ONOFF"]
        except:
            self.on = "OFF"
        self.model = ""
        self.SERIALNUM = ""
        self.ver = 0.0
        self.CURRENT = 0 #MEASURE CURRENT
        self.VOLTAGE = 0 #MEASURE VOLTAGE
        self.POWER = 0 #MEASURE POWER
        try:
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
            self.get_info()
        except:
            print("Error in get_info() and 8CH command")

            self.model = "3645A"
                
        self.update()

        self.set_parameters()

    
    def set_voltage(self,volt):
        """
        :param volt: set voltage in [VOLT]
        :return: None
        """
        if not os.path.exists(self.GLOBAL_VARIABLES):
            self.datos["VOLT"] = volt 


            with open (self.GLOBAL_VARIABLES,"w") as file:
                json.dump(self.datos,file,indent =4)
        else:
            self.datos["VOLT"] = volt 

            with open (self.GLOBAL_VARIABLES,"w") as file:
                json.dump(self.datos,file,indent =4)


        self._voltage = int(volt*1000)

        self.set_parameters()

    def set_current(self,current):

        """
        :param volt: set current in [mA]
        :return: None
        """
        if not os.path.exists(self.GLOBAL_VARIABLES):
            self.datos["CURRENT"] = current 


            with open (self.GLOBAL_VARIABLES,"w") as file:
                json.dump(self.datos,file,indent =4)
        else:
            self.datos["CURRENT"] = current 

            with open (self.GLOBAL_VARIABLES,"w") as file:
                json.dump(self.datos,file,indent =4)


        self._max_current = int(current)

        self.set_parameters()
         
    def update(self):
        MODEL_DIC ={
            "3644A":18000,
            "3645A":36000,
            "3646A":72000
        } 
        
        try:

            max_voltage = MODEL_DIC[self.model]

        except:
            self.model = "3645A"
            max_voltage = 36000
        max_current = self._max_power/max_voltage

        self._max_voltage = max_voltage
        try:
            self._max_current = self.datos["CURRENT"]
        except:
            self._max_current = int(max_current*10000)

    def send(self, command, parameters=None):
        if self.serial is None or not self.serial.is_open:
            raise serial.SerialException("Serial port was not opened!")

        if parameters is None:
            parameters = b''  # Empty byte string
            print("No parameters provided")

        if isinstance(parameters, (list, tuple)):
            if any(not isinstance(c, int) for c in parameters):
                raise ValueError("Lists used as the parameters argument must only contain integers")

            if any((c < 0 or c > 255) for c in parameters):
                raise ValueError("List used as the parameters must only contain integers from 0 to 255")

            parameters = bytes(parameters)  # Convert list/tuple of ints to bytes

        if not isinstance(parameters, (bytes, bytearray)):
            raise ValueError("The parameters argument must be bytes, a list, or a tuple object")

        ## Build command frame --> 26 bytes ##
        data = struct.pack('<B B B 22s', 0xAA, self.address, command, parameters)

        ## Append the checksum of the first 25 bytes to the frame ##
        checksum = sum(data) % 256
        data += bytes([checksum])

        #print(data)
        if self.on =="OFF":
            hex_string="AA00 8202 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 002E".replace(" ", "")
        else:
            hex_string="AA00 8203 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 002F".replace(" ", "")
        PCMODE = bytes.fromhex(hex_string)
        self.serial.write(PCMODE)
        self.serial.flush()
        self.serial.read(26)

        self.serial.write(data)
        self.serial.flush()

        result = self.serial.read(26)
        time.sleep(0.3)
        if self.on == "OFF":
            hex_string ="AA00 8200 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 002C".replace(" ", "")
        else:
            hex_string ="AA00 8201 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 002D".replace(" ", "")
        LOCALMODE = bytes.fromhex(hex_string)
        self.serial.write(LOCALMODE)
        self.serial.flush()
        self.serial.read(26)
        self.serial.flush()
        return result

    def set_parameters(self):
        data = struct.pack(
            '<HIHIB',
            int(self._max_current),  # No need to multiply by 1000 as this value is already in mA
            int(self._max_voltage),  # Voltage in mV
            int(self._max_power ),  # Power in centiwatts
            int(self._voltage),  # Voltage in mV
            self.address
        )

        self.send(self.SET_CMD, data)

    def get_info(self):
        """
        Function used to get information about power supply\n\n
        Saved model parameter in their *pivate* attribute
        """
        data = self.send(self.INFO_CMD) #Send INFO_CMD to serial port and recive the data about psu
    
        self.model = data[9:14].decode() #Model infomation is between from 10th to 15th position (python less 1 position)

    def power_on(self):
        #AA : HEADER  BYTE 1
        #00 : ADDRESS BYTE 2
        #82 : POWER SUPPLY CONTROL BYTE 3

        #03 : ON + PC CONTROL BYTE 4
        #00 : OFF + LOCAL CONTROl BYTE 4
        #01 : ON + LOCAL CONTROL BYTE 4

        """
        Function used to power on the PSU. In a first step send 03 4-byte and them send 01 4-byte\n
        AA : HEADER  BYTE 1
        00 : ADDRESS BYTE 2
        82 : POWER SUPPLY CONTROL BYTE 3

        03 : ON + PC CONTROL BYTE 4
        00 : OFF + LOCAL CONTROl BYTE 4
        01 : ON + LOCAL CONTROL BYTE 4
        02 : OFF + PC CONTROL BYTE 4

        :param None: 
        :return: SET ON POWER SUPPLY
        """
        hex_string="AA00 8203 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 002F".replace(" ", "")
        PCMODE_ON = bytes.fromhex(hex_string)
        self.serial.write(PCMODE_ON)
        self.serial.flush()
        self.serial.read(26)

        time.sleep(0.3)
        hex_string ="AA00 8201 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 002D".replace(" ", "")
        LOCALMODE = bytes.fromhex(hex_string)
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()
        self.serial.write(LOCALMODE)
        self.serial.flush()
        self.serial.read(26)

        self.datos["ONOFF"]= "ON"

        with open (self.GLOBAL_VARIABLES,"w") as file:
                json.dump(self.datos,file,indent =4)


    def power_off(self):


        """
        :param None: 
        :return: SET OFF POWER SUPPLY
        """
        hex_string="AA00 8202 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 002E".replace(" ", "")
        PCMODE_ON = bytes.fromhex(hex_string)
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()
        self.serial.write(PCMODE_ON)
        self.serial.flush()
        self.serial.read(26)

        time.sleep(0.3)
        hex_string ="AA00 8200 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 002C".replace(" ", "")
        LOCALMODE = bytes.fromhex(hex_string)
        self.serial.write(LOCALMODE)
        self.serial.flush()
        self.serial.read(26)
        
        self.datos["ONOFF"]= "OFF"

        with open (self.GLOBAL_VARIABLES,"w") as file:
                json.dump(self.datos,file,indent =4)

    
    def get_current(self,ON = False):

        """
        param ON :*bool* TURN ON/OFF PSU

        return: Set in CURRENT attribute the meassure value of current in Ampers. Return this value
        
        """

        """if ON:
            data = self.send(self.READ_CMD,ONOFF = "ON")
        else:
            data = self.send(self.READ_CMD,ONOFF = "OFF")"""
        data = self.send(self.READ_CMD)
        self.CURRENT = float(struct.unpack_from('<H', data, 3)[0]) / 1000  # Conversión de la corriente a A

        return self.CURRENT/1000 #Devuelve valor en mA

    def get_voltage(self,ON = False):

        """
        param ON :*bool* TURN ON/OFF PSU

        return: Set in VOLTAGE attribute the meassure value of voltage in VOLTS. Return this value
        
        """
        """if ON:
            data = self.send(self.READ_CMD,ONOFF = "ON")
        else:
            data = self.send(self.READ_CMD,ONOFF = "OFF")"""

        data = self.send(self.READ_CMD)
        self.VOLTAGE = float(struct.unpack_from('<L', data, 5)[0]) / 1000 # en voltios

        return 1000*self.VOLTAGE #Devuelve valor de tension en mV
    
    def get_power(self,ON = False):

        """
        param ON :*bool* TURN ON/OFF PSU

        return: Set in POWER attribute the meassure value of POWER in WATTS. Return this value
        
        """
        """if ON:
            data = self.send(self.READ_CMD,ONOFF = "ON")
        else:
            data = self.send(self.READ_CMD,ONOFF = "OFF")"""
        data = self.send(self.READ_CMD)
        self.POWER = float(struct.unpack_from('<H', data, 9)[0]) / 100  # En watts
        return self.POWER       
    

    def close(self):
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()
        self.serial.close()
    


if __name__ =="__main__":
    """
    DC = PSU(0,"COM4",9600)
    DC.set_voltage(6)
    DC.power_on()
    time.sleep(1)
    print(DC.get_power())
    DC.close()"""
    
    """
    ser = serial.Serial(port = "COM4",baudrate=9600)
    hex_string="AA00 8100 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 002B".replace(" ", "")
    read_ = bytes.fromhex(hex_string)
    ser.write(read_)
    ser.flush()
    r = ser.readline()
    
    print(r)
    
    """

    help(PSU)