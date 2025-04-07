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
        
        # İsim giriş alanı odak takibi
        self.name_input_has_focus = False
        
        # Arayüzü oluştur
        self.init_ui()
        
        # Çıktı dizini
        self.output_dir = None
        
        # İş parçacığı
        self.worker = None
        
        # Buton durumunu güncelle
        self.update_button_state()
        
        # Pencere açıldığında DragDropWidget'a odak ver
        QTimer.singleShot(100, self.drag_drop.setFocus)
    
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
            
            # Yeni isim giriş alanına odaklan
            QTimer.singleShot(100, lambda: self.name_input.setFocus())
            
    def select_files(self):
        """Dosya seçme dialogunu açar."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "PDF Dosyaları Seç",
            "",
            "PDF Dosyaları (*.pdf)"
        )
        
        if files:
            # Seçilen dosyaları ekle
            self.add_files(files)
            
            # Yeni isim giriş alanına odaklan
            QTimer.singleShot(100, lambda: self.name_input.setFocus())
                
    def select_output_dir(self):
        """Çıktı dizini seçme dialogunu açar."""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Çıktı Dizini Seç"
        )
        
        if dir_path:
            self.output_dir = dir_path
            self.select_dir_btn.setText(f"Dizin: {dir_path}")
            
            # Buton durumunu güncelle
            self.update_button_state()
            
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
        """Dosya listesindeki bir sonraki dosyayı işler."""
        # Tüm dosyalar işlendiyse tamamla
        if self.processed_count >= len(file_list):
            self.complete_renaming()
            return
        
        # Sıradaki dosyayı al
        current_file = file_list[self.processed_count]
        
        # Çoklu dosya için sıra numarası ekle
        if len(file_list) > 1:
            new_name = f"{base_name}_{self.processed_count + 1}"
        else:
            new_name = base_name
        
        # Yeniden adlandırma için sözlük oluştur
        rename_options = {
            "new_name": new_name
        }
        
        # Worker'ı oluştur
        self.worker = self.pdf_service.create_rename_worker(
            current_file,
            output_dir,
            rename_options
        )
        
        # Sinyalleri bağla
        self.worker.progress.connect(self.show_progress)
        self.worker.finished.connect(lambda success, message: 
                                   self.handle_file_renamed(success, message, file_list, base_name, output_dir))
        
        # İlerleme çubuğunu güncelle
        progress_value = int((self.processed_count / len(file_list)) * 100)
        self.progress.setValue(progress_value)
        
        current_filename = os.path.basename(current_file)
        self.info_label.setText(f"İşleniyor: {current_filename} ({self.processed_count + 1}/{len(file_list)})")
        
        # İş parçacığını başlat
        self.worker.start()
    
    def handle_file_renamed(self, success, message, file_list, base_name, output_dir):
        """Her dosya yeniden adlandırıldığında çağrılır."""
        current_file = file_list[self.processed_count]
        current_filename = os.path.basename(current_file)
        
        if success:
            self.success_count += 1
            # Başarılı olan dosyanın yeni yolunu kaydet
            output_path = message.split("\n")[1] if "\n" in message else ""
            if output_path and os.path.exists(output_path):
                self.renamed_files.append(output_path)
        else:
            # Hatalı dosyaları kaydet
            self.failed_files.append((current_filename, message))
        
        # İşlenen dosya sayısını artır
        self.processed_count += 1
        
        # İlerleme çubuğunu güncelle
        progress_value = int((self.processed_count / len(file_list)) * 100)
        self.progress.setValue(progress_value)
        
        # Bir sonraki dosyayı işle veya tamamla
        self.process_next_file(file_list, base_name, output_dir)
    
    def complete_renaming(self):
        """Tüm dosyalar işlendikten sonra çağrılır."""
        total_files = self.processed_count
        success_files = self.success_count
        
        # İşlem tamamlandı mesajı
        if success_files == total_files:
            # Tüm dosyalar başarılı
            self.info_label.setText(f"Yeniden adlandırma işlemi başarıyla tamamlandı. {success_files} dosya işlendi.")
            
            # Kullanıcıya tamamlanma mesajı göster
            if len(self.renamed_files) == 1:
                output_path = self.renamed_files[0]
                confirm = QMessageBox.question(
                    self,
                    "İşlem Tamamlandı",
                    f"PDF başarıyla yeniden adlandırıldı.\n\nYeni dosya: {os.path.basename(output_path)}\n\nYeniden adlandırılan dosyayı açmak ister misiniz?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                
                if confirm == QMessageBox.StandardButton.Yes:
                    try:
                        open_file(output_path)
                    except Exception as e:
                        QMessageBox.warning(
                            self,
                            "Uyarı",
                            f"Dosya açılamadı: {str(e)}"
                        )
            else:
                # Birden fazla dosya için dizini aç seçeneği sun
                output_dir = os.path.dirname(self.renamed_files[0]) if self.renamed_files else None
                
                QMessageBox.information(
                    self, 
                    "İşlem Tamamlandı", 
                    f"{success_files} PDF dosyası başarıyla yeniden adlandırıldı."
                )
                
                if output_dir and os.path.exists(output_dir):
                    confirm = QMessageBox.question(
                        self,
                        "Dizini Aç",
                        f"Yeniden adlandırılan dosyaların bulunduğu dizini açmak ister misiniz?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.Yes
                    )
                    
                    if confirm == QMessageBox.StandardButton.Yes:
                        try:
                            open_file(output_dir)
                        except Exception as e:
                            QMessageBox.warning(
                                self,
                                "Uyarı",
                                f"Dizin açılamadı: {str(e)}"
                            )
        else:
            # Bazı dosyalar başarısız
            failed_count = len(self.failed_files)
            self.info_label.setText(f"Yeniden adlandırma tamamlandı. {success_files}/{total_files} dosya başarılı.")
            
            # Hata mesajı oluştur
            error_message = f"{failed_count} dosya işlenemedi:\n"
            for i, (filename, error) in enumerate(self.failed_files[:5]):
                error_message += f"- {filename}: {error}\n"
            
            if failed_count > 5:
                error_message += f"... ve {failed_count - 5} dosya daha."
            
            self.error_label.setText(error_message)
            self.error_label.show()
            
            QMessageBox.warning(
                self,
                "İşlem Tamamlandı (Bazı Hatalar Var)",
                f"{success_files}/{total_files} dosya başarıyla yeniden adlandırıldı.\n\n{error_message}"
            )
        
        # Arayüzü sıfırla
        if not self.persistData:
            self.clear()
        else:
            # Düğmeyi yeniden etkinleştir
            self.rename_btn.setEnabled(True)
        
        # DragDropWidget'a odak ver
        QTimer.singleShot(100, self.refocus_drag_drop)
    
    def update_button_state(self):
        """Düğme durumunu günceller."""
        has_file = self.file_list.count() > 0
        has_name = bool(self.name_input.text())
        
        self.rename_btn.setEnabled(has_file and has_name)
        
        # Adım durumlarını güncelle
        if has_file:
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
    
    def refocus_drag_drop(self):
        """DragDropWidget'a odak vermek için çağrılır."""
        if not hasattr(self, 'drag_drop') or not self.isVisible():
            return
        
        # İsim giriş alanı odakta ise, odağı DragDrop'a verme
        if hasattr(self, 'name_input') and hasattr(self.name_input, 'has_focus') and self.name_input.has_focus:
            print("İsim girişi odakta, DragDrop'a odak verilmedi")
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
        # İsim giriş alanı odakta ise, odağı DragDrop'a verme
        if hasattr(self, 'name_input') and hasattr(self.name_input, 'has_focus') and self.name_input.has_focus:
            print("İsim girişi odakta, DragDrop'a odak verilmedi")
            return
        
        if hasattr(self, 'drag_drop') and self.isVisible() and self.drag_drop.isVisible():
            # Widget görünür ve ulaşılabilirse odak ver
            self.drag_drop.setFocus(Qt.FocusReason.OtherFocusReason)
            print("PDF Yeniden Adlandırma: DragDrop'a odak verildi.")
        
    def show_progress(self, value):
        """İlerleme durumunu gösterir."""
        self.progress.setValue(value)
        
        # İlerleme durumuna göre bilgilendirme mesajları
        if value < 20:
            self.info_label.setText("Dosya hazırlanıyor...")
        elif value < 60:
            self.info_label.setText("Yeni dosya oluşturuluyor...")
        elif value < 90:
            self.info_label.setText("PDF içeriği kopyalanıyor...")
        elif value < 100:
            self.info_label.setText("İşlem tamamlanıyor...")
        else:
            self.info_label.setText("Yeniden adlandırma tamamlandı!")
        
        self.info_label.show()
        self.error_label.hide()
        
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
        
        # DragDrop'a odak ver
        self.refocus_drag_drop()
    
    def showEvent(self, event):
        """Pencere gösterildiğinde çağrılır."""
        super().showEvent(event)
        
        # Eğer dosya seçilmişse isim giriş alanına, seçilmemişse drag drop'a odaklan
        if self.file_list.count() > 0:
            QTimer.singleShot(100, lambda: self.name_input.setFocus())
        else:
            # Pencere gösterildiğinde DragDrop'a odak ver
            self.refocus_drag_drop()
        
        # Düğme durumunu güncelle
        self.update_button_state()
        
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
        
        self.step2_label = QLabel("2. Yeni İsim ve Dizin")
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
        
        # Sol panel - Dosya seçimi
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        
        # Dosya seçimi kart widget'ı
        file_card = QWidget()
        file_card.setStyleSheet(CARD_STYLE)
        file_card_layout = QVBoxLayout(file_card)
        file_card_layout.setSpacing(10)
        
        # Dosya seçimi başlığı
        files_header = QLabel("PDF Dosya Seçimi")
        files_header.setStyleSheet(SECTION_TITLE_STYLE)
        file_card_layout.addWidget(files_header)
        
        # Sürükle-bırak alanı
        self.drag_drop = DragDropWidget(self, "rename")
        self.drag_drop.files_dropped.connect(self.add_files)
        file_card_layout.addWidget(self.drag_drop)
        
        # Dosya ekleme düğmesi
        self.add_file_btn = ModernButton("Dosya Seç", primary=False)
        self.add_file_btn.clicked.connect(self.select_files)
        file_card_layout.addWidget(self.add_file_btn)
        
        # Bilgi notu
        info_label = QLabel(
            "PDF Yeniden Adlandırma ile bir veya daha fazla PDF dosyasını yeniden adlandırabilirsiniz. "
            "Birden fazla dosya seçtiğinizde, dosyalar 'yeni_ad_1.pdf', 'yeni_ad_2.pdf' şeklinde adlandırılacaktır."
        )
        info_label.setStyleSheet(INFO_BOX_STYLE)
        info_label.setWordWrap(True)
        file_card_layout.addWidget(info_label)
        
        # Seçili dosyalar
        selected_files_label = QLabel("Seçili Dosya:")
        selected_files_label.setStyleSheet(FORM_STYLE)
        file_card_layout.addWidget(selected_files_label)
        
        # Dosya listesi
        self.file_list = FileListWidget()
        self.file_list.setStyleSheet(FILE_LIST_STYLE)
        self.file_list.setMinimumHeight(100)
        self.file_list.files_changed.connect(self.update_button_state)
        self.file_list.files_removed.connect(self.refocus_drag_drop)
        file_card_layout.addWidget(self.file_list)
        
        left_layout.addWidget(file_card, 1)
        
        # Sağ panel - Yeniden adlandırma ayarları
        right_panel = QScrollArea()
        right_panel.setWidgetResizable(True)
        right_panel.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        right_panel.setFrameShape(QFrame.Shape.NoFrame)
        
        right_content = QWidget()
        right_layout = QVBoxLayout(right_content)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        # Yeniden adlandırma kart widget'ı
        rename_card = QWidget()
        rename_card.setStyleSheet(CARD_STYLE)
        rename_layout = QVBoxLayout(rename_card)
        rename_layout.setSpacing(15)
        
        # Yeniden adlandırma başlığı
        rename_header = QLabel("Yeniden Adlandırma Ayarları")
        rename_header.setStyleSheet(SECTION_TITLE_STYLE)
        rename_layout.addWidget(rename_header)
        
        # Yeni isim girişi
        new_name_label = QLabel("Yeni Dosya Adı:")
        new_name_label.setStyleSheet(FORM_STYLE)
        rename_layout.addWidget(new_name_label)
        
        self.name_input = ModernLineEdit("Yeni dosya adını girin")
        self.name_input.textChanged.connect(self.update_button_state)
        # TabFocus özelliğini etkinleştir
        self.name_input.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        rename_layout.addWidget(self.name_input)
        
        # Dizin seçimi
        dir_label = QLabel("Hedef Dizin:")
        dir_label.setStyleSheet(FORM_STYLE)
        rename_layout.addWidget(dir_label)
        
        dir_layout = QHBoxLayout()
        dir_layout.setSpacing(10)
        
        dir_info = QLabel(
            "Yeniden adlandırılan dosya bu dizine kaydedilecektir. "
            "Boş bırakırsanız, dosya orijinal konumunda yeniden adlandırılır."
        )
        dir_info.setStyleSheet(INFO_BOX_STYLE)
        dir_info.setWordWrap(True)
        rename_layout.addWidget(dir_info)
        
        # Dizin seçme düğmesi
        self.select_dir_btn = ModernButton("Dizin Seç", primary=False)
        self.select_dir_btn.clicked.connect(self.select_output_dir)
        rename_layout.addWidget(self.select_dir_btn)
        
        # İşlem düğmesi
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.rename_btn = ModernButton("Yeniden Adlandır")
        self.rename_btn.setStyleSheet(GREEN_BUTTON_STYLE)  # Özel stil uygula
        self.rename_btn.clicked.connect(self.start_renaming)
        self.rename_btn.setEnabled(False)
        button_layout.addWidget(self.rename_btn)
        
        rename_layout.addLayout(button_layout)
        
        # Durum kartı
        status_card = QWidget()
        status_card.setStyleSheet(CARD_STYLE)
        status_layout = QVBoxLayout(status_card)
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
        
        right_layout.addWidget(rename_card)
        right_layout.addWidget(status_card)
        right_layout.addStretch()
        
        # Scroll alanını ayarla
        right_panel.setWidget(right_content)
        
        # Panelleri splitter'a ekle
        self.splitter.addWidget(left_panel)
        self.splitter.addWidget(right_panel)
        self.splitter.setSizes([400, 400])  # Panel boyutlarını ayarla
        
        layout.addWidget(self.splitter, 1)  # stretch faktörü 1 ile ekle 
        
        # Pencere ayarları
        self.setMinimumSize(900, 600)
        self.setWindowTitle("PDF Yeniden Adlandırma")
        
        # Format bilgisini güncelle
        self.update_format_info()
    
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

    def on_name_input_focus(self):
        """Yeni isim giriş alanı odak aldığında çağrılır."""
        # İsim giriş alanı odak aldığında, bu durumu kaydet
        # Bu durumda, DragDrop widget'ın otomatik odaklanması engellenir
        self.name_input_has_focus = True
        print("İsim girişi odak aldı") 