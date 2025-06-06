from PyQt5.QtWidgets import QVBoxLayout
from CONTROLADORES.DASHWORKER import DashboardWorker
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from collections import Counter
import numpy as np
from datetime import datetime
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
    win.listWidget_Equipos.addItems(win._dic_equipos.keys()) #SE CARGAN LOS EQUIPOS A LA QListWidget
    win.EQUIPO_DASH = "" #CONTROLA EL DICT DEL EQUIPO QUE SE SELECCIONA, POR EJEMPLO SI SE SELECCIONA DESFIBRILADOR 3850; esta variable almacena dinamicamente {PLACA MADRE :208, PLACA FRONTAL:209,.....}
    win.VERSION_DASH = "" #ALMACENA LA VERSION SELECCIONADA
    win.TIPO_DASH = "PPM" #ALMACENA EL TIPO DE PROTOCOLO
    win.NOMBRE_EQUIPO_DASH = "" #GUARDA EL NOMBRE DEL EQUIPO (EN ESTE CASO SI SE SELECCIONA DESFIBRILADOR 3850, guarda DESFIBRILADOR 3850)
    win.PLACA_DASH = "" #GUARDA EL NP DE LA PLACA
    win.OPERADOR_DASH = [] #GUARDA LOS OPERADORES DE MANERA DINAMICA
    win.TIEMPO_DASH=[] #GUARDA EL TIEMPO DE MANERA DINAMICA
    win.RESULTADO_DASH = { #GUARDA LOS RESULTADOS TOTALES
        "PASA":0,
        "NO PASA":0,
        "INCOMPLETO":0
    }
    ####SE ELIMINA EL FONDO DE LAS IMAGENES INCRUSTADAS
    win.imagen1.setStyleSheet("background: transparent")
    win.imagen1.setAutoFillBackground(False)
    win.imagen2.setStyleSheet("background: transparent")
    win.imagen2.setAutoFillBackground(False)
    win.imagen3.setStyleSheet("background: transparent")
    win.imagen3.setAutoFillBackground(False)
    win.imagen4.setStyleSheet("background: transparent")
    win.imagen4.setAutoFillBackground(False)

    #CONFIGURACION DE BOTONES
    win.listWidget_Equipos.currentTextChanged.connect(lambda nombre_equipo: actualizar_partes(win, nombre_equipo))
    win.listWidget_Partes.currentTextChanged.connect(lambda parte: actualizar_version(win, parte))
    win.listWidget_Tipos.currentTextChanged.connect(lambda tipo: actualizar_tipo(win, tipo))
    win.listWidget_Version.currentTextChanged.connect(lambda version: set_version(win, version))
    win.DASHBOARD_btn.clicked.connect(lambda: actualizar_dashboard(win))
    win.TO_MAIN_btn.clicked.connect(lambda: back_to_main(win))
    win.NEXT_PAGE_btn.clicked.connect(lambda: next_page(win))

    ###CONFIGURACION FUNCIONES APARTE
    win.mostrar_grafico_en_widget = lambda widget, figura: mostrar_grafico_en_widget(widget, figura)
def actualizar_partes(win, nombre_equipo):
    win.listWidget_Version.clear()
    win.listWidget_Partes.clear()
    win.NOMBRE_EQUIPO_DASH = nombre_equipo
    try:
        partes = win._dic_equipos.get(nombre_equipo, {})
        win.listWidget_Partes.addItems(partes.keys())
        win.EQUIPO_DASH = win._dic_equipos.get(nombre_equipo, {})
    except:
        pass


def actualizar_version(win,parte):
    win.listWidget_Version.clear() #Limpio la cantidad 
    try:
        win.PLACA_DASH = win.EQUIPO_DASH[parte]
    except:
        pass
    #print(self.PLACA)
    if win.PLACA_DASH!="PSA":
        query_version = f"""SELECT distinct Version FROM {win.database._DATABASE}.protocolos where name like '%{win.PLACA_DASH}%' and Tipo like '%{win.TIPO_DASH}%'"""
        win.cursor.execute(query_version)
        version = win.cursor.fetchall()
        version = [ver[0] for ver in version]
        win.listWidget_Version.addItems(version)
    else:
        dic_ = {
            "DESFIBRILADOR 3850":"DEFI3850",
            "MONITOR PM9000":"PM9000",
            "MULTIPAR":"MULTIPAR"
        }
        query_version = f"""SELECT distinct Version FROM {win.database._DATABASE}.protocolos where name like '%{dic_[win.NOMBRE_EQUIPO_DASH]}%' and Tipo ='PSA'"""
        win.cursor.execute(query_version)
        version = win.cursor.fetchall()
        version = [ver[0] for ver in version]
        win.listWidget_Version.addItems(version)

def actualizar_tipo(win,tipo):
    win.listWidget_Version.clear() #Limpio la cantidad 
    win.TIPO_DASH = tipo
    if win.PLACA_DASH!="PSA":
        query_version = f"""SELECT distinct Version FROM {win.database._DATABASE}.protocolos where name like '%{win.PLACA_DASH}%' and Tipo like '%{win.TIPO_DASH}%'"""
        win.cursor.execute(query_version)
        version = win.cursor.fetchall()
        version = [ver[0] for ver in version]
        win.listWidget_Version.addItems(version)

def set_version(win,version):
    try:
        win.VERSION_DASH=version
    except:
        win.listWidget_Version.clear() #Limpio la cantidad 


def actualizar_dashboard(win):
    try:
        win.OPERADOR_DASH = [] #Los reinicio
        win.TIEMPO_DASH=[]#Los reinicio
        win.RESULTADO_DASH = {#Los reinicio
            "PASA":0,
            "NO PASA":0,
            "INCOMPLETO":0
        }
        win.worker_dash = DashboardWorker(win,win.cursor, win.database._DATABASE, win.PLACA_DASH, win.VERSION_DASH,win.NOMBRE_EQUIPO_DASH,win.TIPO_DASH)
        win.worker_dash.finished.connect(
                                        lambda estado_win, tiempo, operadores, resultado, resultados_hoy:
                                        cuando_termina_dashboard(estado_win, tiempo, operadores, resultado, resultados_hoy)
                                        )
        win.worker_dash.start()
    except:
        pass

def cuando_termina_dashboard(win,tiempo,operadores,resultado,resultados_hoy):
    win = win
    win.TIEMPO_DASH = tiempo
    win.OPERADOR_DASH = operadores
    win.RESULTADO_DASH = resultado

    try:
        fig1 = Figure(figsize=(4, 3))
        fig1.patch.set_alpha(0)
        ax1 = fig1.add_subplot(111)
        ax1.set_facecolor('none')  # Fondo del área del gráfico transparente
        tiempo_array = np.array(win.TIEMPO_DASH)
        q_low, q_high = np.percentile(tiempo_array, [5, 95])  # o [1, 99]
        tiempo_filtrado = tiempo_array[(tiempo_array >= q_low) & (tiempo_array <= q_high)]
        ax1.hist(tiempo_filtrado, bins=7, color='skyblue', edgecolor='black')
        ax1.set_title("Histograma duracion protocolo (h)")
        ax1.set_xlabel("Duración (horas)")
        ax1.set_ylabel("Cantidad")
        ax1.grid(True)
        fig1.tight_layout()
        win.mostrar_grafico_en_widget(win.imagen1, fig1)
    except Exception as e:
        print(f"Hubo un error en {e}")
    # --- Diagrama de barra por operador ---
    operador_count = Counter(win.OPERADOR_DASH)
    fig2 = Figure(figsize=(4, 3))
    fig2.patch.set_alpha(0)
    ax2 = fig2.add_subplot(111)
    ax2.set_facecolor('none')  # Fondo del área del gráfico transparente
    ax2.bar(operador_count.keys(), operador_count.values(), color='orange', edgecolor='black')
    ax2.set_title("Cantidad totales por Operador protocolos seleccionado")
    ax2.set_xlabel("Operador")
    ax2.set_ylabel("Cantidad")
    ax2.set_xticklabels(operador_count.keys(), rotation=45, ha='right')
    ax2.grid(axis='y')
    fig2.tight_layout()
    win.mostrar_grafico_en_widget(win.imagen2, fig2)

    # --- Diagrama de barra de resultados ---
    labels = list(win.RESULTADO_DASH.keys())
    counts = list(win.RESULTADO_DASH.values())

    fig3 = Figure(figsize=(4, 3))
    fig3.patch.set_facecolor('none')  # O 'white'
    ax3 = fig3.add_subplot(111)
    ax3.set_facecolor('none')  # Fondo del área del gráfico transparente
    ax3.bar(labels, counts, color=['green', 'red', 'orange'])
    ax3.set_title("Resultados totales de Protocolos seleccionado")
    ax3.set_xlabel("Resultado")
    ax3.set_ylabel("Cantidad")
    ax3.grid(axis='y', linestyle='--', alpha=0.6)
    fig3.tight_layout()
    win.mostrar_grafico_en_widget(win.imagen3, fig3)

    ###fig4
    fig4 = Figure(figsize=(4, 3))
    fig4.patch.set_facecolor('none')  # O 'white'
    ax4 = fig4.add_subplot(111)
    ax4.set_facecolor('none')  # Fondo del área del gráfico transparente
    hoy = datetime.today()
    hoy_formateado = hoy.strftime("%Y-%m-%d")  # Esto es un string
    win.PASAN_TEXT.setText(str(resultados_hoy["PASA"]))
    win.NOPASAN_TEXT.setText(str(resultados_hoy["NO PASA"]))
    win.INCOMPLETO_TEXT.setText(str(resultados_hoy["INCOMPLETO"]))
    win.FECHA_TEXT.setText(hoy_formateado)
    labels = list(resultados_hoy.keys())
    values = list(resultados_hoy.values())
    colors = ['green', 'red', 'orange']

    ax4.pie(
        values,
        labels=labels,
        autopct='%1.1f%%',
        colors=colors,
        startangle=140
    )
    ax4.set_title(f"Resultados de hoy {hoy_formateado}")
    ax4.axis('equal')  # Para que sea un círculo
    fig4.tight_layout()
    win.mostrar_grafico_en_widget(win.imagen4, fig4)

def mostrar_grafico_en_widget(widget, figura: Figure):
    # Eliminar cualquier gráfico anterior
    for i in reversed(range(widget.layout().count())):
        widget.layout().itemAt(i).widget().setParent(None)

    canvas = FigureCanvas(figura)
    widget.layout().addWidget(canvas)
    canvas.draw()

def back_to_main(win):
    """
    Devuelve a la pagina principal
    """
    win.stacks.setCurrentWidget(win.main)

def next_page(win):
    """
    En caso que querramos agregar mas info
    """
    print("En desarrollo")