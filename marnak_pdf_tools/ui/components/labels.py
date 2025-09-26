"""
Etiket bileşenleri.
"""
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from ..styles import HEADER_LABEL_STYLE, INFO_LABEL_STYLE, ERROR_LABEL_STYLE

class HeaderLabel(QLabel):
    """Başlık etiketi."""
    
    def __init__(self, text="", parent=None):
        """
        Args:
            text: Etiket metni
            parent: Üst widget
        """
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(HEADER_LABEL_STYLE)

class InfoLabel(QLabel):
    """Bilgi etiketi."""
    
    def __init__(self, text="", parent=None):
        """
        Args:
            text: Etiket metni
            parent: Üst widget
        """
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setWordWrap(True)
        self.setStyleSheet(INFO_LABEL_STYLE)

class ErrorLabel(QLabel):
    """Hata etiketi."""
    
    def __init__(self, text="", parent=None):
        """
        Args:
            text: Etiket metni
            parent: Üst widget
        """
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)
        self.setStyleSheet(ERROR_LABEL_STYLE) 