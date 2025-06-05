
from PyQt5.QtWidgets import QVBoxLayout
from CONTROLADORES.DASHWORKER import DashboardWorker
def configurar_logica_dashboard2(win):
    """
    Configura toda la logica del dashboard que se calcula mediante botones\n
    :param:
    **win**: es equivalente al *self* de los objetos; represetanta el puntero al self
    """
    ####CONFIGURACION DEL ENTORNO########
    for widget in [win.imagen1, win.imagen2, win.imagen3,win.imagen4]: #Funcion que le agrega layout para muestrear luego los dashes
        layout = QVBoxLayout()
        widget.setLayout(layout)
        win.cursor = win.database.get_cursor() #Le solicito a la base de datos el cursor ----> puntero que direcciona a la base de datos

        win._dic_equipos = { #Lista de equipos con su respectivo NP
                "DESFIBRILADOR 3850":{
                    "PLACA MADRE":"208",
                    "PLACA FRONTAL":"209",
                    "PLACA DE ALTA BIFASICA":"210",
                    "PLACA DE ALTA MONOFASICA":"180",
                    "PSA":"PSA"
                },
                "MONITOR PM9000":{"PSA":"PSA",
                                  "PLACA MADRE":"299",
                                  "ADQUISICION": "339",
                                  "PROTECCION": "342"},
                "MULTIPAR":{"PSA":"PSA"}
            }
        win.EQUIPO_DASH = "" #CONTROLA EL DICT DEL EQUIPO QUE SE SELECCIONA, POR EJEMPLO SI SE SELECCIONA DESFIBRILADOR 3850; esta variable almacena dinamicamente {PLACA MADRE :208, PLACA FRONTAL:209,.....}
        win.VERSION_DASH = "" #ALMACENA LA VERSION SELECCIONADA
        win.TIPO_DASH = "PPM" #ALMACENA EL TIPO DE PROTOCOLO
        win.NOMBRE_EQUIPO_DASH = "" #GUARDA EL NOMBRE DEL EQUIPO (EN ESTE CASO SI SE SELECCIONA DESFIBRILADOR 3850, guarda DESFIBRILADOR 3850)
        win.PLACA_DASH = "" #GUARDA EL NP DE LA PLACA
