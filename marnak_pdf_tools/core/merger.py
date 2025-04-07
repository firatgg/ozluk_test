"""
PDF dosyalarını birleştirme işlemlerini gerçekleştiren modül.
"""
import os
from typing import List, Tuple, Optional
from PyPDF2 import PdfReader, PdfWriter

class PdfMerger:
    """PDF dosyalarını birleştirme işlemlerini yöneten sınıf."""
    
    def __init__(self, logger=None):
        """
        Args:
            logger: Loglama nesnesi (opsiyonel)
        """
        self.logger = logger
    
    def merge_pdfs(self, 
                  file_paths: List[str], 
                  output_path: str,
                  progress_callback: Optional[callable] = None) -> Tuple[bool, str]:
        """
        PDF dosyalarını birleştirir.
        
        Args:
            file_paths: Birleştirilecek PDF dosyalarının yolları
            output_path: Çıktı dosyasının yolu
            progress_callback: İlerleme durumunu bildiren fonksiyon
            
        Returns:
            Tuple[bool, str]: (Başarılı mı?, Mesaj)
        """
        try:
            # Çıktı klasörünü kontrol et/oluştur
            output_dir = os.path.dirname(output_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # PDF birleştirici oluştur
            merger = PdfWriter()
            total_files = len(file_paths)
            
            # Her dosyayı kontrol et ve birleştir
            for i, file_path in enumerate(file_paths):
                try:
                    # PDF kontrolü
                    if not os.path.exists(file_path):
                        raise FileNotFoundError(f"Dosya bulunamadı: {file_path}")
                    
                    # PDF'i aç ve sayfaları ekle
                    pdf = PdfReader(file_path)
                    if len(pdf.pages) == 0:
                        raise ValueError(f"PDF dosyası boş: {file_path}")
                    
                    for page in pdf.pages:
                        merger.add_page(page)
                    
                    # İlerleme bildirimi
                    if progress_callback:
                        progress = int(((i + 1) / total_files) * 100)
                        progress_callback(progress)
                    
                    if self.logger:
                        self.logger.info(f"Dosya eklendi: {file_path}")
                        
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Dosya işlenirken hata: {str(e)}")
                    raise
            
            # Birleştirilmiş PDF'i kaydet
            with open(output_path, 'wb') as output_file:
                merger.write(output_file)
            
            if self.logger:
                self.logger.info(f"Birleştirme tamamlandı: {output_path}")
            
            return True, "Birleştirme işlemi başarılı"
            
        except Exception as e:
            error_msg = f"PDF birleştirme işlemi başarısız: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            
            # Hata durumunda çıktı dosyasını temizle
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except:
                    pass
            
            return False, error_msg 