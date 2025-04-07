"""
PDF birleştirme penceresi.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFileDialog,
    QMessageBox, QLineEdit, QProgressBar,
    QFrame, QScrollArea, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QIcon, QPixmap, QResizeEvent
import os

from ..components import (
    ModernButton, ModernLineEdit, DragDropWidget,
    FileListWidget, ModernProgressBar, HeaderLabel,
    InfoLabel, ErrorLabel
)
from ...services.pdf_service import PdfService
from ...utils.file_utils import open_file
from ..styles import (
    SECTION_TITLE_STYLE, CARD_STYLE, FILE_LIST_STYLE,
    FORM_STYLE, CHECKBOX_STYLE, RADIO_STYLE,
    INFO_BOX_STYLE, STEP_INDICATOR_STYLE,
    ACTIVE_STEP_STYLE, INACTIVE_STEP_STYLE,
    ARROW_STYLE, SEPARATOR_STYLE, SCROLLBAR_STYLE,
    GREEN_BUTTON_STYLE
)

class PDFMergeWindow(QWidget):
    """PDF birleştirme penceresi."""
    
    # Sinyaller
    merge_requested = pyqtSignal(list, str)  # Dosya listesi, çıktı yolu
    
    def __init__(self, pdf_service):
        super().__init__()
        self.pdf_service = pdf_service
        
        # Veri koruma özelliği (ekranlar arası geçişte veriyi silme)
        self.persistData = True
        
        # Responsive tasarım için boyut bilgisi
        self.is_compact_mode = False
        
        # UI bileşenlerini oluştur
        self.init_ui()
        
        # İş parçacığı
        self.worker = None
        
        # Başlangıç durumunu ayarla
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
            self.splitter.setSizes([int(self.height() * 0.5), int(self.height() * 0.5)])  # Dikey modda boyutları ayarla
        else:
            # Normal mod - Yatay bölücü
            self.splitter.setOrientation(Qt.Orientation.Horizontal)
            self.splitter.setSizes([int(self.width() * 0.6), int(self.width() * 0.4)])  # Yatay modda boyutları ayarla
    
    def init_ui(self):
        """Kullanıcı arayüzünü oluşturur."""
        # Ana düzen
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlık
        header = HeaderLabel("PDF Birleştirme")
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
        
        self.step2_label = QLabel("2. Çıktı Ayarları")
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
        self.drag_drop = DragDropWidget(self, "merge")
        self.drag_drop.files_dropped.connect(self.add_files)
        file_card_layout.addWidget(self.drag_drop)
        
        # Dosya ekleme düğmesi
        add_file_btn = ModernButton("Dosya Ekle", primary=False)
        add_file_btn.clicked.connect(self.select_files)
        file_card_layout.addWidget(add_file_btn)
        
        # Dosya listesi
        file_list_label = QLabel("Birleştirilecek Dosyalar:")
        file_list_label.setStyleSheet(FORM_STYLE)
        file_card_layout.addWidget(file_list_label)
        
        self.file_list = FileListWidget()
        self.file_list.setStyleSheet(FILE_LIST_STYLE)
        self.file_list.setMinimumHeight(200)
        self.file_list.files_changed.connect(self.update_button_state)
        self.file_list.files_removed.connect(self.refocus_drag_drop)
        file_card_layout.addWidget(self.file_list)
        
        file_layout.addWidget(file_card)
        
        # Bilgi kartı
        info_card = QWidget()
        info_card.setStyleSheet(CARD_STYLE)
        info_layout = QVBoxLayout(info_card)
        info_layout.setSpacing(10)
        
        # Bilgi başlığı
        info_header = QLabel("Bilgi")
        info_header.setStyleSheet(SECTION_TITLE_STYLE)
        info_layout.addWidget(info_header)
        
        # Bilgi metni
        info_text = QLabel(
            "PDF dosyalarını sürükleyerek, Ctrl+V ile yapıştırarak veya 'Dosya Ekle' düğmesi ile seçerek ekleyebilirsiniz.\n\n"
            "Dosyalar, listede gösterilen sırada birleştirilecektir. Sırayı değiştirmek için dosyaları sürükleyip bırakabilirsiniz."
        )
        info_text.setStyleSheet(INFO_BOX_STYLE)
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        
        file_layout.addWidget(info_card)
        file_layout.addStretch()
        
        # Sağ panel - çıktı ayarları
        output_panel = QWidget()
        output_layout = QVBoxLayout(output_panel)
        output_layout.setContentsMargins(0, 0, 0, 0)
        output_layout.setSpacing(15)
        
        # Çıktı ayarları kart widget'ı
        output_card = QWidget()
        output_card.setStyleSheet(CARD_STYLE)
        output_card_layout = QVBoxLayout(output_card)
        output_card_layout.setSpacing(15)
        
        # Çıktı başlığı
        output_header = QLabel("Çıktı Ayarları")
        output_header.setStyleSheet(SECTION_TITLE_STYLE)
        output_card_layout.addWidget(output_header)
        
        # Çıktı yolu
        output_path_label = QLabel("Çıktı Dosyası:")
        output_path_label.setStyleSheet(FORM_STYLE)
        output_card_layout.addWidget(output_path_label)
        
        output_path_layout = QHBoxLayout()
        output_path_layout.setSpacing(10)
        
        self.output_path = ModernLineEdit()
        self.output_path.setPlaceholderText("Çıktı dosyasının kaydedileceği yol")
        output_path_layout.addWidget(self.output_path)
        
        browse_button = ModernButton("Gözat", primary=False)
        browse_button.clicked.connect(self.select_output_path)
        output_path_layout.addWidget(browse_button)
        
        output_card_layout.addLayout(output_path_layout)
        
        # Birleştirme düğmesi
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.merge_btn = ModernButton("Birleştir")
        self.merge_btn.setStyleSheet(GREEN_BUTTON_STYLE)  # Özel stil uygula
        self.merge_btn.setEnabled(False)
        self.merge_btn.clicked.connect(self.process_merge)
        button_layout.addWidget(self.merge_btn)
        
        output_card_layout.addLayout(button_layout)
        
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
        
        output_layout.addWidget(output_card)
        output_layout.addWidget(status_card)
        output_layout.addStretch()
        
        # Panelleri splitter'a ekle
        self.splitter.addWidget(file_panel)
        self.splitter.addWidget(output_panel)
        self.splitter.setSizes([500, 300])  # Panel boyutlarını ayarla
        
        layout.addWidget(self.splitter, 1)  # stretch factör 1 ile ekle
        
        # Pencere ayarları
        self.setMinimumSize(900, 600)
        self.setWindowTitle("PDF Birleştirme")
        
    def add_files(self, file_paths):
        """Sürükle-bırak ile dosya ekler."""
        added_count = 0
        for path in file_paths:
            if path.lower().endswith('.pdf'):
                self.file_list.add_file(path)
                added_count += 1
        
        if added_count > 0:
            # Dosya eklendiyse adım 2'ye geç
            self.step1_label.setStyleSheet(INACTIVE_STEP_STYLE)
            self.step2_label.setStyleSheet(ACTIVE_STEP_STYLE)
        else:
            # Dosya yoksa adım 1'de kal
            self.step1_label.setStyleSheet(ACTIVE_STEP_STYLE)
            self.step2_label.setStyleSheet(INACTIVE_STEP_STYLE)
                
    def select_files(self):
        """Dosya seçme dialogunu açar."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "PDF Dosyaları Seç",
            "",
            "PDF Dosyaları (*.pdf)"
        )
        
        if files:
            for file in files:
                self.file_list.add_file(file)
            
            # Dosya seçildiyse adım 2'ye geç
            self.step1_label.setStyleSheet(INACTIVE_STEP_STYLE)
            self.step2_label.setStyleSheet(ACTIVE_STEP_STYLE)
                
    def select_output_path(self):
        """Çıktı dosyası yolunu seçme dialogunu açar."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Çıktı Dosyasını Kaydet",
            "",
            "PDF Dosyası (*.pdf)"
        )
        
        if file_path:
            # Uzantıyı kontrol et ve gerekirse ekle
            if not file_path.lower().endswith('.pdf'):
                file_path += '.pdf'
                
            self.output_path.setText(file_path)
            
            # Çıktı yolu ayarlandıysa adım 2'yi etkinleştir
            if self.file_list.count() > 0:
                self.step1_label.setStyleSheet(INACTIVE_STEP_STYLE)
                self.step2_label.setStyleSheet(ACTIVE_STEP_STYLE)
            
            # Buton durumunu güncelle
            self.update_button_state()
            
    def process_merge(self):
        """PDF birleştirme işlemini başlatır."""
        # Giriş ve çıkış dosyalarını kontrol et
        if not self.output_path.text():
            QMessageBox.warning(self, "Uyarı", "Lütfen çıkış dosyasını seçin.")
            return

        if self.file_list.count() == 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir PDF dosyası ekleyin.")
            return

        # Çıkış dizinini kontrol et
        output_dir = os.path.dirname(self.output_path.text())
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Çıkış dizini oluşturulamadı: {str(e)}")
                return

        # Dosyaların geçerliliğini kontrol et
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
            
            QMessageBox.warning(self, "Uyarı", error_message)
            return
        
        # Birleştirme işlemini onaylat
        file_count = self.file_list.count()
        output_file = self.output_path.text()
        
        confirm = QMessageBox.question(
            self,
            "Birleştirme İşlemini Onayla",
            f"<b>{file_count}</b> PDF dosyası birleştirilecek.\n\n"
            f"Çıktı dosyası: <b>{output_file}</b>\n\n"
            f"İşleme devam etmek istiyor musunuz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if confirm != QMessageBox.StandardButton.Yes:
            return

        # Dosya işleme arayüzünü hazırla
        self.progress.setValue(0)
        self.progress.show()
        self.info_label.setText("Birleştirme işlemi başlatılıyor...")
        self.info_label.show()
        self.error_label.hide()
        self.merge_btn.setEnabled(False)
        
        # İş parçacığını başlat
        try:
            self.worker = self.pdf_service.create_merge_worker(
                self.file_list.get_files(),
                self.output_path.text()
            )
            
            # Sinyalleri bağla
            self.worker.progress.connect(self.update_progress)
            self.worker.finished.connect(self.handle_merge_finished)
            
            # İş parçacığını başlat
            self.worker.start()
        except Exception as e:
            self.handle_error(f"Birleştirme işlemi başlatılamadı: {str(e)}")
    
    def update_progress(self, value):
        """İlerleme çubuğunu günceller."""
        self.progress.setValue(value)
        
        # İlerleme durumuna göre bilgi mesajı güncelle
        if value < 25:
            self.info_label.setText("Dosyalar hazırlanıyor...")
        elif value < 75:
            self.info_label.setText("Dosyalar birleştiriliyor...")
        else:
            self.info_label.setText("Birleştirilmiş dosya kaydediliyor...")
        
    def handle_merge_finished(self, success, message):
        """Birleştirme işlemi tamamlandığında çağrılır."""
        self.progress.hide()
        self.merge_btn.setEnabled(True)
        
        if success:
            self.info_label.setText("Birleştirme işlemi başarıyla tamamlandı.")
            self.info_label.show()
            self.error_label.hide()
            
            if not self.persistData:
                self.clear()
            
            # Sonuç mesajı göster
            result_message = f"PDF dosyaları başarıyla birleştirildi.\n\nÇıktı: {self.output_path.text()}"
            QMessageBox.information(self, "İşlem Tamamlandı", result_message)
            
            # Açma seçeneği sun
            reply = QMessageBox.question(
                self, 
                "Dosyayı Aç", 
                "Birleştirilmiş PDF dosyasını açmak ister misiniz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    open_file(self.output_path.text())
                except Exception as e:
                    QMessageBox.warning(
                        self, 
                        "Uyarı", 
                        f"Dosya açılamadı: {str(e)}"
                    )
        else:
            self.handle_error(f"Birleştirme işlemi başarısız oldu: {message}")
            
    def handle_error(self, message):
        """Hata mesajını gösterir ve durumu sıfırlar."""
        self.progress.setValue(0)
        self.progress.hide()
        self.merge_btn.setEnabled(True)
        self.error_label.setText(message)
        self.error_label.show()
        self.info_label.hide()
        print(f"Birleştirme hatası: {message}")
        
        # Kullanıcıya hata mesajını göster
        QMessageBox.critical(
            self,
            "Birleştirme Hatası",
            f"PDF birleştirme işlemi sırasında bir hata oluştu:\n\n{message}"
        )
        
    def clear(self):
        """Pencereyi temizler."""
        # persistData true ise sadece etiketleri temizle, false ise tam temizlik yap
        if not self.persistData:
            self.file_list.clear()
            self.output_path.clear()
            
            # Adımları sıfırla
            self.step1_label.setStyleSheet(ACTIVE_STEP_STYLE)
            self.step2_label.setStyleSheet(INACTIVE_STEP_STYLE)
        
        # Her durumda temizlenmesi gereken öğeler
        self.progress.hide()
        self.info_label.hide()
        self.error_label.hide()
        
        # Buton durumunu güncelle
        self.update_button_state()
        
    def showEvent(self, event):
        """Pencere gösterildiğinde çağrılır."""
        super().showEvent(event)
        # Pencere her gösterildiğinde DragDropWidget'a odak ver
        QTimer.singleShot(100, lambda: self.drag_drop.setFocus())
        
        # Buton durumunu güncelle
        self.update_button_state()

    def update_button_state(self):
        """Düğme durumunu günceller."""
        # Birleştir düğmesini etkinleştir/devre dışı bırak
        file_count = self.file_list.count()
        has_output = bool(self.output_path.text())
        
        self.merge_btn.setEnabled(file_count > 0 and has_output)
        
        # Adım durumlarını güncelle
        if file_count == 0:
            self.step1_label.setStyleSheet(ACTIVE_STEP_STYLE)
            self.step2_label.setStyleSheet(INACTIVE_STEP_STYLE)
        elif has_output:
            self.step1_label.setStyleSheet(INACTIVE_STEP_STYLE)
            self.step2_label.setStyleSheet(ACTIVE_STEP_STYLE)

    def refocus_drag_drop(self):
        """DragDropWidget'a odak ver."""
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
            print("PDF Birleştirme: DragDrop'a odak verildi.") 