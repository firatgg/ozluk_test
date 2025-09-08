"""
Ana uygulama modülü.
"""
import sys
import os
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

# Python path'ini düzelt
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from marnak_pdf_tools.ui.windows.main_window import MainWindow
from marnak_pdf_tools.services.pdf_service import PdfService

def get_log_path():
    """Kullanıcının yazma izni olan log dosyası yolunu döndürür."""
    try:
        # Kullanıcının Documents klasörünü tercih et
        documents_path = Path.home() / "Documents" / "MarnakPDFAraclari"
        documents_path.mkdir(exist_ok=True)
        return documents_path / "app.log"
    except:
        try:
            # Alternatif: Temp klasörü
            import tempfile
            temp_dir = Path(tempfile.gettempdir()) / "MarnakPDFAraclari"
            temp_dir.mkdir(exist_ok=True)
            return temp_dir / "app.log"
        except:
            # Son çare: Uygulama dizini
            return Path("app.log")

def main():
    """Ana uygulama başlatıcı."""
    # Loglama yapılandırması
    log_path = get_log_path()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger("App")
    logger.info("Uygulama başlatılıyor...")
    logger.info(f"Log dosyası: {log_path}")

    app = QApplication(sys.argv)
    
    # Uygulama ikonunu ayarla
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(current_dir, "icons", "favicon.ico")
    
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        logger.info(f"Uygulama ikonu yüklendi: {icon_path}")
    else:
        logger.warning(f"Uygulama ikonu bulunamadı: {icon_path}")

    # PDF servisini oluştur
    pdf_service = PdfService()
    logger.info("PDF servisi oluşturuldu")

    # Ana pencereyi oluştur ve göster
    main_window = MainWindow(pdf_service)
    main_window.show()
    
    logger.info("Ana pencere gösterildi")
    
    # Uygulama döngüsünü başlat
    try:
        exit_code = app.exec()
        logger.info(f"Uygulama sonlandırıldı. Exit code: {exit_code}")
        return exit_code
    except Exception as e:
        logger.error(f"Uygulama hatası: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 