"""
Ana uygulama modülü.
"""
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from .ui import MainWindow
from .services.pdf_service import PdfService

def main():
    """Ana uygulama başlatıcı."""
    app = QApplication(sys.argv)
    
    # Uygulama ikonunu ayarla
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(current_dir, "icons", "android-chrome-512x512.png")
    app.setWindowIcon(QIcon(icon_path))
    
    # PDF servisi oluştur
    pdf_service = PdfService()
    
    # Hot reload kontrolü
    existing_window = None
    for widget in app.topLevelWidgets():
        if isinstance(widget, MainWindow):
            existing_window = widget
            break
    
    if existing_window:
        # Eğer pencere minimize edilmişse normal haline getir
        if existing_window.isMinimized():
            existing_window.showNormal()
        # Pencereyi öne getir
        existing_window.activateWindow()
        existing_window.raise_()
    else:
        # Yeni pencere oluştur
        window = MainWindow(pdf_service)
        window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 