"""
Hover ile açılan PDF önizleme popup bileşeni.
"""
import os
import threading
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QGraphicsDropShadowEffect, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize, QRect, QPoint
from PyQt6.QtGui import QPixmap, QFont, QPainter, QColor, QCursor
import fitz  # PyMuPDF

from ..styles import get_card_style, get_header_style, get_scaled_styles


class PdfPreviewPopup(QWidget):
    """Hover ile açılan PDF önizleme popup penceresi."""
    
    # Sinyaller
    preview_closed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pdf_path = None
        self.pdf_document = None
        # Daha büyük önizleme boyutu
        self.preview_size = QSize(450, 600)
        
        # Pencere ayarları - daha basit yaklaşım
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        # Transparent background'u kaldırıyoruz - sorun çıkarıyor
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.init_ui()
        # Shadow effect kaldırıldı - popup sorunlarına neden olabilir
        # self.setup_shadow_effect()
        
        # Mouse tracking
        self.setMouseTracking(True)
        
        # Hide timer
        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_preview)
        
    def init_ui(self):
        """UI bileşenlerini oluştur."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(0)
        
        # Ana kart
        self.card = QFrame()
        self.card.setObjectName("preview_card")
        layout.addWidget(self.card)
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(10)
        
        # Başlık
        self.title_label = QLabel("PDF Önizleme")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setObjectName("preview_title")
        card_layout.addWidget(self.title_label)
        
        # PDF görüntü alanı
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(self.preview_size)
        self.image_label.setMaximumSize(self.preview_size)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                background-color: white;
                padding: 10px;
            }
        """)
        card_layout.addWidget(self.image_label)
        
        # Dosya bilgisi
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setObjectName("preview_info")
        self.info_label.setWordWrap(True)
        card_layout.addWidget(self.info_label)
        
        # Stilleri uygula
        self.refresh_styles()
        
    def setup_shadow_effect(self):
        """Gölge efekti ekle."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(shadow)
        
    def refresh_styles(self):
        """Dinamik stilleri yenile."""
        try:
            s = get_scaled_styles()
            
            # Kart stili
            card_style = f"""
            QFrame#preview_card {{
                background-color: white;
                border-radius: {s['border_radius_large']}px;
                border: 1px solid #E0E0E0;
            }}
            """
            self.card.setStyleSheet(card_style)
            
            # Başlık stili
            title_style = f"""
            QLabel#preview_title {{
                color: #2C3E50;
                font-size: {s['font_size_large']}px;
                font-weight: bold;
                padding: {s['padding_small']}px 0;
                border-bottom: 2px solid #3498DB;
                margin-bottom: {s['margin_small']}px;
            }}
            """
            self.title_label.setStyleSheet(title_style)
            
            # Bilgi stili
            info_style = f"""
            QLabel#preview_info {{
                color: #7F8C8D;
                font-size: {s['font_size_small']}px;
                padding: {s['padding_small']}px 0;
            }}
            """
            self.info_label.setStyleSheet(info_style)
            
            # Boyut güncelle - daha büyük base boyutlar
            base_width = 450
            base_height = 600
            scale_factor = s['font_size_normal'] / 14  # Ölçek faktörü
            
            scaled_width = int(base_width * scale_factor)
            scaled_height = int(base_height * scale_factor)
            
            self.preview_size = QSize(scaled_width, scaled_height)
            self.image_label.setMinimumSize(self.preview_size)
            self.image_label.setMaximumSize(self.preview_size)
            
            print(f"Preview boyutu güncellendi: {scaled_width}x{scaled_height} (ölçek: {scale_factor})")
            
        except Exception as e:
            print(f"Preview stilleri yenilenirken hata: {e}")
            
    def show_preview(self, pdf_path: str, position: QPoint):
        """PDF önizlemesini göster."""
        try:
            print(f"Popup show_preview çağrıldı: {pdf_path}")
            
            # Önceki PDF'i temizle
            self.clear_preview()
            print("Önceki preview temizlendi")
            
            self.pdf_path = pdf_path
            
            # Dosya adı
            file_name = os.path.basename(pdf_path)
            if len(file_name) > 35:
                display_name = file_name[:15] + "..." + file_name[-15:]
            else:
                display_name = file_name
            self.title_label.setText(display_name)
            print(f"Başlık ayarlandı: {display_name}")
            
            # PDF yükle ve render et
            self.load_and_render_pdf()
            
            # Pozisyonu ayarla
            self.position_popup(position)
            
            # Göster
            self.show()
            self.raise_()
            self.activateWindow()
            print("Popup gösterildi")
            
        except Exception as e:
            print(f"PDF önizleme gösterilirken hata: {e}")
            import traceback
            traceback.print_exc()
            
    def clear_preview(self):
        """Önceki önizlemeyi temizle."""
        try:
            # PDF belgesini kapat
            if self.pdf_document:
                self.pdf_document.close()
                self.pdf_document = None
                
            # Görüntüyü temizle
            self.image_label.clear()
            self.info_label.clear()
            
            # Başlığı sıfırla
            self.title_label.setText("PDF Önizleme")
            
        except Exception as e:
            print(f"Preview temizlenirken hata: {e}")
            
    def load_and_render_pdf(self):
        """PDF'i yükle ve ilk sayfayı render et."""
        print(f"PDF render başlıyor: {self.pdf_path}")
        
        if not self.pdf_path or not os.path.exists(self.pdf_path):
            print("Dosya bulunamadı")
            self.show_error("Dosya bulunamadı")
            return
            
        try:
            # PDF belgesini aç
            print("PDF belgesi açılıyor...")
            self.pdf_document = fitz.open(self.pdf_path)
            
            if len(self.pdf_document) == 0:
                print("PDF boş")
                self.show_error("PDF boş")
                return
                
            print(f"PDF açıldı, sayfa sayısı: {len(self.pdf_document)}")
                
            # İlk sayfayı render et
            page = self.pdf_document[0]
            
            # Ölçek hesapla - daha yüksek kalite için
            page_rect = page.rect
            available_width = self.preview_size.width() - 30  # Daha fazla padding
            available_height = self.preview_size.height() - 30
            
            scale_x = available_width / page_rect.width
            scale_y = available_height / page_rect.height
            scale = min(scale_x, scale_y, 3.0)  # Maksimum 3x büyütme (daha yüksek kalite)
            
            print(f"Render ölçeği: {scale}, boyut: {self.preview_size}")
            
            # Sayfayı pixmap'e render et
            mat = fitz.Matrix(scale, scale)
            pix = page.get_pixmap(matrix=mat)
            
            # PyQt6 QPixmap'e çevir
            img_data = pix.tobytes("ppm")
            pixmap = QPixmap()
            pixmap.loadFromData(img_data)
            
            print(f"Pixmap oluşturuldu: {pixmap.size()}")
            
            # Görüntüyü label'a set et
            self.image_label.setPixmap(pixmap)
            
            # Dosya bilgisi
            file_size = os.path.getsize(self.pdf_path) / (1024 * 1024)  # MB
            info_text = f"📄 {len(self.pdf_document)} sayfa\n💾 {file_size:.1f} MB"
            self.info_label.setText(info_text)
            
            print("PDF render tamamlandı")
            
        except Exception as e:
            print(f"PDF render hatası: {e}")
            import traceback
            traceback.print_exc()
            self.show_error("PDF yüklenemedi")
            
    def show_error(self, message: str):
        """Hata mesajı göster."""
        self.image_label.setText(f"❌\n{message}")
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #E74C3C;
                border-radius: 8px;
                background-color: #FADBD8;
                color: #C0392B;
                font-size: 14px;
                padding: 20px;
            }
        """)
        self.info_label.setText("")
        
    def position_popup(self, mouse_pos: QPoint):
        """Popup'ı mouse pozisyonuna göre konumlandır."""
        try:
            # Ekran boyutlarını al
            screen = QApplication.primaryScreen().geometry()
            
            # Popup boyutunu hesapla (daha büyük olduğu için)
            self.adjustSize()  # Widget boyutunu güncelle
            popup_size = self.size()
            
            print(f"Popup boyutu: {popup_size}, Ekran: {screen.size()}")
            
            # Varsayılan pozisyon: mouse'un sağ altı
            offset = 20  # Daha büyük offset
            x = mouse_pos.x() + offset
            y = mouse_pos.y() + offset
            
            # Ekran sınırlarını kontrol et - daha büyük popup için
            if x + popup_size.width() > screen.right() - 20:
                x = mouse_pos.x() - popup_size.width() - offset  # Sol tarafa koy
                
            if y + popup_size.height() > screen.bottom() - 20:
                y = mouse_pos.y() - popup_size.height() - offset  # Üst tarafa koy
                
            # Minimum pozisyon kontrolü
            x = max(20, x)
            y = max(20, y)
            
            # Maksimum pozisyon kontrolü (ekrandan taşmasın)
            x = min(x, screen.right() - popup_size.width() - 20)
            y = min(y, screen.bottom() - popup_size.height() - 20)
            
            print(f"Popup pozisyonu: ({x}, {y})")
            self.move(x, y)
            
        except Exception as e:
            print(f"Popup konumlandırma hatası: {e}")
            self.move(mouse_pos.x() + 20, mouse_pos.y() + 20)
            
    def leaveEvent(self, event):
        """Mouse popup'tan çıktığında kapat."""
        # Basit yaklaşım - hemen kapat
        self.hide_preview()
        super().leaveEvent(event)
        
    def hide_preview(self):
        """Önizlemeyi gizle."""
        try:
            self.hide()
            
            # Önizlemeyi temizle
            self.clear_preview()
            
            # Sinyal gönder
            self.preview_closed.emit()
            
        except Exception as e:
            print(f"Preview kapatılırken hata: {e}")
            
    def closeEvent(self, event):
        """Pencere kapatılırken temizlik yap."""
        self.hide_preview()
        super().closeEvent(event)
