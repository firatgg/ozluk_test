from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFileDialog,
    QMessageBox, QLineEdit, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
import os

from ..components import (
    ModernButton, ModernLineEdit, 
    ModernProgressBar, HeaderLabel,
    InfoLabel, ErrorLabel, DragDropWidget
)
from ...services.pdf_service import PdfService
from ...utils.file_utils import open_file

class PDFExtractWindow(QWidget):
    """PDF sayfalarını ayıklama penceresi."""
    
    def __init__(self, pdf_service=None, parent=None):
        super().__init__(parent)
        self.pdf_service = pdf_service or PdfService()
        self.input_file = ""
        self.output_dir = ""
        self.extract_all = True
        self.worker = None
        
        # Veri koruma özelliği (ekranlar arası geçişte veriyi silme)
        self.persistData = True
        
        self.init_ui()
        
    def init_ui(self):
        """Kullanıcı arayüzünü oluşturur."""
        # Ana düzen
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.setLayout(layout)
        
        # Başlık
        header = HeaderLabel("PDF Sayfalarını Ayıkla")
        layout.addWidget(header)
        
        # Sürükle-bırak alanı
        self.drag_drop = DragDropWidget(self, "extract")
        self.drag_drop.files_dropped.connect(self.handle_dropped_files)
        layout.addWidget(self.drag_drop)
        
        # Giriş dosyası seçimi
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        
        input_label = QLabel("Giriş Dosyası:")
        self.input_path = ModernLineEdit("PDF Dosyası Seçin")
        self.input_path.setReadOnly(True)
        
        browse_input_btn = ModernButton("Gözat")
        browse_input_btn.clicked.connect(self.browse_input_file)
        
        input_layout.addWidget(input_label, 1)
        input_layout.addWidget(self.input_path, 3)
        input_layout.addWidget(browse_input_btn, 1)
        layout.addLayout(input_layout)
        
        # Çıkış dizini seçimi
        output_layout = QHBoxLayout()
        output_layout.setSpacing(10)
        
        output_label = QLabel("Çıkış Dizini:")
        self.output_path = ModernLineEdit("Çıkış Dizini Seçin")
        self.output_path.setReadOnly(True)
        
        browse_output_btn = ModernButton("Gözat")
        browse_output_btn.clicked.connect(self.browse_output_dir)
        
        output_layout.addWidget(output_label, 1)
        output_layout.addWidget(self.output_path, 3)
        output_layout.addWidget(browse_output_btn, 1)
        layout.addLayout(output_layout)
        
        # Dosya önek girişi
        prefix_layout = QHBoxLayout()
        prefix_layout.setSpacing(10)
        
        prefix_label = QLabel("Dosya Öneki:")
        self.file_prefix_input = ModernLineEdit("sayfa_")
        
        prefix_layout.addWidget(prefix_label, 1)
        prefix_layout.addWidget(self.file_prefix_input, 4)
        layout.addLayout(prefix_layout)
        
        # Sayfa aralığı seçimi
        range_layout = QHBoxLayout()
        range_layout.setSpacing(10)
        
        range_label = QLabel("Sayfa Aralığı:")
        self.page_range_input = ModernLineEdit("1,3-5,7")
        
        range_layout.addWidget(range_label, 1)
        range_layout.addWidget(self.page_range_input, 4)
        layout.addLayout(range_layout)
        
        # Tüm sayfalar seçeneği
        all_pages_layout = QHBoxLayout()
        self.all_pages_check = QCheckBox("Tüm Sayfaları Ayıkla")
        self.all_pages_check.setChecked(True)
        self.all_pages_check.stateChanged.connect(self.toggle_page_range)
        
        all_pages_layout.addWidget(self.all_pages_check)
        all_pages_layout.addStretch()
        layout.addLayout(all_pages_layout)
        
        # İlerleme çubuğu
        self.progress_bar = ModernProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Bilgi ve hata etiketleri
        self.status_label = InfoLabel("")
        self.status_label.hide()
        layout.addWidget(self.status_label)
        
        self.error_label = ErrorLabel("")
        self.error_label.hide()
        layout.addWidget(self.error_label)
        
        # İşlem düğmeleri
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.extract_button = ModernButton("Ayıkla")
        self.extract_button.clicked.connect(self.process_extract)
        
        self.stop_button = ModernButton("Durdur")
        self.stop_button.clicked.connect(self.stop_process)
        self.stop_button.setEnabled(False)
        
        buttons_layout.addWidget(self.extract_button)
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Boşluk ekleyerek düzeni tamamla
        layout.addStretch()
        
        # Pencere ayarları
        self.setWindowTitle("PDF Sayfalarını Ayıkla")
        self.resize(600, 400)
        
    def browse_input_file(self):
        """Giriş PDF dosyasını seçmek için dosya seçiciyi açar."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "PDF Dosyası Seç", "", "PDF Dosyaları (*.pdf)"
            )
        
            if file_path:
                self.input_file = file_path
                self.input_path.setText(file_path)
                
                # Otomatik çıkış dizini önerisi
                suggested_output = os.path.join(
                    os.path.dirname(file_path), 
                    os.path.splitext(os.path.basename(file_path))[0]
                )
                
                if not self.output_dir:
                    self.output_dir = suggested_output
                    self.output_path.setText(suggested_output)
        except Exception as e:
            self.handle_error(f"Giriş dosyası seçilirken hata oluştu: {str(e)}")
    
    def browse_output_dir(self):
        """Çıkış dizinini seçmek için dizin seçiciyi açar."""
        try:
            dir_path = QFileDialog.getExistingDirectory(
                self, "Çıkış Dizini Seç", ""
            )
            
            if dir_path:
                self.output_dir = dir_path
                self.output_path.setText(dir_path)
        except Exception as e:
            self.handle_error(f"Çıkış dizini seçilirken hata oluştu: {str(e)}")
    
    def toggle_page_range(self, state):
        """Sayfa aralığı giriş alanını etkinleştirir veya devre dışı bırakır."""
        try:
            self.extract_all = (state == Qt.CheckState.Checked)
            self.page_range_input.setEnabled(not self.extract_all)
        except Exception as e:
            self.handle_error(f"Sayfa aralığı ayarlanırken hata oluştu: {str(e)}")
    
    def update_progress(self, value):
        """İlerleme çubuğunu günceller."""
        self.progress_bar.setValue(value)
        self.progress_bar.show()
    
    def stop_process(self):
        """İşlemi durdurur."""
        try:
            if self.worker and self.worker.isRunning():
                self.worker.requestInterruption()
                self.stop_button.setEnabled(False)
                self.status_label.setText("İşlem durduruluyor...")
        except Exception as e:
            self.handle_error(f"İşlem durdurulurken hata oluştu: {str(e)}")

    def process_extract(self):
        """PDF ayıklama işlemini başlatır."""
        # Giriş dosyasını kontrol et
        if not self.input_file or not os.path.exists(self.input_file):
            QMessageBox.warning(self, "Uyarı", "Lütfen geçerli bir PDF dosyası seçin.")
            return

        # Çıkış dizinini kontrol et
        if not self.output_dir:
            QMessageBox.warning(self, "Uyarı", "Lütfen çıkış dizinini seçin.")
            return
            
        # Çıkış dizininin varlığını kontrol et
        if not os.path.exists(self.output_dir):
            try:
                os.makedirs(self.output_dir, exist_ok=True)
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Çıkış dizini oluşturulamadı: {str(e)}")
                return
        
        # Sayfa aralığını kontrol et
        range_text = self.page_range_input.text().strip()
        if not range_text and not self.extract_all:
            QMessageBox.warning(self, "Uyarı", "Lütfen sayfa aralığını girin veya 'Tüm Sayfalar' seçeneğini işaretleyin.")
            return
        
        # Dosya işleme arayüzünü hazırla
        self.progress_bar.setValue(0)
        self.status_label.setText("Ayıklama işlemi başlatılıyor...")
        self.status_label.show()
        self.error_label.hide()
        self.extract_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        # İş parçacığını başlat
        try:
            self.worker = self.pdf_service.create_extract_worker(
                self.input_file,
                self.output_dir,
                self.extract_all,
                range_text if not self.extract_all else "",
                self.file_prefix_input.text()
            )
            
            # Sinyalleri bağla
            self.worker.progress.connect(self.update_progress)
            self.worker.finished.connect(self.handle_extract_finished)
            
            # İş parçacığını başlat
            self.worker.start()
        except Exception as e:
            self.handle_error(f"Ayıklama işlemi başlatılamadı: {str(e)}")
    
    def handle_extract_finished(self, success, message):
        """Ayıklama işlemi tamamlandığında çağrılır."""
        try:
            self.extract_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            
            if success:
                self.progress_bar.setValue(100)
                self.status_label.setText("Ayıklama işlemi tamamlandı.")
                self.error_label.hide()
                
                # Sonuç mesajı göster
                result_message = f"PDF sayfaları başarıyla ayıklandı.\nÇıkış dizini: {self.output_dir}"
                QMessageBox.information(self, "İşlem Tamamlandı", result_message)
                
                # Açma seçeneği sun
                reply = QMessageBox.question(
                    self, 
                    "Dizini Aç", 
                    "Ayıklanan sayfaların bulunduğu dizini açmak ister misiniz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                QMessageBox.StandardButton.Yes
            )
            
                if reply == QMessageBox.StandardButton.Yes:
                    try:
                        open_file(self.output_dir)
                    except Exception as e:
                        QMessageBox.warning(
                            self, 
                            "Uyarı", 
                            f"Dizin açılamadı: {str(e)}"
                        )
            else:
                self.handle_error(f"Ayıklama işlemi başarısız oldu: {message}")
        except Exception as e:
            self.handle_error(f"Ayıklama tamamlama işlemi sırasında hata oluştu: {str(e)}")
    
    def handle_error(self, message):
        """Hata mesajını gösterir ve durumu sıfırlar."""
        self.progress_bar.setValue(0)
        self.status_label.setText("Hata: Ayıklama işlemi başarısız oldu.")
        self.error_label.setText(message)
        self.error_label.show()
        print(f"Ayıklama hatası: {message}")
        
        # Butonları sıfırla
        self.extract_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def showEvent(self, event):
        """Pencere gösterildiğinde çağrılır."""
        super().showEvent(event)
        # Pencere her gösterildiğinde DragDropWidget'a odak ver (Kaldırıldı)
        # QTimer.singleShot(100, lambda: self.drag_drop.setFocus() if hasattr(self, 'drag_drop') else None)

    def handle_dropped_files(self, file_paths):
        """Sürüklenen PDF dosyalarını işler."""
        try:
            pdf_files = [f for f in file_paths if f.lower().endswith('.pdf')]
            if not pdf_files:
                self.handle_error("Sürüklenen dosyalarda PDF bulunamadı.")
                return
            
            # İlk PDF dosyasını kullan
            file_path = pdf_files[0]
            self.input_file = file_path
            self.input_path.setText(file_path)
            
            # Otomatik çıkış dizini önerisi
            suggested_output = os.path.join(
                os.path.dirname(file_path), 
                os.path.splitext(os.path.basename(file_path))[0]
            )
            
            if not self.output_dir:
                self.output_dir = suggested_output
                self.output_path.setText(suggested_output) 
        except Exception as e:
            self.handle_error(f"Sürüklenen dosyalar işlenirken hata oluştu: {str(e)}")

    def clear(self):
        """Pencereyi temizler."""
        if not self.persistData:
            self.input_file = ""
            self.input_path.setText("PDF Dosyası Seçin")
            self.output_dir = ""
            self.output_path.setText("Çıkış Dizini Seçin")
            self.file_prefix_input.setText("sayfa_")
            self.page_range_input.setText("1,3-5,7")
            self.all_pages_check.setChecked(True)
        
        # Durum etiketlerini her durumda temizle
        self.status_label.hide()
        self.error_label.hide()
        self.progress_bar.hide()
        self.extract_button.setEnabled(True)
        self.stop_button.setEnabled(False) 