"""
Ana pencere.
"""
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QFrame, QApplication
)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QFont

from ..components import ModernButton, HeaderLabel
from .pdf_rename_window import PDFRenameWindow
from .pdf_split_window import PDFSplitWindow
from .pdf_merge_window import PDFMergeWindow
from .pdf_extract_window import PDFExtractWindow
from .settings_window import SettingsWindow
from ..styles import (
    MAIN_WINDOW_STYLE,
    MENU_WIDGET_STYLE,
    MENU_HEADER_STYLE,
    MENU_BUTTON_STYLE,
    CONTENT_WIDGET_STYLE,
    get_menu_header_style,
    get_menu_button_style,
    get_scaled_styles,
    get_header_style,
    get_subheader_style,
    get_card_style,
    get_button_style,
    get_primary_button_style,
    get_secondary_button_style
)
from ...utils.settings import get_scale_factor

class MainWindow(QMainWindow):
    """Ana pencere."""
    
    def __init__(self, pdf_service):
        super().__init__()
        self.pdf_service = pdf_service
        self.setWindowTitle(self.tr("Marnak PDF Araçları"))
        
        # İkon yolunu belirle
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(current_dir, "icons", "android-chrome-512x512.png")
        self.setWindowIcon(QIcon(icon_path))
        
        # Ölçeklenmiş boyutları al
        s = get_scaled_styles()
        self.setMinimumSize(s['min_window_width'], s['min_window_height'])
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        
        # Menü genişliği ve açılır-kapanır durumu
        self.menu_width = s['menu_width']
        self.menu_collapsed = False
        self.menu_min_width = int(s['menu_width'] * 0.25)
        
        # Ana widget ve düzen
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sol menü
        self.menu_widget = QWidget()
        self.menu_widget.setFixedWidth(self.menu_width)
        self.menu_widget.setStyleSheet(MENU_WIDGET_STYLE)
        self.menu_layout = QVBoxLayout(self.menu_widget)
        self.menu_layout.setSpacing(10)
        self.menu_layout.setContentsMargins(10, 20, 10, 20)
        
        # Başlık
        self.header = HeaderLabel(self.tr("Marnak\nPDF Araçları"))
        self.header.setStyleSheet(MENU_HEADER_STYLE)
        self.menu_layout.addWidget(self.header)
        
        # Simgeler ile normal yazıları ayır
        self.menu_icons = ["📝", "✂️", "📎", "⚙️"]
        
        # Menü düğmeleri
        self.rename_btn = ModernButton(self.tr("Yeniden Adlandır"), primary=False)
        self.rename_btn.setStyleSheet(MENU_BUTTON_STYLE)
        self.menu_layout.addWidget(self.rename_btn)
        
        self.split_btn = ModernButton(self.tr("Böl"), primary=False)
        self.split_btn.setStyleSheet(MENU_BUTTON_STYLE)
        self.menu_layout.addWidget(self.split_btn)
        
        self.merge_btn = ModernButton(self.tr("Birleştir"), primary=False)
        self.merge_btn.setStyleSheet(MENU_BUTTON_STYLE)
        self.menu_layout.addWidget(self.merge_btn)
        
        # Ayarlar butonu
        self.settings_btn = ModernButton(self.tr("Ayarlar"), primary=False)
        self.settings_btn.setStyleSheet(MENU_BUTTON_STYLE)
        self.menu_layout.addWidget(self.settings_btn)
        
        self.menu_layout.addStretch()
        
        # Menü daraltma/genişletme düğmesi
        toggle_frame = QFrame()
        toggle_layout = QHBoxLayout(toggle_frame)
        toggle_layout.setContentsMargins(0, 0, 0, 0)
        
        self.toggle_button = QPushButton("◀")
        self.toggle_button.setFixedSize(30, 30)
        self.toggle_button.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #166FE5;
                color: white;
                border: none;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #1260C4;
            }
        """)
        self.toggle_button.clicked.connect(self.toggle_menu)
        toggle_layout.addWidget(self.toggle_button, 0, Qt.AlignmentFlag.AlignCenter)
        
        self.menu_layout.addWidget(toggle_frame, 0, Qt.AlignmentFlag.AlignCenter)
        
        self.main_layout.addWidget(self.menu_widget)
        
        # İçerik alanı
        self.content = QStackedWidget()
        self.content.setStyleSheet(CONTENT_WIDGET_STYLE)
        
        # Pencereler
        self.rename_window = PDFRenameWindow(self.pdf_service)
        self.split_window = PDFSplitWindow(self.pdf_service)
        self.merge_window = PDFMergeWindow(self.pdf_service)
        
        self.content.addWidget(self.rename_window)
        self.content.addWidget(self.split_window)
        self.content.addWidget(self.merge_window)
        
        self.main_layout.addWidget(self.content)
        
        # Sinyalleri bağla
        self.connect_signals()
        
        # Mevcut ayarları yükle ve uygula
        self.load_initial_settings()
        
    def toggle_menu(self):
        """Menüyü daralt/genişlet"""
        # Daralt/genişlet durumunu değiştir
        self.menu_collapsed = not self.menu_collapsed
        
        # Hedef genişliği belirle
        target_width = self.menu_min_width if self.menu_collapsed else self.menu_width
        
        # Animasyon oluştur
        self.animation = QPropertyAnimation(self.menu_widget, b"minimumWidth")
        self.animation.setDuration(200)
        self.animation.setStartValue(self.menu_widget.width())
        self.animation.setEndValue(target_width)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # Maksimum genişliği de ayarla
        self.menu_widget.setMaximumWidth(self.menu_widget.width())
        self.animation.valueChanged.connect(
            lambda w: self.menu_widget.setMaximumWidth(w)
        )
        
        # Kenar boşluklarını güncelle
        if self.menu_collapsed:
            self.menu_layout.setContentsMargins(5, 20, 5, 20)
        else:
            self.menu_layout.setContentsMargins(10, 20, 10, 20)
        
        # Menü düğmesini güncelle
        if self.menu_collapsed:
            self.toggle_button.setText("▶")
            
            # Yazıları gizle
            self.header.setVisible(False)
            
            # Düğmeleri güncelle - sadece simgeleri göster
            self.update_buttons_collapsed()
            
        else:
            self.toggle_button.setText("◀")
            
            # Yazıları göster
            self.header.setVisible(True)
            
            # Düğmeleri güncelle - normal hallerine çevir
            self.update_buttons_expanded()
            
        # Animasyonu başlat
        self.animation.start()
        
    def update_buttons_collapsed(self):
        """Düğmeleri daraltılmış görünüme ayarla"""
        buttons = [self.rename_btn, self.split_btn, self.merge_btn, self.settings_btn]
        
        for i, button in enumerate(buttons):
            button.setText(self.menu_icons[i])
            button.setStyleSheet(MENU_BUTTON_STYLE + """
                QPushButton {
                    text-align: center;
                    font-family: "Arial";
                    font-size: 18px;
                    padding: 5px;
                }
            """)
    
    def update_buttons_expanded(self):
        """Düğmeleri genişletilmiş görünüme ayarla"""
        self.rename_btn.setText(self.tr("Yeniden Adlandır"))
        self.split_btn.setText(self.tr("Böl"))
        self.merge_btn.setText(self.tr("Birleştir"))
        self.settings_btn.setText(self.tr("Ayarlar"))
        
        # Normal stilleri geri yükle
        self.rename_btn.setStyleSheet(MENU_BUTTON_STYLE)
        self.split_btn.setStyleSheet(MENU_BUTTON_STYLE)
        self.merge_btn.setStyleSheet(MENU_BUTTON_STYLE)
        self.settings_btn.setStyleSheet(MENU_BUTTON_STYLE)
        
    def connect_signals(self):
        """Sinyal bağlantılarını kurar."""
        # Menü düğmeleri
        self.rename_btn.clicked.connect(self.show_rename_window)
        self.split_btn.clicked.connect(self.show_split_window)
        self.merge_btn.clicked.connect(self.show_merge_window)
        self.settings_btn.clicked.connect(self.show_settings_window)
        
        # İlerleme güncellemelerini takip et
        self.pdf_service.progress_updated.connect(self.update_progress)
        
    def show_rename_window(self):
        """Yeniden adlandırma penceresini gösterir."""
        self.content.setCurrentIndex(0)
        
    def show_split_window(self):
        """Bölme penceresini gösterir."""
        self.content.setCurrentIndex(1)
        
    def show_merge_window(self):
        """Birleştirme penceresini gösterir."""
        self.content.setCurrentIndex(2)
        
    def show_settings_window(self):
        """Ayarlar penceresini gösterir."""
        self.settings_window = SettingsWindow(self)
        self.settings_window.settings_changed.connect(self.on_settings_changed)
        self.settings_window.scale_changed.connect(self.on_scale_changed)
        self.settings_window.show()
        
    def on_settings_changed(self):
        """Ayarlar değiştiğinde çağrılır."""
        # Artık ayarlar anında uygulandığı için yeniden başlatma mesajı gerekmiyor
        pass
        
    def on_scale_changed(self, scale_factor: float):
        """Program ölçeği değiştiğinde çağrılır."""
        print(f"Program ölçeği güncellendi: {scale_factor}")
        
        # QApplication seviyesinde font ölçeğini ayarla
        app = QApplication.instance()
        if app:
            base_font_size = 14
            new_font_size = int(base_font_size * scale_factor)
            new_font = QFont("Segoe UI", new_font_size)
            app.setFont(new_font)
            
            # Stilleri yeniden yükle ve uygula
            self.refresh_styles()
            
            # Tüm pencereler için ölçek güncelle
            self.update_all_windows_scale(scale_factor)
            
    def refresh_styles(self):
        """Ölçek değiştiğinde stilleri yenile."""
        try:
            # Yeni ölçeklenmiş boyutları al
            s = get_scaled_styles()
            
            # Ana pencere boyutunu güncelle
            self.setMinimumSize(s['min_window_width'], s['min_window_height'])
            
            # Menü genişliğini güncelle
            self.menu_width = s['menu_width']
            self.menu_widget.setFixedWidth(self.menu_width)
            
            # Menü stillerini yenile
            self.header.setStyleSheet(get_menu_header_style())
            
            # Menü butonlarının stillerini yenile
            menu_button_style = get_menu_button_style()
            self.rename_btn.setStyleSheet(menu_button_style)
            self.split_btn.setStyleSheet(menu_button_style)
            self.merge_btn.setStyleSheet(menu_button_style)
            self.settings_btn.setStyleSheet(menu_button_style)
            
            # Tüm içerik pencerelerinin stillerini yenile
            self.refresh_content_windows_styles()
            
            print(f"Stiller yenilendi - Menü genişliği: {self.menu_width}px")
            
        except Exception as e:
            print(f"Stiller yenilenirken hata: {e}")
            
    def refresh_content_windows_styles(self):
        """İçerik pencerelerinin stillerini yenile."""
        try:
            # Yeni dinamik stiller
            header_style = get_header_style()
            subheader_style = get_subheader_style()
            card_style = get_card_style()
            button_style = get_button_style()
            primary_button_style = get_primary_button_style()
            secondary_button_style = get_secondary_button_style()
            
            # StackedWidget içindeki tüm pencereler
            for i in range(self.content.count()):
                widget = self.content.widget(i)
                if widget and hasattr(widget, 'refresh_styles'):
                    # Eğer pencerede refresh_styles metodu varsa çağır
                    widget.refresh_styles()
                elif widget:
                    # Yoksa manuel olarak stilleri güncelle
                    self.apply_styles_to_widget(widget, {
                        'header': header_style,
                        'subheader': subheader_style,
                        'card': card_style,
                        'button': button_style,
                        'primary_button': primary_button_style,
                        'secondary_button': secondary_button_style
                    })
                    
        except Exception as e:
            print(f"İçerik penceresi stilleri yenilenirken hata: {e}")
            
    def apply_styles_to_widget(self, widget, styles):
        """Widget'a stilleri uygula."""
        try:
            # Tüm alt widget'ları bul ve stillerini güncelle
            for child in widget.findChildren(QWidget):
                if hasattr(child, 'objectName'):
                    obj_name = child.objectName()
                    if 'header' in obj_name.lower():
                        child.setStyleSheet(styles['header'])
                    elif 'card' in obj_name.lower():
                        child.setStyleSheet(styles['card'])
                        
                # Buton tipine göre stil uygula
                if hasattr(child, 'text'):  # QPushButton
                    button_text = child.text().lower()
                    if any(word in button_text for word in ['kaydet', 'save', 'başlat', 'start']):
                        child.setStyleSheet(styles['primary_button'])
                    elif any(word in button_text for word in ['iptal', 'cancel', 'kapat', 'close']):
                        child.setStyleSheet(styles['secondary_button'])
                    else:
                        child.setStyleSheet(styles['button'])
                        
        except Exception as e:
            print(f"Widget stillerini uygularken hata: {e}")
            
    def update_all_windows_scale(self, scale_factor: float):
        """Tüm pencerelerin ölçeğini güncelle."""
        base_font_size = 14
        new_font_size = int(base_font_size * scale_factor)
        new_font = QFont("Segoe UI", new_font_size)
        
        # Ana pencere
        self.setFont(new_font)
        
        # StackedWidget içindeki tüm pencereler
        for i in range(self.content.count()):
            widget = self.content.widget(i)
            if widget:
                widget.setFont(new_font)
                # Alt widget'ları da güncelle
                self.update_widget_scale_recursive(widget, new_font)
                
        # Menü widget'ı
        self.menu_widget.setFont(new_font)
        self.update_widget_scale_recursive(self.menu_widget, new_font)
        
    def update_widget_scale_recursive(self, widget, font):
        """Widget ve alt widget'larının ölçeğini recursive güncelle."""
        try:
            for child in widget.findChildren(QWidget):
                if child and hasattr(child, 'setFont'):
                    child.setFont(font)
        except:
            pass
        
            
    def load_initial_settings(self):
        """Uygulama başladığında mevcut ayarları yükle."""
        try:
            # Mevcut ölçek faktörünü yükle ve uygula
            current_scale = get_scale_factor()
            self.on_scale_changed(current_scale)
            
            print(f"Başlangıç ayarları yüklendi: Ölçek={current_scale}")
            
        except Exception as e:
            print(f"Başlangıç ayarları yüklenirken hata: {e}")
        
    def update_progress(self, value):
        """İlerleme çubuğunu günceler."""
        pass
            
    def show_error(self, message):
        """Hata mesajını gösterir."""
        current_window = self.content.currentWidget()
        if hasattr(current_window, 'show_error'):
            current_window.show_error(message)
            
    def operation_completed(self):
        """İşlem tamamlandığında çağrılır."""
        current_window = self.content.currentWidget()
        if hasattr(current_window, 'hide_progress'):
            current_window.hide_progress()
        if hasattr(current_window, 'clear'):
            current_window.clear() 