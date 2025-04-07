"""
Ana pencere.
"""
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QFont

from .components import ModernButton, HeaderLabel
from .windows import (
    PDFRenameWindow,
    PDFSplitWindow,
    PDFMergeWindow
)
from .styles import (
    MAIN_WINDOW_STYLE,
    MENU_WIDGET_STYLE,
    MENU_HEADER_STYLE,
    MENU_BUTTON_STYLE,
    CONTENT_WIDGET_STYLE
)

class MainWindow(QMainWindow):
    """Ana pencere."""
    
    def __init__(self, pdf_service):
        super().__init__()
        self.pdf_service = pdf_service
        self.setWindowTitle("Marnak PDF Araçları")
        
        # İkon yolunu belirle
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(current_dir, "icons", "android-chrome-512x512.png")
        self.setWindowIcon(QIcon(icon_path))
        
        self.setMinimumSize(1000, 700)
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        
        # Menü genişliği ve açılır-kapanır durumu
        self.menu_width = 200
        self.menu_collapsed = False
        self.menu_min_width = 50
        
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
        self.header = HeaderLabel("Marnak\nPDF Araçları")
        self.header.setStyleSheet(MENU_HEADER_STYLE)
        self.menu_layout.addWidget(self.header)
        
        # Simgeler ile normal yazıları ayır
        self.menu_icons = ["📝", "✂️", "📎"]
        
        # Menü düğmeleri
        self.rename_btn = ModernButton("Yeniden Adlandır", primary=False)
        self.rename_btn.setStyleSheet(MENU_BUTTON_STYLE)
        self.menu_layout.addWidget(self.rename_btn)
        
        self.split_btn = ModernButton("Böl", primary=False)
        self.split_btn.setStyleSheet(MENU_BUTTON_STYLE)
        self.menu_layout.addWidget(self.split_btn)
        
        self.merge_btn = ModernButton("Birleştir", primary=False)
        self.merge_btn.setStyleSheet(MENU_BUTTON_STYLE)
        self.menu_layout.addWidget(self.merge_btn)
        
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
        buttons = [self.rename_btn, self.split_btn, self.merge_btn]
        
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
        self.rename_btn.setText("Yeniden Adlandır")
        self.split_btn.setText("Böl")
        self.merge_btn.setText("Birleştir")
        
        # Normal stilleri geri yükle
        self.rename_btn.setStyleSheet(MENU_BUTTON_STYLE)
        self.split_btn.setStyleSheet(MENU_BUTTON_STYLE)
        self.merge_btn.setStyleSheet(MENU_BUTTON_STYLE)
        
    def connect_signals(self):
        """Sinyal bağlantılarını kurar."""
        # Menü düğmeleri
        self.rename_btn.clicked.connect(self.show_rename_window)
        self.split_btn.clicked.connect(self.show_split_window)
        self.merge_btn.clicked.connect(self.show_merge_window)
        
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