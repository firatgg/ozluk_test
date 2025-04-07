"""
Etiket bileşenleri.
"""
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt

# Marnak Lojistik Kurumsal Renkleri
MARNAK_BLUE = "#0066B3"
MARNAK_GREEN = "#3AB54A"
MARNAK_LIGHT_BLUE = "#E5F1F9"
MARNAK_LIGHT_GREEN = "#E8F5EA"

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
        self.setStyleSheet(f"""
            QLabel {{
                color: {MARNAK_BLUE};
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
            }}
        """)

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
        self.setStyleSheet(f"""
            QLabel {{
                color: {MARNAK_BLUE};
                font-size: 13px;
                padding: 5px;
            }}
        """)

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
        self.setStyleSheet("""
            QLabel {
                color: red;
                font-size: 13px;
                padding: 5px;
            }
        """) 