from serial.tools import list_ports
import serial, os, json


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
print(BASE_DIR)
JSON_FILE = os.path.join(BASE_DIR, "_TEMPS_\devices.json")
print(JSON_FILE)

def ident_devices():
    used_ports = list_ports.comports()

    if os.path.exists(JSON_FILE):
        return

    for port in used_ports:
        baudrates = (9600, 38400, 115200)
        found_devices = []

        for baudrate in baudrates:
            try:

                connection = serial.Serial(
                    port=port.device,
                    baudrate=baudrate,
                    parity="N",
                    stopbits=1,
                    bytesize=8,
                    timeout=0.1,
                    write_timeout=0.1)
                
                connection.write("REMOTE\r".encode())
                connection.readline().decode()
                connection.write("IDENT\r".encode())
                respuesta = connection.readline().decode()

                if not respuesta == "":
                    device_info = {
                        "port": port.device,
                        "device": respuesta
                        }
                    found_devices.append(device_info)

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






ident_devices()