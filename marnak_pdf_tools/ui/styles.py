"""
Uygulama genelinde kullanılan stil tanımlamaları.
"""
from ..utils.settings import get_scale_factor

def scale_value(base_value: int) -> int:
    """Değeri mevcut ölçek faktörüne göre ölçekle."""
    scale = get_scale_factor()
    return int(base_value * scale)

def get_scaled_styles():
    """Ölçeklenmiş stilleri döndür."""
    scale = get_scale_factor()
    return {
        'font_size_small': scale_value(12),
        'font_size_normal': scale_value(14), 
        'font_size_large': scale_value(16),
        'font_size_xlarge': scale_value(18),
        'font_size_xxlarge': scale_value(22),
        'font_size_xxxlarge': scale_value(24),
        'padding_small': scale_value(5),
        'padding_normal': scale_value(10),
        'padding_large': scale_value(15),
        'padding_xlarge': scale_value(20),
        'margin_small': scale_value(5),
        'margin_normal': scale_value(10),
        'margin_large': scale_value(15),
        'border_radius': scale_value(6),
        'border_radius_small': scale_value(4),
        'border_radius_large': scale_value(8),
        'button_height': scale_value(40),
        'menu_width': scale_value(200),
        'min_window_width': scale_value(1200),
        'min_window_height': scale_value(800)
    }

# Kurumsal Renkler
CORP_BLUE = "#2C3E50"       # Koyu lacivert - ana renk
CORP_LIGHT_BLUE = "#ECF0F1" # Açık gri-mavi
CORP_DARK_BLUE = "#1A252F"  # Çok koyu lacivert
CORP_ACCENT = "#3498DB"     # Vurgu mavi
CORP_GRAY = "#F8F9FA"       # Arkaplan açık gri
CORP_DARK_GRAY = "#7F8C8D"  # Metin gri
CORP_TEXT = "#2C3E50"       # Ana metin rengi
CORP_SUCCESS = "#2ECC71"    # Başarı rengi

# Eski Facebook Renkleri (referans olarak kalsın)
FB_BLUE = "#1877F2"         # Facebook ana mavi
FB_LIGHT_BLUE = "#E7F3FF"   # Açık mavi arkaplan
FB_DARK_BLUE = "#166FE5"    # Koyu mavi (hover ve butonlar için)
FB_GRAY = "#F0F2F5"         # Arkaplan gri
FB_DARK_GRAY = "#65676B"    # Metin gri
FB_TEXT = "#050505"         # Ana metin rengi
FB_GREEN = "#42B72A"        # Facebook yeşil (butonlar için)

# Marnak Lojistik Kurumsal Renkleri (referans olarak kalsın)
MARNAK_BLUE = "#0066B3"
MARNAK_GREEN = "#3AB54A"
MARNAK_LIGHT_BLUE = "#E5F1F9"
MARNAK_LIGHT_GREEN = "#E8F5EA"
MARNAK_GRAY = "#F5F5F5"
MARNAK_DARK_GRAY = "#E0E0E0"
MARNAK_TEXT = "#333333"

# Ana pencere stili
MAIN_WINDOW_STYLE = """
    QMainWindow {
        background-color: """ + CORP_GRAY + """;
    }
"""

# Menü widget'ı stili
MENU_WIDGET_STYLE = f"""
    QWidget {{
        background-color: {CORP_BLUE};
        border-right: 1px solid {CORP_DARK_BLUE};
    }}
"""

def get_menu_header_style():
    """Ölçeklenmiş menü başlık stilini döndür."""
    s = get_scaled_styles()
    return f"""
    QLabel {{
        color: white;
        font-size: {s['font_size_xxlarge']}px;
        font-weight: bold;
        padding: {s['padding_normal']}px {s['padding_small']}px;
        text-align: center;
    }}
    """

# Geriye uyumluluk için
MENU_HEADER_STYLE = get_menu_header_style()

def get_menu_button_style():
    """Ölçeklenmiş menü düğme stilini döndür."""
    s = get_scaled_styles()
    return f"""
    QPushButton {{
        background-color: transparent;
        color: white;
        border: none;
        border-radius: {s['border_radius']}px;
        padding: {s['padding_normal'] + 2}px;
        text-align: left;
        font-size: {s['font_size_normal']}px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: rgba(255, 255, 255, 0.15);
    }}
    QPushButton:pressed {{
        background-color: rgba(255, 255, 255, 0.25);
    }}
    """

# Geriye uyumluluk için
MENU_BUTTON_STYLE = get_menu_button_style()

# İçerik widget'ı stili
CONTENT_WIDGET_STYLE = """
    QWidget {
        background-color: white;
    }
"""

# Responsive stiller
RESPONSIVE_CONTAINER = f"""
    QWidget {{
        margin: 0;
        padding: 0;
    }}
"""

def get_header_style():
    """Ölçeklenmiş başlık stilini döndür."""
    s = get_scaled_styles()
    return f"""
    QLabel {{
        color: {CORP_BLUE};
        font-size: {s['font_size_xxxlarge']}px;
        font-weight: bold;
        padding: {s['padding_normal']}px 0;
    }}
    """

# Modern başlık stili
HEADER_STYLE = get_header_style()

def get_subheader_style():
    """Ölçeklenmiş alt başlık stilini döndür."""
    s = get_scaled_styles()
    return f"""
    QLabel {{
        color: {CORP_BLUE};
        font-size: {s['font_size_xlarge']}px;
        font-weight: bold;
        padding: {s['padding_small']}px 0;
    }}
    """

# Modern alt başlık stili
SUBHEADER_STYLE = get_subheader_style()

# Modern bölüm başlığı stili
SECTION_TITLE_STYLE = f"""
    QLabel {{
        color: {CORP_BLUE};
        font-size: 16px;
        font-weight: bold;
        padding-bottom: 5px;
        border-bottom: 2px solid {CORP_ACCENT};
        margin-top: 10px;
        margin-bottom: 10px;
    }}
"""

def get_card_style():
    """Ölçeklenmiş kart stilini döndür."""
    s = get_scaled_styles()
    return f"""
    QWidget {{
        background-color: white;
        border-radius: {s['border_radius']}px;
        padding: {s['padding_large']}px;
        border: 1px solid #E0E0E0;
    }}
    """

# Modern kart stili
CARD_STYLE = get_card_style()

def get_button_style():
    """Ölçeklenmiş düğme stilini döndür."""
    s = get_scaled_styles()
    return f"""
    QPushButton {{
        background-color: {CORP_BLUE};
        color: white;
        border: none;
        border-radius: {s['border_radius_small']}px;
        padding: {s['padding_small'] + 3}px {s['padding_large'] + 1}px;
        font-weight: bold;
        font-size: {s['font_size_normal']}px;
        min-height: {s['button_height'] - 20}px;
    }}
    QPushButton:hover {{
        background-color: {CORP_DARK_BLUE};
    }}
    QPushButton:pressed {{
        background-color: {CORP_DARK_BLUE};
    }}
    QPushButton:disabled {{
        background-color: #BEC3C9;
        color: #F5F6F7;
    }}
    """

# Düğme stili
BUTTON_STYLE = get_button_style()

def get_primary_button_style():
    """Ölçeklenmiş birincil düğme stilini döndür."""
    s = get_scaled_styles()
    return f"""
    QPushButton {{
        background-color: {MARNAK_BLUE};
        color: white;
        border: none;
        border-radius: {s['border_radius_large']}px;
        padding: {s['padding_normal']}px {s['padding_xlarge']}px;
        font-weight: bold;
        font-size: {s['font_size_small'] + 1}px;
        min-height: {s['button_height'] - 10}px;
    }}
    QPushButton:hover {{
        background-color: #005599;
    }}
    QPushButton:pressed {{
        background-color: #004477;
    }}
    QPushButton:disabled {{
        background-color: #CCCCCC;
        color: #666666;
    }}
    """

# Birincil buton stili
PRIMARY_BUTTON_STYLE = get_primary_button_style()

def get_secondary_button_style():
    """Ölçeklenmiş ikincil düğme stilini döndür."""
    s = get_scaled_styles()
    return f"""
    QPushButton {{
        background-color: {MARNAK_LIGHT_BLUE};
        color: {MARNAK_BLUE};
        border: 2px solid {MARNAK_BLUE};
        border-radius: {s['border_radius_large']}px;
        padding: {s['padding_normal']}px {s['padding_xlarge']}px;
        font-size: {s['font_size_small'] + 1}px;
        font-weight: bold;
        min-height: {s['button_height'] - 10}px;
    }}
    QPushButton:hover {{
        background-color: #D5E6F3;
        border-color: {MARNAK_GREEN};
        color: {MARNAK_GREEN};
    }}
    QPushButton:pressed {{
        background-color: #C5DBE8;
    }}
    QPushButton:disabled {{
        background-color: #F5F5F5;
        border-color: #CCCCCC;
        color: #666666;
    }}
    """

# İkincil buton stili
SECONDARY_BUTTON_STYLE = get_secondary_button_style()

# Başarı düğme stili
GREEN_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {CORP_ACCENT};
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
        font-size: 14px;
    }}
    QPushButton:hover {{
        background-color: #2980B9;
    }}
    QPushButton:pressed {{
        background-color: #1F618D;
    }}
    QPushButton:disabled {{
        background-color: #BEC3C9;
        color: #F5F6F7;
    }}
"""

# Adım göstergeleri stilleri
STEP_INDICATOR_STYLE = f"""
    QWidget {{
        background-color: {CORP_LIGHT_BLUE};
        border-radius: 6px;
    }}
"""

ACTIVE_STEP_STYLE = f"""
    QLabel {{
        color: {CORP_BLUE};
        font-weight: bold;
        background-color: white;
        border: 1px solid {CORP_ACCENT};
        border-radius: 4px;
        padding: 8px 16px;
    }}
"""

INACTIVE_STEP_STYLE = f"""
    QLabel {{
        color: {CORP_DARK_GRAY};
        background-color: transparent;
        border: 1px solid {CORP_DARK_GRAY};
        border-radius: 4px;
        padding: 8px 16px;
    }}
"""

SEPARATOR_STYLE = f"""
    QFrame {{
        color: #E0E0E0;
    }}
"""

ARROW_STYLE = f"""
    QLabel {{
        color: {CORP_DARK_GRAY};
        font-size: 16px;
        font-weight: bold;
    }}
"""

# Hata ve bilgi kutuları
ERROR_LABEL_STYLE = f"""
    QLabel {{
        color: #C0392B;
        background-color: #FADBD8;
        border: 1px solid #E74C3C;
        border-radius: 4px;
        padding: 8px;
    }}
"""

INFO_LABEL_STYLE = f"""
    QLabel {{
        color: {CORP_BLUE};
        background-color: {CORP_LIGHT_BLUE};
        border: 1px solid #BDC3C7;
        border-radius: 4px;
        padding: 8px;
    }}
"""

# Aranabilir seçim kutusu stili
SEARCH_COMBOBOX_STYLE = f"""
    QComboBox {{
        border: 1px solid #BDC3C7;
        border-radius: 4px;
        padding: 8px;
        background-color: white;
    }}
    QComboBox:hover {{
        border: 1px solid {CORP_ACCENT};
    }}
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 25px;
        border-left-width: 0px;
    }}
"""

# İlerleme çubuğu stili
PROGRESS_BAR_STYLE = f"""
    QProgressBar {{
        border: 1px solid #BDC3C7;
        border-radius: 4px;
        text-align: center;
        background-color: white;
    }}

    QProgressBar::chunk {{
        background-color: {CORP_ACCENT};
        border-radius: 3px;
    }}
"""

# Metin giriş alanı stili
TEXT_INPUT_STYLE = f"""
    QLineEdit {{
        border: 1px solid #BDC3C7;
        border-radius: 4px;
        padding: 8px;
        background-color: white;
    }}
    QLineEdit:hover {{
        border: 1px solid {CORP_ACCENT};
    }}
    QLineEdit:focus {{
        border: 2px solid {CORP_ACCENT};
    }}
"""

# Liste widget stili
LIST_WIDGET_STYLE = f"""
    QListWidget {{
        border: 1px solid #BDC3C7;
        border-radius: 4px;
        background-color: white;
        padding: 4px;
    }}
    
    QListWidget::item {{
        border-radius: 3px;
        padding: 4px;
        margin: 2px;
    }}
    
    QListWidget::item:selected {{
        background-color: {CORP_LIGHT_BLUE};
        color: {CORP_BLUE};
    }}
    
    QListWidget::item:hover {{
        background-color: #F5F5F5;
    }}
"""

# Sürükle bırak alanı stili
DRAG_DROP_STYLE = f"""
    QFrame {{
        background-color: {CORP_LIGHT_BLUE};
        border: 2px dashed {CORP_ACCENT};
        border-radius: 4px;
    }}
"""

# Dosya listesi stili
FILE_LIST_STYLE = f"""
    QListWidget {{
        border: 1px solid {CORP_DARK_GRAY};
        border-radius: 4px;
        padding: 8px;
        background-color: white;
        font-size: 13px;
        min-height: 150px;
    }}
    QListWidget::item {{
        border-bottom: 1px solid #ECF0F1;
        padding: 10px;
        margin: 2px 0;
        border-radius: 3px;
    }}
    QListWidget::item:selected {{
        background-color: {CORP_LIGHT_BLUE};
        color: {CORP_BLUE};
        border: none;
    }}
    QListWidget::item:hover {{
        background-color: #F8F9FA;
    }}
"""

# Modern form stili
FORM_STYLE = f"""
    QLabel {{
        color: {CORP_TEXT};
        font-size: 14px;
        font-weight: bold;
        padding: 5px 0;
    }}
    QLineEdit, QComboBox, QSpinBox {{
        border: 1px solid {CORP_DARK_GRAY};
        border-radius: 4px;
        padding: 8px;
        background-color: white;
        selection-background-color: {CORP_LIGHT_BLUE};
        font-size: 14px;
        min-height: 20px;
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
        border: 2px solid {CORP_ACCENT};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QSpinBox::up-button, QSpinBox::down-button {{
        border-radius: 3px;
        width: 20px;
        background-color: {CORP_LIGHT_BLUE};
    }}
    QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
        background-color: #D6DBDF;
    }}
"""

# Modern onay kutusu stili
CHECKBOX_STYLE = f"""
    QCheckBox {{
        color: {CORP_TEXT};
        font-size: 14px;
        spacing: 5px;
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 1px solid {CORP_DARK_GRAY};
        border-radius: 3px;
    }}
    QCheckBox::indicator:checked {{
        background-color: {CORP_ACCENT};
        border: 1px solid {CORP_ACCENT};
        image: url(icons/check-white.png);
    }}
    QCheckBox::indicator:hover {{
        border: 1px solid {CORP_ACCENT};
    }}
"""

# Modern radio düğmesi stili
RADIO_STYLE = f"""
    QRadioButton {{
        color: {CORP_TEXT};
        font-size: 14px;
        spacing: 5px;
    }}
    QRadioButton::indicator {{
        width: 18px;
        height: 18px;
        border: 1px solid {CORP_DARK_GRAY};
        border-radius: 9px;
    }}
    QRadioButton::indicator:checked {{
        background-color: {CORP_ACCENT};
        border: 1px solid {CORP_ACCENT};
        image: url(icons/circle-white.png);
    }}
    QRadioButton::indicator:hover {{
        border: 1px solid {CORP_ACCENT};
    }}
"""

# Bilgi kutusu stili
INFO_BOX_STYLE = f"""
    QLabel {{
        background-color: {CORP_LIGHT_BLUE};
        border-radius: 4px;
        padding: 10px;
        color: {CORP_BLUE};
        font-style: italic;
    }}
"""

# Kaydırma çubuğu stili
SCROLLBAR_STYLE = f"""
    QScrollBar:vertical {{
        border: none;
        background: {CORP_GRAY};
        width: 8px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {CORP_DARK_GRAY};
        min-height: 20px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {CORP_BLUE};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}
"""

# Tablo stili
TABLE_STYLE = f"""
    QTableView {{
        border: 1px solid #BDC3C7;
        background-color: white;
        gridline-color: #ECF0F1;
        border-radius: 4px;
    }}
    
    QTableView::item {{
        padding: 6px;
    }}
    
    QTableView::item:selected {{
        background-color: {CORP_LIGHT_BLUE};
        color: {CORP_BLUE};
    }}
    
    QHeaderView::section {{
        background-color: {CORP_BLUE};
        color: white;
        padding: 8px;
        border: none;
        font-weight: bold;
    }}
"""

# Durum Kartı Stili
STATUS_CARD_STYLE = f"""
    QFrame {{
        background-color: white;
        border: 1px solid #E0E0E0;
        border-radius: 4px;
        padding: 10px;
        margin-top: 10px;
    }}
""" 

# HeaderLabel Stili
HEADER_LABEL_STYLE = f"""
    QLabel {{
        color: {MARNAK_BLUE};
        font-size: 18px;
        font-weight: bold;
        padding: 10px;
    }}
"""

# InfoLabel Stili
INFO_LABEL_STYLE = f"""
    QLabel {{
        color: {MARNAK_BLUE};
        font-size: 13px;
        padding: 5px;
    }}
"""

# ErrorLabel Stili
ERROR_LABEL_STYLE = """
    QLabel {
        color: red;
        font-size: 13px;
        padding: 5px;
    }
"""

# Mesaj kutuları ve diğer metinler 