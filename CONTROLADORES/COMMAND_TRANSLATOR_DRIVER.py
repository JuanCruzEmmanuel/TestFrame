"""

   ____ ___  __  __ __  __    _    _   _ ____    _____ ____      _    _   _ ____  _        _  _____ ___  ____  
  / ___/ _ \|  \/  |  \/  |  / \  | \ | |  _ \  |_   _|  _ \    / \  | \ | / ___|| |      / \|_   _/ _ \|  _ \ 
 | |  | | | | |\/| | |\/| | / _ \ |  \| | | | |   | | | |_) |  / _ \ |  \| \___ \| |     / _ \ | || | | | |_) |
 | |__| |_| | |  | | |  | |/ ___ \| |\  | |_| |   | | |  _ <  / ___ \| |\  |___) | |___ / ___ \| || |_| |  _ < 
  \____\___/|_|  |_|_|  |_/_/   \_\_| \_|____/    |_| |_| \_\/_/   \_\_| \_|____/|_____/_/   \_\_| \___/|_| \_\
                                                                                                               
"""
"""
Scripts que cumple la funcion de lectura de los comandos en smva3
"""
######IMPORTS DRIVERS
from CONTROLADORES.driver import DRIVER
from CONTROLADORES.ReleDriver import TorreRele

class COMMAND_TRANSLATOR:
    def __init__(self,win):
        """
        Con el fin de que tenga a su vez control sobre las ventanas, es encesario darle el estado actual de la aplicacion
        """
        self.win = win #Esto funcionara en caso que quiera modificar la ventana actual y esas cosas por el estilo

    def translate(self,CMD):
        try:
            if "*" in CMD:
                cmd = CMD.split("*")[1]
                rt = DRIVER(cmd=cmd) #Con esto controlaria los driver desde cualquier punto

                self.win.command_box.setText(rt)
            elif "TOR" in CMD:
                torre = TorreRele()
                torre.readComando(CMD=CMD.split("TOR")[1])
                self.win.command_box.setText("OK")
            elif "mov" in CMD.lower():
                cmd = CMD.split("->")[1]
                if "run_protocolo" in cmd:
                    self.win.stacks.setCurrentWidget(self.win.run_protocolo)
                    self.win.command_box.setText(f"Desplazado a run protocolo")
            else:
                self.win.command_box.setText(f"No se pudo decodificar el comando: {CMD}")
        except:
            self.win.command_box.setText(f"Hubo un error en el comando: {CMD}")