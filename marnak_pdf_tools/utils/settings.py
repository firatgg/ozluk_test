"""
Uygulama ayarlarını yöneten modül.
"""
import json
import os
from typing import Dict, Any
from PyQt6.QtCore import QSettings

def get_settings_file_path() -> str:
    """Ayarlar dosyasının yolunu döndürür."""
    # Kullanıcının AppData dizininde ayarlar dosyası oluştur
    app_data_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "MarnakPDFTools")
    os.makedirs(app_data_dir, exist_ok=True)
    return os.path.join(app_data_dir, "settings.json")

def load_settings() -> Dict[str, Any]:
    """
    Ayarları dosyadan yükler.
    
    Returns:
        Dict[str, Any]: Ayarlar sözlüğü
    """
    settings_file = get_settings_file_path()
    
    # Varsayılan ayarlar
    default_settings = {
        "default_output_dir": "",
        "default_file_prefix": "sayfa_",
        "window_geometry": None,
        "last_used_directory": "",
        "remember_settings": True,
        "font_size": 14,
        "language": "tr"
    }
    
    try:
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as f:
                loaded_settings = json.load(f)
                # Varsayılan ayarlarla birleştir
                default_settings.update(loaded_settings)
    except Exception as e:
        # Hata durumunda varsayılan ayarları kullan
        print(f"Ayarlar yüklenirken hata: {e}")
    
    return default_settings

def save_settings(settings: Dict[str, Any]) -> bool:
    """
    Ayarları dosyaya kaydeder.
    
    Args:
        settings: Kaydedilecek ayarlar sözlüğü
        
    Returns:
        bool: Kaydetme başarılı mı?
    """
    try:
        settings_file = get_settings_file_path()
        
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
                
        return True
    except Exception as e:
        print(f"Ayarlar kaydedilirken hata: {e}")
        return False

def reset_settings() -> bool:
    """
    Ayarları varsayılan değerlere sıfırlar.
    
    Returns:
        bool: Sıfırlama başarılı mı?
    """
    try:
        settings_file = get_settings_file_path()
        if os.path.exists(settings_file):
            os.remove(settings_file)
        return True
    except Exception as e:
        print(f"Ayarlar sıfırlanırken hata: {e}")
        return False

# Qt'nin kendi QSettings sistemi
def get_qt_settings():
    """Qt'nin kendi ayar sistemini döndür."""
    return QSettings("Marnak", "PDFTools")

def get_scale_factor():
    """Mevcut ölçek faktörünü döndür."""
    settings = get_qt_settings()
    return settings.value("scale_factor", 1.0, type=float)

def set_scale_factor(scale: float):
    """Ölçek faktörünü ayarla."""
    settings = get_qt_settings()
    settings.setValue("scale_factor", scale)

def get_scale_name():
    """Mevcut ölçek adını döndür."""
    scale = get_scale_factor()
    if scale <= 0.75:
        return "Çok Küçük"
    elif scale <= 0.85:
        return "Küçük"
    elif scale <= 0.95:
        return "Biraz Küçük"
    elif scale <= 1.05:
        return "Normal"
    elif scale <= 1.15:
        return "Biraz Büyük"
    elif scale <= 1.25:
        return "Büyük"
    else:
        return "Çok Büyük"

def get_scale_options():
    """Mevcut ölçek seçeneklerini döndür."""
    return [
        ("Çok Küçük (75%)", 0.75),
        ("Küçük (85%)", 0.85),
        ("Biraz Küçük (95%)", 0.95),
        ("Normal (100%)", 1.0),
        ("Biraz Büyük (105%)", 1.05),
        ("Büyük (115%)", 1.15),
        ("Çok Büyük (125%)", 1.25)
    ]
