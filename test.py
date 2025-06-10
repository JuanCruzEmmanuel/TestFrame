from serial.tools import list_ports
import serial, os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JSON_FILE = os.path.join(BASE_DIR, "devices.json")

def ident_devices():
    used_ports = list_ports.comports()

    for port in used_ports:
        baudrates = (9600, 38400, 115200)

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

                
                if connection and connection.is_open:
                    connection.close()

                print(f"Respuesta de el puerto {port.device} a {baudrate} baudios: {respuesta}")

            except serial.SerialException as e:
                print("Conexion fallida con {} a {} baudios".format(port.device,baudrate))



ident_devices()