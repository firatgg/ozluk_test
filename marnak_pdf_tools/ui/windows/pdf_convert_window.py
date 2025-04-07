import os
import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QComboBox, QMessageBox, QSplitter, QLineEdit,
    QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QFont, QIcon, QColor

from marnak_pdf_tools.ui.components.drag_drop import DragDropWidget
from marnak_pdf_tools.ui.components import FileListWidget
from marnak_pdf_tools.ui.styles import (
    BUTTON_STYLE, HEADER_STYLE, ACTIVE_STEP_STYLE, INACTIVE_STEP_STYLE, 
    STATUS_CARD_STYLE, SEPARATOR_STYLE, ARROW_STYLE,
    ERROR_LABEL_STYLE, INFO_LABEL_STYLE, GREEN_BUTTON_STYLE
)
from marnak_pdf_tools.utils import open_file


class PDFConvertWindow(QWidget):
    """PDF dönüştürme penceresi."""
    
    convert_requested = pyqtSignal(list, str, dict)
    
    def __init__(self, pdf_service, parent=None):
        super().__init__(parent)
        self.pdf_service = pdf_service
        self.output_dir = None
        self.is_compact_mode = False
        self.format_options = {
            "PDF - PDF": {"input": "pdf", "output": "pdf", "enabled": True},
            "PDF - PNG": {"input": "pdf", "output": "png", "enabled": True},
            "PDF - JPEG": {"input": "pdf", "output": "jpeg", "enabled": True},
            "PDF - TIFF": {"input": "pdf", "output": "tiff", "enabled": True},
            "PDF - SVG": {"input": "pdf", "output": "svg", "enabled": True},
            "PDF - DOCX": {"input": "pdf", "output": "docx", "enabled": False, "message": "DOCX dönüşümü yakında!"},
            "PNG - PDF": {"input": "png", "output": "pdf", "enabled": False, "message": "Görüntüden PDF yakında!"},
            "JPEG - PDF": {"input": "jpeg", "output": "pdf", "enabled": False, "message": "Görüntüden PDF yakında!"},
        }
        
        self.init_ui()
    
    def resizeEvent(self, event):
        """Pencere boyutlandırıldığında arayüzü uyarla."""
        super().resizeEvent(event)
        
        is_now_compact = self.width() < 900
        
        # Mod değiştiyse UI'ı güncelle
        if is_now_compact != self.is_compact_mode:
            self.is_compact_mode = is_now_compact
            
            if is_now_compact:
                # Kompakt mod ayarları
                self.splitter.setOrientation(Qt.Orientation.Vertical)
                self.splitter.setSizes([int(self.height() * 0.5), int(self.height() * 0.5)])
            else:
                # Normal mod ayarları
                self.splitter.setOrientation(Qt.Orientation.Horizontal)
                self.splitter.setSizes([int(self.width() * 0.5), int(self.width() * 0.5)])
                
    def init_ui(self):
        """Arayüzü oluşturur."""
        # Ana düzen
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Başlık ekle
        header_label = QLabel("PDF Dönüştürme")
        header_label.setStyleSheet(HEADER_STYLE)
        main_layout.addWidget(header_label)
        
        # Adım göstergeleri
        step_widget = QWidget()
        step_layout = QHBoxLayout(step_widget)
        step_layout.setContentsMargins(0, 0, 0, 0)
        
        self.step1_label = QLabel("1. Dosya Seçimi")
        self.step1_label.setStyleSheet(ACTIVE_STEP_STYLE)
        step_layout.addWidget(self.step1_label)
        
        arrow_label = QLabel("➔")
        arrow_label.setStyleSheet(ARROW_STYLE)
        step_layout.addWidget(arrow_label)
        
        self.step2_label = QLabel("2. Format Seçimi")
        self.step2_label.setStyleSheet(INACTIVE_STEP_STYLE)
        step_layout.addWidget(self.step2_label)
        
        arrow_label2 = QLabel("➔")
        arrow_label2.setStyleSheet(ARROW_STYLE)
        step_layout.addWidget(arrow_label2)
        
        self.step3_label = QLabel("3. Dönüştürme")
        self.step3_label.setStyleSheet(INACTIVE_STEP_STYLE)
        step_layout.addWidget(self.step3_label)
        
        step_layout.addStretch()
        main_layout.addWidget(step_widget)
        
        # Ayırıcı çizgi
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(SEPARATOR_STYLE)
        main_layout.addWidget(separator)
        
        # Splitter (Sol ve Sağ panel bölücü)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # SOL PANEL - Dosya seçimi
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 10, 0)
        
        # Dosya sürükle-bırak alanı
        self.drag_drop = DragDropWidget("PDF veya görüntü dosyalarını buraya sürükleyin")
        self.drag_drop.files_dropped.connect(self.add_files)
        self.drag_drop.setMinimumHeight(120)
        left_layout.addWidget(self.drag_drop)
        
        # Dosya seçme düğmesi
        self.select_files_btn = QPushButton("Dosya Seç")
        self.select_files_btn.setStyleSheet(BUTTON_STYLE)
        self.select_files_btn.clicked.connect(self.select_files)
        left_layout.addWidget(self.select_files_btn)
        
        # Bilgi etiketi
        left_info = QLabel("Dönüştürmek istediğiniz PDF veya görüntü dosyalarını seçin.")
        left_info.setWordWrap(True)
        left_layout.addWidget(left_info)
        
        # Dosya listesi
        self.file_list = FileListWidget()
        self.file_list.item_count_changed.connect(self.update_button_state)
        left_layout.addWidget(self.file_list, 1)
        
        self.splitter.addWidget(left_panel)
        
        # SAĞ PANEL - Dönüştürme ayarları
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        # Format seçim bölümü
        format_label = QLabel("Dönüştürme Formatı:")
        right_layout.addWidget(format_label)
        
        self.format_combo = QComboBox()
        
        # Format seçeneklerini ekle
        for format_name, format_data in self.format_options.items():
            self.format_combo.addItem(format_name)
            
            # Devre dışı formatları disable et
            if not format_data["enabled"]:
                index = self.format_combo.count() - 1
                self.format_combo.setItemData(index, 0, Qt.ItemDataRole.UserRole - 1)
        
        self.format_combo.currentIndexChanged.connect(self.update_button_state)
        right_layout.addWidget(self.format_combo)
        
        # Format bilgisi
        self.format_info = QLabel()
        self.format_info.setWordWrap(True)
        self.format_info.setStyleSheet(INFO_LABEL_STYLE)
        right_layout.addWidget(self.format_info)
        
        # Dosya kayıt ayarları
        output_label = QLabel("Çıktı Dizini:")
        right_layout.addWidget(output_label)
        
        # Dizin seçme
        output_layout = QHBoxLayout()
        
        self.select_dir_btn = QPushButton("Dizin Seç")
        self.select_dir_btn.setStyleSheet(BUTTON_STYLE)
        self.select_dir_btn.clicked.connect(self.select_output_dir)
        output_layout.addWidget(self.select_dir_btn)
        
        right_layout.addLayout(output_layout)
        
        # Dönüştürme düğmesi
        self.convert_btn = QPushButton("Dönüştür")
        self.convert_btn.setStyleSheet(GREEN_BUTTON_STYLE)
        self.convert_btn.setEnabled(False)
        self.convert_btn.clicked.connect(self.start_conversion)
        right_layout.addWidget(self.convert_btn)
        
        # Durum kartı
        status_card = QFrame()
        status_card.setStyleSheet(STATUS_CARD_STYLE)
        status_layout = QVBoxLayout(status_card)
        
        # İlerleme çubuğu
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.hide()
        status_layout.addWidget(self.progress)
        
        # Bilgi etiketi
        self.info_label = QLabel("")
        self.info_label.setStyleSheet(INFO_LABEL_STYLE)
        self.info_label.hide()
        status_layout.addWidget(self.info_label)
        
        # Hata etiketi
        self.error_label = QLabel("")
        self.error_label.setStyleSheet(ERROR_LABEL_STYLE)
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        status_layout.addWidget(self.error_label)
        
        right_layout.addWidget(status_card)
        
        # Boşluk ekle
        right_layout.addStretch()
        
        self.splitter.addWidget(right_panel)
        
        # Splitter'ı ana düzene ekle
        main_layout.addWidget(self.splitter, 1)
        
        # Pencere ayarları
        self.setMinimumSize(900, 600)
        self.setWindowTitle("PDF Dönüştürme")
        
        # Format bilgisini güncelle
        self.update_format_info() 

    def add_files(self, file_paths):
        """Sürükle-bırak ile dosya ekler."""
        # Desteklenen dosya türlerini kontrol et
        supported_exts = ['.pdf', '.png', '.jpg', '.jpeg']
        valid_files = [f for f in file_paths if os.path.splitext(f)[1].lower() in supported_exts]
        
        # Geçerli dosyaları ekle
        if valid_files:
            self.file_list.add_files(valid_files)
            
            # Adımları güncelle
            if self.file_list.count() > 0:
                self.step1_label.setStyleSheet(INACTIVE_STEP_STYLE)
                self.step2_label.setStyleSheet(ACTIVE_STEP_STYLE)
                
                # Format seçimini aktif yap
                self.update_format_info()
                
            # Düğme durumunu güncelle
            self.update_button_state()
            
        elif file_paths:
            # Desteklenmeyen dosya formatı hatası
            self.show_error("Yalnızca PDF, PNG, JPG ve JPEG dosyaları desteklenmektedir.")
    
    def select_files(self):
        """Dosya seçme dialogunu açar."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Dönüştürülecek Dosyaları Seç",
            "",
            "Desteklenen Dosyalar (*.pdf *.png *.jpg *.jpeg)"
        )
        
        if files:
            self.add_files(files)
            
    def update_format_info(self):
        """Format bilgisini günceller."""
        current_format = self.format_combo.currentText()
        format_data = self.format_options.get(current_format, {})
        
        if not format_data:
            self.format_info.hide()
            return
            
        if not format_data.get("enabled", True):
            # Devre dışı format için mesaj göster
            self.format_info.setText(format_data.get("message", "Bu format şu anda desteklenmiyor."))
            self.format_info.show()
            return
            
        # Format bilgisini göster
        input_format = format_data.get("input", "").upper()
        output_format = format_data.get("output", "").upper()
        
        if input_format == "pdf" and output_format in ["png", "jpeg", "tiff", "svg"]:
            self.format_info.setText(f"PDF dosyanız {output_format} görüntülerine dönüştürülecek.")
        else:
            self.format_info.setText(f"{input_format} dosyalarınız {output_format} formatına dönüştürülecek.")
            
        self.format_info.show()
    
    def select_output_dir(self):
        """Çıktı dizini seçme dialogunu açar."""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Çıktı Dizini Seç"
        )
        
        if dir_path:
            self.output_dir = dir_path
            self.select_dir_btn.setText(f"Dizin: {dir_path}")
            
            # Düğme durumunu güncelle
            self.update_button_state()
    
    def update_button_state(self):
        """Düğme durumunu günceller."""
        has_files = self.file_list.count() > 0
        current_format = self.format_combo.currentText()
        format_data = self.format_options.get(current_format, {})
        is_format_enabled = format_data.get("enabled", False)
        
        # Dönüştürme düğmesini etkinleştir/devre dışı bırak
        self.convert_btn.setEnabled(has_files and is_format_enabled)
        
        # Adım durumlarını güncelle
        if has_files:
            self.step1_label.setStyleSheet(INACTIVE_STEP_STYLE)
            self.step2_label.setStyleSheet(ACTIVE_STEP_STYLE)
            
            if is_format_enabled:
                self.step3_label.setStyleSheet(INACTIVE_STEP_STYLE)
            else:
                self.step3_label.setStyleSheet(INACTIVE_STEP_STYLE)
        else:
            self.step1_label.setStyleSheet(ACTIVE_STEP_STYLE)
            self.step2_label.setStyleSheet(INACTIVE_STEP_STYLE)
            self.step3_label.setStyleSheet(INACTIVE_STEP_STYLE)
        
        # Format bilgisini güncelle
        self.update_format_info()
    
    def start_conversion(self):
        """Dönüştürme işlemini başlatır."""
        # Girdileri kontrol et
        if self.file_list.count() == 0:
            self.show_error("Lütfen en az bir dosya seçin.")
            return
            
        # Geçerli bir format seçildiğinden emin ol
        current_format = self.format_combo.currentText()
        format_data = self.format_options.get(current_format, {})
        
        if not format_data or not format_data.get("enabled", False):
            self.show_error("Lütfen geçerli bir dönüştürme formatı seçin.")
            return
            
        # Dosyaların varlığını kontrol et
        invalid_files = []
        for file_path in self.file_list.get_files():
            if not os.path.exists(file_path):
                invalid_files.append(file_path)
        
        if invalid_files:
            error_message = "Aşağıdaki dosyalar bulunamadı:\n"
            for file in invalid_files[:5]:  # En fazla 5 dosya göster
                try:
                    file_name = os.path.basename(file)
                except:
                    file_name = str(file)
                error_message += f"- {file_name}\n"
            
            if len(invalid_files) > 5:
                error_message += f"... ve {len(invalid_files) - 5} dosya daha."
            
            self.show_error(error_message)
            return
            
        # Çıktı dizini kontrolü
        output_dir = self.output_dir
        if not output_dir:
            # Varsayılan olarak ilk dosyanın dizinini kullan
            first_file = self.file_list.get_files()[0]
            output_dir = os.path.dirname(first_file)
            
        # Dizinin yazılabilir olup olmadığını kontrol et
        if not os.path.isdir(output_dir) or not os.access(output_dir, os.W_OK):
            self.show_error(f"Seçilen dizin yazılabilir değil: {output_dir}")
            return
            
        # İşlemi onaylat
        input_format = format_data.get("input", "").upper()
        output_format = format_data.get("output", "").upper()
        file_count = self.file_list.count()
        
        confirm = QMessageBox.question(
            self,
            "Dönüştürme İşlemini Onayla",
            f"<b>{file_count}</b> adet {input_format} dosyası {output_format} formatına dönüştürülecek.\n\n"
            f"Hedef dizin: <b>{output_dir}</b>\n\n"
            f"İşleme devam etmek istiyor musunuz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if confirm != QMessageBox.StandardButton.Yes:
            return
            
        # İş parçacığını başlat
        try:
            # Dönüştürme için sözlük oluştur
            convert_options = {
                "output_format": format_data.get("output")
            }
            
            self.worker = self.pdf_service.create_convert_worker(
                self.file_list.get_files(),
                output_dir,
                convert_options
            )
            
            # Sinyalleri bağla
            self.worker.progress.connect(self.show_progress)
            self.worker.finished.connect(self.handle_finished)
            
            # Arayüzü güncelle
            self.progress.setValue(0)
            self.progress.show()
            self.info_label.setText("Dönüştürme işlemi başlatılıyor...")
            self.info_label.show()
            self.error_label.hide()
            self.convert_btn.setEnabled(False)
            
            # Adımları güncelle
            self.step2_label.setStyleSheet(INACTIVE_STEP_STYLE)
            self.step3_label.setStyleSheet(ACTIVE_STEP_STYLE)
            
            # İş parçacığını başlat
            self.worker.start()
        except Exception as e:
            self.show_error(f"Dönüştürme işlemi başlatılamadı: {str(e)}") 

    def show_progress(self, value):
        """İlerleme çubuğunu günceller."""
        self.progress.setValue(value)
        
        # İlerleme durumuna göre bilgi mesajı güncelle
        if value < 25:
            self.info_label.setText("Dosyalar hazırlanıyor...")
        elif value < 75:
            self.info_label.setText("Dosyalar dönüştürülüyor...")
        else:
            self.info_label.setText("İşlem tamamlanıyor...")
    
    def handle_finished(self, success, message):
        """İşlem tamamlandığında çağrılır."""
        self.progress.hide()
        self.convert_btn.setEnabled(True)
        
        # Adımları güncelle
        self.step3_label.setStyleSheet(INACTIVE_STEP_STYLE)
        self.step2_label.setStyleSheet(ACTIVE_STEP_STYLE)
        
        if success:
            self.info_label.setText(message)
            self.info_label.show()
            self.error_label.hide()
            
            # Sonuç mesajını göster
            output_dir = self.output_dir if self.output_dir else os.path.dirname(self.file_list.get_files()[0])
            file_count = self.file_list.count()
            
            result_message = f"{file_count} dosya başarıyla dönüştürüldü.\n\nÇıktı Dizini: {output_dir}"
            QMessageBox.information(self, "İşlem Tamamlandı", result_message)
            
            # Çıktı klasörünü açmayı teklif et
            reply = QMessageBox.question(
                self, 
                "Klasörü Aç", 
                "Çıktı klasörünü açmak ister misiniz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    open_file(output_dir)
                except Exception as e:
                    QMessageBox.warning(
                        self, 
                        "Uyarı", 
                        f"Klasör açılamadı: {str(e)}"
                    )
            
            # Arayüzü temizle
            self.clear()
        else:
            self.show_error(message)
    
    def show_error(self, message):
        """Hata mesajı gösterir."""
        self.error_label.setText(message)
        self.error_label.show()
        self.info_label.hide()
        
        # Kritik hata mesajları için kullanıcıya MessageBox da göster
        if message.startswith("Hata:") or "bulunamadı" in message:
            QMessageBox.critical(self, "Hata", message)
    
    def clear(self, persistData=False):
        """Pencereyi temizler."""
        # Dosya listesini temizle
        self.file_list.clear()
        
        if not persistData:
            # Çıktı dizini sıfırla
            self.output_dir = None
            self.select_dir_btn.setText("Dizin Seç")
            
            # Format seçimini ilk öğeye ayarla
            self.format_combo.setCurrentIndex(0)
        
        # İlerleme çubuğunu gizle
        self.progress.hide()
        
        # Bilgi etiketini güncelle ve gizle
        self.info_label.setText("")
        self.info_label.hide()
        
        # Hata etiketini gizle
        self.error_label.hide()
        
        # Adım göstergelerini sıfırla
        self.step1_label.setStyleSheet(ACTIVE_STEP_STYLE)
        self.step2_label.setStyleSheet(INACTIVE_STEP_STYLE)
        self.step3_label.setStyleSheet(INACTIVE_STEP_STYLE)
        
        # Düğme durumunu güncelle
        self.update_button_state()
        
        # DragDrop'a odak ver
        self.refocus_drag_drop()
    
    def refocus_drag_drop(self):
        """DragDropWidget'a odak vermek için çağrılır."""
        if not hasattr(self, 'drag_drop') or not self.isVisible():
            return
            
        # Önce widget'ın güncellenmesini sağla
        self.drag_drop.updateGeometry()
        self.drag_drop.repaint()
        
        # Kısa bir gecikme ile odak vermeyi dene (50ms)
        QTimer.singleShot(50, self._set_focus_to_drag_drop)
        # Daha uzun bir gecikme ile tekrar dene (ikinci şans)
        QTimer.singleShot(250, self._set_focus_to_drag_drop)
        
    def _set_focus_to_drag_drop(self):
        """DragDropWidget'a odak verme işlemi"""
        if hasattr(self, 'drag_drop') and self.isVisible() and self.drag_drop.isVisible():
            # Widget görünür ve ulaşılabilirse odak ver
            self.drag_drop.setFocus(Qt.FocusReason.OtherFocusReason)
            print("PDF Dönüştürme: DragDrop'a odak verildi.")
    
    def showEvent(self, event):
        """Pencere gösterildiğinde çağrılır."""
        super().showEvent(event)
        
        # Pencere gösterildiğinde DragDrop'a odak ver
        self.refocus_drag_drop()
        
        # Düğme durumunu güncelle
        self.update_button_state() 