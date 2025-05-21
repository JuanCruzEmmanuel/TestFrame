"""
  _____  _____   ____   _____ _____ __  __    ___           _____  _____  _______      ________ _____  
 |  __ \|  __ \ / __ \ / ____|_   _|  \/  |  / _ \         |  __ \|  __ \|_   _\ \    / /  ____|  __ \ 
 | |__) | |__) | |  | | (___   | | | \  / | | (_) |        | |  | | |__) | | |  \ \  / /| |__  | |__) |
 |  ___/|  _  /| |  | |\___ \  | | | |\/| |  > _ <         | |  | |  _  /  | |   \ \/ / |  __| |  _  / 
 | |    | | \ \| |__| |____) |_| |_| |  | | | (_) |        | |__| | | \ \ _| |_   \  /  | |____| | \ \ 
 |_|    |_|  \_\\____/|_____/|_____|_|  |_|  \___/         |_____/|_|  \_\_____|   \/   |______|_|  \_\
                                                                                                                                                                                                                                                                                                                                                                             
prosim8.py - Driver para control remoto de ProSim 8 (Fluke Biomedical)
Versión 1.2.1

Este módulo implementa la clase PROSIM8 para gestionar la comunicación
con un simulador de paciente ProSim 8 a través de un puerto serie USB.
Permite poner el equipo en modo remoto, configurar parámetros fisiológicos
(ECG, NIBP, SpO₂, ritmo cardíaco, arritmias, estimulación, etc.), y
manejar la conexión de forma robusta con timeouts y reintentos básicos.


COMO SE DEBERIA ARMAR LOS COMANDOS PARA USO CON LENGUAJE TIPO CMD

VAMOS A DESARROLLAR UN ARBOL DE EJECUCION

-Esto me recomiendo chat gpt para desarrollar los comandos, realmente no me convence; pero deriamos desarrollarlo


PS8 -run ECG --frec <BPM> --amp <AMPLITUD> --artifact <TIPO> --lead <DER/IZQ> --dev <DESVIACION>
PS8 -run ARRITMIA --tipo <TIPO> --side <DER/IZQ>
PS8 -run MARCAPASO --modo <ATR/ASY/AVS/...> --amp <AMP> --width <WIDTH> --polo <P/N> --chamber <A/V>
PS8 -run FIB --tipo <A/V> --granularidad <fine/coarse>
PS8 -run VTACH --frec <BPM>
PS8 -run SpO2 --sat <SAT> --perf <PERF> --sensor <TIPO>
PS8 -run RESP --rate <BRPM> --ratio <1-5> --ampl <AMP> --base <0500-2000> --lead <ABDOMINAL/TORACICA> --apnea <ON/OFF>
PS8 -run SEÑAL --forma <SINE/TRIANGLE/SQUARE/PULSE> --frec <HZ/BPM>
PS8 -run TEMP --valor <30.0–42.0>


"""
import serial
from typing import Optional
import numpy
from time import sleep

__company__ = "Feas Electronica"
__author__ = "Juan Cruz Noya & Julian Font"
__version__ = "1.2.1"
__country__ = "Argentina"

class PROSIM8:
    """
    Clase para controlar el simulador ProSim 8 vía puerto serie.

    Métodos principales:
    - Abrir/cerrar conexión serial:                     connect()/disconnect()
    - Cambiar entre modo remoto y local:                remote()/local(): 
    - Configurar ritmo sinusal:                         setHeartRate(), NormalRate()
    - Ajustar señales ECG:                              setDeviation(), setECGAmplitude(), setArtifact(), etc.
    - Métodos de arritmias:                             setPreVentricularArrhythmia(), setSupArrhythmia(), VentricularArrhythmia(), ConductionArrythmia().
    - Métodos de marcapasos:                            setPacerPolarity(), setPacerAmplitude(), setPacerWidth(), setPacerChamber(), setPacerPulse().
    - Simular fibrilación y taquicardia ventricular:    setFibrilation(), setMonovtach()
    - Simular Parametricas:                             setSENO(), setTRIANGULAR(), setSQUARE(), setPulse()
    - Simular SpO2:                                     set_SpO2_saturacion(), set_SpO2_perfusion(), set_SpO2_ppm(), set_SpO2_Sensor()
    - Simular Respiratoria:                             RespCurveOn(), RespCurveOff(), setRespRate(), setRespRatio(), setRespAmpl(), setRespBase(), setRespLead(), APNEA()
    - Simular Temperatura:                              setTemperature()

    Ejemplo de uso básico:
        ps8 = PROSIM8(port="COM11")
        ps8.connect()
        ps8.setHeartRate(70)
        ps8.NormalRate()
        ...
        ps8.disconnect()
    """
    def __init__(self,port,debug=False,baudrate=115200):
        
        self.port = port
        self.baudrate = baudrate
        self.debug = debug
        self.HEARTRATE = 60
        self.MODE = "ADULTO"
        self.LEAD_ARTIFACT = "ALL"
        self.LEAD_SIZE = "025"
        self.SIDE = "Left"
        self.PACER_POLARITY = "P"
        self.PACER_AMP = "010"
        self.PACER_WIDTH = "1.0"
        self.PACER_CHAMBER = "A"
        self.FIB_GRANULARITY = "COARSE"
        self.con: Optional[serial.Serial] = None
        self.PRESSURECHANNEL = "1"
    def connect(self):
        """
        CONECTA PROSIM8 CON PUERTO SERIE\n
        DATOS:\n
        serial.STOPBITS_ONE = 1\n
        serial.PARITY_NONE = 'None'\n
        """
        if self.con is not None and self.con.is_open:
            return
        try:
            self.con = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                stopbits=serial.STOPBITS_ONE,
                parity=serial.PARITY_NONE,
                bytesize=8,
                xonxoff=False,
                timeout=1
            )
            self.remote()
        except serial.SerialException as e:
            self.con = None
            raise ConnectionError(f"Error de conexión: {e}")
        
    def remote(self):
        self.sendCommand(cmd="REMOTE")


    def disconnect(self):
        """
        DESCONECTA PROSIM8 CON PUERTO SERIE\n
        """
        if self.con is not None:
            if self.con.is_open:
                self.con.close()
            self.con = None

    def _format_int(self, value, width= 3):
        try:
            iv = int(value)
            return str(iv).zfill(width)
        except (ValueError, TypeError):
            return str(value)

    def _format_decimal(self, value, int_digits=2, dec_digits=2):
        """
        Formatea un número decimal con dígitos fijos antes y después del punto.
        """
        try:
            fv = float(value)
            fmt = f"{{:0{int_digits + 1 + dec_digits}.{dec_digits}f}}"
            return fmt.format(fv)
        except (ValueError, TypeError):
            return str(value)
        
    
    def sendCommand(self, cmd,type="3digits"):
        """
        type es una variable que va a controla el tipo de dato que hay:\n
        3digits: Numeros sin signo de la forma xxx por ejemplo 25--->025\n
        2digits: Numeros de dos digitos con coma y dos valores despues de la coma por ejemplo 2 ---> 02.00\n
        1digits:Numeros de 1 digito con coma y dos valores despues de la coma por ejemplo 2 ---> 2.00\n
        4digits: Numero sin signo con 4 espacios xxxx por ejemplo 500 ---> 0500 #solo para baseline\n
        string: sin formato numerico\n
        temp: 2 digitos, coma 1 cero 30 ---> 30.0
        
        """
        if self.con is None or not self.con.is_open:
            raise serial.SerialException("Puerto serie no está conectado")
        
        # Formatear número a 3 dígitos si el comando contiene un "="
        if '=' in cmd:
            key, value = cmd.split('=', 1)
            if '.' in value:
                if type=="1digits":
                    value = self._format_decimal(value, int_digits=1, dec_digits=2)
                elif type=="2digits":
                    value = self._format_decimal(value, int_digits=2, dec_digits=2)
                elif type =="temp":
                    value = self._format_decimal(value, int_digits=2, dec_digits=1)
            elif value.isdigit():
                if type=="3digits":
                    value = self._format_int(value, width=3)
                elif type=="4digits":
                    value = self._format_int(value, width=4)
                elif type=="string":
                    pass #En caso de las arritmias y esas cosas
            cmd = f"{key}={value}"
        
        cmd = cmd + "\r"
        self.con.write(cmd.encode('utf-8'))  # type: ignore
        if self.debug:
            print(f"Comando enviado: {cmd}")

        if self.con is None or not self.con.is_open:
            raise serial.SerialException("Puerto serie no está conectado")
        raw = self.con.readline()  # type: ignore
        try:
            if self.debug:
                print(f"Status recibido: {raw.decode('utf-8').strip()}")
            return
        except UnicodeDecodeError:
            if self.debug:
                print(f"Status recibido: {raw.decode('latin1').strip()}")
            return

    def sendCommandNoNumerico(self, cmd):
        cmd = cmd + "\r"
        self.con.write(cmd.encode('utf-8'))  # type: ignore

        if self.debug:
            print(f"Comando enviado: {cmd}")
        raw = self.con.readline()  # type: ignore
        try:
            if self.debug:
                print(f"Status recibido: {raw.decode('utf-8').strip()}")
            return
        except UnicodeDecodeError:
            if self.debug:
                print(f"Status recibido: {raw.decode('latin1').strip()}")
            return
#*****************************************************************ECG**********************************************************************
    
    def setPacerPolarity(self,polarity):
        self.PACER_POLARITY = polarity
    
    def setPacerAmplitude(self,ampl):

        self.PACER_AMP = ampl

    def setPacerWidth(self,width):
        self.PACER_WIDTH = width

    def setHeartRate(self,rate):
        """
        SETEA LA FRECUENCIA DE LATIDOS\n
        :rate: 10 - 360\n
        """
        if int(rate)<10:
            print("Valor por debajo del limite")
            self.HEARTRATE=10
        elif int(rate)>360:
            print("Valor por encima del limite")
            self.HEARTRATE = 360
        else:
            print(f"Se setea el valor frecuencia cardiaca en: {int(rate)}")
            self.HEARTRATE = int(rate)

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
        cmd = f"NSRA={self.HEARTRATE}"
        self.sendCommand(cmd)


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

        cmd=f"STDEV={param}"
        self.sendCommand(cmd)
    
    def setECGAmplitude(self,param="1.00"):
        """
        Setea la amplitud del ECG\n
        
        """
        #No me voy a gastar en esta instancia en poner la amplitud correcta, se hace muy largo;
        #Se tiene que saber que entre 0.05 a 0.45; saltos de 0.05mV;
        #Saltos de 0.50 a 5.00 saltos de 0.25mV
        cmd=f"ECGAMPL={param}"
        self.sendCommand(cmd)
    
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
            "respiratoria":"RESP",
            "off":"OFF",
            "OFF":"OFF"
        }

        try:
            param = dic_artifact[param]
        except:
            param = param
        
        #configura
        cmd = f"EART={param}"
        self.sendCommandNoNumerico(cmd)



    def setArtifactLead(self,lead):

        self.LEAD_ARTIFACT = "LEAD"
        cmd = f"EARTLD={self.LEAD_ARTIFACT}"
        self.sendCommand(cmd)

    def SetArtifactSize(self,size):
        if int(size)<25:
            size = "25"
        elif int(size)>100:
            size = "100"
        if len(str(size))==2:
            self.LEAD_SIZE =f"0{size}"
        else:
            self.LEAD_SIZE = "100"

        cmd = f"EARTSZ={self.LEAD_SIZE}"
        self.sendCommand(cmd)

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
        
        cmd = f"PREWAVE={arrh}"
        self.sendCommand(cmd)

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
        cmd=f"SPVWAVE={arrh}"
        self.sendCommand(cmd)
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
        cmd = f"VNTWAVE={arrh}"
        self.sendCommand(cmd)


    def RunAsistolia(self):
        cmd=f"VNTWAVE=ASYS"
        self.sendCommand(cmd)

    def ConductionArrythmia(self,param): #El alias puede ser bloqueo

        
        _conduction_arrythmia_dic = {
            "PrimerBloqueo":"1DB",
            "PrimerGrado":"1DB",
            "FirstDegeeBlock":"1DB",
            "BloqueoAV":"1DB",
            "Wenck":"2DB1",
            "Wenckebach":"2DB1",
            "SegundoGrade":"2DB2",
            "SecondDegree":"2DB2",
            "Tipo2":"2DB2",
            "2DG":"2DB2",
            "TercerGrado":"3DB",
            "ThirdDegree":"3DB",
            "BloqueoTercerGrado":"3DB",
            "RamaDerecha":"RBBB",
            "RightBundleBranchBlock":"RBBB",
            "RightBranch":"RBBB",
            "RamaIzquierda":"LBBB",
            "LeftBranch":"LBBB",
            "LeftBundleBranchBlock":"LBBB"
        }
        try:
            arrh = _conduction_arrythmia_dic[param]
        except:
            arrh = "1DB"

        cmd = f"CNDWAVE={arrh}"
        self.sendCommand(cmd)

    def setPacerChamber(self,chamber):

        self.PACER_CHAMBER = chamber

    def setPacerPulse(self,wave):

        tvp_wave_dic = {
            "Atrial":"ATR",
            "atrial":"ATR",
            "ATR":"ATR",
            "Asincronica":"ASY",
            "asincronica":"ASY",
            "Asincronico":"ASY",
            "asincronico":"ASY",
            "ASIN":"ASY",
            "ASI":"ASY",
            "Asynchronous":"ASY",
            "ASY":"ASY",
            "Frecuente":"DFS",
            "Frequent":"DFS",
            "DFS":"DFS",
            "Ocasional":"DOS",
            "Occasional":"DOS",
            "DOS":"DOS",
            "AtrioVentricular":"AVS",
            "Atrio-Ventricular":"AVS",
            "SinCaputra":"NCP",
            "Sin-Captura":"NPC",
            "NonCapture":"NPC",
            "Non-Capture":"NPC",
            "NPC":"NPC",
            "Sin-Funcion":"NFN",
            "Non-Function":"NFN"
        }

        try:
            wave_selected = tvp_wave_dic[wave]
        except:
            wave_selected = "ATR"
            print("ERROR-502")


        #Setea polaridad
        cmd = f"TVPPOL={self.PACER_CHAMBER},{self.PACER_POLARITY}"
        self.sendCommand(cmd)
        #Setea Amplitud
        cmd = f"TVPAMPL={self.PACER_CHAMBER},{self.PACER_AMP}"
        self.sendCommand(cmd)
        #Setea Ancho de pulso
        cmd = f"TVPWID={self.PACER_CHAMBER},{self.PACER_WIDTH}"
        self.sendCommand(cmd)

        #######################################
        #Setea el tipo de onda
        cmd = f"TVPWAVE={wave_selected}"
        self.sendCommand(cmd)

    def setGranularity(self,param):
        _granularity_dic = {
            "fino":"FINE",
            "Fino":"FINE",
            "Fine":"FINE",
            "FINE":"FINE",
            "fine":"FINE",
            "Grueso":"COARSE",
            "grueso":"COARSE",
            "COARSE":"COARSE",
            "Coarse":"COARSE",
            "coarse":"COARSE"
        }
        try:
            self.FIB_GRANULARITY = _granularity_dic[param]
        except:
            self.FIB_GRANULARITY = "COARSE"
            print("ERROR-503")

    def setFibrilation(self,param):
        """
        Setea la fibrilacion, puede ser de atrio, o ventricular
        """
        _fibrilation_dic = {
            "Atrio":"ATRIAL",
            "Atrial":"ATRIAL",
            "ATRIO":"ATRIAL",
            "atrio":"ATRIAL",
            "atrial":"ATRIAL",
            "A":"ATRIAL",
            "V":"VENTRICULAR",
            "Ventricular":"VENTRICULAR",
            "VENTRICULAR":"VENTRICULAR",
            "ventricular":"VENTRICULAR",
            "VENTRICULO":"VENTRICULAR",
            "ventriculo":"VENTRICULAR",
            "Ventriculo":"VENTRICULAR"

        }
        try:
            switcher = _fibrilation_dic[param]
        except:
            switcher = "VENTRICULAR"
        
        if switcher=="ATRIAL":
            cmd = f"AFIB={self.FIB_GRANULARITY}"
            self.sendCommand(cmd)
        else:
            cmd = f"VFIB={self.FIB_GRANULARITY}"
            self.sendCommand(cmd)

    def setMonovtach(self):
        """
        SOLO FUNCIONA SI HEARTRATE >120
        """
        """try:
            if int(param)<120:
                _rate = "120"
            elif int(param)>300:
                _rate = "300"
            else:
                _rate = str(int(param))
        except:
            print("ERROR-505")
            _rate = "120"
        """
        cmd = f"MONOVTACH={self.HEARTRATE}"
        self.sendCommand(cmd)

    #*****************************************************************SpO2**********************************************************************
    def set_SpO2_saturacion(self, SATURATION):
        """
        Sets SpO2 Saturation Percentage\n
        Unsigned 3 digits 000 to 100
        """
        cmd = f"SAT={SATURATION}"
        self.sendCommand(cmd)
    
    def set_SpO2_perfusion(self, PERFUSION):
        """
        Sets SpO2 perfsusion, the pusle amplitude in percent\n
        2 digits w/dp: 00.01 to 20.00 [by 00.01]
        """
        cmd = f"PERF={PERFUSION}"
        self.sendCommand(cmd,type="2digits")

    def set_SpO2_ppm(self, PERFUSION):
        cmd = f"PERF={PERFUSION}"
        self.sendCommand(cmd)
 
    def set_SpO2_Sensor(self,sensor):
        """
        Setea el tipo de sensor de oximetría.

        Args:
            sensor (str): Tipo de sensor a configurar.

        Returns:
            str: "OK" si la configuración fue exitosa.
        """
        sensor_type_dic = {
            "NELCOR":"NELCR",
            "NELCR":"NELCR",
            "MASIMO":"MASIM",
            "MASIM":"MASIM",
            "MASIMORAD":"MASIMR",
            "MASIMOR":"MASIMR",
            "MASIMR":"MASIMR",
            "NONIN":"NONIN",
            "OHMED":"OHMED",
            "PHIL":"PHIL",
            "NIHON":"NIHON",
            "MINDRAY":"MINDR",
            "MINDR":"MINDR",
            "BCI":"BCI"
        }

        try:
            selected_sensor = sensor_type_dic[sensor]
        except:
            selected_sensor="BCI"
        
        self.sendCommand(cmd=f"SPO2TYPE={selected_sensor}")

    #*****************************************************************RESPIRATORIO**********************************************************************

    def RespCurveOn(self):
        """
        Inicia la curva de respiratoria
        """
        self.sendCommand(cmd="RESPRUN=TRUE")

    def RespCurveOff(self):
        """
        Finaliza la curva de respiratoria
        """
        self.sendCommand(cmd="RESPRUN=FALSE")
        
    
    def setRespRate(self,rate):
        """
        en el caso de agregar una variable global, hay que tener cuidado\n
        :param:
        **rate**: respiration rate in brpm: 3 digits 010 to 150
        """
        self.sendCommand(cmd = f"RESPRATE={rate}")
    
    def setRespRatio(self,ratio):
        """
        No se que es el ratio (se que es relacion, pero no se a que hace referencia en una señal respiraria\n
        :param:
        **ratio**: 1 digit from 1 to 5
        """
        self.sendCommand(cmd = f"RESPRATIO={ratio}")
        
    def setRespAmpl(self,ampl):
        """
        Setea la amplitud de la curva respiratoria\n
        :param:
        **ampl**: 3 digits w/dp: 0.00 to 5.00 by 0.05
        """
        self.sendCommand(cmd = f"RESPAMPL={ampl}",type="1digits")

    def setRespBase(self,baseline):
        """
        Setea la impedancia base en valores 4 digitos 0000\n
        :param:
        
        **baseline**: Va desde 0500, 1000, 1500 o 2000
        """
        self.sendCommand(cmd=f"RESPBASE={baseline}",type="4digits")
        
    def setRespLead(self,lead):
        lead_dic = {
            "TRANSABD":"LA",
            "LA":"LA",
            "ABDOMINAL":"LA",
            "TORACICA":"LL",
            "LL":"LL",
        }
        
        try:
            selected_lead = lead_dic[lead]
        except :
            selected_lead = "LA"
        
        self.sendCommand(cmd=f"RESPLEAD={selected_lead}")

    def APNEA(self,atrib):
        """
        Set APNEA
        """
        if atrib:
            flag = "ON"
        else:
            flag = "OFF"
        self.sendCommand(cmd=f"RESPAPNEA={flag}")
        
#*******************************************************************OTRAS SEÑALES*****************************************************************
#OTRAS SEÑALES HACE REFERENCIA A:
#                               *SENO
#                               *CUADRADA
#                               *TRIANGULAR
#                               *PULSO


    def setSINE(self,freq):
        """
        SETEA UNA SEÑAL SENO\n
        :param:
        **freq**: frequency in hz; 0.05, 0.5, 1, 2, 5, 10, 25, 30, 40, 50, 60, 100 or 150\n
        *user notes: In practice we can used it in between ranges. P.E. 70*
        """
        try:
            freq= float(freq)
            if freq <0.5:
                freq = "0.05"
            elif freq <1:
                freq ="0.5"
            elif freq <2:
                freq ="1"
            elif freq<5:
                freq ="2"
            elif freq<10:
                freq="5"
            elif freq<25:
                freq="10"
            elif freq<30:
                freq ="25"

            elif freq<40:
                freq="30"
            elif freq<50:
                freq="40"
            elif freq<60:
                freq ="50"

            elif freq<100:
                freq="60"
            elif freq<150:
                freq="100"
            elif freq>=150:
                freq ="150"

        except:
            freq="60"
        self.sendCommand(cmd=f"SINE={freq}",type="string")
    
    def setTRIANGLE(self,freq):
        """
        set ECG WAVE to TRIANGLE\n
        :param:
        **freq**: frecuency in Hz: 0.125,2.0 or 2.5
        """
        try:
            freq = float(freq)
            if freq <2.0:
                freq = "0.125"
            elif freq <2.5:
                if freq >=2.0:
                    freq="2.0"
            else:
                freq = "2.5"
        except:
            freq = "2.0"
        self.sendCommand(cmd=f"TRI={freq}")       

    def setSQUARE(self,freq):
        """
        Set ECG wave to square\n
        :param:
        **freq**: frecuency in Hz: 0.125,2.0 or 2.5
        """
        try:
            freq = float(freq)
            if freq <2.0:
                freq = "0.125"
            elif freq <2.5:
                if freq >=2.0:
                    freq="2.0"
            else:
                freq = "2.5"

        except:
            freq = "2.0"
        self.sendCommand(cmd=f"SQUARE={freq}")
    def setPULSE(self,rate):
        """
        Set ECG wave to Pulse\n
        :param:
        **rate**: rate in bpm 30, 60 or 80
        """
        #Hay que testear si solo esos valores se pueden agregar

        self.sendCommand(cmd=f"PULSE={rate}")

    #*****************************************************************PRESION NO INVASIVA**********************************************************************
    #In-develpment SUMULATION COMMANDS

    def ZPRESS(self):
        """
        CANAL DE PRESION NO INVASIVA EN CERO
        """
        self.sendCommand(cmd=f"ZPRESS")

    def NIBP(self,at=False):
        """
        NIBP SIMULATION ON/OFF
        """
        if at:
            self.sendCommand(cmd=f"NIBPRUN=ON")
        else:
            self.sendCommand(cmd=f"NIBPRUN=OFF")
    def NIBPENVELOPE(self,shift):
        """
        Set the NIBP envelope shift\n
        :param:

        **shift**: Envelope shift porcentage: 2 digits signed:-10 to +10
        """
        sign = '-' if shift < 0 else "+"
        number = abs(shift)
        formatted_shift = f"{sign}{number:02}"
  

        self.sendCommand(cmd=f"NIBPES={formatted_shift}")
    def NIBPVOLUME(self,volume):
        """
        Set the NIBP volume\n
        **volume**: Volume in mL: 3 digits w/dp: 0.10 to 1.25; by 0.05
        """
        self.sendCommand(cmd=f"NIBPV={volume}",type="1digits")
    #In-develpment MEASUREMENT AND CONTROL COMMANDS
    #*****************************************************************PRESION INVASIVA*************************************************************************
    #In-develpment

    def setPressChannel(self,channel):
        """
        Selecciona el canal de presion invasiva\n
        :param:
        **channel**: IBP channel 1 or 2
        """
        if channel !="1" or channel !="2":
            print("ERROR DE CANALES DE PRESIONES")
            self.PRESSURECHANNEL = "1"
        else:
            self.PRESSURECHANNEL = channel

    def presure_format(self,value):

        sign = '-' if value < 0 else ''
        number = abs(value)
        formatted = f"{sign}{number:03}"
        return formatted

    def setPressPressure(self,pressure):
        """
        Ingresa la presion estatica\n
        :param:
        **pressure** : signed static pressure: 3 digits: -010 to +300
        """
        pressure = self.presure_format(value=pressure)
        self.sendCommand(cmd=f"IBPS={self.PRESSURECHANNEL},{pressure}")
    def setPressWave(self,wave):
        """
        Se setean ondas precargadas\n
        :param:
        ***wave*** : {
        ART:arterial,
        RART:radial artery,
        LV:left ventricule,
        LA:left atrium,
        RV:right ventricle,
        PA:pulmary artery,
        PAW:pa wedge
        RA:right atrium
        }
        """
        pressure_dic={
            "arterial":"ART",
            "art":"ART",
            "rad":"RART",
            "radial":"RART",
            "lv":"LV",
            "ventriculoizquierdo":"LV",
            "la":"LA",
            "atrioizquierdo":"LA",
            "ventriculoderecho":"RV",
            "rightventricle":"RV",
            "rv":"RV",
            "arteriapulmonar":"PA",
            "pulmonar":"PA",
            "pa":"PA",
            "wedge":"PAW",
            "atrioderecho":"RA",
            "rightatrium":"RA",
            "ra":"RA"
        }

        self.sendCommand(cmd=f"IBPW={self.PRESSURECHANNEL},{pressure_dic[wave]}")

    #SE PUEDE SEGUIR DESARROLLANDO PARA LOS ARTEFACTOS, AUNQUE ESTO GENERA UN AUMENTO EN EL TIEMPO DE DESARROLLO.......

    #*****************************************************************TEMPERATURA******************************************************************************
    def setTemperature(self,degree):
        """
        Set the temperature\n
        :param:
        **degree** Temperature un degree C: 3 digits w/dp: 30.0 to 42.0 by 00.5
        """
        self.sendCommand(cmd=f"TEMP={degree}",type="temp")
    #*****************************************************************GASTO CARDIACO***************************************************************************
    #In-develpment
if __name__=="__main__":
    ps8 = PROSIM8(port="COM11", debug = True)
    ps8.connect()
    ps8.setECGAmplitude(param="1.00")


""" 
Ejemplos de uso:

    Primero conectar el PS8 y crear el objeto:
        ps8 = PROSIM8(port="COM11")
        ps8.connect()
    

    Configurar en PS8 curva ECG de 100ppm:
        ps8.setHeartRate(100)
        ps8.NormalRate()

    Configurar en PS8 curva pletismografica en 85%:
        ps8.set_SpO2_saturacion(85)
    
"""