"""
Modern buton bileşenleri.
"""
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt
from ..styles import PRIMARY_BUTTON_STYLE, SECONDARY_BUTTON_STYLE

class ModernButton(QPushButton):
    """Modern görünümlü buton bileşeni."""
    
    def __init__(self, text, parent=None, primary=False):
        """
        Args:
            text: Buton metni
            parent: Üst widget
            primary: Ana buton mu?
        """
        super().__init__(text, parent)
        self.setMinimumHeight(45)
        self.setMinimumWidth(120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        if primary:
            self.setStyleSheet(PRIMARY_BUTTON_STYLE)
        else:
            self.setStyleSheet(SECONDARY_BUTTON_STYLE) 