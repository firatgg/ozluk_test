"""
PDF işlemlerini yöneten servis sınıfı.
"""
import os
import logging
from typing import List, Tuple, Optional, Callable
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from ..core import PdfRenamer, PdfSplitter, PdfMerger
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
    
    def __init__(self, pdf_file, output_dir, options=None):
        super().__init__()
        self.pdf_file = pdf_file
        self.output_dir = output_dir
        self.options = options or {}
        self._interrupted = False
        
    def run(self):
        try:
            self.progress.emit(10)
            # Dosyanın varlığını kontrol et
            if not os.path.exists(self.pdf_file):
                self.finished.emit(False, f"Dosya bulunamadı: {self.pdf_file}")
                return
                
            # Çıkış dizinini kontrol et
            if not os.path.exists(self.output_dir):
                try:
                    os.makedirs(self.output_dir, exist_ok=True)
                except Exception as e:
                    self.finished.emit(False, f"Çıkış dizini oluşturulamadı: {str(e)}")
                    return
            
            self.progress.emit(20)
            
            # Orijinal dosyanın PDF olup olmadığını kontrol et
            try:
                pdf = fitz.open(self.pdf_file)
                page_count = len(pdf)
                pdf.close()
                
                if page_count == 0:
                    self.finished.emit(False, "PDF dosyası geçerli sayfalar içermiyor.")
                    return
            except Exception as e:
                self.finished.emit(False, f"Geçersiz PDF dosyası: {str(e)}")
                return
            
            self.progress.emit(30)
            
            # Yeni isim al
            new_name = self.options.get("new_name", "renamed")
            if not new_name:
                new_name = "renamed"
                
            # Yeni dosya yolu oluştur
            output_path = os.path.join(self.output_dir, f"{new_name}.pdf")
            
            # Hedef dosya zaten varsa, ismi değiştir
            counter = 1
            original_name = new_name
            while os.path.exists(output_path):
                new_name = f"{original_name}_{counter}"
                output_path = os.path.join(self.output_dir, f"{new_name}.pdf")
                counter += 1
                
            self.progress.emit(50)
            
            # Orijinal ve hedef dosya aynı konumda mı kontrol et
            source_is_target = os.path.normpath(os.path.abspath(self.pdf_file)) == os.path.normpath(os.path.abspath(output_path))
            
            if source_is_target:
                self.finished.emit(False, "Kaynak ve hedef dosya aynı olamaz.")
                return
                
            # PDF dosyasını kopyala ve yeniden adlandır
            try:
                self.progress.emit(70)
                
                # PDF'i aç
                pdf = fitz.open(self.pdf_file)
                
                # Yeni dosyaya kaydet
                pdf.save(output_path)
                pdf.close()
                
                self.progress.emit(90)
                
                # Başarılı işlem kontrolü
                if os.path.exists(output_path):
                    # Yeni dosyanın içeriğini kontrol et
                    try:
                        check_pdf = fitz.open(output_path)
                        if len(check_pdf) == page_count:
                            # İşlem başarılı
                            check_pdf.close()
                            result_message = f"PDF başarıyla yeniden adlandırıldı:\n{output_path}"
                            self.progress.emit(100)
                            self.finished.emit(True, result_message)
                        else:
                            # İçerik eksik, dosyayı sil
                            check_pdf.close()
                            try:
                                os.remove(output_path)
                            except:
                                pass
                            self.finished.emit(False, f"Yeniden adlandırma işlemi sırasında içerik kaybı oldu.")
                    except Exception as e:
                        # Yeni dosya açılamadı, sil
                        try:
                            os.remove(output_path)
                        except:
                            pass
                        self.finished.emit(False, f"Yeni oluşturulan dosya doğrulanamadı: {str(e)}")
                else:
                    self.finished.emit(False, "Yeni dosya oluşturulamadı.")
            except Exception as e:
                # Hata durumunda yarım kalan dosyayı temizle
                if os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                    except:
                        pass
                self.finished.emit(False, f"PDF işleme hatası: {str(e)}")
        except Exception as e:
            self.finished.emit(False, f"Hata: {str(e)}")
    
    def requestInterruption(self):
        """İşlemi nazikçe durdurmak için."""
        self._interrupted = True
        super().requestInterruption()

class PDFSplitWorker(QThread):
    """PDF bölme işlemini arka planda yürüten iş parçacığı."""
    
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, pdf_file, output_dir, options):
        super().__init__()
        self.pdf_file = pdf_file
        self.output_dir = output_dir
        self.options = options or {}
        self._interrupted = False
        
    def run(self):
        try:
            if not os.path.exists(self.pdf_file):
                self.finished.emit(False, f"Dosya bulunamadı: {self.pdf_file}")
                return
                
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir, exist_ok=True)
                
            # PDF belgesini aç
            try:
                pdf = fitz.open(self.pdf_file)
            except Exception as e:
                self.finished.emit(False, f"PDF dosyası açılamadı: {str(e)}")
                return
                
            # İşlem özellikleri
            split_method = self.options.get("method", "page_count")
            pages_per_file = self.options.get("pages_per_file", 1)
            custom_ranges = self.options.get("custom_ranges", "")
            file_prefix = self.options.get("file_prefix", "split_")
            
            # PDF adını al
            try:
                base_name = os.path.splitext(os.path.basename(self.pdf_file))[0]
            except:
                base_name = "dokuman"
            
            # Toplam sayfa sayısı
            total_pages = len(pdf)
            if total_pages == 0:
                self.finished.emit(False, "PDF dosyası sayfa içermiyor.")
                pdf.close()
                return
                
            # Dosyanın ayırma yöntemine göre işlenmesi
            try:
                if split_method == "custom_ranges":
                    # Özel sayfa aralıklarına göre böl
                    if not custom_ranges:
                        self.finished.emit(False, "Özel sayfa aralıkları belirtilmedi.")
                        pdf.close()
                        return
                        
                    # Sayfa aralıklarını ayrıştır
                    ranges = parse_page_ranges(custom_ranges, total_pages)
                    if not ranges:
                        self.finished.emit(False, "Geçersiz sayfa aralığı biçimi.")
                        pdf.close()
                        return
                        
                    # Her aralık için yeni bir PDF oluştur
                    total_ranges = len(ranges)
                    for i, page_range in enumerate(ranges):
                        if self._interrupted:
                            break
                            
                        # İlerleme durumunu bildir
                        progress_value = int((i / total_ranges) * 100)
                        self.progress.emit(progress_value)
                        
                        # Yeni belge oluştur
                        output_pdf = fitz.open()
                        
                        # Sayfaları ekle
                        for page_num in page_range:
                            if 0 <= page_num < total_pages:
                                output_pdf.insert_pdf(pdf, from_page=page_num, to_page=page_num)
                                
                        # Dosyayı kaydet
                        output_path = os.path.join(
                            self.output_dir, 
                            f"{file_prefix}{base_name}_{i+1}.pdf"
                        )
                        output_pdf.save(output_path)
                        output_pdf.close()
                        
                else:  # page_count yöntemi
                    # Sayfa sayısına göre böl
                    if pages_per_file <= 0:
                        pages_per_file = 1
                        
                    # Kaç dosya oluşacağını hesapla
                    file_count = (total_pages + pages_per_file - 1) // pages_per_file
                    
                    # Her dosya için sayfaları ayır
                    for i in range(file_count):
                        if self._interrupted:
                            break
                            
                        # İlerleme durumunu bildir
                        progress_value = int((i / file_count) * 100)
                        self.progress.emit(progress_value)
                        
                        # Yeni belge oluştur
                        output_pdf = fitz.open()
                        
                        # Bu dosya için sayfa aralığı
                        start_page = i * pages_per_file
                        end_page = min((i + 1) * pages_per_file, total_pages) - 1
                        
                        # Sayfaları ekle
                        for page_num in range(start_page, end_page + 1):
                            output_pdf.insert_pdf(pdf, from_page=page_num, to_page=page_num)
                            
                        # Dosyayı kaydet
                        output_path = os.path.join(
                            self.output_dir, 
                            f"{file_prefix}{base_name}_{i+1}.pdf"
                        )
                        output_pdf.save(output_path)
                        output_pdf.close()
                
                # Kaynağı temizle ve başarıyı bildir
                pdf.close()
                
                if self._interrupted:
                    self.finished.emit(False, "İşlem kullanıcı tarafından durduruldu.")
                else:
                    self.progress.emit(100)
                    self.finished.emit(True, "PDF başarıyla bölündü.")
                    
            except Exception as e:
                pdf.close()
                self.finished.emit(False, f"PDF bölme işlemi sırasında hata: {str(e)}")
                
        except Exception as e:
            self.finished.emit(False, f"PDF işleme hatası: {str(e)}")
            
    def requestInterruption(self):
        """İşlemi nazikçe durdurmak için."""
        self._interrupted = True
        super().requestInterruption()

class PDFMergeWorker(QThread):
    """PDF birleştirme işlemini arka planda yürüten iş parçacığı."""
    
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, pdf_files, output_file):
        super().__init__()
        self.pdf_files = pdf_files
        self.output_file = output_file
        self._interrupted = False
        
    def run(self):
        try:
            # Dosya listesini kontrol et
            if not self.pdf_files:
                self.finished.emit(False, "Birleştirilecek dosya bulunamadı.")
                return
                
            # Çıkış dizinini kontrol et
            output_dir = os.path.dirname(self.output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                
            # Yeni bir PDF oluştur
            output_pdf = fitz.open()
            
            # Her dosyayı ekle
            total_files = len(self.pdf_files)
            for i, pdf_file in enumerate(self.pdf_files):
                if self._interrupted:
                    break
                    
                # İlerleme durumunu bildir
                progress_value = int((i / total_files) * 100)
                self.progress.emit(progress_value)
                
                # Dosya var mı?
                if not os.path.exists(pdf_file):
                    continue
                    
                try:
                    # PDF'i aç ve tüm sayfaları ekle
                    pdf = fitz.open(pdf_file)
                    output_pdf.insert_pdf(pdf)
                    pdf.close()
                except Exception as e:
                    print(f"Dosya eklenirken hata: {pdf_file} - {str(e)}")
                    # Hatayı göster ama devam et
                    continue
                    
            # Çıkış dosyasını kaydet
            try:
                if not self._interrupted and output_pdf.page_count > 0:
                    output_pdf.save(self.output_file)
                    output_pdf.close()
                    
                    self.progress.emit(100)
                    self.finished.emit(True, f"PDF başarıyla birleştirildi: {self.output_file}")
                else:
                    output_pdf.close()
                    if self._interrupted:
                        self.finished.emit(False, "İşlem kullanıcı tarafından durduruldu.")
                    else:
                        self.finished.emit(False, "Birleştirilebilir sayfa bulunamadı.")
            except Exception as e:
                output_pdf.close()
                self.finished.emit(False, f"PDF kaydetme hatası: {str(e)}")
                
        except Exception as e:
            self.finished.emit(False, f"PDF birleştirme hatası: {str(e)}")
            
    def requestInterruption(self):
        """İşlemi nazikçe durdurmak için."""
        self._interrupted = True
        super().requestInterruption()

class PDFExtractWorker(QThread):
    """PDF sayfa çıkarma işlemini arka planda yürüten iş parçacığı."""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, pdf_file, output_dir, extract_all, page_range, file_prefix):
        super().__init__()
        self.pdf_file = pdf_file
        self.output_dir = output_dir
        self.extract_all = extract_all
        self.page_range = page_range
        self.file_prefix = file_prefix or "sayfa_"
        self._interrupted = False
        
    def run(self):
        try:
            # Dosyanın varlığını kontrol et
            if not os.path.exists(self.pdf_file):
                self.finished.emit(False, f"Dosya bulunamadı: {self.pdf_file}")
                return
                
            # Çıkış dizinini kontrol et
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir, exist_ok=True)
                
            # PDF belgesini aç
            try:
                pdf = fitz.open(self.pdf_file)
            except Exception as e:
                self.finished.emit(False, f"PDF dosyası açılamadı: {str(e)}")
                return
                
            # Toplam sayfa sayısı
            total_pages = len(pdf)
            if total_pages == 0:
                pdf.close()
                self.finished.emit(False, "PDF dosyası sayfa içermiyor.")
                return
                
            # Çıkarılacak sayfaları belirle
            pages_to_extract = []
            
            if self.extract_all:
                # Tüm sayfaları çıkar
                pages_to_extract = list(range(total_pages))
            else:
                # Belirli sayfaları çıkar
                if not self.page_range:
                    pdf.close()
                    self.finished.emit(False, "Çıkarılacak sayfa aralığı belirtilmedi.")
                    return
                    
                # Sayfa aralıklarını ayrıştır
                try:
                    ranges = parse_page_ranges(self.page_range, total_pages)
                    for page_range in ranges:
                        pages_to_extract.extend(page_range)
                except Exception as e:
                    pdf.close()
                    self.finished.emit(False, f"Geçersiz sayfa aralığı formatı: {str(e)}")
                    return
                    
            # Sayfaları çıkar
            total_to_extract = len(pages_to_extract)
            if total_to_extract == 0:
                pdf.close()
                self.finished.emit(False, "Çıkarılacak geçerli sayfa bulunamadı.")
                return
                
            # Her sayfayı ayrı bir PDF olarak kaydet
            try:
                for i, page_num in enumerate(pages_to_extract):
                    if self._interrupted:
                        break
                        
                    # İlerlemeyi bildir
                    progress_value = int((i / total_to_extract) * 100)
                    self.progress.emit(progress_value)
                    
                    # Sayfa geçerli aralıkta mı?
                    if page_num < 0 or page_num >= total_pages:
                        continue
                        
                    # Yeni belge oluştur
                    output_pdf = fitz.open()
                    output_pdf.insert_pdf(pdf, from_page=page_num, to_page=page_num)
                    
                    # Dosyayı kaydet
                    output_path = os.path.join(
                        self.output_dir,
                        f"{self.file_prefix}{page_num+1}.pdf"
                    )
                    output_pdf.save(output_path)
                    output_pdf.close()
                    
                # Kaynağı temizle ve başarıyı bildir
                pdf.close()
                
                if self._interrupted:
                    self.finished.emit(False, "İşlem kullanıcı tarafından durduruldu.")
                else:
                    self.progress.emit(100)
                    self.finished.emit(True, "PDF sayfaları başarıyla çıkarıldı.")
                    
            except Exception as e:
                pdf.close()
                self.finished.emit(False, f"PDF çıkarma işlemi sırasında hata: {str(e)}")
                
        except Exception as e:
            self.finished.emit(False, f"PDF işleme hatası: {str(e)}")
            
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
        
    def check_pdf(self, file_path: str) -> tuple:
        """PDF dosyasını kontrol eder."""
        try:
            if not os.path.exists(file_path):
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
            
            return True, "PDF dosyası geçerli.", info
        except Exception as e:
            return False, f"PDF dosyası açılamadı: {str(e)}", None
    
    def create_split_worker(self, file_path: str, output_dir: str, options=None) -> PDFSplitWorker:
        """Bölme iş parçacığı oluşturur."""
        self.split_worker = PDFSplitWorker(file_path, output_dir, options)
        self.split_worker.progress.connect(self.progress_updated)
        return self.split_worker
    
    def create_merge_worker(self, file_paths: List[str], output_path: str) -> PDFMergeWorker:
        """Birleştirme iş parçacığı oluşturur."""
        self.merge_worker = PDFMergeWorker(file_paths, output_path)
        self.merge_worker.progress.connect(self.progress_updated)
        return self.merge_worker
    
    def create_extract_worker(self, pdf_file: str, output_dir: str, 
                             extract_all: bool, page_range: str,
                             file_prefix: str) -> PDFExtractWorker:
        """Ayıklama iş parçacığı oluşturur."""
        self.extract_worker = PDFExtractWorker(
            pdf_file, output_dir, extract_all, page_range, file_prefix
        )
        self.extract_worker.progress.connect(self.progress_updated)
        return self.extract_worker
        
    def create_rename_worker(self, file_path: str, output_dir: str, options=None) -> PDFRenameWorker:
        """Yeniden adlandırma iş parçacığı oluşturur."""
        self.rename_worker = PDFRenameWorker(file_path, output_dir, options)
        self.rename_worker.progress.connect(self.progress_updated)
        return self.rename_worker 