"""
Modern input bileşenleri.
"""
from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import Qt
from ..styles import TEXT_INPUT_STYLE

class ModernLineEdit(QLineEdit):
    """Modern görünümlü metin giriş bileşeni."""
    
    def __init__(self, placeholder="", parent=None):
        """
        Args:
            placeholder: Yer tutucu metin
            parent: Üst widget
        """
        super().__init__(parent)
        self.setMinimumHeight(35)
        
        # Stil uygula
        self.setStyleSheet(TEXT_INPUT_STYLE)
        
        # Placeholder ayarla
        if placeholder:
            self.setPlaceholderText(placeholder)
            
        # Focus politikasını ayarla
        # StrongFocus: hem tıklama hem de tab tuşu ile odaklanabilir
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def keyPressEvent(self, event):
        """Klavye olaylarını yakala"""
        # Ctrl+V kombinasyonunu normal metin yapıştırma olarak işle
        if event.key() == Qt.Key.Key_V and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.paste()
        # ESC tuşuna basıldığında odağı kaybet
        elif event.key() == Qt.Key.Key_Escape:
            self.clearFocus()
        else:
            # Diğer tüm tuş basımlarını normal işle
            super().keyPressEvent(event) 