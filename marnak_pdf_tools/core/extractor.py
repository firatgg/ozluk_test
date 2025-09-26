"""
PDF sayfalarını çıkarma işlemlerini gerçekleştiren modül.
"""
import os
from typing import List, Tuple, Optional, Any, Dict
from PyPDF2 import PdfReader, PdfWriter
import fitz # PyMuPDF
from .utils import parse_page_ranges

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
                      progress_callback: Optional[callable] = None,
                      interrupt_check: Optional[callable] = None) -> Tuple[bool, str, List[str]]:
        """
        PDF dosyasından belirtilen sayfa aralıklarını çıkarır.
        
        Args:
            file_path: PDF dosyasının yolu
            output_dir: Çıktı klasörü
            options: Çıkarma seçenekleri (extract_all, page_range, file_prefix)
            progress_callback: İlerleme durumunu bildiren fonksiyon
            interrupt_check: İşlem iptal edildi mi kontrol eden fonksiyon
            
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
                    # İptal kontrolü
                    if interrupt_check and interrupt_check():
                        pdf_document.close()
                        return False, "İşlem kullanıcı tarafından iptal edildi.", []
                    
                    pages_to_extract.append(i)
            else:
                # Sayfa aralığını ayrıştır (merkezi fonksiyon kullan)
                parsed_ranges = parse_page_ranges(page_range_str, total_pages)
                for page_list in parsed_ranges:
                    for page_num in page_list:
                        # İptal kontrolü
                        if interrupt_check and interrupt_check():
                            pdf_document.close()
                            return False, "İşlem kullanıcı tarafından iptal edildi.", []
                        
                        if 0 <= page_num < total_pages:
                            pages_to_extract.append(page_num)
                pages_to_extract = sorted(list(set(pages_to_extract))) # Tekrarları kaldır ve sırala

            if not pages_to_extract:
                pdf_document.close()
                return False, "Çıkarılacak geçerli sayfa bulunamadı.", []

            total_extracted = len(pages_to_extract)
            for i, page_idx in enumerate(pages_to_extract):
                # İptal kontrolü
                if interrupt_check and interrupt_check():
                    pdf_document.close()
                    return False, "İşlem kullanıcı tarafından iptal edildi.", output_files
                
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
    

    def _cleanup_files(self, file_paths: List[str]):
        """Oluşturulan dosyaları temizler."""
        for path in file_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except:
                pass 