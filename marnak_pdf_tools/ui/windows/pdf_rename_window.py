"""
PDF yeniden adlandırma penceresi.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QFileDialog, QMessageBox, QTableWidget, QHeaderView,
    QPushButton, QLineEdit, QLabel, QFrame, QSplitter,
    QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QIcon, QPixmap, QResizeEvent
import os

from ..components import (
    ModernButton, ModernLineEdit, DragDropWidget,
    FileListWidget, ModernProgressBar, HeaderLabel,
    InfoLabel, ErrorLabel
)
from ..styles import (
    SECTION_TITLE_STYLE, CARD_STYLE, FILE_LIST_STYLE,
    FORM_STYLE, CHECKBOX_STYLE, RADIO_STYLE,
    INFO_BOX_STYLE, STEP_INDICATOR_STYLE,
    ACTIVE_STEP_STYLE, INACTIVE_STEP_STYLE,
    ARROW_STYLE, SEPARATOR_STYLE, SCROLLBAR_STYLE,
    GREEN_BUTTON_STYLE
)
from ...services.pdf_service import PdfService
from ...utils.file_utils import open_file

class PDFRenameWindow(QWidget):
    """PDF yeniden adlandırma penceresi."""
    
    # Sinyaller
    rename_requested = pyqtSignal(list, str, str)  # Dosya listesi, çıktı dizini, yeni ad
    
    def __init__(self, pdf_service):
        super().__init__()
        self.pdf_service = pdf_service
        
        # Veri koruma özelliği (ekranlar arası geçişte veriyi silme)
        self.persistData = True
        
        # Responsive tasarım için boyut bilgisi
        self.is_compact_mode = False
        
        # İsim giriş alanı odak takibi (Kaldırıldı)
        # self.name_input_has_focus = False
        
        # Arayüzü oluştur
        self.init_ui()
        
        # Çıktı dizini
        self.output_dir = None
        
        # İş parçacığı
        self.worker = None
        self.rename_worker = None
        
        # Buton durumunu güncelle
        self.update_button_state()
        
        # Pencere açıldığında DragDropWidget'a otomatik odaklanma (Kaldırıldı)
        # QTimer.singleShot(100, self.drag_drop.setFocus)
    
    def init_ui(self):
        """Kullanıcı arayüzünü oluşturur."""
        # Ana düzen
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlık
        header = HeaderLabel("PDF Yeniden Adlandırma")
        layout.addWidget(header)
        
        # İşlem adımları
        steps_widget = QWidget()
        steps_widget.setStyleSheet(STEP_INDICATOR_STYLE)
        steps_layout = QHBoxLayout(steps_widget)
        steps_layout.setContentsMargins(10, 10, 10, 10)
        steps_layout.setSpacing(15)
        
        # Adım etiketleri oluştur
        self.step1_label = QLabel("1. Dosya Seçimi")
        self.step1_label.setStyleSheet(ACTIVE_STEP_STYLE)
        
        self.step2_label = QLabel("2. Yeni İsim")
        self.step2_label.setStyleSheet(INACTIVE_STEP_STYLE)
        
        # Ok etiketleri
        arrow1 = QLabel("➔")
        arrow1.setStyleSheet(ARROW_STYLE)
        arrow1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Adımları düzene ekle
        steps_layout.addWidget(self.step1_label)
        steps_layout.addWidget(arrow1)
        steps_layout.addWidget(self.step2_label)
        steps_layout.addStretch()
        
        layout.addWidget(steps_widget)
        
        # Ayırıcı çizgi
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(SEPARATOR_STYLE)
        layout.addWidget(separator)
        
        # Ana içerik - bölücü
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Sol panel - Dosya listesi
        file_panel = QWidget()
        file_layout = QVBoxLayout(file_panel)
        file_layout.setContentsMargins(0, 0, 0, 0)
        file_layout.setSpacing(15)
        
        # Dosya seçimi kart widget'ı
        file_card = QWidget()
        file_card.setStyleSheet(CARD_STYLE)
        file_card_layout = QVBoxLayout(file_card)
        file_card_layout.setSpacing(15)
        
        # Dosya seçimi başlığı
        files_header = QLabel("PDF Dosyaları")
        files_header.setStyleSheet(SECTION_TITLE_STYLE)
        file_card_layout.addWidget(files_header)
        
        # Sürükle-bırak alanı
        self.drag_drop = DragDropWidget(self, "rename")
        self.drag_drop.files_dropped.connect(self.add_files)
        file_card_layout.addWidget(self.drag_drop)
        
        # Dosya seçimi düğmeleri
        buttons_layout = QHBoxLayout()
        
        select_files_btn = ModernButton("Dosya Seç", primary=False)
        select_files_btn.clicked.connect(self.select_files)
        buttons_layout.addWidget(select_files_btn)
        
        buttons_layout.addStretch()
        file_card_layout.addLayout(buttons_layout)
        
        # Dosya listesi
        self.file_list = FileListWidget()
        self.file_list.setStyleSheet(FILE_LIST_STYLE)
        self.file_list.setMaximumHeight(200)
        file_card_layout.addWidget(self.file_list)
        
        file_layout.addWidget(file_card)
        file_layout.addStretch()
        
        # Sağ panel - Ayarlar ve işlem
        settings_panel = QWidget()
        settings_layout = QVBoxLayout(settings_panel)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        settings_layout.setSpacing(15)
        
        # Yeniden adlandırma ayarları
        rename_card = QWidget()
        rename_card.setStyleSheet(CARD_STYLE)
        rename_layout = QVBoxLayout(rename_card)
        rename_layout.setSpacing(15)
        
        # Ayarlar başlığı
        settings_header = QLabel("Yeniden Adlandırma Ayarları")
        settings_header.setStyleSheet(SECTION_TITLE_STYLE)
        rename_layout.addWidget(settings_header)
        
        # Form alanları
        form_widget = QWidget()
        form_widget.setStyleSheet(FORM_STYLE)
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(15)
        
        # Yeni isim giriş alanı
        name_label = QLabel("Yeni Dosya Adı:")
        form_layout.addWidget(name_label)
        
        self.name_input = ModernLineEdit()
        self.name_input.setPlaceholderText("Örnek: yeni_dosya_adi")
        self.name_input.textChanged.connect(self.update_button_state)
        form_layout.addWidget(self.name_input)
        
        # Çıktı dizini seçimi
        output_label = QLabel("Çıktı Dizini:")
        form_layout.addWidget(output_label)
        
        self.select_dir_btn = ModernButton("Dizin Seç", primary=False)
        self.select_dir_btn.clicked.connect(self.select_output_dir)
        form_layout.addWidget(self.select_dir_btn)
        
        rename_layout.addWidget(form_widget)
        
        # İşlem düğmesi
        self.rename_btn = ModernButton("Yeniden Adlandır", primary=True)
        self.rename_btn.clicked.connect(self.start_renaming)
        self.rename_btn.setEnabled(False)
        rename_layout.addWidget(self.rename_btn)
        
        settings_layout.addWidget(rename_card)
        settings_layout.addStretch()
        
        # Panelleri bölücüye ekle
        self.splitter.addWidget(file_panel)
        self.splitter.addWidget(settings_panel)
        self.splitter.setSizes([400, 300])  # Başlangıç boyutları
        
        layout.addWidget(self.splitter)
        
        # Alt panel - İlerleme ve mesajlar
        status_widget = QWidget()
        status_layout = QVBoxLayout(status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(10)
        
        # İlerleme çubuğu
        self.progress = ModernProgressBar()
        self.progress.hide()
        status_layout.addWidget(self.progress)
        
        # Bilgi etiketi
        self.info_label = InfoLabel()
        self.info_label.hide()
        status_layout.addWidget(self.info_label)
        
        # Hata etiketi
        self.error_label = ErrorLabel()
        self.error_label.hide()
        status_layout.addWidget(self.error_label)
        
        layout.addWidget(status_widget)
    
    def resizeEvent(self, event: QResizeEvent):
        """Yeniden boyutlandırma olayı"""
        super().resizeEvent(event)
        
        # Genişliğe göre compact moda geç
        new_width = event.size().width()
        is_compact = new_width < 800
        
        # Compact mod değiştiyse UI'ı güncelle
        if is_compact != self.is_compact_mode:
            self.is_compact_mode = is_compact
            self.update_layout_mode()
            
    def update_layout_mode(self):
        """Genişliğe göre düzen modunu güncelle"""
        if self.is_compact_mode:
            # Compact mod - Yatay bölücüyü dikey hale getir
            self.splitter.setOrientation(Qt.Orientation.Vertical)
            self.splitter.setSizes([int(self.height() * 0.4), int(self.height() * 0.6)])  # Dikey modda boyutları ayarla
        else:
            # Normal mod - Yatay bölücü
            self.splitter.setOrientation(Qt.Orientation.Horizontal)
            self.splitter.setSizes([int(self.width() * 0.5), int(self.width() * 0.5)])  # Yatay modda boyutları ayarla
    
    def add_files(self, file_paths):
        """Sürükle-bırak ile dosya ekler."""
        try:
            # PDF dosyalarını filtrele
            pdf_files = [f for f in file_paths if f.lower().endswith('.pdf')]
            
            if pdf_files:
                # Dosyaları ekle
                for pdf_file in pdf_files:
                    self.file_list.add_file(pdf_file)
                
                # Varsayılan yeni isim oluştur - ilk dosya adına göre
                base_name = os.path.basename(pdf_files[0])
                file_name = os.path.splitext(base_name)[0]
                
                if len(pdf_files) > 1:
                    suggested_name = "yeni_dosya_adı"
                else:
                    suggested_name = f"{file_name}_renamed"
                
                # Yeni isim alanına yerleştir
                self.name_input.setText(suggested_name)
                
                # Adımları güncelle
                self.step1_label.setStyleSheet(INACTIVE_STEP_STYLE)
                self.step2_label.setStyleSheet(ACTIVE_STEP_STYLE)
                
                # Buton durumunu güncelle
                self.update_button_state()
                
        except Exception as e:
            self.show_error(f"Dosya eklenirken hata oluştu: {str(e)}")
            
    def select_files(self):
        """Dosya seçme dialogunu açar."""
        try:
            files, _ = QFileDialog.getOpenFileNames(
                self,
                "PDF Dosyaları Seç",
                "",
                "PDF Dosyaları (*.pdf)"
            )
            
            if files:
                # Seçilen dosyaları ekle
                self.add_files(files)
                
        except Exception as e:
            self.show_error(f"Dosya seçilirken hata oluştu: {str(e)}")
                
    def select_output_dir(self):
        """Çıktı dizini seçme dialogunu açar."""
        try:
            dir_path = QFileDialog.getExistingDirectory(
                self,
                "Çıktı Dizini Seç"
            )
            
            if dir_path:
                self.output_dir = dir_path
                self.select_dir_btn.setText(f"Dizin: {dir_path}")
                
                # Buton durumunu güncelle
                self.update_button_state()
                
        except Exception as e:
            self.show_error(f"Çıktı dizini seçilirken hata oluştu: {str(e)}")
            
    def start_renaming(self):
        """Yeniden adlandırma işlemini başlatır."""
        # Girdileri kontrol et
        if self.file_list.count() == 0:
            self.show_error("Lütfen en az bir PDF dosyası seçin.")
            return
        
        new_name = self.name_input.text().strip()
        if not new_name:
            self.show_error("Lütfen yeni dosya adını girin.")
            return
        
        # Geçersiz karakterleri kontrol et
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            if char in new_name:
                self.show_error(f"Dosya adında geçersiz karakter kullanılamaz: {char}")
                return
        
        # Dosyaların varlığını kontrol et
        source_files = self.file_list.get_files()
        if not source_files:
            self.show_error("Seçili PDF dosyası bulunamadı.")
            return
        
        # Tüm dosyaların varlığını ve erişim izinlerini kontrol et
        invalid_files = []
        for file_path in source_files:
            if not os.path.exists(file_path):
                invalid_files.append(f"{os.path.basename(file_path)} (bulunamadı)")
            elif not os.access(file_path, os.R_OK):
                invalid_files.append(f"{os.path.basename(file_path)} (okuma izni yok)")
        
        if invalid_files:
            error_message = "Aşağıdaki dosyalar işlenemez:\n"
            for file in invalid_files[:5]:  # En fazla 5 dosya göster
                error_message += f"- {file}\n"
            
            if len(invalid_files) > 5:
                error_message += f"... ve {len(invalid_files) - 5} dosya daha."
            
            self.show_error(error_message)
            return
        
        # Hedef dizinin yazılabilir olup olmadığını kontrol et
        output_dir = self.output_dir if self.output_dir else os.path.dirname(source_files[0])
        
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                self.show_error(f"Hedef dizin oluşturulamadı: {str(e)}")
                return
        
        # Dizin yazma izni kontrolü
        if not os.access(output_dir, os.W_OK):
            self.show_error(f"Hedef dizine yazma izni yok: {output_dir}")
            return
        
        # İşlemi onaylat
        file_count = len(source_files)
        confirm_message = ""
        
        if file_count == 1:
            source_name = os.path.basename(source_files[0])
            new_filename = f"{new_name}.pdf"
            confirm_message = f"<b>{source_name}</b> dosyası <b>{new_filename}</b> olarak yeniden adlandırılacak."
        else:
            confirm_message = f"<b>{file_count}</b> dosya aşağıdaki kurala göre yeniden adlandırılacak:\n\n"
            confirm_message += f"<b>{new_name}_1.pdf, {new_name}_2.pdf, ...</b>"
            
            # Örnek dosyaları göster
            confirm_message += "\n\nÖrneğin:"
            for i, file_path in enumerate(source_files[:3], 1):
                orig_name = os.path.basename(file_path)
                confirm_message += f"\n• {orig_name} → <b>{new_name}_{i}.pdf</b>"
            
            if file_count > 3:
                confirm_message += f"\n• ... ve {file_count - 3} dosya daha"
        
        confirm_message += f"\n\nHedef dizin: <b>{output_dir}</b>\n\nİşleme devam etmek istiyor musunuz?"
        
        confirm = QMessageBox.question(
            self,
            "Yeniden Adlandırma İşlemini Onayla",
            confirm_message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if confirm != QMessageBox.StandardButton.Yes:
            return
        
        # Her dosya için yeniden adlandırma işlemini sırayla başlat
        try:
            # İlerleme göstergelerini ayarla
            self.progress.setValue(0)
            self.progress.setRange(0, 100)
            self.progress.show()
            self.info_label.setText("Yeniden adlandırma işlemi başlatılıyor...")
            self.info_label.show()
            self.error_label.hide()
            self.rename_btn.setEnabled(False)
            
            # İşlenen dosya sayısı ve başarılı olanları takip et
            self.processed_count = 0
            self.success_count = 0
            self.failed_files = []
            self.renamed_files = []
            
            # İlk dosyayı işlemeye başla
            self.process_next_file(source_files, new_name, output_dir)
        except Exception as e:
            self.show_error(f"Yeniden adlandırma işlemi başlatılamadı: {str(e)}")
    
    def process_next_file(self, file_list, base_name, output_dir):
        """Dosyaları sırayla işler."""
        try:
            # PDF service'i kullanarak yeniden adlandırma işlemini başlat
            options = {
                "new_name": base_name,
                "keep_originals": False  # Gereksiz kopyalama yapmayacak
            }
            
            # Worker thread ile yeniden adlandırma işlemini başlat
            if len(file_list) > 0:
                self.rename_worker = self.pdf_service.create_rename_worker(
                    file_list,  # Tüm dosya listesini gönder
                    output_dir,
                    options
                )
                self.rename_worker.progress.connect(self.show_progress)
                self.rename_worker.finished.connect(self.handle_rename_completed)
                self.rename_worker.start()
            else:
                self.show_error("İşlenecek dosya bulunamadı.")
            
        except Exception as e:
            self.show_error(f"Dosya işleme hatası: {str(e)}")
            self.complete_renaming()
    
    def handle_rename_completed(self, success, message):
        """Yeniden adlandırma tamamlandığında çağrılır."""
        try:
            if success:
                self.success_count = len(self.file_list)  # İşlenen dosya sayısını file_list'ten al
                self.info_label.setText(f"✅ Başarılı! {self.success_count} dosya yeniden adlandırıldı.")
                
                # Başarı mesajı göster
                success_msg = f"Yeniden adlandırma işlemi tamamlandı!\n\n"
                success_msg += f"Toplam işlenen dosya: {self.success_count}\n"
                success_msg += f"Çıktı dizini: {self.output_dir if self.output_dir else 'Varsayılan'}"
                
                QMessageBox.information(self, "İşlem Tamamlandı", success_msg)
                
            else:
                self.show_error(f"Yeniden adlandırma işlemi başarısız: {message}")
                
        except Exception as e:
            self.show_error(f"İşlem sonucu işlenirken hata: {str(e)}")
        finally:
            self.complete_renaming()

    def complete_renaming(self):
        """Yeniden adlandırma işlemini tamamlar ve UI'yi sıfırlar."""
        try:
            # İlerleme çubuğunu gizle
            self.progress.hide()
            
            # Rename düğmesini tekrar aktif et
            self.rename_btn.setEnabled(True)
            
            # Worker'ı temizle
            self.worker = None
            
        except Exception as e:
            self.show_error(f"İşlem tamamlanırken hata: {str(e)}")

    def start_file_processing(self, file_list, base_name, output_dir):
        """Alternatif dosya işleme başlatma metodu."""
        self.process_next_file(file_list, base_name, output_dir)
    
    def update_button_state(self):
        """Butonların durumunu günceller."""
        has_files = self.file_list.count() > 0
        has_name = bool(self.name_input.text().strip())
        
        self.rename_btn.setEnabled(has_files and has_name)
        
        # Adım durumlarını güncelle
        if has_files:
            self.step1_label.setStyleSheet(INACTIVE_STEP_STYLE)
            if has_name:
                self.step2_label.setStyleSheet(ACTIVE_STEP_STYLE)
            else:
                self.step2_label.setStyleSheet(INACTIVE_STEP_STYLE)
        else:
            self.step1_label.setStyleSheet(ACTIVE_STEP_STYLE)
            self.step2_label.setStyleSheet(INACTIVE_STEP_STYLE)
        
        # UI güncellemesini zorla
        self.repaint()
    
    # Odak sorunlarına neden olan metotlar kaldırıldı
    # def refocus_drag_drop(self):
    #     """DragDropWidget'a yeniden odak verir."""
    #     # Eğer isim giriş alanında odak yoksa DragDropWidget'a odak ver
    #     # Bu, dosya listesinden dosya silindiğinde kullanılır.
    #     if not self.name_input_has_focus:
    #         self._set_focus_to_drag_drop()
    #         print("DragDrop refocussed.")
        
    # def _set_focus_to_drag_drop(self):
    #     """DragDropWidget'a odak verme işlemi"""
    #     # Eğer bu pencere şu anda aktifse ve DragDropWidget görünür durumdaysa odak ver
    #     if self.window().isActiveWindow() and self.drag_drop.isVisible():
    #         self.drag_drop.setFocus(Qt.FocusReason.OtherFocusReason)
    #         print("PDF Rename Window: DragDrop set focus")
        
    def show_progress(self, value):
        """İlerleme çubuğunu günceller."""
        self.progress.setValue(value)
        self.progress.show()
        self.info_label.setText(f"İşlem ilerliyor: %{value}")
        self.info_label.show()
        
    def show_error(self, message):
        """Hata mesajı gösterir."""
        self.error_label.setText(message)
        self.error_label.setWordWrap(True)  # Uzun hata mesajları için satır kaydırma
        self.error_label.show()
        self.info_label.hide()
        
        # Kritik hata mesajları için kullanıcıya MessageBox da göster
        if (message.startswith("Hata:") or 
            "bulunamadı" in message or 
            "geçersiz" in message.lower() or
            "oluşturulamadı" in message or
            "kaybı oldu" in message):
            QMessageBox.critical(self, "Hata", message)
        
    def clear(self, persistData=False):
        """Pencereyi temizler."""
        # Dosya listesini temizle
        self.file_list.clear()
        
        if not persistData:
            # Yeni isim alanını temizle
            self.name_input.clear()
            # Çıktı dizini sıfırla
            self.output_dir = None
            self.select_dir_btn.setText("Dizin Seç")
        
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
        
        # Düğme durumunu güncelle
        self.update_button_state()
        
        # DragDrop'a otomatik odaklanma (Kaldırıldı)
        # self.refocus_drag_drop() # Kaldırıldı
    
    def showEvent(self, event):
        """Widget görünür hale geldiğinde çağrılır"""
        super().showEvent(event)
        # Otomatik odaklanma kaldırıldı
        # print("PDF Yeniden Adlandırma: DragDrop'a odak verildi.") # Kaldırıldı
    
    def update_format_info(self):
        # Bu metodun içeriği, format bilgisini güncellemek için kullanılabilir.
        # Örneğin, format bilgisini pencere başlığına eklemek gibi.
        pass

    def update_layout_mode(self):
        """Genişliğe göre düzen modunu güncelle"""
        if self.is_compact_mode:
            # Compact mod - Yatay bölücüyü dikey hale getir
            self.splitter.setOrientation(Qt.Orientation.Vertical)
            self.splitter.setSizes([int(self.height() * 0.4), int(self.height() * 0.6)])  # Dikey modda boyutları ayarla
        else:
            # Normal mod - Yatay bölücü
            self.splitter.setOrientation(Qt.Orientation.Horizontal)
            self.splitter.setSizes([int(self.width() * 0.5), int(self.width() * 0.5)])  # Yatay modda boyutları ayarla 

    # on_name_input_focus metodu (Kaldırıldı)
    # def on_name_input_focus(self):
    #     """Yeni isim giriş alanı odak aldığında çağrılır."""
    #     # İsim giriş alanı odak aldığında, bu durumu kaydet
    #     # Bu durumda, DragDrop widget'ın otomatik odaklanması engellenir
    #     self.name_input_has_focus = True
    #     print("İsim girişi odak aldı") 