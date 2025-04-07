"""
Modern buton bileşenleri.
"""
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt

# Marnak Lojistik Kurumsal Renkleri
MARNAK_BLUE = "#0066B3"
MARNAK_GREEN = "#3AB54A"
MARNAK_LIGHT_BLUE = "#E5F1F9"
MARNAK_LIGHT_GREEN = "#E8F5EA"

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
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {MARNAK_BLUE};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background-color: #005599;
                }}
                QPushButton:pressed {{
                    background-color: #004477;
                }}
                QPushButton:disabled {{
                    background-color: #CCCCCC;
                    color: #666666;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {MARNAK_LIGHT_BLUE};
                    color: {MARNAK_BLUE};
                    border: 2px solid {MARNAK_BLUE};
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-size: 13px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #D5E6F3;
                    border-color: {MARNAK_GREEN};
                    color: {MARNAK_GREEN};
                }}
                QPushButton:pressed {{
                    background-color: #C5DBE8;
                }}
                QPushButton:disabled {{
                    background-color: #F5F5F5;
                    border-color: #CCCCCC;
                    color: #666666;
                }}
            """) 