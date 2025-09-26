"""
PDF önizleme bileşeni.
"""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QFont
import fitz  # PyMuPDF

from .modern_button import ModernButton
from ..styles import (
    CARD_STYLE, FORM_STYLE, PRIMARY_BUTTON_STYLE, 
    SECONDARY_BUTTON_STYLE, INFO_BOX_STYLE
)

class PdfViewer(QWidget):
    """PDF önizleme bileşeni."""
    
    # Sinyaller
    page_changed = pyqtSignal(int)  # Sayfa değiştiğinde
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pdf_document = None
        self.current_page = 0
        self.total_pages = 0
        self.page_scale = 1.0
        
        self.init_ui()
        
    def init_ui(self):
        """Kullanıcı arayüzünü oluşturur."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Başlık kaldırıldı - merge window'da başlık var
        
        # Zoom kontrolleri
        zoom_layout = QHBoxLayout()
        zoom_layout.setSpacing(10)
        
        # Zoom out butonu
        self.zoom_out_btn = ModernButton("−", primary=False)
        self.zoom_out_btn.setFixedSize(30, 30)
        self.zoom_out_btn.setToolTip("Uzaklaştır")
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        zoom_layout.addWidget(self.zoom_out_btn)
        
        # Zoom seviyesi
        self.zoom_label = QLabel("100%")
        self.zoom_label.setStyleSheet(INFO_BOX_STYLE)
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.zoom_label.setMinimumWidth(60)
        zoom_layout.addWidget(self.zoom_label)
        
        # Zoom in butonu
        self.zoom_in_btn = ModernButton("+", primary=False)
        self.zoom_in_btn.setFixedSize(30, 30)
        self.zoom_in_btn.setToolTip("Yakınlaştır")
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        zoom_layout.addWidget(self.zoom_in_btn)
        
        # Fit to width butonu
        self.fit_width_btn = ModernButton("Sığdır", primary=False)
        self.fit_width_btn.setFixedSize(60, 30)
        self.fit_width_btn.setToolTip("Genişliğe sığdır")
        self.fit_width_btn.clicked.connect(self.fit_to_width)
        zoom_layout.addWidget(self.fit_width_btn)
        
        zoom_layout.addStretch()
        layout.addLayout(zoom_layout)
        
        # Sayfa kontrolleri
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        
        # Önceki sayfa butonu
        self.prev_btn = ModernButton("◀", primary=False)
        self.prev_btn.setFixedSize(30, 30)
        self.prev_btn.setToolTip("Önceki sayfa")
        self.prev_btn.clicked.connect(self.previous_page)
        self.prev_btn.setEnabled(False)
        controls_layout.addWidget(self.prev_btn)
        
        # Sayfa bilgisi
        self.page_info_label = QLabel("Sayfa: 0 / 0")
        self.page_info_label.setStyleSheet(INFO_BOX_STYLE)
        self.page_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_info_label.setMinimumWidth(100)
        controls_layout.addWidget(self.page_info_label)
        
        # Sonraki sayfa butonu
        self.next_btn = ModernButton("▶", primary=False)
        self.next_btn.setFixedSize(30, 30)
        self.next_btn.setToolTip("Sonraki sayfa")
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setEnabled(False)
        controls_layout.addWidget(self.next_btn)
        
        layout.addLayout(controls_layout)
        
        # PDF görüntü alanı
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setFrameShape(QFrame.Shape.Box)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: #f8f8f8;
            }
        """)
        
        # PDF sayfası için label
        self.page_label = QLabel()
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_label.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        self.page_label.setText(self.tr("PDF dosyası seçin"))
        self.page_label.setMinimumSize(400, 600)
        
        self.scroll_area.setWidget(self.page_label)
        layout.addWidget(self.scroll_area, 1)  # Stretch factor 1
        
        # Zoom kontrolleri
        zoom_layout = QHBoxLayout()
        zoom_layout.setSpacing(10)
        
        zoom_out_btn = ModernButton(self.tr("Uzaklaştır"), primary=False)
        zoom_out_btn.setStyleSheet(SECONDARY_BUTTON_STYLE)
        zoom_out_btn.clicked.connect(self.zoom_out)
        zoom_layout.addWidget(zoom_out_btn)
        
        self.zoom_label = QLabel(self.tr("Zoom: 100%"))
        self.zoom_label.setStyleSheet(INFO_BOX_STYLE)
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        zoom_layout.addWidget(self.zoom_label)
        
        zoom_in_btn = ModernButton(self.tr("Yakınlaştır"), primary=False)
        zoom_in_btn.setStyleSheet(SECONDARY_BUTTON_STYLE)
        zoom_in_btn.clicked.connect(self.zoom_in)
        zoom_layout.addWidget(zoom_in_btn)
        
        layout.addLayout(zoom_layout)
        
    def load_pdf(self, file_path):
        """PDF dosyasını yükler."""
        try:
            if not os.path.exists(file_path):
                self.show_error(self.tr("Dosya bulunamadı: {}").format(file_path))
                return False
                
            # PDF belgesini aç
            self.pdf_document = fitz.open(file_path)
            self.total_pages = len(self.pdf_document)
            self.current_page = 0
            
            if self.total_pages > 0:
                self.show_page(0)
                self.update_controls()
                return True
            else:
                self.show_error(self.tr("PDF dosyası boş"))
                return False
                
        except Exception as e:
            self.show_error(self.tr("PDF yüklenirken hata: {}").format(str(e)))
            return False
    
    def show_page(self, page_number):
        """Belirtilen sayfayı gösterir."""
        if not self.pdf_document or page_number < 0 or page_number >= self.total_pages:
            return
            
        try:
            # Sayfayı al
            page = self.pdf_document[page_number]
            
            # Sayfayı görüntüye dönüştür
            mat = fitz.Matrix(self.page_scale, self.page_scale)
            pix = page.get_pixmap(matrix=mat)
            
            # QPixmap'e dönüştür
            img_data = pix.tobytes("png")
            pixmap = QPixmap()
            pixmap.loadFromData(img_data)
            
            # Label'a yerleştir
            self.page_label.setPixmap(pixmap)
            self.current_page = page_number
            
            # Sayfa bilgisini güncelle
            self.page_info_label.setText(self.tr("Sayfa: {} / {}").format(
                self.current_page + 1, self.total_pages))
            
            # Sinyal gönder
            self.page_changed.emit(self.current_page)
            
        except Exception as e:
            self.show_error(self.tr("Sayfa gösterilirken hata: {}").format(str(e)))
    
    def previous_page(self):
        """Önceki sayfaya geçer."""
        if self.current_page > 0:
            self.show_page(self.current_page - 1)
            self.update_controls()
    
    def next_page(self):
        """Sonraki sayfaya geçer."""
        if self.current_page < self.total_pages - 1:
            self.show_page(self.current_page + 1)
            self.update_controls()
    
    def zoom_in(self):
        """Yakınlaştırır."""
        if self.page_scale < 3.0:
            self.page_scale += 0.25
            self.update_zoom()
            if self.pdf_document:
                self.show_page(self.current_page)
    
    def zoom_out(self):
        """Uzaklaştırır."""
        if self.page_scale > 0.25:
            self.page_scale -= 0.25
            self.update_zoom()
            if self.pdf_document:
                self.show_page(self.current_page)
    
    def fit_to_width(self):
        """Genişliğe sığdır."""
        if not self.pdf_document or self.current_page < 0:
            return
            
        try:
            # Mevcut sayfanın genişliğini al
            page = self.pdf_document[self.current_page]
            page_width = page.rect.width
            
            # Scroll area'nın kullanılabilir genişliğini al
            available_width = self.scroll_area.viewport().width() - 20  # Padding için
            
            # Ölçek hesapla
            self.page_scale = available_width / page_width
            self.update_zoom()
            self.show_page(self.current_page)
            
        except Exception as e:
            print(f"Fit to width hatası: {e}")

    def update_zoom(self):
        """Zoom bilgisini günceller."""
        zoom_percent = int(self.page_scale * 100)
        self.zoom_label.setText(f"{zoom_percent}%")
        
        # Buton durumlarını güncelle
        self.zoom_out_btn.setEnabled(self.page_scale > 0.2)
        self.zoom_in_btn.setEnabled(self.page_scale < 3.0)
    
    def update_controls(self):
        """Kontrol butonlarının durumunu günceller."""
        if not self.pdf_document:
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            return
            
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < self.total_pages - 1)
    
    def show_error(self, message):
        """Hata mesajını gösterir."""
        self.page_label.setText(message)
        self.page_label.setStyleSheet("""
            QLabel {
                background-color: #ffe6e6;
                border: 1px solid #ff9999;
                border-radius: 4px;
                padding: 10px;
                color: #cc0000;
            }
        """)
        self.update_controls()
    
    def clear(self):
        """Önizlemeyi temizler."""
        if self.pdf_document:
            self.pdf_document.close()
            self.pdf_document = None
            
        self.current_page = 0
        self.total_pages = 0
        self.page_scale = 1.0
        
        self.page_label.setText(self.tr("PDF dosyası seçin"))
        self.page_label.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        
        self.page_info_label.setText(self.tr("Sayfa: 0 / 0"))
        self.zoom_label.setText(self.tr("Zoom: 100%"))
        self.update_controls()
    
    def closeEvent(self, event):
        """Widget kapatılırken PDF belgesini temizle."""
        if self.pdf_document:
            self.pdf_document.close()
        event.accept()
