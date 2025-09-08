"""
PDF sayfalarını çıkarma işlemlerini gerçekleştiren modül.
"""
import os
from typing import List, Tuple, Optional, Any, Dict
from PyPDF2 import PdfReader, PdfWriter
import fitz # PyMuPDF

class PdfExtractor:
    """PDF sayfalarını çıkarma işlemlerini yöneten sınıf."""
    
    def __init__(self, logger=None):
        """
        Args:
            logger: Loglama nesnesi (opsiyonel)
        """
        self.logger = logger
    
    def extract_pages(self,
                      file_path: str,
                      output_dir: str,
                      options: Optional[Dict[str, Any]] = None,
                      progress_callback: Optional[callable] = None) -> Tuple[bool, str, List[str]]:
        """
        PDF dosyasından belirtilen sayfa aralıklarını çıkarır.
        
        Args:
            file_path: PDF dosyasının yolu
            output_dir: Çıktı klasörü
            options: Çıkarma seçenekleri (extract_all, page_range, file_prefix)
            progress_callback: İlerleme durumunu bildiren fonksiyon
            
        Returns:
            Tuple[bool, str, List[str]]: (Başarılı mı?, Mesaj, Oluşturulan dosyalar)
        """
        if options is None:
            options = {}

        extract_all = options.get("extract_all", True)
        page_range_str = options.get("page_range", "")
        file_prefix = options.get("file_prefix", "sayfa_")

        output_files = []
        try:
            if not os.path.exists(file_path):
                return False, f"Dosya bulunamadı: {file_path}", []

            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            pdf_document = fitz.open(file_path)
            total_pages = pdf_document.page_count
            if total_pages == 0:
                pdf_document.close()
                return False, "PDF dosyası sayfa içermiyor.", []

            pages_to_extract = []
            if extract_all:
                for i in range(total_pages):
                    pages_to_extract.append(i)
            else:
                # Sayfa aralığını ayrıştır
                parsed_ranges = self._parse_page_ranges(page_range_str, total_pages)
                for page_list in parsed_ranges:
                    for page_num in page_list:
                        if 0 <= page_num < total_pages:
                            pages_to_extract.append(page_num)
                pages_to_extract = sorted(list(set(pages_to_extract))) # Tekrarları kaldır ve sırala

            if not pages_to_extract:
                pdf_document.close()
                return False, "Çıkarılacak geçerli sayfa bulunamadı.", []

            total_extracted = len(pages_to_extract)
            for i, page_idx in enumerate(pages_to_extract):
                writer = PdfWriter()
                writer.add_page(pdf_document.load_page(page_idx))

                # Dosya adı oluştur
                original_filename = os.path.splitext(os.path.basename(file_path))[0]
                output_filename = f"{file_prefix}{original_filename}_sayfa_{page_idx + 1}.pdf"
                output_path = os.path.join(output_dir, output_filename)

                # Aynı isimde dosya varsa yeni isim oluştur
                counter = 1
                while os.path.exists(output_path):
                    output_filename = f"{file_prefix}{original_filename}_sayfa_{page_idx + 1}_{counter}.pdf"
                    output_path = os.path.join(output_dir, output_filename)
                    counter += 1

                with open(output_path, "wb") as output_pdf_file:
                    writer.write(output_pdf_file)
                
                output_files.append(output_path)

                if progress_callback:
                    progress = int(((i + 1) / total_extracted) * 100)
                    progress_callback(progress)
                
                if self.logger:
                    self.logger.info(f"Sayfa çıkarıldı: {output_path}")

            pdf_document.close()
            return True, f"Sayfa çıkarma işlemi başarılı. {len(output_files)} dosya oluşturuldu.", output_files

        except Exception as e:
            error_msg = f"PDF sayfa çıkarma işlemi başarısız: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            
            # Hata durumunda oluşturulan dosyaları temizle
            self._cleanup_files(output_files)
            if 'pdf_document' in locals() and not pdf_document.is_closed:
                pdf_document.close()
            return False, error_msg, []
    
    def _parse_page_ranges(self, range_text: str, total_pages: int) -> List[List[int]]:
        """
        Sayfa aralıkları metnini ayrıştırır ve sayfa listesi listesi döndürür.
        Bu metod PdfSplitter'dan kopyalanmıştır.
        """
        result = []
        if not range_text or range_text.strip() == "":
            return result
            
        parts = range_text.split(",")
        
        for part in parts:
            part = part.strip()
            if "-" in part:
                try:
                    start, end = part.split("-", 1)
                    start = int(start.strip())
                    end = int(end.strip())
                    
                    start = max(1, start) - 1
                    end = min(total_pages, end) - 1
                    
                    if start <= end:
                        result.append(list(range(start, end + 1)))
                except:
                    continue
            else:
                try:
                    page = int(part)
                    page = max(1, page) - 1
                    
                    if 0 <= page < total_pages:
                        result.append([page])
                except:
                    continue
                    
        return result

    def _cleanup_files(self, file_paths: List[str]):
        """Oluşturulan dosyaları temizler."""
        for path in file_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except:
                pass 