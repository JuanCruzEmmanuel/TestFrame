from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

def configurar_logica_dashboard(win):
        """
        CONFIGURAR el tablero hay que ver si dejarlo local o web
        """
        win.web_view = QWebEngineView()
        win.web_view.load(QUrl("http://localhost:8050"))  # tu dashboard en Dash, Flask, etc.
        win.dash_layout.addWidget(win.web_view)