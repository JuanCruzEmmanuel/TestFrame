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
PURPLE_MODE = """
QWidget {
    background-color: #0E2148;
    color: #E3D095;
}
QPushButton {
    background-color: #483AA0;
    border: 1px solid #7965C1;
    color: #E3D095;
    font: 75 12pt "MS Shell Dlg 2";
}
QPushButton:pressed {
    background-color: #7965C1;
    border: 1px solid #483AA0;
    color: #0E2148;
    font: 75 12pt "MS Shell Dlg 2";
}
QPushButton:hover {
    background-color: #E3D095;
    border: 1px solid #7965C1;
    color: #0E2148;
    font: 75 12pt "MS Shell Dlg 2";
}
QComboBox {
    background-color: #483AA0;
    font: 75 12pt "MS Shell Dlg 2";
    color: #E3D095;
}
QTextEdit {
    background-color: #483AA0;
    font: 75 12pt "MS Shell Dlg 2";
    color: #E3D095;
}
QLineEdit {
    background-color: #483AA0;
    font: 75 12pt "MS Shell Dlg 2";
    color: #E3D095;
}
QTableWidget {
    background-color: #483AA0;
    color: #E3D095;
    gridline-color: #7965C1;
    font: 75 12pt "MS Shell Dlg 2";
    selection-background-color: #7965C1;
    selection-color: #0E2148;
    alternate-background-color: #3a3a3a;
}
QHeaderView::section {
    background-color: #0E2148;
    color: #E3D095;
    padding: 4px;
    border: 1px solid #7965C1;
    font-weight: bold;
}
QTableWidget::item:selected {
    background-color: #E3D095;
    color: #0E2148;
}

/* Scrollbar Vertical */
QScrollBar:vertical {
    background: #0E2148;
    width: 12px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #7965C1;
    min-height: 20px;
    border-radius: 6px;
}
QScrollBar::handle:vertical:hover {
    background: #E3D095;
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
    background: #0E2148;
    height: 12px;
    margin: 0px;
}
QScrollBar::handle:horizontal {
    background: #7965C1;
    min-width: 20px;
    border-radius: 6px;
}
QScrollBar::handle:horizontal:hover {
    background: #E3D095;
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
ORANGE_BLUE_MODE = """
QWidget {
    background-color: #000000;
    color: #FE7743;
}
QPushButton {
    background-color: #273F4F;
    border: 1px solid #EFEEEA;
    color: #FE7743;
    font: 75 12pt "MS Shell Dlg 2";
}
QPushButton:pressed {
    background-color: #FE7743;
    border: 1px solid #EFEEEA;
    color: #000000;
    font: 75 12pt "MS Shell Dlg 2";
}
QPushButton:hover {
    background-color: #EFEEEA;
    border: 1px solid #FE7743;
    color: #000000;
    font: 75 12pt "MS Shell Dlg 2";
}
QComboBox {
    background-color: #273F4F;
    font: 75 12pt "MS Shell Dlg 2";
    color: #FE7743;
}
QTextEdit {
    background-color: #273F4F;
    font: 75 12pt "MS Shell Dlg 2";
    color: #FE7743;
}
QLineEdit {
    background-color: #273F4F;
    font: 75 12pt "MS Shell Dlg 2";
    color: #FE7743;
}
QTableWidget {
    background-color: #273F4F;
    color: #FE7743;
    gridline-color: #EFEEEA;
    font: 75 12pt "MS Shell Dlg 2";
    selection-background-color: #FE7743;
    selection-color: #000000;
    alternate-background-color: #1E2E3A;
}
QHeaderView::section {
    background-color: #000000;
    color: #FE7743;
    padding: 4px;
    border: 1px solid #EFEEEA;
    font-weight: bold;
}
QTableWidget::item:selected {
    background-color: #FE7743;
    color: #000000;
}

/* Scrollbar Vertical */
QScrollBar:vertical {
    background: #000000;
    width: 12px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #273F4F;
    min-height: 20px;
    border-radius: 6px;
}
QScrollBar::handle:vertical:hover {
    background: #FE7743;
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
    background: #000000;
    height: 12px;
    margin: 0px;
}
QScrollBar::handle:horizontal {
    background: #273F4F;
    min-width: 20px;
    border-radius: 6px;
}
QScrollBar::handle:horizontal:hover {
    background: #FE7743;
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
