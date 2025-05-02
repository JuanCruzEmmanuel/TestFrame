######## SE va a encargar de controlar al PROSIM 8 INSTRUMENTO TRONCAL, seguiremos con la misma logica creada hasta el momento
import serial
import numpy
from INSTRUCONTRACT import instru_contract
from time import sleep
class PROSIM8(instru_contract):
    def __init__(self,port,baudare=115200):
        self.port = port
        self.baudrate = baudare
        self.con = None
        self.HEARTRATE = 60
        self.MODE = "ADULT"
        self.LEAD_ARTIFACT = "ALL"
        self.LEAD_SIZE = "025"
        self.SIDE = "Left"
    def connect(self):
        """
        CONECTA PROSIM8 CON PUERTO SERIE\n
        DATOS:\n
        serial.STOPBITS_ONE = 1\n
        serial.PARITY_NONE = 'None'\n
        """
        self.con = serial.Serial(port=self.port,baudrate=self.baudrate,stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE,bytesize=8,xonxoff=False)
        #Lo conecto y lo dejo en estado remoto
        self.remote()
    def remote(self):

        self.writecommand(cmd="REMOTE")
        
        print(self.readcommand()) #DEBERIA DEVOLVER RMAIN


    def disconnect(self):
        """
        DESCONECTA PROSIM8 CON PUERTO SERIE\n
        """
        self.con.close()

    def readcommand(self):
        response = self.con.readline().decode("utf-8")

        return response
    def writecommand(self,cmd):

        self.con.write(cmd.encode())
        sleep(0.5) #Delay de seguridad

    def setHeartRate(self,rate):
        """
        SETEA LA FRECUENCIA DE LATIDOS\n
        :rate: 10 - 360\n
        """
        if int(rate)<10:
            print("Valor por debajo del limite")
            self.setHeartRate=10
        elif int(rate)>360:
            print("Valor por encima del limite")
            self.setHeartRate = 360
        else:
            print(f"Se setea el valor frecuencia cardiaca en: {int(rate)}")
            self.setHeartRate = int(rate)

    def setMode(self,mode):
        """
        SETEA EL MODO\n
        :mode: ADULTO, NEO,.... y los que sean necesarios\n
        """

        self.MODE =mode

    def NormalRate(self):
        """
        Se encarga de enviar el comando para configurar el control normal de la señal cardiaca\n
        """
        if self.MODE=="ADULTO":
            if len(self.NormalRate)==2: #por ejemplo 99, se debe enviar de la forma 099

                _temp_cmd = f"NSRA=0{self.NormalRate}" #Normal Sinus Rate Adult
            else:
                _temp_cmd = f"NSRA={self.NormalRate}"
        elif self.MODE =="PEDIATRICO":
            if len(self.NormalRate)==2: #por ejemplo 99, se debe enviar de la forma 099
                _temp_cmd = f"NSRP=0{self.NormalRate}" #Normal Sinus Rate Pediatric
            else:
                _temp_cmd = f"NSRP={self.NormalRate}"
        else:
            _temp_cmd = "...."

        self.writecommand(cmd=_temp_cmd)
        #Creo que no responde nada especifico, pero por una cuestion de buenas practicas....
        self.readcommand()

    def truncar_dos_decimales(self,valor):
        return int(valor * 100) / 100

    def setDeviation(self,param="0.00"):
        """
        Setea desviacion de la linea base\n
        :param:
        param: valor que puede ir desde:\n
        ± 0.00 a 0.05 a 0.01mV de paso\n
        ± 0.10 a 0.80 a 0.10mV de paso
        """ 
        #En este caso particular como es un valor "numerico" puedo determinar si el valor ingresado tiene forma de valor flotante
        
        _float_param = float(param)
        try:
            if -0.05<=_float_param<= 0.05:
                _float_param = self.truncar_dos_decimales(valor=_float_param)
                param = str(_float_param)
            elif (0.10 <= _float_param <= 0.80 or -0.80 <= _float_param <= -0.10):
                # Solo aceptar si es múltiplo de 0.10 exacto
                if round(_float_param % 0.10, 8) == 0:
                    param = str(_float_param)
            else:
                print("ERR-150")
                print("El formato ingresado es incorrecto")
                param = "0.00"
        except:
            print("ERR-151")
            print("El formato ingresado es incorrecto")
            param = "0.00"
        
        self.writecommand(cmd=f"STDEV={param}")

        self.readcommand()
    
    def setECGAmplitude(self,param="1.00"):
        """
        Setea la amplitud del ECG\n
        
        """
        #No me voy a gastar en esta instancia en poner la amplitud correcta, se hace muy largo;
        #Se tiene que saber que entre 0.05 a 0.45; saltos de 0.05mV;
        #Saltos de 0.50 a 5.00 saltos de 0.25mV
        self.writecommand(cmd=f"ECGAMPL={param}")
        self.readcommand()
    
    def setArtifact(self,param="OFF"):
        """
        Funcion que setea el tipo de artefacto\n
        :param:
        DIC: El diccionario va a tener una cantidad de posibles valores para que la funcion tenga un accionar correcto\n
        """

        dic_artifact={
            "50":"50",
            "60": "60",
            "50HZ":"50",
            "50Hz":"50",
            "60HZ": "60",
            "60Hz": "60",
            "60hz": "60",
            "50hz": "50",
            "Musc": "MSC",
            "MUSC": "MSC",
            "musc": "MSC",
            "MUSCULAR": "MSC",
            "muscular": "MSC",
            "MSC": "MSC",
            "WANDERING": "WAND",
            "BASELINE": "WAND",
            "wandering": "WAND",
            "wand": "WAND",
            "base": "WAND",
            "wanderingBaseline":"WAND",
            "WanderingBaseline":"WAND",
            "RESP":"RESP",
            "resp":"RESP",
            "Resp":"RESP",
            "RESPIRATORIA":"RESP",
            "respiratoria":"RESP"
        }

        try:
            param = dic_artifact[param]
        except:
            param = param
        
        #configura
        self.writecommand(cmd = f"EART={param}")

        self.readcommand()


    def setArtifactLead(self,lead):

        self.LEAD_ARTIFACT = "LEAD"

        self.writecommand(cmd = f"EARTLD={self.LEAD_ARTIFACT}")

        self.readcommand()

    def SetArtifactSize(self,size):
        if int(size)<25:
            size = "25"
        elif int(size)>100:
            size = "100"
        if len(size)==2:
            self.LEAD_SIZE =f"0{size}"
        else:
            self.LEAD_SIZE = "100"

        
        self.writecommand(cmd = f"EARTSZ={self.LEAD_SIZE}")
        
        self.readcommand()

    def setSide(self,param):

        _side_dic = {

            "Izquierda":"Left",
            "IZQ": "Left",
            "I":"Left",
            "L":"Left",
            "Left":"Left",
            "izq":"Left",
            "izquierda":"Left",
            "DER":"Right",
            "der":"Right",
            "D":"Right",
            "R":"Right",
            "Right":"Right",
            "Derecha":"Right",
            "derecha":"Right"
        }

        self.SIDE = _side_dic[param] #Selecciona el lado donde se va a realizar la arrimia


    def setPreVentricularArrhythmia(self,param):

        _pre_ventricular_arrhythmia_dic = {
            "prematureatrialcontraction":"PAC",
            "PrematureAtrialContraction":"PAC",
            "PAC":"PAC",
            "AtrialContraction":"PAC",
            "ACONTRACTION":"PAC",
            "prematurenodalcontraction":"PNC",
            "PrematureNodalContraction":"PNC",
            "PNC":"PNC",
            "NodalContraction":"PNC",
            "NCONTRACTION":"PNC",
            "ContraccionVentricular": "PVC1",
            "PVC":"PVC1",
            "VentricularContraction":"PVC1",
            "Early":"PVC1E",
            "early":"PVC1E",
            "Temprana":"PVC1E",
            "temprana":"PVC1E",
            "ContraccionTemprana":"PVC1E",
            "RenT":"PVC1R",
            "RonT":"PVC1R",
            "ContraccionRenT":"PVC1R",
            "ContraccionRT":"PVC1R",
            "RTContraction":"PVC1R",
            "RT":"PVC1R",
        }
        try:
            arrh = _pre_ventricular_arrhythmia_dic[param]
        except:
            arrh = "PAC" #Para que no se detenga la ejecucion.....
        if not self.SIDE=="Left":
            if "1" in arrh:
                arrh = arrh.replace("1","2") #Cambio el 1 por el 2, ya que eso simboliza que el pvc se realiza a la derecha
        
        self.writecommand(cmd=f"PREWAVE={arrh}")

        self.readcommand()

    def setSupArrhythmia(self,param):
        """
        ***GLOSARIO***:\n
        **AFL**: Atrial Flutter\n
        **SNA**: Sinus Arrhythmia\n
        **MB80**: Missed Beat at 80 BPM\n
        **MB120**: Missed Beat at 120 BPM\n
        **ATC**: Atrial Tachycaria\n
        **PAT**: Paroxismal Atrial Tachycardia\n
        **NOD**: Nodal Rhythm\n
        **SVT**: Supraventricual Tachycardia 
        
        """
        supra_ventricular_arrhythmia_dic = {
            "Flutter": "AFL",
            "AtrialFlutter": "AFL",
            "flutter": "AFL",
            "AFL":"AFL",
            "Sinus":"SNA",
            "sinus":"SNA",
            "SNA":"SNA",
            "Sinusal":"SNA",
            "ArritmiaSinusal":"SNA",
            "SinusArrhythmia":"SNA",
            "80BPM" :"MB80",
            "80":"MB80",
            "80LPM":"MB80",
            "120BPM":"MB120",
            "120":"MB120",
            "120LPM":"MB120",
            "SupraventricularTachycardia":"SVT",
            "TaquicardiaSupraventricular":"SVT",
            "SupTaquicardia":"SVT",
            "SVT":"SVT",
            "SupTachycardia":"SVT",
            "Nodal":"NOD",
            "NOD":"NOD",
            "Paraox": "PAT",
            "PAT":"PAT",
            "Paroxismal":"PAT",
            "Paroxysmal":"PAT",
            "TaquicardiaAtrialParoxismal":"PAT",
            "ParoxysmalAtrialTachycardia":"PAT",
            "TaquicardiaAtrial":"ATC",
            "ATC":"ATC",
            "Taquicardia":"ATC",
            "Tachycardia":"ATC",
            "TaquicardiaAtrial":"ATC",
            "AtrialTachycardia":"ATC"
        }

        try:
            arrh = supra_ventricular_arrhythmia_dic[param]
        except:
            arrh = "AFL" #Para que no se detenga la ejecucion.....

        self.writecommand(cmd=f"SPVWAVE={arrh}")
        self.readcommand()

    def VentricularArrhythmia(self,param):

        _ventricular_arrhythmia_dic = {
            "6":"PVC6M",
            "6min":"PVC6M",
            "PVC6M":"PVC6M",
            "12":"PVC12M",
            "12min":"PVC12M",
            "PVC12M":"PVC12M",
            "24":"PVC24M",
            "24min":"PVC24M",
            "PVC24M":"PVC24M",
            "MultiFocal":"FMF",
            "Multi":"FMF",
            "FrequentMultiFocal":"FMF",
            "Trigeminismo":"TRIG",
            "Trigeminy":"TRIG",
            "TRIG":"TRIG",
            "Trig":"TRIG",
            "Bigeminismo":"BIG",
            "Bigeminy":"BIG",
            "BIG":"BIG",
            "Big":"BIG",
            "PAIR":"PAIR",
            "PAR":"PAIR",
            "5": "RUN5",
            "11":"RUN11"
        }
    
        try:
            arrh = _ventricular_arrhythmia_dic[param]
        except:
            arrh = "FMF" #Para que no se detenga la ejecucion.....

        self.writecommand(cmd=f"VNTWAVE={arrh}")
        self.readcommand()

    def RunAsistolia(self):
        
        self.writecommand(cmd=f"VNTWAVE=ASYS")
        self.readcommand()