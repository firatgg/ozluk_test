"""
PDF dosyalarını yeniden adlandırma işlemlerini gerçekleştiren modül.
"""
import os
import shutil
from typing import List, Tuple, Optional, Dict, Any
from PyPDF2 import PdfReader

class PdfRenamer:
    """PDF dosyalarını yeniden adlandırma işlemlerini yöneten sınıf."""
    
    def __init__(self, logger=None):
        """
        Args:
            logger: Loglama nesnesi (opsiyonel)
        """
        self.logger = logger
    
    def check_pdf(self, file_path: str) -> Tuple[bool, str]:
        """
        PDF dosyasının geçerliliğini kontrol eder.
        
        Args:
            file_path: Kontrol edilecek dosyanın yolu
            
        Returns:
            Tuple[bool, str]: (Geçerli mi?, Hata mesajı)
        """
        try:
            if not os.path.exists(file_path):
                return False, "Dosya bulunamadı"
                
            if os.path.getsize(file_path) == 0:
                return False, "Dosya boş"
                
            # PDF header kontrolü
            with open(file_path, 'rb') as f:
                header = f.read(4)
                if header != b'%PDF':
                    return False, "Geçerli bir PDF dosyası değil"
                    
            # PyPDF2 ile açılabilirlik kontrolü
            PdfReader(file_path)
            return True, ""
            
        except Exception as e:
            return False, f"PDF kontrolü başarısız: {str(e)}"
    
    def rename_pdfs(self,
                   file_paths: List[str],
                   output_dir: str,
                   options: Optional[Dict[str, Any]] = None,
                   progress_callback: Optional[callable] = None) -> Tuple[bool, str, List[str]]:
        """
        PDF dosyalarını yeniden adlandırır.

        Args:
            file_paths: İşlenecek PDF dosyalarının yolları
            output_dir: Çıktı klasörü
            options: Yeniden adlandırma seçenekleri (new_name, keep_originals)
            progress_callback: İlerleme durumunu bildiren fonksiyon

        Returns:
            Tuple[bool, str, List[str]]: (Başarılı mı?, Mesaj, İşlenen dosyalar)
        """
        if options is None:
            options = {}

        new_name = options.get("new_name")
        if not new_name:
            return False, "Yeni dosya adı belirtilmemiş.", []

        keep_originals = options.get("keep_originals", True)

        try:
            # Çıktı klasörünü kontrol et/oluştur
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # Orijinal dosyalar klasörü
            original_dir = os.path.join(output_dir, "Orijinal_Dosyalar")
            if keep_originals:
                os.makedirs(original_dir, exist_ok=True)
            
            processed_files = []
            total_files = len(file_paths)
            
            for i, file_path in enumerate(file_paths):
                try:
                    # PDF kontrolü
                    is_valid, error = self.check_pdf(file_path)
                    if not is_valid:
                        raise ValueError(f"Geçersiz PDF: {error}")
                    
                    # Orijinal dosyayı kopyala
                    if keep_originals:
                        original_name = os.path.basename(file_path)
                        original_target = os.path.join(original_dir, original_name)
                        shutil.copy2(file_path, original_target)
                        
                    # Yeni isimle kopyala
                    new_filename = f"{new_name}_{i+1}.pdf"
                    new_path = os.path.join(output_dir, new_filename)
                    
                    # Aynı isimde dosya varsa yeni isim oluştur
                    counter = 1
                    while os.path.exists(new_path):
                        new_filename = f"{new_name}_{i+1}_{counter}.pdf"
                        new_path = os.path.join(output_dir, new_filename)
                        counter += 1
                    
                    shutil.copy2(file_path, new_path)
                    processed_files.append(new_path)
                    
                    # İlerleme bildirimi
                    if progress_callback:
                        progress = int(((i + 1) / total_files) * 100)
                        progress_callback(progress)
                    
                    if self.logger:
                        self.logger.info(f"Dosya yeniden adlandırıldı: {new_path}")
                        
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Dosya işlenirken hata: {str(e)}")
                    raise
            
            return True, "İşlem başarılı", processed_files
            
        except Exception as e:
            error_msg = f"PDF'ler yeniden adlandırılırken hata oluştu: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            
            # Hata durumunda temizlik
            self._cleanup_files(processed_files)
            if keep_originals and os.path.exists(original_dir) and not os.listdir(original_dir):
                os.rmdir(original_dir)
                
            return False, error_msg, []
    
    def _cleanup_files(self, file_paths: List[str]):
        """İşlenmiş dosyaları temizler."""
        for path in file_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except:
                pass 