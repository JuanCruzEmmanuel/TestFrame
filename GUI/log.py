from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
import json
import sys
import pyodbc

class LogWindow(QMainWindow):
    login_successful = pyqtSignal()  # Señal personalizada
    def __init__(self,database=None):
        super().__init__()
        self.BD = database
        self.datos = self.check()
        uic.loadUi('GUI/login.ui', self)  # Carga el archivo log.ui
        self.logButton.clicked.connect(self.login)  # Conectar el botón
        
        self.intentos = 4
        
        
        
    def login(self,debug =False):
        User = self.User.text()  # Se lee el usuario
        self.BD.setUser(usuario = User)
        Pass = self.Pass.text() #Se lee la constraseña
        if Pass[0] =="*":
            if Pass[-1]=="*":
                self.BD.set_test() #Agrego modo test
                Pass = Pass[1:-1]
            else:
                pass
        else:
            pass
        try:
            if debug:
                if self.datos[User]["password"] == Pass:
                    self.login_successful.emit()  # Emitir señal
                    print("Se ha ingresado correctamente")
                else:
                    print("Error contraseña")
            else:
                if self.datos[User][2] == Pass: #En caso que estemos usando la BD debemos convertir a los datos que esta trabaja, ya que me devuelve una lista con tuplas
                    self.login_successful.emit()  # Emitir señal
                    print("Se ha ingresado correctamente")
                else:
                    print("Error contraseña")                

        except:
            print("ERROR EN CONTRASEÑA O USUARIO")
            self.intentos -=1
            if self.intentos == 0:
                self.close()

    def check(self,debug=False):
        if debug == True:
            with open("GUI/user.json", "r",encoding="utf-8") as file:
                data = json.load(file)
            
            user_dic  ={user["username"]: user for user in data} #Convierto el json de la bbdd en un diccionario de acceso rapido
            
            return user_dic   
        else:
            data = self.BD.userQuery()  
            user_dic  ={user[0]: user for user in data}
            return user_dic

if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = LogWindow()
    window.show()
    sys.exit(app.exec_())
