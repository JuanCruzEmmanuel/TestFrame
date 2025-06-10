import sys
from PyQt5.QtCore import Qt, QRectF, QPropertyAnimation, pyqtProperty
from PyQt5.QtGui import QColor, QPainter, QFont
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout


class ToggleSwitch(QWidget):
    def __init__(self, on_toggle=None, parent=None):
        super().__init__(parent)
        self._checked = False
        self._handle_position = 2
        self._on_toggle = on_toggle  # <--- Guardamos el callback

        self.setFixedSize(60, 28)
        self.setCursor(Qt.PointingHandCursor)

        # Animation
        self._animation = QPropertyAnimation(self, b"handle_position", self)
        self._animation.setDuration(200)

    def mousePressEvent(self, event):
        self._checked = not self._checked
        self._animate()
        if self._on_toggle:
            self._on_toggle(self._checked)  # <--- Llamamos al callback

    def _animate(self):
        start = self._handle_position
        end = self.width() - self.height() + 2 if self._checked else 2
        self._animation.stop()
        self._animation.setStartValue(start)
        self._animation.setEndValue(end)
        self._animation.start()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Background
        if self._checked:
            p.setBrush(QColor("#00bfa5"))
        else:
            p.setBrush(QColor("#ccc"))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(self.rect(), self.height() / 2, self.height() / 2)

        # Icons
        p.setPen(Qt.white)
        font = QFont()
        font.setPointSize(10)
        p.setFont(font)

        if self._checked:
            p.drawText(QRectF(5, 4, 20, 20), Qt.AlignCenter, "☀️")
        else:
            p.drawText(QRectF(self.width() - 25, 4, 20, 20), Qt.AlignCenter, "🌙")

        # Handle
        p.setBrush(QColor("white"))
        p.drawEllipse(QRectF(self._handle_position, 2, self.height() - 4, self.height() - 4))

    def get_handle_position(self):
        return self._handle_position

    def set_handle_position(self, pos):
        self._handle_position = pos
        self.update()

    handle_position = pyqtProperty(float, get_handle_position, set_handle_position)

    def isChecked(self):
        return self._checked

    def setChecked(self, value):
        self._checked = value
        self._handle_position = self.width() - self.height() + 2 if value else 2
        self.update()