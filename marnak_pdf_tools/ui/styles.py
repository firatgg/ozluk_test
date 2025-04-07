"""
Uygulama genelinde kullanılan stil tanımlamaları.
"""

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

# Menü başlık stili
MENU_HEADER_STYLE = """
    QLabel {
        color: white;
        font-size: 22px;
        font-weight: bold;
        padding: 10px 5px;
        text-align: center;
    }
"""

# Menü düğme stili
MENU_BUTTON_STYLE = """
    QPushButton {
        background-color: transparent;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 12px;
        text-align: left;
        font-size: 14px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: rgba(255, 255, 255, 0.15);
    }
    QPushButton:pressed {
        background-color: rgba(255, 255, 255, 0.25);
    }
"""

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

# Modern başlık stili
HEADER_STYLE = f"""
    QLabel {{
        color: {CORP_BLUE};
        font-size: 24px;
        font-weight: bold;
        padding: 10px 0;
    }}
"""

# Modern alt başlık stili
SUBHEADER_STYLE = f"""
    QLabel {{
        color: {CORP_BLUE};
        font-size: 18px;
        font-weight: bold;
        padding: 5px 0;
    }}
"""

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

# Modern kart stili
CARD_STYLE = f"""
    QWidget {{
        background-color: white;
        border-radius: 6px;
        padding: 15px;
        border: 1px solid #E0E0E0;
    }}
"""

# Düğme stili
BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {CORP_BLUE};
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
        font-size: 14px;
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

# İkincil düğme stili
SECONDARY_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {CORP_GRAY};
        color: {CORP_TEXT};
        border: 1px solid #CED0D4;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
        font-size: 14px;
    }}
    QPushButton:hover {{
        background-color: #E4E6E9;
    }}
    QPushButton:pressed {{
        background-color: #DADDE1;
    }}
    QPushButton:disabled {{
        background-color: #F5F6F7;
        color: #BEC3C9;
        border: 1px solid #DADDE1;
    }}
"""

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