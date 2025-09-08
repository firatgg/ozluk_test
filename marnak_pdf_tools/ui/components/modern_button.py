from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QSize
from ..styles import BUTTON_STYLE, GREEN_BUTTON_STYLE, SECONDARY_BUTTON_STYLE_OLD

class ModernButton(QPushButton):
    """Modern düğme komponenti."""
    
    def __init__(self, text, icon=None, primary=True, style=None):
        super().__init__(text)
        
        # Düğmenin primer/sekonder durumu
        self.is_primary = primary
        
        # İkon varsa ayarla
        if icon:
            self.setIcon(icon)
            self.setIconSize(QSize(24, 24))
        
        # Stil seçenekleri
        if style:
            # Özel stil verilmişse onu kullan
            self.setStyleSheet(style)
        elif primary:
            # Primary düğme için varsayılan stil
            self.setStyleSheet(BUTTON_STYLE)
        else:
            # Secondary düğme için varsayılan stil
            self.setStyleSheet(SECONDARY_BUTTON_STYLE_OLD) 