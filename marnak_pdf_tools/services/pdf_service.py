"""
PDF işlemlerini yöneten servis sınıfı.
"""
import os
import logging
from typing import List, Tuple, Optional, Callable
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from ..core import PdfRenamer, PdfSplitter, PdfMerger, PdfExtractor
import fitz

def parse_page_ranges(range_text: str, total_pages: int) -> List[List[int]]:
    """
    Sayfa aralıkları metnini ayrıştırır ve sayfa listesi listesi döndürür.
    
    Args:
        range_text: Sayfa aralıkları metni, örn. "1,3-5,7"
        total_pages: PDF'deki toplam sayfa sayısı
    
    Returns:
        Sayfa numaraları listesi listesi
    """
    result = []
    
    # Metin boş ise boş liste döndür
    if not range_text or range_text.strip() == "":
        return result
        
    # Virgülle ayrılmış parçalara böl
    parts = range_text.split(",")
    
    for part in parts:
        part = part.strip()
        
        # Aralık (örn. 3-5)
        if "-" in part:
            try:
                start, end = part.split("-", 1)
                start = int(start.strip())
                end = int(end.strip())
                
                # 0 tabanlı indeksleme için ayarla (PDF okuyucu 1 tabanlı gösterir)
                start = max(1, start) - 1  # En az 1, sonra 0-tabanlı için -1
                end = min(total_pages, end) - 1  # En fazla toplam sayfa, sonra 0-tabanlı için -1
                
                if start <= end:
                    result.append(list(range(start, end + 1)))
            except:
                # Ayrıştırma hatası, bu parçayı atla
                continue
        
        # Tek sayfa (örn. 3)
        else:
            try:
                page = int(part)
                # 0 tabanlı indeksleme için ayarla
                page = max(1, page) - 1  # En az 1, sonra 0-tabanlı için -1
                
                if 0 <= page < total_pages:
                    result.append([page])
            except:
                # Ayrıştırma hatası, bu parçayı atla
                continue
                
    return result

class PDFRenameWorker(QThread):
    """PDF yeniden adlandırma işlemini arka planda yürüten iş parçacığı."""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, pdf_files, output_dir, options=None, logger=None):
        super().__init__()
        self.pdf_files = pdf_files if isinstance(pdf_files, list) else [pdf_files]
        self.output_dir = output_dir
        self.options = options or {}
        self._interrupted = False
        self.renamer = PdfRenamer(logger=logger) # PdfRenamer instance ve logger aktarımı
        self.logger = logger # Logger'ı sakla
        
    def run(self):
        try:
            success, message, _ = self.renamer.rename_pdfs(
                file_paths=self.pdf_files,
                output_dir=self.output_dir,
                options=self.options,
                progress_callback=self._update_progress
            )
            if self._interrupted:
                self.finished.emit(False, "İşlem kullanıcı tarafından iptal edildi.")
                return
            self.finished.emit(success, message)
        except Exception as e:
            self.finished.emit(False, f"Hata: {str(e)}")
    
    def _update_progress(self, value):
        self.progress.emit(value)

    def requestInterruption(self):
        """İşlemi nazikçe durdurmak için."""
        self._interrupted = True
        super().requestInterruption()

class PDFSplitWorker(QThread):
    """PDF bölme işlemini arka planda yürüten iş parçacığı."""
    
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, pdf_file, output_dir, options, logger=None):
        super().__init__()
        self.pdf_file = pdf_file
        self.output_dir = output_dir
        self.options = options or {}
        self._interrupted = False
        self.splitter = PdfSplitter(logger=logger) # PdfSplitter instance ve logger aktarımı
        self.logger = logger # Logger'ı sakla
        
    def run(self):
        try:
            success, message, _ = self.splitter.split_pdf(
                file_path=self.pdf_file,
                output_dir=self.output_dir,
                options=self.options,
                progress_callback=self._update_progress
            )
            if self._interrupted:
                self.finished.emit(False, "İşlem kullanıcı tarafından iptal edildi.")
                return
            self.finished.emit(success, message)
        except Exception as e:
            self.finished.emit(False, f"Hata: {str(e)}")

    def _update_progress(self, value):
        self.progress.emit(value)
            
    def requestInterruption(self):
        """İşlemi nazikçe durdurmak için."""
        self._interrupted = True
        super().requestInterruption()

class PDFMergeWorker(QThread):
    """PDF birleştirme işlemini arka planda yürüten iş parçacığı."""
    
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, pdf_files, output_file, logger=None):
        super().__init__()
        self.pdf_files = pdf_files
        self.output_file = output_file
        self._interrupted = False
        self.merger = PdfMerger(logger=logger) # PdfMerger instance ve logger aktarımı
        self.logger = logger # Logger'ı sakla
        
    def run(self):
        try:
            success, message, _ = self.merger.merge_pdfs(
                file_paths=self.pdf_files,
                output_path=self.output_file,
                progress_callback=self._update_progress
            )
            if self._interrupted:
                self.finished.emit(False, "İşlem kullanıcı tarafından iptal edildi.")
                return
            self.finished.emit(success, message)
        except Exception as e:
            self.finished.emit(False, f"Hata: {str(e)}")

    def _update_progress(self, value):
        self.progress.emit(value)
            
    def requestInterruption(self):
        """İşlemi nazikçe durdurmak için."""
        self._interrupted = True
        super().requestInterruption()

class PDFExtractWorker(QThread):
    """PDF sayfa çıkarma işlemini arka planda yürüten iş parçacığı."""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, pdf_file, output_dir, extract_all, page_range, file_prefix, logger=None):
        super().__init__()
        self.pdf_file = pdf_file
        self.output_dir = output_dir
        self.options = {
            "extract_all": extract_all,
            "page_range": page_range,
            "file_prefix": file_prefix
        }
        self._interrupted = False
        self.extractor = PdfExtractor(logger=logger) # PdfExtractor instance ve logger aktarımı
        self.logger = logger # Logger'ı sakla
        
    def run(self):
        try:
            success, message, _ = self.extractor.extract_pages(
                file_path=self.pdf_file,
                output_dir=self.output_dir,
                options=self.options,
                progress_callback=self._update_progress
            )
            if self._interrupted:
                self.finished.emit(False, "İşlem kullanıcı tarafından iptal edildi.")
                return
            self.finished.emit(success, message)
        except Exception as e:
            self.finished.emit(False, f"Hata: {str(e)}")

    def _update_progress(self, value):
        self.progress.emit(value)
            
    def requestInterruption(self):
        """İşlemi nazikçe durdurmak için."""
        self._interrupted = True
        super().requestInterruption()

class PdfService(QObject):
    """PDF işlemleri için servis sınıfı."""
    
    progress_updated = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.split_worker = None
        self.merge_worker = None
        self.extract_worker = None
        self.rename_worker = None
        self.logger = logging.getLogger("PdfService") # Logger ekle
        
    def check_pdf(self, file_path: str) -> tuple:
        """PDF dosyasını kontrol eder."""
        try:
            if not os.path.exists(file_path):
                self.logger.warning(f"PDF kontrolü: Dosya bulunamadı: {file_path}")
                return False, "Dosya bulunamadı: " + file_path, None
                
            # PDF'i aç ve bilgileri al
            pdf = fitz.open(file_path)
            info = {
                "sayfa_sayısı": len(pdf),
                "başlık": pdf.metadata.get("title", ""),
                "yazar": pdf.metadata.get("author", ""),
                "oluşturma_tarihi": pdf.metadata.get("creationDate", ""),
                "boyut": os.path.getsize(file_path)
            }
            pdf.close()
            
            self.logger.info(f"PDF kontrolü başarılı: {file_path}")
            return True, "PDF dosyası geçerli.", info
        except Exception as e:
            self.logger.error(f"PDF kontrolü başarısız ({file_path}): {str(e)}")
            return False, f"PDF dosyası açılamadı: {str(e)}", None
    
    def create_split_worker(self, file_path: str, output_dir: str, options=None) -> PDFSplitWorker:
        """Bölme iş parçacığı oluşturur."""
        self.split_worker = PDFSplitWorker(file_path, output_dir, options, logger=self.logger) # Logger'ı aktar
        self.split_worker.progress.connect(self.progress_updated)
        self.split_worker.finished.connect(lambda success, message: self._handle_worker_finished(self.split_worker, success, message))
        return self.split_worker
    
    def create_merge_worker(self, file_paths: List[str], output_path: str) -> PDFMergeWorker:
        """Birleştirme iş parçacığı oluşturur."""
        self.merge_worker = PDFMergeWorker(file_paths, output_path, logger=self.logger) # Logger'ı aktar
        self.merge_worker.progress.connect(self.progress_updated)
        self.merge_worker.finished.connect(lambda success, message: self._handle_worker_finished(self.merge_worker, success, message))
        return self.merge_worker
    
    def create_extract_worker(self, pdf_file: str, output_dir: str, 
                             extract_all: bool, page_range: str,
                             file_prefix: str) -> PDFExtractWorker:
        """Ayıklama iş parçacığı oluşturur."""
        self.extract_worker = PDFExtractWorker(pdf_file, output_dir, extract_all, page_range, file_prefix, logger=self.logger) # Logger'ı aktar
        self.extract_worker.progress.connect(self.progress_updated)
        self.extract_worker.finished.connect(lambda success, message: self._handle_worker_finished(self.extract_worker, success, message))
        return self.extract_worker
        
    def create_rename_worker(self, file_paths, output_dir: str, options=None) -> PDFRenameWorker:
        """Yeniden adlandırma iş parçacığı oluşturur."""
        self.rename_worker = PDFRenameWorker(file_paths, output_dir, options, logger=self.logger) # Logger'ı aktar
        self.rename_worker.progress.connect(self.progress_updated)
        self.rename_worker.finished.connect(lambda success, message: self._handle_worker_finished(self.rename_worker, success, message))
        return self.rename_worker 

    def _handle_worker_finished(self, worker_thread: QThread, success: bool, message: str):
        """İş parçacığı tamamlandığında çağrılır."""
        if success:
            self.logger.info(f"İşlem başarılı: {message}")
        else:
            self.logger.error(f"İşlem başarısız: {message}")