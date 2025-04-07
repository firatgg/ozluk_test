"""
İlerleme çubuğu bileşenleri.
"""
from PyQt6.QtWidgets import QProgressBar
from PyQt6.QtCore import Qt

# Marnak Lojistik Kurumsal Renkleri
MARNAK_BLUE = "#0066B3"
MARNAK_GREEN = "#3AB54A"
MARNAK_LIGHT_BLUE = "#E5F1F9"
MARNAK_LIGHT_GREEN = "#E8F5EA"

class ModernProgressBar(QProgressBar):
    """Modern tasarımlı ilerleme çubuğu."""
    
    def __init__(self, parent=None):
        """
        Args:
            parent: Üst widget
        """
        super().__init__(parent)
        self.setMinimumHeight(20)
        self.setTextVisible(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {MARNAK_BLUE};
                border-radius: 8px;
                background-color: white;
                text-align: center;
                font-size: 13px;
                color: {MARNAK_BLUE};
            }}
            QProgressBar::chunk {{
                background-color: {MARNAK_LIGHT_BLUE};
                border-radius: 6px;
            }}
        """) 