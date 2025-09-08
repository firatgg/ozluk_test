"""
Marnak PDF Tools - PDF işleme araçları.

Bu paket PDF dosyalarını bölme, birleştirme, yeniden adlandırma ve sayfa çıkarma
işlemlerini kolaylaştıran modern bir GUI uygulamasıdır.
"""

__version__ = "1.0.0"
__author__ = "Marnak Team"
__email__ = "info@marnak.com"

# Ana bileşenleri export et
from .core import PdfRenamer, PdfSplitter, PdfMerger, PdfExtractor, PdfConverter
from .services import PdfService
from .ui import MainWindow

__all__ = [
    'PdfRenamer', 'PdfSplitter', 'PdfMerger', 'PdfExtractor', 'PdfConverter',
    'PdfService', 'MainWindow'
] 