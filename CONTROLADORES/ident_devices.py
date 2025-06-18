from serial.tools import list_ports
import serial, os, json, sys
from CONTROLADORES.DCPOWERSUPPLY import PSU

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JSON_FILE_PATH = os.path.join(BASE_DIR, "_TEMPS_\devices.json")

def ident_devices(debug=False,JSON_FILE=JSON_FILE_PATH):
    used_ports = list_ports.comports()
    rta_1 = ""
    rta_2 = ""
    rta_3 = ""
    
    if debug:
        print("\nPuertos encontrados:")
        for p in used_ports:
            print(p.description)

    found_devices = {}

    for port in used_ports:
        baudrates = (9600, 38400, 115200)


        for baudrate in baudrates:
            respuesta = ""
            try:
                connection = serial.Serial(
                    port=port.device,
                    baudrate=baudrate,
                    parity="N",
                    stopbits=1,
                    bytesize=8,
                    timeout=0.1,
                    write_timeout=0.1)

                # Intento identificar ESA620
                connection.write("REMOTE\r".encode())
                connection.readline().decode()
                connection.write("IDENT\r".encode())
                rta_1 = connection.readline().decode()
                if "ESA 620" in rta_1:
                    respuesta = rta_1

                # Intento identificar Fluke8845A y Fluke45
                connection.write("*IDN?\r\n".encode())
                rta_2 = connection.readline().decode()
                if "8845A" in rta_2:
                    respuesta = rta_2
                if "45" in rta_2 and "88" not in rta_2:
                    respuesta = rta_2

                # Intento identificar Fuente Array/Protek


                if debug:
                    print(f"Respuesta de {port.device} a {baudrate} baudios: {respuesta}")

                if not respuesta == "":
                    if "ESA 620" in respuesta:
                        device = "ESA620"
                    elif "8845A" in respuesta:
                        device = "8845A"
                    elif "45" in respuesta and "88" not in respuesta:
                        device = "45"
                    else:
                        device = "Desconocido"

                    device_info = {
                                    "port":port.device,
                                    "baudrate":baudrate,
                                    "id":1
                                }
                    
                    found_devices[device]=device_info

                if connection and connection.is_open:
                    connection.close()

            except serial.SerialException as e:
                print(f"Error de conexión: {e}")
                pass

    if found_devices:
        try:
            with open(JSON_FILE, "w") as file:
                json.dump(found_devices, file, indent=4)
        except IOError as e:
            print(f"Error al escribir el archivo JSON: {e}")

def verify_connection(key, instrument, device_pool):
    if instrument and device_pool != None:
        with open (JSON_FILE_PATH,"r") as file:
            data = json.load(file)
        if key in data.keys():
            instru = instrument(port=data[key]["port"])
            device_pool["ESA620"] = instru
        else:
            raise Exception(f"No se encuentra el instrumento {key}")
    return instru


if __name__ == "__main__":
    ident_devices(debug=True, JSON_FILE=JSON_FILE_PATH)