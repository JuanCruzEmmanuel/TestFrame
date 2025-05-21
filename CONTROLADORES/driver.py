import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from CONTROLADORES.Multimetro import Fluke45, Fluke8845
from CONTROLADORES.psu364x import PSU
from CONTROLADORES.IMPULSE7000 import IMPULSE7000
from CONTROLADORES.ESA620 import ESA620
from CONTROLADORES.OSCILOSCOPIO import TEKTRONIX
from CONTROLADORES.PROSIM8 import PROSIM8
from CONTROLADORES.GUIAPRESION import GUIAPRESION
import serial
import time
from datetime import datetime
import json

__version__ ="1.2.3"

__autor__ ="Juan Cruz Noya & Julian Font"

__propiedad__ ="Feas Electronica"

"""
Version 1.0.0   Se incia el driver
Version 1.0.1   Se agregan funcionabilidad para control de Fluke multimetros
Version 1.0.2   Se agrega funcionabilidad para deteccion automatica de multimetros
Version 1.0.3   Se agrega el instrumento fuente programable PSU
Version 1.0.4   Se mejora comandos de Fuente para agregar la lectura de la misma
Version 1.0.5   Se agrega control del impulse 7000
Version 1.0.6   Se Agregan comandos y funciones para el ESA620
Version 1.0.7   Se agrega el control de todas las funciones del ESA620 que se utilizan en la empresa
Version 1.1     Se agrega la opcion de LOG. Este se guardara especificamente en la carpeta data del SMVA2
Version 1.1.1   Se agrega un try except en esa620() para corregir error al seleccionar el puerto. Se agregan palabras a los diccionarios.
Version 1.1.2   Se agrega el diccionario power a esa620(), para utilziarlo como alimentacion de los equipos bajo ensayo.
version 1.1.3   Se Agrega la capacidad de agregarle rango manual al multimetro fluke 8845
Version 1.1.4   Se agrega la funcion diode_measure() en multimetro fluke 8845 para medir diodos.
Version 1.1.5   Se agrega mediciones con osciloscopio tektronix
Version 1.1.6   Se agrega sleep(1) al luego de cerrar el puerto en el metodo esa620()
Version 1.2     Se comienza a trabajar en el manejo de errores de comunicación. Se agrega el error -101 en ESA620. Si el driver no encuentra el puerto serie, retorna el string -101
                Error -101: Puerto serie no encontrado (Acceso denegado).
Version 1.2.1   Se implementa la funcion LOCAL() en esa620() antes de cerrar el puerto.
Version 1.2.2   Se corrige un error, en donde la instruccion LOCAL() se ejecutaba despues de cerrar el puerto
Version 1.2.3   Se agrega el PROSIM8
Version 1.2.4   Se agrega codigo de guia de presion
"""


def LOG(valor, nombre_log="log.json"):
    """
    Guarda un valor numérico y su fecha/hora actual en un archivo JSON.

    Args:
        valor (float|int): El valor numérico que se quiere guardar.
        nombre_log (str): El nombre del archivo de log. Por defecto, 'log.json'.
    """
    #EN CASO QUE NO SE AGREGUE EL .JSON HAY QUE AGREGAR
    if ".json" not in nombre_log: 
        nombre_log +=".json"
    try:
        # Crear una entrada con el valor y la fecha/hora
        entrada_log = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "valor": valor
        }
        
        # Leer el archivo existente si existe
        try:
            with open(f"C:\Program Files (x86)\FeasSMVA_2_0Project\data\{nombre_log}", "r") as file:
                logs = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            logs = []  # Iniciar lista vacía si no existe el archivo o está corrupto
        
        # Agregar la nueva entrada
        logs.append(entrada_log)
        
        # Guardar el archivo actualizado
        with open(f"C:\Program Files (x86)\FeasSMVA_2_0Project\data\{nombre_log}", "w") as file:
            json.dump(logs, file, indent=4)
        
        print("Log guardado correctamente.")
    except Exception as e:
        print(f"Error al guardar en el log: {e}")



def ident(port, instr: str):

    if instr.lower() == "multimetro":

        ser = serial.Serial(port=port, baudrate=9600,timeout=0.1)

        ser.write("*IDN?\r\n".encode())
        ins = ser.readline().decode()
        ins_l = ins.split(",")
        ser.close()
        return str(ins_l[1]),str(ins_l[2])
def multimetro(CMD:list):

    ejecutar = "None"
    instrument_type = "multimetro"
    port = next((COM for COM in CMD if "port" in COM.lower()), "COM1") #Se busca si encuentra el port si no lo localiza usa el valor por defecto
    try:
        port = port.split(" ")[1]   #En caso de encontrar port debo tomar el valor del COM
    except:
        port = port #Caso simplemete para evitar problemas en el except; tambien se podria agregar un pass aunque asi es mas elegante
    # Identificar el modelo de multímetro
    inst,NS= ident(port=port, instr=instrument_type)
    if "45" in inst and "88" not in inst:
        instr = Fluke45(port=port, baudrate=9600)
    else:
        if NS =="9441009":
            instr = Fluke8845(port=port, baudrate=9600,fetch_trouble=True)
        else:
            instr = Fluke8845(port=port, baudrate=9600)

    LOGFLAG = False

    #INCICALIZO UN SWITCH CASE CON DICCIONARIO DE ACCIONES
    parametros = {
        "scale":"scale",
        "escala":"scale",
        "delay": "delay",
        "t": "delay",
        "DCAC": "AC_DC",
        "ACDC": "AC_DC",
        "AC/DC": "AC_DC",
        "DC/AC": "AC_DC",
        "4W":"four_wire",
        "4H": "four_wire",
        "4_wire": "four_wire",
        "4_hilos":"four_wire",
        "range": "range",
        "rango":"range",
        "rang" : "range",
        "highvoltage":"diodehighvoltage",
        "HV":"diodehighvoltage",
        "lowcurr":"diodelowcurrent",
        "lowcur":"diodelowcurrent",
        "lowcurrent":"diodelowcurrent"
    }
    #RECORRO LA LISTA DE PARAMETROS
    for param in CMD:
        param_split = param.split(" ")
        accion = param_split[0]
        if accion.lower() == "run" or accion.lower() == "r":
            ejecutar = param_split[1]

        else:
            valor = param_split[1]
            if accion.lower() != "port":
                if accion.lower() != "log":
                    if valor.lower() != "true" or valor.lower() != "verdadero":
                        try:
                            setattr(instr,parametros[accion],int(valor))
                        except:
                            setattr(instr,parametros[accion],valor)

                    else:
                        setattr(instr,parametros[accion],True)
                else:
                    LOGFLAG = True
                    LOGNAME = valor
            else:
                pass

    # Acciones soportadas
    actions = {
        "resistance": instr.resistance_measure,
        "voltage": instr.voltage_measure,
        "voltaje":instr.voltage_measure,
        "volt":instr.voltage_measure,
        "current": instr.current_measure,
        "corriente":instr.current_measure,
        "frecuency": instr.freq_measure,
        "None": instr.None_function,
        "res": instr.resistance_measure,
        "resistencia": instr.resistance_measure,
        "diode": instr.diode_measure,
        "diodo":instr.diode_measure,
        "diodecheck": instr.diode_measure

    }

    atributo ={
        "resistencia":"resistance",
        "volt": "voltage",
        "voltaje": "voltage",
        "voltage": "voltage",
        "current": "current",
        "corriente":"current",
        "frecuency": "frecuency",
        "resistance": "resistance",
        "res":"resistance",
        "diode": "diode",
        "diodo":"diode",
        "diodecheck": "diode"

    }

    try:
        actions[ejecutar]()
        result = getattr(instr, atributo[ejecutar])
    except:
        raise ValueError(f"Unsupported action: {ejecutar}")

    instr.stop()

    if LOGFLAG:
        LOG(valor=result,nombre_log=LOGNAME)
    return result
def psu(CMD:list):
    port = next((COM for COM in CMD if "port" in COM.lower()), "COM4") #Se busca si encuentra el port si no lo localiza usa el valor por defecto
    try:
        port = port.split(" ")[1]   #En caso de encontrar port debo tomar el valor del COM
    except:
        port = port #Caso simplemete para evitar problemas en el except; tambien se podria agregar un pass aunque asi es mas elegante
        
    instru = PSU(0,port = port, baudrate=9600)
    #INCICALIZO UN SWITCH CASE CON DICCIONARIO DE ACCIONES
    set = {
        "volt":instru.set_voltage,
        "on":instru.power_on,
        "off":instru.power_off
    }
    get = {
        "volt":instru.get_voltage,
        "current":instru.get_current,
        "power":instru.get_power
    }

    for _cmd in CMD:
        if "set" in _cmd:
            if "=" in _cmd:
                num = float(_cmd.split("=")[1]) #me divide la palabra segun el igual
                action = _cmd.split("=")[0].strip().split(maxsplit=1)[1] #ignoro la cantidad de espacios por si hay errores de tipeo
                set[action](num) #En este caso va a setear el voltage para la fuente
            else:
                action = _cmd.split("=")[0].strip().split(maxsplit=1)[1] #Esto en el caso que se quiera prender o apagar la fuente
                set[action]()
        elif "get" in _cmd:
            action = _cmd.split("=")[0].strip().split(maxsplit=1)[1]
            return get[action]()
    
    return "OK"

def guiaPresion(CMD:list):
    """
    UN EJEMPLO DE COMANDO DESDE EL SMVA SERIA *GuiaPresion --run ganancia --value 33761
    """


    instru = GUIAPRESION(port="COM24")
    instru.connection() #Conecto el instrumento
    prioridades = { #Es importante el orden donde se establecen ciertos parametros
        "value":1,
        "Value":1,
        "Valor":1,
        "valor":1,
        "run": 2,
        "Run":2
    }

    run_dic = {
        "ganancia":instru.ganancia,
        "gain":instru.ganancia,
        "Gain":instru.ganancia,
        "Ganancia":instru.ganancia,
        "Pos":instru.posicionamiento,
        "Posicion":instru.posicionamiento,
        "pos":instru.posicionamiento
    }

    guia_presion_setter={
        "value":instru.setValue,
        "Value":instru.setValue,
        "valor":instru.setValue,
        "Valor":instru.setValue
    }

    def obtener_prioridad(elemento): #lo hago funcion para trabajar con la funcion lamda mas facil
        palabras = elemento.split()
    # Buscar la palabra clave que existe en las prioridades
        for palabra in palabras:
            if palabra.lower() in prioridades:
                return prioridades[palabra]
    # Si no encuentra ninguna palabra clave, asignar una prioridad muy alta
        return float('inf')
    

    CMD_SORTED = sorted(CMD,key=obtener_prioridad)
    #print(CMD_SORTED)
    for cmd in CMD_SORTED:
        cmd = cmd.split(" ")
        
        if cmd[0] == "port":
            pass
        elif "run" in cmd[0].lower():
            ejecutar = cmd[1] #Tomo el elemento por ejemplo gain

        else: #En caso de no ser run, va a ser un setter 
            guia_presion_setter[cmd[0]](value=cmd[1]) #En este caso va a setear el valor separado por el espacio

    try:
        exc = run_dic[ejecutar]()

        return exc
    except:
        "EN CASO DE ERROR"
        return "NO OK"


def impulse(CMD:list):
    port = next((COM for COM in CMD if "port" in COM.lower()), "COM14") #Se busca si encuentra el port si no lo localiza usa el valor por defecto
    try:
        port = port.split(" ")[1]   #En caso de encontrar port debo tomar el valor del COM
    except:
        port = port #Caso simplemete para evitar problemas en el except; tambien se podria agregar un pass aunque asi es mas elegante
    
    instru = IMPULSE7000(port = port) #Se conecta al impulse7000

    parametros = {
    }

    MEDICIONES = {

        "energy":instru.read_energy,
        "energia":instru.read_energy
    }

    for cmd in CMD:
        cmd = cmd.split(" ")
        if "run" in cmd[0].lower() or "r" in cmd[0].lower():
            getter = cmd[1]


    try:
        meas = MEDICIONES[getter]()
    except:
        instru.local_mode()
        instru.close()
        return "Error Driver Impulse"
    

    instru.local_mode()
    instru.close()
    
    return meas
def esa620(CMD:list):
    port = next((COM for COM in CMD if "port" in COM.lower()), "COM22") #Se busca si encuentra el port si no lo localiza usa el valor por defecto
    try:
        port = port.split(" ")[1]   #En caso de encontrar port debo tomar el valor del COM
    except:
        port = port
    try:
        instru = ESA620(port = port)
        time.sleep(1.5)
        run = {
            "mainVoltage":instru.voltMeasure,
            "MainVoltage":instru.voltMeasure,
            "Voltage":instru.voltMeasure,
            "TierraProteccion":instru.protectiveEarthResistance,
            "Resistencia":instru.protectiveEarthResistance,
            "ResistenciaTierra":instru.protectiveEarthResistance,
            "EarthResistance":instru.protectiveEarthResistance,
            "TierraAislada":instru.insulationResistance,
            "Insulation": instru.insulationResistance,
            "InsulationResistance": instru.insulationResistance,
            "CorrienteEquipo":instru.equipmentCurrent,
            "Current":instru.equipmentCurrent,
            "Corriente":instru.equipmentCurrent,
            "EquipmentCurrent":instru.equipmentCurrent,
            "CorrienteDeEquipo":instru.equipmentCurrent,
            "FuegaATierra":instru.leakageEarth,
            "LeakageEarth":instru.leakageEarth,
            "EarthLeakage":instru.leakageEarth,
            "FugaATierra":instru.leakageEarth,
            "CorreinteDeFuga":instru.leakageEarth,
            "FugaACarcasa":instru.enclosureLeakageCurrent,
            "Carcasa":instru.enclosureLeakageCurrent,
            "EnclosureLeakageCurrent":instru.enclosureLeakageCurrent,
            "CorrienteDeFugaACarcasa":instru.enclosureLeakageCurrent,
            "CorrienteFugaPaciente":instru.patientLeakageCurrent,
            "FugaPaciente":instru.patientLeakageCurrent,
            "PatientLeakageCurrent":instru.patientLeakageCurrent,
            "CorrienteDeFugaPaciente":instru.patientLeakageCurrent,
            "Paciente":instru.patientLeakageCurrent,
            "CorrienteDeFugaAPaciente":instru.patientLeakageCurrent,
            "MainsOnAppliedParts":instru.mainAppliedParts,
            "Mains":instru.mainAppliedParts,
            "MainsAppliedParts":instru.mainAppliedParts,
            "PrincipalPartesAplicadas":instru.mainAppliedParts,
            "PrincipalPartes":instru.mainAppliedParts,
            "PrincipalPartesAplicadas":instru.mainAppliedParts,
            "auxiliaryCurrent":instru.patientAuxiliaryCurrent,
            "patientAuxiliaryCurrent":instru.patientAuxiliaryCurrent,
            "AuxiliaryCurrent":instru.patientAuxiliaryCurrent,
            "CorrienteAuxiliar":instru.patientAuxiliaryCurrent,
            "CorrientePacienteAuxiliar":instru.patientAuxiliaryCurrent,
            "Auxiliary":instru.patientAuxiliaryCurrent
        }
        power = {
            "on":instru.powerON,
            "ON":instru.powerON,
            "On":instru.powerON,
            "off":instru.powerOFF,
            "Off":instru.powerOFF,
            "OFF":instru.powerOFF
        }
        #COMANDO PARA PRENDER EL EQUIPO BAJO ENSAYO: *ESA620 --power On
        #COMANDO PARA APAGAR EL EQUIPO BAJO ENSAYO: *ESA620 --power Off
        SET_ATRIBUTO = {
            "TIPO":instru.setTest,
            "TYPE":instru.setTest,
            "type":instru.setTest,
            "tipo":instru.setTest,
            "leads":instru.setLeads,
            "electrodos":instru.setLeads,
            "lead":instru.setLeads,
            "elect":instru.setLeads,
            "neutro":instru.setNeutral,
            "NEUTRAL":instru.setNeutral,
            "neutral":instru.setNeutral,
            "neut":instru.setNeutral,
            "NEUTRO":instru.setNeutral,
            "polarity":instru.setPolarity,
            "POL":instru.setPolarity,
            "POLARITY":instru.setPolarity,
            "polaridad":instru.setPolarity,
            "POLARIDAD":instru.setPolarity,
            "TIERRA":instru.setEarth,
            "Tierra":instru.setEarth,
            "EARTH":instru.setEarth,
            "tierra":instru.setEarth,
            "earth":instru.setEarth,
            "GND":instru.setEarth,
            "gnd":instru.setEarth
        }

        for cmd in CMD:
            cmd = cmd.split(" ")
            
            if cmd[0] == "port":
                pass
            elif "run" in cmd[0].lower():
                ejecutar = cmd[1]

            else:
                SET_ATRIBUTO[cmd[0]](value=cmd[1])

        
        exc = run[ejecutar]()

        
        instru.LOCAL()
        instru.close()
        time.sleep(1)
        return exc
    except:
        return "-101"
def osciloscopio(CMD):
    #POR EL MOMENTO SOLO ESTA EL TEKTRONIX TBS1064
    instru = TEKTRONIX()

    #La configuracion del osciloscopio es muy importante. si bien yo puedo poner donde quiera ciertas cosas, es importante que siga una cierta secuencia logica como la existencia de canal y el tipo de medicion
    #Para esto lo mejor es tener un diccionario con las prioridades

    prioridades = {
        "ON":1,
        "on":1,
        "off":2,
        "OFF":2,
        "ch":3,
        "CH":3,
        "canal":3,
        "CANAL":3,
        "tipo":5,
        "type":5,
        "TIPO":5,
        "TYPE":5,
        "timpomedicion":5,
        "pos":4,
        "posicion":4,
        "POS":4,
    }

    SET_OSCI ={
        "ch":instru.setChannel,
        "CH":instru.setChannel,
        "canal":instru.setChannel,
        "CANAL":instru.setChannel,
        "tipo":instru.setMeasType,
        "type":instru.setMeasType,
        "TIPO":instru.setMeasType,
        "TYPE":instru.setMeasType,
        "escalavertical":instru.setVerticalScale,
        "ESCALAVERTICAL":instru.setVerticalScale,
        "vscale":instru.setVerticalScale,
        "VSCALE":instru.setVerticalScale,
        "vertiscale":instru.setVerticalScale,
        "VERTISCALE":instru.setVerticalScale,
        "VS":instru.setVerticalScale,
        "VPOS":instru.setVerticalPosition,
        "vpos":instru.setVerticalPosition,
        "posvertical":instru.setVerticalPosition,
        "posicionvertical":instru.setVerticalPosition,
        "POSVERTICAL":instru.setVerticalPosition,
        "POSICIONVERTICAL":instru.setVerticalPosition,
        "VP":instru.setVerticalPosition,
        "vp":instru.setVerticalPosition,
        "HS":instru.setHorizontalScale,
        "horizontal":instru.setHorizontalScale,
        "tiempo":instru.setHorizontalScale,
        "HORSCALE":instru.setHorizontalScale,
        "posicionhorizontal":instru.setHorizontalPosition,
        "POSICIONHORIZONTAL":instru.setHorizontalPosition,
        "PosicionHorizontal":instru.setHorizontalPosition,
        "HSCALE":instru.setHorizontalScale,
        "hpos":instru.setHorizontalPosition,
        "hscale":instru.setHorizontalScale,
        "trigger":instru.setTriggerLevel,
        "TRIGGER":instru.setTriggerLevel,
        "TRIGLEVEL":instru.setTriggerLevel,
        "niveltrigger":instru.setTriggerLevel,
        "valortrigger":instru.setTriggerLevel,
        "POS":instru.setMedicionPosicion,
        "pos":instru.setMedicionPosicion,
        "posicion":instru.setMedicionPosicion,
        "ON":instru.setON,
        "on":instru.setON,
        "OFF":instru.setOFF,
        "off":instru.setOFF
    }

    run = {
        "medicion":instru.getMEAS,
        "med":instru.getMEAS,
        "getMed":instru.getMEAS,
        "getMedicion":instru.getMEAS
    }

    def obtener_prioridad(elemento): #lo hago funcion para trabajar con la funcion lamda mas facil
        palabras = elemento.split()
    # Buscar la palabra clave que existe en las prioridades
        for palabra in palabras:
            if palabra in prioridades:
                return prioridades[palabra]
    # Si no encuentra ninguna palabra clave, asignar una prioridad muy alta
        return float('inf')

    CMD_SORTED = sorted(CMD,key=obtener_prioridad)
    #print(CMD_SORTED)
    for cmd in CMD_SORTED:
        cmd = cmd.split(" ")
        
        if cmd[0] == "port":
            pass
        elif "run" in cmd[0].lower():
            ejecutar = cmd[1]

        else:
            SET_OSCI[cmd[0]](value=cmd[1])

    try:
        exc = run[ejecutar]()

        return exc
    except:

        "EN CASO QUE SOLO SE BUSQUE EJECUTAR CONFIGURACIONES DE OSCILOSCOPIO DEBE DEVOLVER OK"
        return "OK"

def prosim8(CMD):
    port = next((COM for COM in CMD if "port" in COM.lower()), "COM11") #Se busca si encuentra el port si no lo localiza usa el valor por defecto
    try:
        port = port.split(" ")[1]   #En caso de encontrar port debo tomar el valor del COM
    except:
        port = port
    try:
        instru = PROSIM8(port = port,debug=True)
        args_dic = {} #Diccionario para guardar todos los argumentos que van a estar en el comando CMD
        for arg in CMD:
            splited_arg = arg.split(" ")#Separo la palabra que se encuentra con espacio y me la divide en 2 mitades
            args_dic[splited_arg[0]]=splited_arg[1] #La primer mitad la uso como clave, la segunda como value
        instru.connect() #Conecto
        if args_dic["run"] =="ECG":
            for key, value in args_dic.items():
                if key == "frec" or key =="FREC" or key=="FREQ" or key =="FRECUENCIA" or key =="BPM" or key =="LPM":
                    instru.setHeartRate(rate=args_dic[key])
                    instru.NormalRate()
                elif key == "amp" or key =="AMP" or key=="amplitud" or key =="importancia" or key =="AMPLITUD":
                    instru.setECGAmplitude(param=args_dic[key])
                elif key in ["artifact", "artefacto","ghost"]:
                    instru.setArtifact(param=value)
                elif key in ["artsize","asize"]:
                    instru.SetArtifactSize(size=value)
                elif key in ["dev", "desviacion"]:
                    instru.setDeviation(param=value)
        elif args_dic["run"] in ["asistolia", "asist", "ASISTOLIA", "ASYS","asis"]:
            instru.RunAsistolia() #corre asistolia
        elif args_dic["run"] in ["seno", "sen", "SENO", "SEN","SIN","sine","sin"]:
            for key, value in args_dic.items():
                if key == "frec" or key =="FREC" or key=="FREQ" or key =="FRECUENCIA":
                    instru.setSINE(freq=value) #SENO
        elif args_dic["run"] in ["square", "sqr", "cuad", "cuadrada","SQRT","SQR","CUAD","CUADRADA"]:
            for key, value in args_dic.items():
                if key == "frec" or key =="FREC" or key=="FREQ" or key =="FRECUENCIA":
                    instru.setSQUARE(freq=value) #CUADRADA
        elif args_dic["run"] in ["tri", "TRI", "triangular", "TRIANGLE"]:
            for key, value in args_dic.items():
                if key == "frec" or key =="FREC" or key=="FREQ" or key =="FRECUENCIA":
                    instru.setTRIANGLE(freq=value) #TRIANGULAR
        elif args_dic["run"] in ["pulso", "PULSO", "PUL", "PULSE","pulse"]:
            for key, value in args_dic.items():
                if key == "frec" or key =="FREC" or key=="FREQ" or key =="FRECUENCIA":
                    instru.setPULSE(rate=value) #PULSO
        elif args_dic["run"] in ["PreVentricular","PV","preventricular","pv","premature","PREMATURE"]: #PREMATURE ARRHYTM
            for key, value in args_dic.items():
                if key in ["arr", "arritmia","type","tipo","ARRITMIA","ARRHY","ARRIT"]:
                    instru.setPreVentricularArrhythmia(param = value)
        elif args_dic["run"] in ["SupraVentricular","SV","supraventricular","sv","supra","SUPRA","suprav","SUPRAV"]: #SUPRAVENTRICULAR ARRHYTM
            for key, value in args_dic.items():
                if key in ["arr", "arritmia","type","tipo","ARRITMIA","ARRHY","ARRIT"]:
                    instru.setSupArrhythmia(param = value)
        elif args_dic["run"] in ["Ventricular","ven","ventricular","VEN"]: #VENTRICULAR
            for key, value in args_dic.items():
                if key in ["arr", "arritmia","type","tipo","ARRITMIA","ARRHY","ARRIT"]:
                    instru.VentricularArrhythmia(param = value)
        elif args_dic["run"].lower() in ["conduccion","con","conduc","conduction"]: #arritmia de conduccion
            for key, value in args_dic.items():
                if key in ["arr", "arritmia","type","tipo","ARRITMIA","ARRHY","ARRIT"]:
                    instru.ConductionArrythmia(param = value)
        elif args_dic["run"] =="MARCAPASO":
            pass
        elif args_dic["run"].lower() =="afib":
            for key, value in args_dic.items():
                if key.lower() in ["granulacion","gran","granularity"]:
                    instru.setGranularity(param=value)
            instru.setFibrilation(param="Atrial")
        elif args_dic["run"].lower() =="vfib":
            for key, value in args_dic.items():
                if key.lower() in ["granulacion","gran","granularity"]:
                    instru.setGranularity(param=value)
            instru.setFibrilation(param="VENTRICULAR")
        elif args_dic["run"] =="VTACH":
            instru.setMonovtach()
        elif args_dic["run"] in ["SpO2","SPO2"]:
            for key, value in args_dic.items():
                if key.lower() in ["sat","saturacion","saturation"]:
                    instru.set_SpO2_saturacion(SATURATION=value)
                elif key.lower() in ["perf","perfusion"]:
                    instru.set_SpO2_perfusion(PERFUSION=value)
                elif key.lower() in ["freq","frecuencia","fp","pulso","frec"]:
                    instru.setHeartRate(rate=value)
                    instru.NormalRate()
                elif key.lower() in ["sensor","tipo","type"]:
                    instru.set_SpO2_Sensor(sensor=value)
        elif args_dic["run"] =="RESP":
            for key, value in args_dic.items():
                if key.lower() in ["freq","frec","frecuencia"]:
                    instru.setRespRate(rate=value)
                elif key.lower() in ["amplitud","amp"]:
                    instru.setRespAmpl(ampl=value)
                elif key.lower() in ["base","baseline","bline"]:
                    instru.setRespBase(baseline=value)
                elif key.lower() in ["lead","type","tipo"]:
                    instru.setRespLead(lead=value)
            instru.RespCurveOn()
        elif args_dic["run"].lower() =="apnea":
            instru.APNEA(atrib=True)
        elif args_dic["run"] =="TEMP":
            for key, value in args_dic.items():
                if key.lower() in ["temp","temperature"]: #Seteo la temperatura
                    instru.setTemperature(degree=value)
        elif args_dic["run"] =="GC":
            pass
        elif args_dic["run"].lower() in ["pi","ip","invasivepresure","presioninvasiva","ibp"]:
            for key, value in args_dic.items():
                if key.lower() in ["press","presion","pressure","pres","estatica","static"]:
                    presion=value #Porq sino se sobre escribe
                    for key, value in args_dic.items(): #Es mucho muy importante que se setee primero el canal
                        if key.lower() in ["canal","ch","channel"]:
                            instru.setPressChannel(channel=value)
                    instru.setPressPressure(pressure=presion)
                if key.lower() in ["wave","señal","onda","tipo"]:
                    señal=value #Porq sino se sobre escribe
                    for key, value in args_dic.items(): #Es mucho muy importante que se setee primero el canal
                        if key.lower() in ["canal","ch","channel"]:
                            instru.setPressChannel(channel=value)
                    instru.setPressWave(wave=señal)

        elif args_dic["run"].lower() =="pni": #PNI
            for key, value in args_dic.items():
                if key.lower() in ["zero","zeropress","zpress","cero"]:
                    instru.ZPRESS()
                elif key.lower() in ["vol","volumen","v"]:
                    instru.NIBPVOLUME(volume=value)
                elif key.lower() in ["envolvente","envelope","e"]:
                    instru.NIBPENVELOPE(shift=value)
            instru.NIBP(at=True)
    except:
        return "-110"

def DRIVER(cmd:str):
    """
    Funcion mas general. Se encarga de recibir el comando y luego valuarlo segun sea el tipo de instrumento

    :param cmd: Comando que recibe desde el SMVA2 este tiene que tener la estructura instrumento --run accion --parametros. accion es cualquier cosa que se quiera ejecutar; por ejemplo
    medicion de resistencia con multimetro multimetro --run resistance
    :return: El resultado de la medicion, o un OK en caso que sea de configuracion
    """
    controlador_especifico = { #Simulador de switch case
        "multimetro":multimetro,
        "Multimetro":multimetro,
        "mul":multimetro,
        "PSU":psu,
        "psu":psu,
        "array":psu,
        "impulse":impulse,
        "IMPULSE":impulse,
        "IMPULSE7000":impulse,
        "impulse7000":impulse,
        "ESA620":esa620,
        "ESA":esa620,
        "osc":osciloscopio,
        "osciloscopio":osciloscopio,
        "tektronix":osciloscopio,
        "OSC":osciloscopio,
        "PS8":prosim8,
        "prosim":prosim8,
        "PROSIM":prosim8,
        "prosim8":prosim8,
        "GuiaPresion":guiaPresion,
        "GuiaDePresion":guiaPresion
    }
    CMD = cmd.split(sep=" --")
    """
    ESA620 --run leaktest --lead 5 --pol N --neutro O
    [ESA620, run leaktest, lead 5, pol N, neutro O]
    """

    instr = CMD[0]
    r = controlador_especifico[instr](CMD[1:]) #No se envia el tipo de instrumento ya que no cumpliria ninguna funcion


    return str(r)


if __name__ == "__main__":
    N = 50
    #Probar todas las caracteristicas de ECG// frec: frecuencia //amp: amplitud //artifact: artefacto //asize: artifact size
    #-print(DRIVER(cmd = "PS8 --run ECG --frec 200 --amp 1.0 --artifact musc --asize 200"))
    #Probar todas las caracteristicas de Spo2// frec: frecuencia //sat: saturacion //perf: perfusion //sensor: sensor
    #-DRIVER(cmd = "PS8 --run SPO2 --frec 80 --sat 99 --perf 1.00 --sensor BCI")
    #Probar todas las caracteristicas de cuadrada// frec: frecuencia
    #-DRIVER(cmd = "PS8 --run cuadrada --frec 1.5")
    #Probar todas las caracteristicas de trianguluar// frec: frecuencia
    #-DRIVER(cmd = "PS8 --run tri --frec 2")

    DRIVER(cmd = "PS8 --run seno --frec 1")

    #print(DRIVER("osc --vscale 2 --vpos 0 --run medicion --pos 1"))
    
    


