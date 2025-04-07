"""
Dosya işlemleri için yardımcı fonksiyonlar.
"""
import os
import platform
import subprocess

def open_file(file_path):
    """
    Dosya veya dizini işletim sisteminin varsayılan uygulamasıyla açar.
    
    Args:
        file_path: Açılacak dosya veya dizinin yolu
        
    Raises:
        Exception: Dosya açılamazsa
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dosya veya dizin bulunamadı: {file_path}")
    
    try:
        # İşletim sistemine göre uygun komutu çalıştır
        if platform.system() == 'Windows':
            os.startfile(file_path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.call(['open', file_path])
        else:  # Linux
            subprocess.call(['xdg-open', file_path])
        return True
    except Exception as e:
        raise Exception(f"Dosya açılırken hata oluştu: {str(e)}") 