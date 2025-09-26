"""
PDF dosyalarını sayfalara bölme işlemlerini gerçekleştiren modül.
"""
import os
import re
from typing import List, Tuple, Optional, Dict, Any
from PyPDF2 import PdfReader, PdfWriter
from .utils import parse_page_ranges

class PdfSplitter:
    """PDF dosyalarını sayfalara bölme işlemlerini yöneten sınıf."""
    
    # Bölme modları
    SPLIT_MODE_ALL_PAGES = "all_pages"  # Tüm sayfaları böl
    SPLIT_MODE_PAGE_RANGE = "page_range"  # Sayfa aralığına göre böl
    SPLIT_MODE_EVERY_N_PAGES = "every_n_pages"  # Her N sayfada bir böl
    SPLIT_MODE_ODD_EVEN = "odd_even"  # Tek/Çift sayfalara göre böl
    
    def __init__(self, logger=None):
        """
        Args:
            logger: Loglama nesnesi (opsiyonel)
        """
        self.logger = logger
    
    def split_pdf(self, 
                  file_path: str, 
                  output_dir: str,
                  options: Optional[Dict[str, Any]] = None,
                  progress_callback: Optional[callable] = None,
                  interrupt_check: Optional[callable] = None) -> Tuple[bool, str, List[str]]:
        """
        PDF dosyasını belirtilen seçeneklere göre böler.
        
        Args:
            file_path: Bölünecek PDF dosyasının yolu
            output_dir: Çıktı klasörü
            options: Bölme seçenekleri
            progress_callback: İlerleme durumunu bildiren fonksiyon
            interrupt_check: İşlem iptal edildi mi kontrol eden fonksiyon
            
        Returns:
            Tuple[bool, str, List[str]]: (Başarılı mı?, Mesaj, Oluşturulan dosyalar)
        """
        output_files = []
        
        try:
            # Dosya yolu kontrolü
            if file_path is None:
                return False, "Dosya yolu belirtilmemiş (None)", []
                
            if not isinstance(file_path, (str, bytes, os.PathLike)):
                return False, f"Geçersiz dosya yolu: {type(file_path)}", []
            
            # Dosya var mı?
            if not os.path.exists(file_path):
                return False, f"Dosya bulunamadı: {file_path}", []
                
            # Çıktı dizini kontrolü
            if output_dir is None:
                return False, "Çıktı dizini belirtilmemiş (None)", []
                
            if not isinstance(output_dir, (str, bytes, os.PathLike)):
                return False, f"Geçersiz çıktı dizini: {type(output_dir)}", []
                
            # Çıktı klasörünü kontrol et/oluştur
            try:
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
            except (OSError, PermissionError) as e:
                return False, f"Çıktı dizini oluşturulamadı: {str(e)}", []
            except Exception as e:
                return False, f"Beklenmeyen hata: {str(e)}", []
            
            # PDF dosyasını aç
            try:
                pdf = PdfReader(file_path)
                total_pages = len(pdf.pages)
            except (FileNotFoundError, PermissionError) as e:
                return False, f"PDF dosyası açılamadı: {str(e)}", []
            except Exception as e:
                return False, f"PDF işleme hatası: {str(e)}", []
            
            if total_pages == 0:
                return False, "PDF dosyası boş", []
            
            # Seçenekleri kontrol et
            if not options:
                options = {"mode": self.SPLIT_MODE_ALL_PAGES}
            
            # Bölme moduna göre işlem yap
            mode = options.get("mode", self.SPLIT_MODE_ALL_PAGES)
            
            if mode == self.SPLIT_MODE_ALL_PAGES:
                return self._split_all_pages(pdf, file_path, output_dir, progress_callback, interrupt_check)
            elif mode == self.SPLIT_MODE_PAGE_RANGE:
                return self._split_page_range(pdf, file_path, output_dir, options, progress_callback, interrupt_check)
            elif mode == self.SPLIT_MODE_EVERY_N_PAGES:
                return self._split_every_n_pages(pdf, file_path, output_dir, options, progress_callback, interrupt_check)
            elif mode == self.SPLIT_MODE_ODD_EVEN:
                return self._split_odd_even(pdf, file_path, output_dir, options, progress_callback, interrupt_check)
            else:
                return False, f"Bilinmeyen bölme modu: {mode}", []
            
        except Exception as e:
            error_msg = f"PDF bölme işlemi başarısız: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            
            # Hata durumunda oluşturulan dosyaları temizle
            self._cleanup_files(output_files)
            return False, error_msg, []
    
    def _split_all_pages(self, 
                         pdf: PdfReader, 
                         file_path: str, 
                         output_dir: str, 
                         progress_callback: Optional[callable] = None,
                         interrupt_check: Optional[callable] = None) -> Tuple[bool, str, List[str]]:
        """Her sayfayı ayrı bir PDF olarak böler."""
        try:
            total_pages = len(pdf.pages)
            output_files = []
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            
            for i in range(total_pages):
                # İptal kontrolü
                if interrupt_check and interrupt_check():
                    pdf.close()
                    return False, "İşlem kullanıcı tarafından iptal edildi.", output_files
                
                # Yeni PDF oluştur
                writer = PdfWriter()
                writer.add_page(pdf.pages[i])
                
                # Dosya adı oluştur
                output_filename = f"{base_name}_sayfa_{i+1}.pdf"
                output_path = os.path.join(output_dir, output_filename)
                
                # Aynı isimde dosya varsa yeni isim oluştur
                counter = 1
                while os.path.exists(output_path):
                    output_filename = f"{base_name}_sayfa_{i+1}_{counter}.pdf"
                    output_path = os.path.join(output_dir, output_filename)
                    counter += 1
                
                # Dosyayı kaydet
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                output_files.append(output_path)
                
                # İlerleme bildirimi
                if progress_callback:
                    progress = int(((i + 1) / total_pages) * 100)
                    progress_callback(progress)
                
                if self.logger:
                    self.logger.info(f"Sayfa oluşturuldu: {output_path}")
            
            return True, f"Bölme işlemi başarılı. {len(output_files)} sayfa oluşturuldu.", output_files
            
        except Exception as e:
            error_msg = f"Sayfaları bölerken hata oluştu: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            
            # Hata durumunda temizlik
            self._cleanup_files(output_files)
            return False, error_msg, []
    
    def _split_page_range(self, 
                          pdf: PdfReader, 
                          file_path: str, 
                          output_dir: str, 
                          options: Dict[str, Any], 
                          progress_callback: Optional[callable] = None,
                          interrupt_check: Optional[callable] = None) -> Tuple[bool, str, List[str]]:
        """Sayfa aralığına göre böler."""
        try:
            page_range_str = options.get("page_range", "")
            if not page_range_str:
                return False, "Sayfa aralığı belirtilmemiş", []
            
            # Sayfa aralıklarını ayrıştır (merkezi fonksiyon kullan)
            parsed_ranges = parse_page_ranges(page_range_str, len(pdf.pages))
            if not parsed_ranges:
                return False, "Geçersiz sayfa aralığı", []
            
            # List[List[int]] formatını List[Tuple[int, int]] formatına dönüştür
            page_ranges = []
            for page_list in parsed_ranges:
                if page_list:
                    start = min(page_list) + 1  # 1-tabanlı indeksleme için +1
                    end = max(page_list) + 1    # 1-tabanlı indeksleme için +1
                    page_ranges.append((start, end))
            
            total_ranges = len(page_ranges)
            output_files = []
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            
            for i, (start, end) in enumerate(page_ranges):
                # İptal kontrolü
                if interrupt_check and interrupt_check():
                    pdf.close()
                    return False, "İşlem kullanıcı tarafından iptal edildi.", output_files
                
                # Yeni PDF oluştur
                writer = PdfWriter()
                
                # Sayfa aralığındaki sayfaları ekle
                for page_idx in range(start - 1, end):
                    writer.add_page(pdf.pages[page_idx])
                
                # Dosya adı oluştur
                if start == end:
                    output_filename = f"{base_name}_sayfa_{start}.pdf"
                else:
                    output_filename = f"{base_name}_sayfa_{start}-{end}.pdf"
                
                output_path = os.path.join(output_dir, output_filename)
                
                # Aynı isimde dosya varsa yeni isim oluştur
                counter = 1
                while os.path.exists(output_path):
                    if start == end:
                        output_filename = f"{base_name}_sayfa_{start}_{counter}.pdf"
                    else:
                        output_filename = f"{base_name}_sayfa_{start}-{end}_{counter}.pdf"
                    output_path = os.path.join(output_dir, output_filename)
                    counter += 1
                
                # Dosyayı kaydet
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                output_files.append(output_path)
                
                # İlerleme bildirimi
                if progress_callback:
                    progress = int(((i + 1) / total_ranges) * 100)
                    progress_callback(progress)
                
                if self.logger:
                    self.logger.info(f"Sayfa aralığı oluşturuldu: {output_path}")
            
            return True, f"Bölme işlemi başarılı. {len(output_files)} PDF oluşturuldu.", output_files
            
        except Exception as e:
            error_msg = f"Sayfa aralığını bölerken hata oluştu: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            
            # Hata durumunda temizlik
            self._cleanup_files(output_files)
            return False, error_msg, []
    
    def _split_every_n_pages(self, 
                            pdf: PdfReader, 
                            file_path: str, 
                            output_dir: str, 
                            options: Dict[str, Any], 
                            progress_callback: Optional[callable] = None,
                            interrupt_check: Optional[callable] = None) -> Tuple[bool, str, List[str]]:
        """Her N sayfada bir böler."""
        try:
            pages_per_split = options.get("pages_per_split", 1)
            if pages_per_split < 1:
                pages_per_split = 1
            
            total_pages = len(pdf.pages)
            output_files = []
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # Kaç PDF oluşacağını hesapla
            split_count = (total_pages + pages_per_split - 1) // pages_per_split
            
            for i in range(split_count):
                # İptal kontrolü
                if interrupt_check and interrupt_check():
                    pdf.close()
                    return False, "İşlem kullanıcı tarafından iptal edildi.", output_files
                
                # Yeni PDF oluştur
                writer = PdfWriter()
                
                # Bu PDF için sayfa aralığını belirle
                start_page = i * pages_per_split
                end_page = min((i + 1) * pages_per_split, total_pages)
                
                # Sayfaları ekle
                for page_idx in range(start_page, end_page):
                    writer.add_page(pdf.pages[page_idx])
                
                # Dosya adı oluştur
                output_filename = f"{base_name}_bolum_{i+1}.pdf"
                output_path = os.path.join(output_dir, output_filename)
                
                # Aynı isimde dosya varsa yeni isim oluştur
                counter = 1
                while os.path.exists(output_path):
                    output_filename = f"{base_name}_bolum_{i+1}_{counter}.pdf"
                    output_path = os.path.join(output_dir, output_filename)
                    counter += 1
                
                # Dosyayı kaydet
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                output_files.append(output_path)
                
                # İlerleme bildirimi
                if progress_callback:
                    progress = int(((i + 1) / split_count) * 100)
                    progress_callback(progress)
                
                if self.logger:
                    self.logger.info(f"Bölüm oluşturuldu: {output_path}")
            
            return True, f"Bölme işlemi başarılı. {len(output_files)} bölüm oluşturuldu.", output_files
            
        except Exception as e:
            error_msg = f"Sayfaları bölerken hata oluştu: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            
            # Hata durumunda temizlik
            self._cleanup_files(output_files)
            return False, error_msg, []
    
    def _split_odd_even(self, 
                       pdf: PdfReader, 
                       file_path: str, 
                       output_dir: str, 
                       options: Dict[str, Any], 
                       progress_callback: Optional[callable] = None,
                       interrupt_check: Optional[callable] = None) -> Tuple[bool, str, List[str]]:
        """Tek/Çift sayfalara göre böler."""
        try:
            odd_even_mode = options.get("odd_even_mode", "odd")
            total_pages = len(pdf.pages)
            output_files = []
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            
            if odd_even_mode == "both":
                # Tek ve çift sayfaları ayrı PDF'lere böl
                
                # Tek sayfalar için PDF oluştur
                odd_writer = PdfWriter()
                for i in range(0, total_pages):
                    # İptal kontrolü
                    if interrupt_check and interrupt_check():
                        pdf.close()
                        return False, "İşlem kullanıcı tarafından iptal edildi.", output_files
                    
                    if (i + 1) % 2 == 1:  # Tek sayfa
                        odd_writer.add_page(pdf.pages[i])
                
                odd_filename = f"{base_name}_tek_sayfalar.pdf"
                odd_path = os.path.join(output_dir, odd_filename)
                
                # Aynı isimde dosya varsa yeni isim oluştur
                counter = 1
                while os.path.exists(odd_path):
                    odd_filename = f"{base_name}_tek_sayfalar_{counter}.pdf"
                    odd_path = os.path.join(output_dir, odd_filename)
                    counter += 1
                
                # Tek sayfalar dosyasını kaydet
                with open(odd_path, 'wb') as output_file:
                    odd_writer.write(output_file)
                
                output_files.append(odd_path)
                
                # İlerleme bildirimi
                if progress_callback:
                    progress_callback(50)  # İşin yarısı tamamlandı
                
                # Çift sayfalar için PDF oluştur
                even_writer = PdfWriter()
                for i in range(0, total_pages):
                    # İptal kontrolü
                    if interrupt_check and interrupt_check():
                        pdf.close()
                        return False, "İşlem kullanıcı tarafından iptal edildi.", output_files
                    
                    if (i + 1) % 2 == 0:  # Çift sayfa
                        even_writer.add_page(pdf.pages[i])
                
                even_filename = f"{base_name}_cift_sayfalar.pdf"
                even_path = os.path.join(output_dir, even_filename)
                
                # Aynı isimde dosya varsa yeni isim oluştur
                counter = 1
                while os.path.exists(even_path):
                    even_filename = f"{base_name}_cift_sayfalar_{counter}.pdf"
                    even_path = os.path.join(output_dir, even_filename)
                    counter += 1
                
                # Çift sayfalar dosyasını kaydet
                with open(even_path, 'wb') as output_file:
                    even_writer.write(output_file)
                
                output_files.append(even_path)
                
                # İlerleme bildirimi
                if progress_callback:
                    progress_callback(100)  # İş tamamlandı
                
            else:
                # Tek veya çift sayfaları seç
                writer = PdfWriter()
                for i in range(0, total_pages):
                    # İptal kontrolü
                    if interrupt_check and interrupt_check():
                        pdf.close()
                        return False, "İşlem kullanıcı tarafından iptal edildi.", output_files
                    
                    is_odd = (i + 1) % 2 == 1
                    
                    if (odd_even_mode == "odd" and is_odd) or (odd_even_mode == "even" and not is_odd):
                        writer.add_page(pdf.pages[i])
                
                # Dosya adı oluştur
                if odd_even_mode == "odd":
                    output_filename = f"{base_name}_tek_sayfalar.pdf"
                else:
                    output_filename = f"{base_name}_cift_sayfalar.pdf"
                
                output_path = os.path.join(output_dir, output_filename)
                
                # Aynı isimde dosya varsa yeni isim oluştur
                counter = 1
                while os.path.exists(output_path):
                    if odd_even_mode == "odd":
                        output_filename = f"{base_name}_tek_sayfalar_{counter}.pdf"
                    else:
                        output_filename = f"{base_name}_cift_sayfalar_{counter}.pdf"
                    output_path = os.path.join(output_dir, output_filename)
                    counter += 1
                
                # Dosyayı kaydet
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                output_files.append(output_path)
                
                # İlerleme bildirimi
                if progress_callback:
                    progress_callback(100)  # İş tamamlandı
            
            return True, f"Bölme işlemi başarılı. {len(output_files)} PDF oluşturuldu.", output_files
            
        except Exception as e:
            error_msg = f"Tek/Çift sayfa bölmede hata oluştu: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            
            # Hata durumunda temizlik
            self._cleanup_files(output_files)
            return False, error_msg, []
    
    
    def _cleanup_files(self, file_paths: List[str]):
        """İşlenmiş dosyaları temizler."""
        for path in file_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except:
                pass 