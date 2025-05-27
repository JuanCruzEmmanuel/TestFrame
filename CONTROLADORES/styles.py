# styles.py (opcional para mantener limpio el código)
LIGHT_STYLE = """
QWidget {
    background-color: #ffffff;
    color: #000000;
}
QPushButton {
    background-color: #f0f0f0;
    border: 1px solid #cccccc;
    font: 75 12pt "MS Shell Dlg 2";
}
QPushButton:pressed {
    background-color: #e9e9e9;
    border: 1px solid #444444;
    font: 75 12pt "MS Shell Dlg 2";
}
QComboBox {
    background-color: rgb(255, 255, 255);
    font: 75 12pt "MS Shell Dlg 2";
}
QFrame {
    background-color: rgb(238, 238, 238);
}
QTextEdit {
    background-color: rgb(238, 238, 238);
    font: 75 12pt "MS Shell Dlg 2";
    color: rgb(50, 50, 50);
}
"""

DARK_STYLE = """

QWidget {
    background-color: #121212;
    color: #ffffff;
}
QPushButton {
    background-color: #444444;
    border: 1px solid #5c5c5c;
    color: #E0E0E0;
    font: 75 12pt "MS Shell Dlg 2";
}
QPushButton:pressed {
    background-color: #888888;
    border: 1px solid #444444;
    color: #E0E0E0;
    font: 75 12pt "MS Shell Dlg 2";
}
QPushButton:hover {
    background-color: #333333;
    border: 1px solid #888888; /* Accent al pasar el mouse */
    color: #E0E0E0;
    font: 75 12pt "MS Shell Dlg 2";
}
QComboBox {
    background-color: #444444;
    font: 75 12pt "MS Shell Dlg 2";
    color: #E0E0E0;
}
QTextEdit {
    background-color: #444444;
    font: 75 12pt "MS Shell Dlg 2";
    color: #E0E0E0;
}
QTableWidget {
    background-color: #444444;
    font: 75 12pt "MS Shell Dlg 2";
    color: #E0E0E0;
}
"""
