# styles.py (opcional para mantener limpio el código)
LIGHT_STYLE = """
QWidget {
    background-color: #fafafa;
    color: #000000;
}
QPushButton {
    background-color: #e4e5f1;
    border: 1px solid #484b6a;
    font: 75 12pt "MS Shell Dlg 2";
}
QPushButton:hover {
    background-color: #d2d3db;
    border: 1px solid #484b6a; /* Accent al pasar el mouse */
    color: #fafafa;
    font: 75 12pt "MS Shell Dlg 2";
}
QPushButton:pressed {
    background-color: #484b6a;
    border: 1px solid #fafafa;
    font: 75 12pt "MS Shell Dlg 2";
}

QComboBox {
    background-color: #e4e5f1;
    font: 75 12pt "MS Shell Dlg 2";
    color: #484b6a;
}
/* entrada texto */
QTextEdit {
    background-color: #e4e5f1;
    font: 75 12pt "MS Shell Dlg 2";
    color: #484b6a;
}
QLineEdit {
    background-color: #e4e5f1;
    font: 75 12pt "MS Shell Dlg 2";
    color: #484b6a;
}
/* tablas */
QTableWidget {
    background-color: #fafafa;
    color: #484b6a;
    gridline-color: #484b6a;
    font: 75 12pt "MS Shell Dlg 2";
    selection-background-color: #e4e5f1;
    selection-color: #e4e5f1;
    alternate-background-color: #3a3a3a;
}
QHeaderView::section {
    background-color: #e4e5f1;
    color: #484b6a;
    padding: 4px;
    border: 1px solid #fafafa;
    font-weight: bold;
}
QTableWidget::item:selected {
    background-color: #e4e5f1;  /* color de fondo al seleccionar */
    color: #000000;             /* texto al seleccionar */
}

/* Scrollbar Vertical */
QScrollBar:vertical {
    background: #d2d3db;
    width: 12px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #9394a5;
    min-height: 20px;
    border-radius: 6px;
}

QScrollBar::handle:vertical:hover {
    background: #484b6a;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    background: none;
    height: 0px;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: none;
}

/* Scrollbar Horizontal */
QScrollBar:horizontal {
    background: #d2d3db;
    height: 12px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: #9394a5;
    min-width: 20px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal:hover {
    background: #484b6a;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    background: none;
    width: 0px;
}

QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    background: none;
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
QLineEdit {
    background-color: #444444;
    font: 75 12pt "MS Shell Dlg 2";
    color: #E0E0E0;
}
QTableWidget {
    background-color: #444444;
    color: #E0E0E0;
    gridline-color: #666666;
    font: 75 12pt "MS Shell Dlg 2";
    selection-background-color: #666666;
    selection-color: #ffffff;
    alternate-background-color: #3a3a3a;
}
QHeaderView::section {
    background-color: #2b2b2b;
    color: #E0E0E0;
    padding: 4px;
    border: 1px solid #444444;
    font-weight: bold;
}
QTableWidget::item:selected {
    background-color: #888888;  /* color de fondo al seleccionar */
    color: #000000;             /* texto al seleccionar */
}

/* Scrollbar Vertical */
QScrollBar:vertical {
    background: #2b2b2b;
    width: 12px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #5c5c5c;
    min-height: 20px;
    border-radius: 6px;
}

QScrollBar::handle:vertical:hover {
    background: #888888;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    background: none;
    height: 0px;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: none;
}


/* Scrollbar Horizontal */
QScrollBar:horizontal {
    background: #2b2b2b;
    height: 12px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: #5c5c5c;
    min-width: 20px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal:hover {
    background: #888888;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    background: none;
    width: 0px;
}

QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    background: none;
}
"""
