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
from CONTROLADORES.styles import LIGHT_STYLE, DARK_STYLE,PURPLE_MODE,ORANGE_BLUE_MODE  # Si lo pones en un archivo externo
from CONTROLADORES.CONVERT_EXCEL_TO_SMVA import excel_to_smva, load_smva_file
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
                elif "serial" in cmd:
                    self.win.stacks.setCurrentWidget(self.win.asoconfig)
                    self.win.command_box.setText(f"Desplazado a configuracion")
            elif "debug" in CMD.lower():
                if "theme" in CMD.lower():
                    if "light" in CMD.lower():
                        self.win.setStyleSheet(LIGHT_STYLE)
                    elif "dark" in CMD.lower():
                        self.win.setStyleSheet(DARK_STYLE)
                    elif "purple" in CMD.lower():
                        self.win.setStyleSheet(PURPLE_MODE)
                    elif "orange" in CMD.lower():
                        self.win.setStyleSheet(ORANGE_BLUE_MODE)
            elif "dash" in CMD.lower():
                self.win.stacks.setCurrentWidget(self.win.dashboard)
            elif "convert" in CMD.lower() or "save" in CMD.lower(): #--convert smva path
                if "smva" in CMD.lower():
                    path = CMD.split(" ")[-1]
                    try:
                        excel_to_smva(PATH=path)
                        self.win.command_box.setText(f"Convertido en .SMVA")
                    except:
                        self.win.command_box.setText(f"Existio un problema al convertir en .SMVA")
            elif "load" in CMD.lower(): #--load smva path
                if "smva" in CMD.lower():
                    path = CMD.split(",")[-1]
                    path =rf"{path}"
                    load_smva_file(PATH=path, basedato=self.win.database)
                    
                    self.win.cargarDatos()
                    self.win.stacks.setCurrentWidget(self.win.run_protocolo)
                    self.win.iniciarEjecucion() #Para incializar la ejecucion(el worker)
                    self.win.worker.setsmvafile()#Para iniciar la variable en True C:\Users\juanc\Desktop\SISTEMA MEDICIONES\_TEMPS_\test_archivo_smva3.SMVA
            else:
                self.win.command_box.setText(f"No se pudo decodificar el comando: {CMD}")
        except Exception as e:
            self.win.command_box.setText(f"Hubo un error en el comando: {CMD} debido a {e}")