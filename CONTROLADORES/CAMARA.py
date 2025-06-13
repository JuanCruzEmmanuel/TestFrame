"""
DRIVER QUE CONTROLA FUNCIONES RELACIONADAS A LA CAMARA;
Se debera evaluar si lo correcta es que esta siempre este en su propio hilo
  ____  ____  _____     _______ ____     ____    _    __  __    _    ____      _    
 |  _ \|  _ \|_ _\ \   / / ____|  _ \   / ___|  / \  |  \/  |  / \  |  _ \    / \   
 | | | | |_) || | \ \ / /|  _| | |_) | | |     / _ \ | |\/| | / _ \ | |_) |  / _ \  
 | |_| |  _ < | |  \ V / | |___|  _ <  | |___ / ___ \| |  | |/ ___ \|  _ <  / ___ \ 
 |____/|_| \_\___|  \_/  |_____|_| \_\  \____/_/   \_\_|  |_/_/   \_\_| \_\/_/   \_\
                                                                                    
"""

###IMPORTs
import cv2
from time import sleep
import threading

#INFORMACION CONTACTO
__version__ = "1.0.0"
__author__ = "Juan Cruz Noya"
__company__ = "Feas Electronica S.A"
__year__ = "2025"
class CAMARA:
    """
    Se crea la clase *CAMARA*
    """
    def __init__(self,camera=0):
        self._camera = camera
        self._cap = cv2.VideoCapture(self._camera)
        self._backup_name = ""
        self._FRONT_PANEL = False
        self.ret=None
        self.frame = None
    def connect(self,camera=0):
        """
        Metodo que se utiliza para conectar la camara
        """
        self._cap = cv2.VideoCapture(camera)
    def set_backup_name(self,backup_name):
        """
        Metodo que se encarga de agregar un nombre propio a lo que se va a guardar
        """
        self._backup_name = backup_name
    
    def show_front_panel(self):
        """
        Se encarga de abrir el monitor remoto en tiempo real.
        """
        self._FRONT_PANEL = True
        while True:
            self.ret, self.frame = self._cap.read()
            if not self.ret:
                print("Error al capturar frame")
                break

            cv2.imshow("Live Camera", self.frame)
            key = cv2.waitKey(1) & 0xFF

            # Presionar 'q' para salir del panel frontal
            if key == ord('q'):
                break
        cv2.destroyWindow("Live Camera")

    def SNAP(self,debug=False,backup = False):
        """
        Metodo que se encarga de la toma de imagenes
        """
        if not self._FRONT_PANEL:
            self.ret, self.frame = self._cap.read() #Se inicia la lectura de la camara
            sleep(0.2)
            if not self.ret:
                raise Exception("Error al utilizar la camara")

        img_name = "SNAP.jpeg"
        cv2.imwrite(img_name, self.frame)
        if backup:
            print("Desarrollar metodo para guardar en el backup")
        if debug:
            if not self._FRONT_PANEL:
                cv2.imshow("captura", self.frame) #Muestro la foto tomada
                cv2.waitKey(1000)  # Show for 1 second

        if not self._FRONT_PANEL:
            cv2.destroyAllWindows()

    def close(self):
        self._cap.release() #Cierro el opturador
if __name__ == "__main__":
    camara = CAMARA(camera=0)
    
    # Lanzar el panel frontal en un hilo separado
    front_thread = threading.Thread(target=camara.show_front_panel, daemon=True)
    front_thread.start()
    
    s = "n"
    while s != "s":
        accion = input("Que accion desea realizar: ")
        if accion == "snap":
            camara.SNAP()
        else:
            print("No se reconoce accion")
        s = input("Desea salir s/n: ")
    
    camara.close()