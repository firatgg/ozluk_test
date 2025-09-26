"""
Ayarlar penceresi modülü.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QMessageBox, QFrame, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from ..styles import (CARD_STYLE, HEADER_LABEL_STYLE, FORM_STYLE, 
                     PRIMARY_BUTTON_STYLE, SECONDARY_BUTTON_STYLE)
from ...utils.settings import load_settings, save_settings, get_scale_factor, set_scale_factor, get_scale_name, get_scale_options

class SettingsWindow(QWidget):
    """Ayarlar penceresi."""
    
    # Ayarlar değiştiğinde sinyal gönder
    settings_changed = pyqtSignal()
    scale_changed = pyqtSignal(float)  # Ölçek değiştiğinde
    
    def __init__(self, parent=None):
        """
        Args:
            parent: Üst widget
        """
        super().__init__(parent)
        self.setWindowTitle(self.tr("Ayarlar"))
        self.setFixedSize(480, 380)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)
        
        # Pencereyi ortalamak için
        if parent:
            parent_geometry = parent.geometry()
            x = parent_geometry.x() + (parent_geometry.width() - 480) // 2
            y = parent_geometry.y() + (parent_geometry.height() - 380) // 2
            self.move(x, y)
        
        self.setup_ui()
        self.load_current_settings()
        
    def setup_ui(self):
        """Kullanıcı arayüzünü oluştur."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlık
        title_label = QLabel(self.tr("Ayarlar"))
        title_label.setStyleSheet(HEADER_LABEL_STYLE)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Ayarlar kartı
        settings_card = QFrame()
        settings_card.setStyleSheet(CARD_STYLE)
        card_layout = QVBoxLayout(settings_card)
        card_layout.setSpacing(20)
        card_layout.setContentsMargins(25, 25, 25, 25)
        
        # Program ölçeği ayarı
        scale_layout = QHBoxLayout()
        scale_label = QLabel("Program Ölçeği:")
        scale_label.setStyleSheet("""
            QLabel {
                color: #2C3E50;
                font-size: 14px;
                font-weight: bold;
                padding: 5px 0;
                min-width: 120px;
            }
        """)
        
        self.scale_combo = QComboBox()
        # Dinamik olarak ölçek seçeneklerini yükle
        scale_options = get_scale_options()
        for option_text, _ in scale_options:
            self.scale_combo.addItem(option_text)
        self.scale_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #7F8C8D;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
                selection-background-color: #ECF0F1;
                font-size: 14px;
                min-height: 20px;
                min-width: 180px;
            }
            QComboBox:focus {
                border: 2px solid #3498DB;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
                padding-right: 5px;
            }
            QComboBox::down-arrow {
                image: none;
                border: 2px solid #7F8C8D;
                width: 0px;
                height: 0px;
                border-top: 5px solid #7F8C8D;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-bottom: none;
            }
        """)
        
        # Ölçek değişikliği sinyalini bağla
        self.scale_combo.currentTextChanged.connect(self.on_scale_preview)
        
        scale_layout.addWidget(scale_label)
        scale_layout.addWidget(self.scale_combo)
        scale_layout.addStretch()
        card_layout.addLayout(scale_layout)
        
        # Boş alan ekle
        card_layout.addStretch()
        
        # Butonlar
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.cancel_button = QPushButton(self.tr("İptal"))
        self.cancel_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        self.cancel_button.clicked.connect(self.close)
        self.cancel_button.setMinimumWidth(100)
        
        self.save_button = QPushButton(self.tr("Kaydet"))
        self.save_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        self.save_button.clicked.connect(self.save_settings)
        self.save_button.setMinimumWidth(100)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        card_layout.addLayout(button_layout)
        
        layout.addWidget(settings_card)
        
    def load_current_settings(self):
        """Mevcut ayarları yükle."""
        # Qt Settings'den ölçek faktörünü al
        current_scale = get_scale_factor()
        
        # En yakın seçeneği bul ve ayarla
        scale_options = get_scale_options()
        closest_option = None
        min_diff = float('inf')
        
        for option_text, scale_value in scale_options:
            diff = abs(current_scale - scale_value)
            if diff < min_diff:
                min_diff = diff
                closest_option = option_text
                
        if closest_option:
            self.scale_combo.setCurrentText(closest_option)
            
    def save_settings(self):
        """Ayarları kaydet."""
        try:
            # Seçilen ölçek faktörünü bul
            current_text = self.scale_combo.currentText()
            scale_options = get_scale_options()
            scale_factor = 1.0  # varsayılan
            
            for option_text, scale_value in scale_options:
                if current_text == option_text:
                    scale_factor = scale_value
                    break
                
            # Qt Settings ile kaydet
            set_scale_factor(scale_factor)
            
            # Ayarları anında uygula
            self.apply_settings_immediately(scale_factor)
            
            # Başarı mesajı
            QMessageBox.information(
                self, 
                "Başarılı", 
                "Program ölçeği başarıyla kaydedildi ve uygulandı."
            )
            
            # Pencereyi kapat
            self.close()
                
        except Exception as e:
            QMessageBox.critical(
                self, 
                self.tr("Hata"), 
                self.tr("Ayarlar kaydedilirken beklenmeyen bir hata oluştu:\n{error}").format(error=str(e))
            )
            
    def apply_settings_immediately(self, scale_factor: float):
        """Ayarları anında uygula."""
        try:
            print(f"Program ölçeği anında uygulama: {scale_factor}")
            
            # Sinyal gönder - Ana pencere bunu alacak ve uygulayacak
            self.scale_changed.emit(scale_factor)
            
            print("Ölçek sinyali gönderildi")
            
        except Exception as e:
            print(f"Ayarları uygularken hata: {e}")
            
    def on_scale_preview(self, text):
        """Ölçek değiştiğinde önizleme göster."""
        try:
            # Seçilen ölçek faktörünü bul
            scale_options = get_scale_options()
            scale_factor = 1.0  # varsayılan
            
            for option_text, scale_value in scale_options:
                if text == option_text:
                    scale_factor = scale_value
                    break
                
            print(f"Ölçek önizleme: {scale_factor}")
                
            # Ayarlar penceresinin ölçeğini anında değiştir (önizleme için)
            # Font boyutunu ölçeğe göre ayarla
            base_font_size = 14
            preview_font_size = int(base_font_size * scale_factor)
            preview_font = QFont("Segoe UI", preview_font_size)
            
            self.setFont(preview_font)
            
            # Tüm alt widget'ları da güncelle
            for child in self.findChildren(QWidget):
                if hasattr(child, 'setFont'):
                    child.setFont(preview_font)
            
            # Pencereyi yeniden çiz
            self.update()
            
        except Exception as e:
            print(f"Ölçek önizleme hatası: {e}")
