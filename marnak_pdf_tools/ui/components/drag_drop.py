"""
Sürükle-bırak bileşenleri.
"""
from PyQt6.QtWidgets import QLabel, QFileDialog, QApplication
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QKeyEvent, QIcon

# Marnak Lojistik Kurumsal Renkleri
MARNAK_BLUE = "#0066B3"
MARNAK_GREEN = "#3AB54A"
MARNAK_LIGHT_BLUE = "#E5F1F9"
MARNAK_LIGHT_GREEN = "#E8F5EA"

class DragDropWidget(QLabel):
    """Modern sürükle-bırak destekli widget."""
    
    # Sinyaller
    files_dropped = pyqtSignal(list)  # Dosya yolları listesi
    
    def __init__(self, parent=None, tab_type=None):
        """
        Args:
            parent: Üst widget
            tab_type: Sekme türü (split, merge, rename, extract)
        """
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumHeight(180)  # Daha büyük, daha kolay hedeflenebilir alan
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # Odaklanma politikasını ayarla
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)  # Odak stilini etkinleştir
        self.setWordWrap(True)  # Uzun metinleri satır sonunda böl
        
        # İkon resimleri yolu
        self.pdf_icon = "📄"  # Default emoji icon
        
        # Stil tanımlamaları
        self.default_style = f"""
            QLabel {{
                border: 2px dashed {MARNAK_BLUE};
                border-radius: 12px;
                background-color: {MARNAK_LIGHT_BLUE};
                color: {MARNAK_BLUE};
                font-size: 15px;
                padding: 30px;
            }}
            QLabel:hover {{
                background-color: {MARNAK_LIGHT_GREEN};
                border-color: {MARNAK_GREEN};
                color: {MARNAK_GREEN};
                border-style: solid;
            }}
            QLabel:focus {{
                border: 3px solid {MARNAK_GREEN};
                border-radius: 12px;
                background-color: {MARNAK_LIGHT_GREEN};
                color: {MARNAK_GREEN};
                font-size: 15px;
                padding: 30px;
                outline: none;  /* Varsayılan odak gösterimini kapat */
            }}
        """
        self.drag_over_style = f"""
            QLabel {{
                border: 3px solid {MARNAK_GREEN};
                border-radius: 12px;
                background-color: {MARNAK_LIGHT_GREEN};
                color: {MARNAK_GREEN};
                font-size: 15px;
                padding: 30px;
            }}
        """
        self.focus_received_style = f"""
            QLabel {{
                border: 3px solid {MARNAK_GREEN};
                border-radius: 12px;
                background-color: {MARNAK_LIGHT_GREEN};
                color: {MARNAK_GREEN};
                font-size: 15px;
                padding: 30px;
                outline: none;  /* Varsayılan odak gösterimini kapat */
            }}
        """
        self.setStyleSheet(self.default_style)
        
        # Sekmeye göre özelleştirilmiş metinler
        tab_texts = {
            "split": "PDF dosyalarını buraya sürükleyin veya tıklayarak seçin\n\n"
                     "PDF sayfalarını ayrı dosyalara bölmek için Ctrl+V ile dosya yapıştırabilirsiniz",
            "merge": "PDF dosyalarını buraya sürükleyin veya tıklayarak seçin\n\n"
                     "Birden fazla PDF'i tek dosyada birleştirmek için Ctrl+V ile dosya yapıştırabilirsiniz",
            "rename": "PDF dosyasını buraya sürükleyin veya tıklayarak seçin\n\n"
                     "Dosyayı yeniden adlandırmak için Ctrl+V ile dosya yapıştırabilirsiniz",
            "extract": "PDF dosyasını buraya sürükleyin veya tıklayarak seçin\n\n"
                     "Belirli sayfaları çıkartmak için Ctrl+V ile dosya yapıştırabilirsiniz"
        }
        
        # Varsayılan metin veya sekmeye özel metin
        if tab_type in tab_texts:
            self.setText(f"{self.pdf_icon} {tab_texts[tab_type]}")
        else:
            self.setText(f"{self.pdf_icon} PDF dosyalarını buraya sürükleyin\n"
                         f"veya tıklayarak seçin\n\n"
                         f"Ctrl+V ile dosya yapıştırabilirsiniz")
            
        self.tab_type = tab_type
        
        # Animasyon için zamanlayıcı
        self.animation_timer = QTimer()
        self.animation_timer.setSingleShot(True)
        self.animation_timer.timeout.connect(self.reset_style)
        
        # Odak kaybını izlemek için zamanlayıcı
        self.focus_check_timer = QTimer()
        self.focus_check_timer.setInterval(500)  # 500ms'de bir kontrol et
        self.focus_check_timer.timeout.connect(self.check_focus)
        self.focus_check_timer.start()
        
    def check_focus(self):
        """Odak durumunu düzenli olarak kontrol eder ve gerekirse odak alır"""
        if not self.hasFocus() and self.isVisible() and self.parent() and self.parent().isVisible():
            # Ana pencere aktifse ve bu widget görünür durumdaysa odak almaya çalış
            window = self.window()
            if window and window.isActiveWindow():
                self.setFocus(Qt.FocusReason.MouseFocusReason)
                print("Odak yeniden alındı")
                
    def keyPressEvent(self, event: QKeyEvent):
        """Klavye olaylarını yakala"""
        # Ctrl+V kısayolu için
        # Tuş ve modifiye edici kontrolü birleştirilmiş şekilde
        try:
            is_ctrl_v = (event.key() == Qt.Key.Key_V and 
                         event.modifiers() & Qt.KeyboardModifier.ControlModifier)
            
            if is_ctrl_v:
                clipboard = QApplication.clipboard()
                mime_data = clipboard.mimeData()
                
                if mime_data and mime_data.hasUrls():
                    files = [url.toLocalFile() for url in mime_data.urls()]
                    pdf_files = [f for f in files if f.lower().endswith('.pdf')]
                    if pdf_files:
                        self.files_dropped.emit(pdf_files)
                        self.show_animation()
                        print(f"Yapıştırıldı: {len(pdf_files)} PDF dosyası")
                    else:
                        print("Yapıştırılan içerikte PDF dosyası yok")
                else:
                    print("Yapıştırılan içerikte dosya URL'si yok")
                
                # Etkinliği işle ve durdur
                event.accept()
                return
        except Exception as e:
            print(f"Ctrl+V işleme hatası: {str(e)}")
            
        # Enter tuşu dosya seçim dialogunu açar
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.open_file_dialog()
            event.accept()
            return
            
        # Diğer tuş olaylarını üst sınıfa ilet
        super().keyPressEvent(event)
        
    def showEvent(self, event):
        """Widget görünür hale geldiğinde çağrılır"""
        super().showEvent(event)
        # Kısa bir gecikme ile odak almaya çalış
        QTimer.singleShot(100, lambda: self.setFocus(Qt.FocusReason.OtherFocusReason))
        print("DragDrop widget görünür oldu")
        
    def focusInEvent(self, event):
        """Widget odak aldığında çağrılır."""
        super().focusInEvent(event)
        # Odak durumunu görsel olarak belirginleştir
        self.setStyleSheet(self.focus_received_style)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.raise_()  # Widget'ı en üste getir
        print("DragDrop widget odak aldı")
        
    def open_file_dialog(self):
        """Dosya seçim dialogunu açar"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "PDF Dosyaları Seç",
            "",
            "PDF Dosyaları (*.pdf)"
        )
        
        if files:
            self.files_dropped.emit(files)
            self.show_animation()
        
    def mousePressEvent(self, event):
        """Tıklama olayını yakala"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.setFocus()  # Tıklandığında odağı al
            self.open_file_dialog()
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Sürükleme başladığında çağrılır"""
        try:
            if event.mimeData().hasUrls():
                # Sadece PDF dosyalarını kabul et
                urls = event.mimeData().urls()
                if any(url.toLocalFile().lower().endswith('.pdf') for url in urls):
                    self.setStyleSheet(self.drag_over_style)
                    event.acceptProposedAction()
        except Exception as e:
            print(f"Sürükleme hatası: {str(e)}")
    
    def dragLeaveEvent(self, event):
        """Sürükleme alanından çıkıldığında çağrılır"""
        # Odak durumuna göre uygun stili ayarla
        if self.hasFocus():
            self.setStyleSheet(self.focus_received_style)
        else:
            self.setStyleSheet(self.default_style)
        
    def dropEvent(self, event: QDropEvent):
        """Dosya bırakıldığında çağrılır"""
        try:
            files = [url.toLocalFile() for url in event.mimeData().urls()]
            pdf_files = [f for f in files if f.lower().endswith('.pdf')]
            
            if not pdf_files:
                return
            
            # Sinyal gönder
            self.files_dropped.emit(pdf_files)
            self.show_animation()
        except Exception as e:
            print(f"Bırakma hatası: {str(e)}")
            
    def show_animation(self):
        """Başarılı dosya ekleme animasyonunu göster"""
        self.setStyleSheet(self.drag_over_style)
        self.animation_timer.start(800)  # 800ms sonra stili sıfırla
        
    def reset_style(self):
        """Stili varsayılana döndür"""
        # Eğer hala odak bu widget'taysa, odak stilini kullan
        if self.hasFocus():
            self.setStyleSheet(self.focus_received_style)
        else:
            self.setStyleSheet(self.default_style)
            
    def minimumSizeHint(self):
        """Minimum boyut önerisi"""
        return QSize(200, 180)
        
    def sizeHint(self):
        """Tercih edilen boyut önerisi"""
        return QSize(400, 200) 