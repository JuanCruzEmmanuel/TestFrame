from abc import ABC, abstractmethod

"""

Para que el codigo que se realice sea mas elegante y formal se deben usar herencias y contratos. Esto nos asegura de que todos los instrumentos sigan estructuras similares
y que no se realice cualquier cosa. En este caso, voy a crear 4 basicos que es conexion, desconexion, leer y escribir. Si el instrumento herada esta clase, y es un contrato formal
(ABC) abstract Base Class, es obligacion que la clase hija, contenga las misma como minimo


"""

class instru_contract(ABC):
    @abstractmethod
    def connect(self):
        pass
    @abstractmethod
    def disconnect(self):
        pass
    @abstractmethod
    def readcommand(self):
        pass
    @abstractmethod
    def writecommand(self):
        pass