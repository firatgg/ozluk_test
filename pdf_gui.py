import sys
import os
import traceback
import shutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                           QFileDialog, QMessageBox, QTabWidget, QListWidget,
                           QFrame, QListWidgetItem, QToolButton, QStyle,
                           QProgressBar)
from PyQt6.QtCore import Qt, QMimeData, QSize
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QIcon, QPalette, QColor, QFont
from PyPDF2 import PdfReader, PdfWriter
from pdf_rename import rename_pdfs
from pdf_merger import merge_pdfs
from pdf_splitter import split_pdf

# Marnak Lojistik Kurumsal Renkleri
MARNAK_BLUE = "#0066B3"
MARNAK_GREEN = "#3AB54A"
MARNAK_LIGHT_BLUE = "#E5F1F9"
MARNAK_LIGHT_GREEN = "#E8F5EA"

class ModernButton(QPushButton):
    def __init__(self, text, parent=None, primary=False):
        super().__init__(text, parent)
        self.setMinimumHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        if primary:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {MARNAK_BLUE};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #005599;
                }}
                QPushButton:pressed {{
                    background-color: #004477;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {MARNAK_LIGHT_BLUE};
                    color: {MARNAK_BLUE};
                    border: 1px solid {MARNAK_BLUE};
                    border-radius: 4px;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background-color: #D5E6F3;
                }}
                QPushButton:pressed {{
                    background-color: #C5DBE8;
                }}
            """)

class ModernLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(40)
        self.setStyleSheet(f"""
            QLineEdit {{
                border: 2px solid {MARNAK_BLUE};
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                selection-background-color: {MARNAK_BLUE};
            }}
            QLineEdit:focus {{
                border-color: {MARNAK_GREEN};
            }}
        """)

    def keyPressEvent(self, event):
        """Klavye olaylarını yakala"""
        # Ctrl+V kombinasyonunu normal metin yapıştırma olarak işle
        if event.key() == Qt.Key.Key_V and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.paste()
        # ESC tuşuna basıldığında odağı kaybet
        elif event.key() == Qt.Key.Key_Escape:
            self.clearFocus()
        else:
            super().keyPressEvent(event)
            
    def focusOutEvent(self, event):
        """Odak kaybedildiğinde çağrılır"""
        super().focusOutEvent(event)
        # Odağı tamamen bırak
        self.clearFocus()
        # Ana pencereye odağı ver
        if self.window():
            self.window().setFocus()

class DragDropWidget(QLabel):
    def __init__(self, parent=None, tab_type=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumHeight(120)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.default_style = f"""
            QLabel {{
                border: 2px dashed {MARNAK_BLUE};
                border-radius: 8px;
                background-color: {MARNAK_LIGHT_BLUE};
                color: {MARNAK_BLUE};
                font-size: 14px;
                padding: 20px;
            }}
            QLabel:hover {{
                background-color: {MARNAK_LIGHT_GREEN};
                border-color: {MARNAK_GREEN};
                color: {MARNAK_GREEN};
            }}
        """
        self.drag_over_style = f"""
            QLabel {{
                border: 2px solid {MARNAK_GREEN};
                border-radius: 8px;
                background-color: {MARNAK_LIGHT_GREEN};
                color: {MARNAK_GREEN};
                font-size: 14px;
                padding: 20px;
            }}
        """
        self.setStyleSheet(self.default_style)
        self.setText("📄 PDF dosyalarını buraya sürükleyin\nveya tıklayarak seçin")
        self.tab_type = tab_type
        
    def mousePressEvent(self, event):
        """Tıklama olayını yakala"""
        if event.button() == Qt.MouseButton.LeftButton:
            # En üst seviyedeki pencere widget'ını bul
            main_window = self.window()
            if isinstance(main_window, PDFGUI):
                main_window.select_files(self.tab_type)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
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
        self.setStyleSheet(self.default_style)
        
    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet(self.default_style)
        try:
            files = [url.toLocalFile() for url in event.mimeData().urls()]
            # En üst seviyedeki pencere widget'ını bul
            main_window = self.window()
            if isinstance(main_window, PDFGUI):
                main_window.handle_dropped_files(files, self.tab_type)
        except Exception as e:
            print(f"Bırakma hatası: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Dosya işlenirken hata oluştu: {str(e)}")

class PDFListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.setAcceptDrops(True)
        self.setStyleSheet(f"""
            QListWidget {{
                border: 1px solid {MARNAK_BLUE};
                border-radius: 8px;
                padding: 8px;
                background-color: white;
            }}
            QListWidget::item {{
                border-bottom: 1px solid {MARNAK_LIGHT_BLUE};
                padding: 12px;
                margin: 2px 0;
                border-radius: 4px;
            }}
            QListWidget::item:selected {{
                background-color: {MARNAK_LIGHT_BLUE};
                color: {MARNAK_BLUE};
                border: none;
            }}
            QListWidget::item:hover {{
                background-color: {MARNAK_LIGHT_GREEN};
            }}
        """)

    def get_file_paths(self):
        return [self.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.count())]

class PDFGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Marnak PDF İşlem Araçları")
        self.setMinimumSize(1000, 700)
        
        # İşlem durumu
        self.is_processing = False
        self.cancel_requested = False
        
        # Hata loglama
        self.setup_logging()
        
        # Aktif sekme takibi
        self.current_tab = "rename"
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: white;
            }}
            QTabWidget::pane {{
                border: none;
                background-color: white;
            }}
            QTabWidget::tab-bar {{
                alignment: center;
            }}
            QTabBar::tab {{
                background-color: {MARNAK_LIGHT_BLUE};
                color: {MARNAK_BLUE};
                min-width: 150px;
                min-height: 40px;
                padding: 8px 16px;
                margin: 4px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }}
            QTabBar::tab:selected {{
                background-color: {MARNAK_BLUE};
                color: white;
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {MARNAK_LIGHT_GREEN};
                color: {MARNAK_GREEN};
            }}
            QLabel {{
                color: {MARNAK_BLUE};
                font-size: 13px;
                font-weight: bold;
            }}
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background-color: {MARNAK_LIGHT_BLUE};
                height: 8px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {MARNAK_GREEN};
                border-radius: 4px;
            }}
        """)
        self.setup_ui()
        
        # Pencereye tıklanabilirlik özelliği ekle
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

    def setup_logging(self):
        """Hata loglama sistemini kur"""
        import logging
        logging.basicConfig(
            filename='pdf_gui.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def check_pdf(self, file_path):
        """PDF dosyasını kontrol et"""
        try:
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                if reader.is_encrypted:
                    return False, "PDF şifrelenmiş"
                if len(reader.pages) == 0:
                    return False, "PDF dosyası boş"
                return True, None
        except Exception as e:
            return False, f"PDF dosyası bozuk veya okunamıyor: {str(e)}"
    
    def add_file_to_list(self, file_path, list_widget):
        """Dosyayı listeye ekle"""
        # Önce PDF'i kontrol et
        is_valid, error = self.check_pdf(file_path)
        if not is_valid:
            QMessageBox.warning(self, "Uyarı", f"{os.path.basename(file_path)}: {error}")
            return False
            
        item = QListWidgetItem(self.get_pdf_info(file_path))
        item.setData(Qt.ItemDataRole.UserRole, file_path)
        list_widget.addItem(item)
        return True

    def create_cancel_button(self):
        """İptal butonu oluştur"""
        cancel_btn = ModernButton("❌ İşlemi İptal Et")
        cancel_btn.clicked.connect(self.cancel_operation)
        cancel_btn.setVisible(False)
        return cancel_btn

    def cancel_operation(self):
        """İşlemi iptal et"""
        self.cancel_requested = True
        QMessageBox.information(self, "Bilgi", "İşlem iptal ediliyor, lütfen bekleyin...")

    def set_processing(self, state: bool):
        """İşlem durumunu ayarla ve butonları güncelle"""
        self.is_processing = state
        self.cancel_requested = False
        
        # İptal butonlarını güncelle
        self.merge_cancel_btn.setVisible(state)
        self.split_cancel_btn.setVisible(state)
        self.rename_cancel_btn.setVisible(state)
        
        # Diğer butonları güncelle
        for button in self.findChildren(ModernButton):
            if not button.text().startswith("❌"):  # İptal butonlarını hariç tut
                button.setEnabled(not state)

    def safe_filename(self, filename: str, folder: str) -> str:
        """Güvenli ve benzersiz dosya adı oluştur"""
        base, ext = os.path.splitext(filename)
        counter = 1
        new_filename = filename
        while os.path.exists(os.path.join(folder, new_filename)):
            new_filename = f"{base}_{counter}{ext}"
            counter += 1
        return new_filename

    def select_files(self, tab_type):
        """Dosya seçme dialogunu göster"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "PDF Dosyaları Seç",
            "",
            "PDF Dosyaları (*.pdf)"
        )
        if files:
            self.handle_dropped_files(files, tab_type)

    def handle_paste(self, tab_type):
        """Panodaki dosyaları işle"""
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        
        if mime_data.hasUrls():
            files = [url.toLocalFile() for url in mime_data.urls()]
            self.handle_dropped_files(files, tab_type)
        else:
            QMessageBox.warning(self, "Uyarı", "Panoda PDF dosyası bulunamadı!")

    def setup_ui(self):
        # Ana widget ve layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Tab widget oluştur
        tabs = QTabWidget()
        tabs.currentChanged.connect(self.on_tab_changed)
        layout.addWidget(tabs)
        
        # Yeniden Adlandırma Sekmesi
        rename_tab = QWidget()
        rename_layout = QVBoxLayout(rename_tab)
        rename_layout.setContentsMargins(20, 20, 20, 20)
        rename_layout.setSpacing(15)
        
        # Başlık ve açıklama
        title_label = QLabel("📝 Toplu PDF Yeniden Adlandırma")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {MARNAK_BLUE};
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                background-color: {MARNAK_LIGHT_BLUE};
                border-radius: 4px;
            }}
        """)
        rename_layout.addWidget(title_label)
        
        info_label = QLabel(
            "Bu bölümde birden fazla PDF dosyasını tek seferde yeniden adlandırabilirsiniz.\n"
            "Örnek: Dosya adı girişine 'Fatura' yazarsanız:\n"
            "• Fatura_1.pdf\n"
            "• Fatura_2.pdf\n"
            "• Fatura_3.pdf\n"
            "şeklinde sıralı olarak adlandırılacaktır."
        )
        info_label.setStyleSheet(f"""
            QLabel {{
                color: {MARNAK_BLUE};
                font-size: 13px;
                padding: 10px;
                background-color: {MARNAK_LIGHT_BLUE};
                border-radius: 4px;
            }}
        """)
        info_label.setWordWrap(True)
        rename_layout.addWidget(info_label)
        
        # İsim girişi
        name_layout = QHBoxLayout()
        name_label = QLabel("Dosya Adı:")
        name_label.setFont(QFont("Segoe UI", 10))
        self.name_input = ModernLineEdit()
        self.name_input.setPlaceholderText("Örnek: Fatura, Belge, Rapor vb.")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        rename_layout.addLayout(name_layout)
        
        # Konum seçme alanı
        location_layout = QHBoxLayout()
        
        # Konum etiketi ve giriş alanı
        self.rename_location = ModernLineEdit()
        self.rename_location.setPlaceholderText("Yeniden adlandırılan dosyaların kaydedileceği konum...")
        self.rename_location.setReadOnly(True)
        
        # Konum seçme butonu
        browse_btn = ModernButton("📂 Konum Seç")
        browse_btn.clicked.connect(self.select_rename_location)
        
        location_layout.addWidget(self.rename_location, stretch=1)
        location_layout.addWidget(browse_btn)
        
        rename_layout.addLayout(location_layout)
        
        # Çıktı konumu etiketi
        self.rename_output_label = QLabel("📍 Yeniden adlandırılan dosyaların konumu: -")
        self.rename_output_label.setStyleSheet(f"""
            QLabel {{
                color: {MARNAK_BLUE};
                padding: 10px;
                background-color: {MARNAK_LIGHT_BLUE};
                border-radius: 4px;
                font-size: 13px;
            }}
        """)
        self.rename_output_label.setWordWrap(True)
        rename_layout.addWidget(self.rename_output_label)
        
        # Sürükle-bırak alanı
        self.rename_drop = DragDropWidget(rename_tab, "rename")
        rename_layout.addWidget(self.rename_drop)
        
        # Dosya listesi başlığı
        files_label = QLabel("📋 Seçili Dosyalar (Yeni isimleri bu sırayla verilecek):")
        files_label.setStyleSheet(f"color: {MARNAK_BLUE}; font-weight: bold;")
        rename_layout.addWidget(files_label)
        
        # Liste ve butonlar için layout
        list_buttons_layout = QHBoxLayout()
        
        # Dosya listesi
        self.rename_list = PDFListWidget()
        list_buttons_layout.addWidget(self.rename_list, stretch=1)
        
        # Butonlar için dikey layout
        buttons_layout = QVBoxLayout()
        
        # Dosya kaldır butonu
        remove_btn = ModernButton("🗑️ Seçili Dosyaları Kaldır")
        remove_btn.clicked.connect(lambda: self.remove_selected_files(self.rename_list))
        buttons_layout.addWidget(remove_btn)
        
        # Tümünü temizle butonu
        clear_btn = ModernButton("🧹 Tümünü Temizle")
        clear_btn.clicked.connect(lambda: self.clear_list(self.rename_list))
        buttons_layout.addWidget(clear_btn)
        
        buttons_layout.addStretch()
        list_buttons_layout.addLayout(buttons_layout)
        
        rename_layout.addLayout(list_buttons_layout)
        
        # İşlem butonu
        rename_btn = ModernButton("✨ PDF'leri Yeniden Adlandır", primary=True)
        rename_btn.clicked.connect(self.rename_pdfs)
        rename_layout.addWidget(rename_btn)
        
        # İlerleme çubuğu
        self.rename_progress = QProgressBar()
        self.rename_progress.setVisible(False)
        rename_layout.addWidget(self.rename_progress)
        
        # İptal butonu
        self.rename_cancel_btn = self.create_cancel_button()
        rename_layout.addWidget(self.rename_cancel_btn)
        
        # Birleştirme Sekmesi
        merge_tab = QWidget()
        merge_layout = QVBoxLayout(merge_tab)
        merge_layout.setContentsMargins(20, 20, 20, 20)
        merge_layout.setSpacing(15)
        
        # Sürükle-bırak alanı
        self.merge_drop = DragDropWidget(merge_tab, "merge")
        merge_layout.addWidget(self.merge_drop)
        
        # Dosya listesi
        self.merge_list = PDFListWidget()
        merge_layout.addWidget(QLabel("Seçili Dosyalar:"))
        
        # Liste ve butonlar için layout
        list_buttons_layout = QHBoxLayout()
        
        # Dosya listesi
        list_buttons_layout.addWidget(self.merge_list, stretch=1)
        
        # Butonlar için dikey layout
        buttons_layout = QVBoxLayout()
        
        # Dosya kaldır butonu
        remove_btn = ModernButton("🗑️ Seçili Dosyaları Kaldır")
        remove_btn.clicked.connect(lambda: self.remove_selected_files(self.merge_list))
        buttons_layout.addWidget(remove_btn)
        
        # Tümünü temizle butonu
        clear_btn = ModernButton("🧹 Tümünü Temizle")
        clear_btn.clicked.connect(lambda: self.clear_list(self.merge_list))
        buttons_layout.addWidget(clear_btn)
        
        # Sıralama butonları
        sort_name_btn = ModernButton("📝 Ada Göre Sırala")
        sort_name_btn.clicked.connect(lambda: self.sort_files(self.merge_list, "name"))
        buttons_layout.addWidget(sort_name_btn)
        
        sort_date_btn = ModernButton("📅 Tarihe Göre Sırala")
        sort_date_btn.clicked.connect(lambda: self.sort_files(self.merge_list, "date"))
        buttons_layout.addWidget(sort_date_btn)
        
        buttons_layout.addStretch()
        list_buttons_layout.addLayout(buttons_layout)
        
        merge_layout.addLayout(list_buttons_layout)
        
        # Çıktı konumu
        self.merge_output_label = QLabel("📍 Birleştirilmiş dosya konumu: -")
        self.merge_output_label.setStyleSheet("""
            QLabel {
                color: #1976D2;
                padding: 10px;
                background-color: #E3F2FD;
                border-radius: 4px;
                font-size: 13px;
            }
        """)
        self.merge_output_label.setWordWrap(True)
        merge_layout.addWidget(self.merge_output_label)
        
        # İşlem butonu
        merge_btn = ModernButton("PDF'leri Birleştir", primary=True)
        merge_btn.clicked.connect(self.merge_pdfs)
        merge_layout.addWidget(merge_btn)
        
        # İlerleme çubuğu
        self.merge_progress = QProgressBar()
        self.merge_progress.setVisible(False)
        merge_layout.addWidget(self.merge_progress)
        
        # İptal butonu
        self.merge_cancel_btn = self.create_cancel_button()
        merge_layout.addWidget(self.merge_cancel_btn)
        
        # Bölme Sekmesi
        split_tab = QWidget()
        split_layout = QVBoxLayout(split_tab)
        split_layout.setContentsMargins(20, 20, 20, 20)
        split_layout.setSpacing(15)
        
        # Sürükle-bırak alanı
        self.split_drop = DragDropWidget(split_tab, "split")
        split_layout.addWidget(self.split_drop)
        
        # Dosya listesi
        self.split_list = PDFListWidget()
        split_layout.addWidget(QLabel("Seçili Dosyalar:"))
        
        # Liste ve butonlar için layout
        list_buttons_layout = QHBoxLayout()
        
        # Dosya listesi
        list_buttons_layout.addWidget(self.split_list, stretch=1)
        
        # Butonlar için dikey layout
        buttons_layout = QVBoxLayout()
        
        # Dosya kaldır butonu
        remove_btn = ModernButton("🗑️ Seçili Dosyaları Kaldır")
        remove_btn.clicked.connect(lambda: self.remove_selected_files(self.split_list))
        buttons_layout.addWidget(remove_btn)
        
        # Tümünü temizle butonu
        clear_btn = ModernButton("🧹 Tümünü Temizle")
        clear_btn.clicked.connect(lambda: self.clear_list(self.split_list))
        buttons_layout.addWidget(clear_btn)
        
        buttons_layout.addStretch()
        list_buttons_layout.addLayout(buttons_layout)
        
        split_layout.addLayout(list_buttons_layout)
        
        # Konum seçme alanı
        location_layout = QHBoxLayout()
        
        # Konum etiketi ve giriş alanı
        self.split_location = ModernLineEdit()
        self.split_location.setPlaceholderText("Bölünen dosyaların kaydedileceği konum...")
        self.split_location.setReadOnly(True)
        
        # Konum seçme butonu
        browse_btn = ModernButton("📂 Konum Seç")
        browse_btn.clicked.connect(self.select_split_location)
        
        location_layout.addWidget(self.split_location, stretch=1)
        location_layout.addWidget(browse_btn)
        
        split_layout.addLayout(location_layout)
        
        # Çıktı konumu etiketi
        self.split_output_label = QLabel("📍 Bölünen dosyaların konumu: -")
        self.split_output_label.setStyleSheet(f"""
            QLabel {{
                color: {MARNAK_BLUE};
                padding: 10px;
                background-color: {MARNAK_LIGHT_BLUE};
                border-radius: 4px;
                font-size: 13px;
            }}
        """)
        self.split_output_label.setWordWrap(True)
        split_layout.addWidget(self.split_output_label)
        
        # İşlem butonu
        split_btn = ModernButton("PDF'leri Böl", primary=True)
        split_btn.clicked.connect(self.split_pdfs)
        split_layout.addWidget(split_btn)
        
        # İlerleme çubuğu
        self.split_progress = QProgressBar()
        self.split_progress.setVisible(False)
        split_layout.addWidget(self.split_progress)
        
        # İptal butonu
        self.split_cancel_btn = self.create_cancel_button()
        split_layout.addWidget(self.split_cancel_btn)
        
        # Sekmeleri ekle
        tabs.addTab(rename_tab, "Yeniden Adlandır")
        tabs.addTab(merge_tab, "Birleştir")
        tabs.addTab(split_tab, "Böl")
        
        self.current_files = []

    def get_pdf_info(self, file_path):
        """PDF dosyası hakkında bilgi al"""
        try:
            reader = PdfReader(file_path)
            page_count = len(reader.pages)
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB cinsinden
            return f"📄 {os.path.basename(file_path)}\n    📋 {page_count} sayfa  📦 {file_size:.1f} MB"
        except Exception as e:
            return f"📄 {os.path.basename(file_path)}"

    def remove_selected_files(self, list_widget):
        """Seçili dosyaları listeden kaldır"""
        for item in list_widget.selectedItems():
            list_widget.takeItem(list_widget.row(item))

    def clear_list(self, list_widget):
        """Listeyi temizle"""
        list_widget.clear()

    def natural_sort_key(self, file_path):
        """Windows tarzı doğal sıralama için anahtar fonksiyonu"""
        import re
        
        # Dosya adını al
        filename = os.path.basename(file_path)
        # Uzantıyı kaldır
        filename = os.path.splitext(filename)[0]
        
        def convert(text):
            # Eğer text sayısal ise int'e çevir, değilse aynen bırak
            return int(text) if text.isdigit() else text.lower()
        
        # Metni sayısal ve metinsel parçalara ayır
        return [convert(c) for c in re.split('([0-9]+)', filename)]

    def sort_files(self, list_widget, sort_type):
        """Dosyaları sırala"""
        try:
            # Tüm öğelerin verilerini güvenli bir şekilde topla
            items_data = []
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                if item:  # Öğenin var olduğundan emin ol
                    file_path = item.data(Qt.ItemDataRole.UserRole)
                    display_text = item.text()
                    if file_path and os.path.exists(file_path):  # Dosya yolunun geçerli olduğundan emin ol
                        items_data.append((file_path, display_text))
            
            if not items_data:  # Liste boşsa işlem yapma
                QMessageBox.warning(self, "Uyarı", "Sıralanacak dosya bulunamadı!")
                return
            
            # Sıralama kriterine göre sırala
            if sort_type == "name":
                # Windows tarzı doğal sıralama kullan
                items_data.sort(key=lambda x: self.natural_sort_key(x[0]))
            elif sort_type == "date":
                items_data.sort(key=lambda x: os.path.getmtime(x[0]))
            
            # Listeyi güvenli bir şekilde güncelle
            list_widget.clear()  # Önce listeyi temizle
            
            # Yeni öğeleri ekle
            for file_path, _ in items_data:
                new_item = QListWidgetItem(self.get_pdf_info(file_path))
                new_item.setData(Qt.ItemDataRole.UserRole, file_path)
                list_widget.addItem(new_item)
                
        except Exception as e:
            error_msg = str(e)
            print(f"Sıralama hatası: {error_msg}")
            QMessageBox.critical(self, "Hata", f"Dosyalar sıralanırken hata oluştu:\n{error_msg}")
            return False
        
        return True

    def handle_dropped_files(self, files, tab_type):
        try:
            pdf_files = [f for f in files if f.lower().endswith('.pdf')]
            if not pdf_files:
                QMessageBox.warning(self, "Uyarı", "Lütfen PDF dosyaları sürükleyin!")
                return
                
            # Dosyaları ilgili listeye ekle
            if tab_type == "rename":
                list_widget = self.rename_list
            elif tab_type == "merge":
                list_widget = self.merge_list
            elif tab_type == "split":
                list_widget = self.split_list
            
            for file in pdf_files:
                self.add_file_to_list(file, list_widget)
            
            # Sürükle-bırak alanının etiketini güncelle
            if tab_type == "rename":
                self.rename_drop.setText(f"{list_widget.count()} PDF dosyası seçildi")
            elif tab_type == "merge":
                self.merge_drop.setText(f"{list_widget.count()} PDF dosyası seçildi")
            elif tab_type == "split":
                self.split_drop.setText(f"{list_widget.count()} PDF dosyası seçildi")
                
        except Exception as e:
            print(f"Dosya işleme hatası: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Dosyalar işlenirken hata oluştu: {str(e)}")

    def check_disk_space(self, required_space, path):
        """Disk alanı kontrolü"""
        try:
            total, used, free = shutil.disk_usage(path)
            return free > required_space
        except Exception as e:
            self.logger.error(f"Disk alanı kontrolü hatası: {str(e)}")
            return False

    def estimate_required_space(self, file_paths):
        """Gerekli disk alanını tahmin et"""
        try:
            total_size = 0
            for path in file_paths:
                total_size += os.path.getsize(path)
            return total_size * 2  # Güvenli bir tahmin için 2 katı
        except Exception as e:
            self.logger.error(f"Dosya boyutu hesaplama hatası: {str(e)}")
            return 0

    def cleanup_temp_files(self, folder):
        """Geçici dosyaları temizle"""
        try:
            if os.path.exists(folder):
                for file in os.listdir(folder):
                    try:
                        file_path = os.path.join(folder, file)
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        self.logger.error(f"Dosya silme hatası: {str(e)}")
                os.rmdir(folder)
        except Exception as e:
            self.logger.error(f"Klasör temizleme hatası: {str(e)}")

    def select_rename_location(self):
        """Yeniden adlandırılan dosyaların kaydedileceği konumu seç"""
        folder = QFileDialog.getExistingDirectory(self, "Kayıt Konumu Seç")
        if folder:
            self.rename_location.setText(folder)
            self.rename_output_label.setText(f"📍 Yeniden adlandırılan dosyaların konumu: {folder}")

    def rename_pdfs(self):
        """PDF'leri yeniden adlandır"""
        if self.is_processing:
            return
            
        try:
            self.set_processing(True)
            list_widget = self.rename_list
            if list_widget.count() == 0:
                QMessageBox.warning(self, "Uyarı", "Lütfen PDF dosyaları sürükleyin!")
                return
                
            name = self.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Uyarı", "Lütfen bir isim girin!")
                return

            # Konum kontrolü
            output_folder = self.rename_location.text()
            if not output_folder:
                QMessageBox.warning(self, "Uyarı", "Lütfen kayıt konumu seçin!")
                return
            
            # Çıktı klasörünün varlığını kontrol et ve oluştur
            try:
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                elif not os.path.isdir(output_folder):
                    raise Exception("Seçilen konum bir klasör değil!")
            except Exception as e:
                raise Exception(f"Çıktı klasörü oluşturulamadı: {str(e)}")
            
            # İlerleme çubuğunu göster
            self.rename_progress.setVisible(True)
            self.rename_progress.setMaximum(list_widget.count())
            self.rename_progress.setValue(0)
            
            # Dosya yollarını topla
            file_paths = []
            for i in range(list_widget.count()):
                file_path = list_widget.item(i).data(Qt.ItemDataRole.UserRole)
                if os.path.exists(file_path):
                    file_paths.append(file_path)
            
            # Disk alanı kontrolü
            required_space = self.estimate_required_space(file_paths)
            if not self.check_disk_space(required_space, output_folder):
                raise Exception("Yeterli disk alanı yok!")
            
            # 4.1. Seçilen konuma PDF'leri taşı
            moved_files = []  # Taşınan dosyaların yeni yollarını tut
            for i, file_path in enumerate(file_paths):
                if self.cancel_requested:
                    raise Exception("İşlem kullanıcı tarafından iptal edildi")
                
                try:
                    # Dosyayı seçilen konuma taşı
                    file_name = os.path.basename(file_path)
                    target_path = os.path.join(output_folder, file_name)
                    shutil.move(file_path, target_path)
                    moved_files.append(target_path)  # Yeni dosya yolunu kaydet
                    self.logger.info(f"Dosya taşındı: {file_path} -> {target_path}")
                except Exception as e:
                    self.logger.error(f"Dosya taşıma hatası: {str(e)}")
                    raise Exception(f"Dosya taşınırken hata oluştu: {str(e)}")
            
            # 4.2. Orijinal dosyalar klasörü oluştur
            original_folder = os.path.join(output_folder, "Orijinal_Dosyalar")
            try:
                os.makedirs(original_folder, exist_ok=True)
                
                # 4.3. Orijinal dosyaları klasörüne kopyala ve yeniden adlandır
                for i, file_path in enumerate(moved_files):
                    if self.cancel_requested:
                        raise Exception("İşlem kullanıcı tarafından iptal edildi")
                    
                    # Orijinal dosyayı kopyala
                    file_name = os.path.basename(file_path)
                    original_path = os.path.join(original_folder, file_name)
                    shutil.copy2(file_path, original_path)
                    
                    # Dosyayı yeni ismiyle yeniden adlandır
                    new_name = f"{name}_{i+1}.pdf"
                    target_path = os.path.join(output_folder, new_name)
                    target_path = self.safe_filename(new_name, output_folder)
                    
                    # Dosyayı yeniden adlandır
                    os.rename(file_path, target_path)
                    self.rename_progress.setValue(i + 1)
                    
                    self.logger.info(f"Dosya işlendi: {file_name}")
                    self.logger.info(f"Orijinal kopya: {original_path}")
                    self.logger.info(f"Yeni isim: {target_path}")
                
                # Çıktı klasörünü kontrol et
                if os.path.exists(output_folder):
                    files = [f for f in os.listdir(output_folder) if f.endswith('.pdf') and f != "Orijinal_Dosyalar"]
                    if not files:
                        raise Exception("Hiçbir PDF dosyası oluşturulamadı!")
                
                self.rename_output_label.setText(f"📍 Yeniden adlandırılan dosyaların konumu: {output_folder}")
                
                QMessageBox.information(self, "Başarılı", 
                    f"PDF'ler başarıyla yeniden adlandırıldı!\nKonum: {output_folder}\nOrijinal dosyalar: {original_folder}")
                
                self.rename_drop.setText("PDF dosyalarını buraya sürükleyin")
                list_widget.clear()
                
            except Exception as e:
                # Hata durumunda orijinal klasörü temizle
                if os.path.exists(original_folder):
                    self.cleanup_temp_files(original_folder)
                raise e
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Yeniden adlandırma hatası: {error_msg}", exc_info=True)
            if "iptal edildi" in error_msg:
                QMessageBox.information(self, "Bilgi", "İşlem iptal edildi")
            else:
                QMessageBox.critical(self, "Hata", 
                    f"PDF'ler yeniden adlandırılırken hata oluştu:\n{error_msg}")
        finally:
            self.rename_progress.setVisible(False)
            self.set_processing(False)

    def merge_pdfs(self):
        """PDF'leri birleştir"""
        if self.is_processing:
            return
            
        try:
            self.set_processing(True)
            list_widget = self.merge_list
            if list_widget.count() == 0:
                QMessageBox.warning(self, "Uyarı", "Lütfen PDF dosyaları sürükleyin!")
                return
            
            # Dosya yollarını topla
            file_paths = []
            for i in range(list_widget.count()):
                file_path = list_widget.item(i).data(Qt.ItemDataRole.UserRole)
                if os.path.exists(file_path):
                    file_paths.append(file_path)
            
            # Disk alanı kontrolü
            folder_path = os.path.dirname(file_paths[0])
            required_space = self.estimate_required_space(file_paths)
            if not self.check_disk_space(required_space, folder_path):
                raise Exception("Yeterli disk alanı yok!")
            
            # İlerleme çubuğunu göster
            self.merge_progress.setVisible(True)
            self.merge_progress.setMaximum(len(file_paths) * 2)
            self.merge_progress.setValue(0)
            
            temp_folder = os.path.join(folder_path, "temp_merge")
            
            try:
                os.makedirs(temp_folder, exist_ok=True)
                
                # Dosyaları temp klasöre kopyala
                for i, file_path in enumerate(file_paths):
                    if self.cancel_requested:
                        raise Exception("İşlem kullanıcı tarafından iptal edildi")
                    
                    shutil.copy2(file_path, temp_folder)
                    self.merge_progress.setValue(i + 1)
                
                if self.cancel_requested:
                    raise Exception("İşlem kullanıcı tarafından iptal edildi")
                
                # Birleştirme işlemi
                merge_pdfs(temp_folder)
                self.merge_progress.setValue(len(file_paths) * 2)
                
                # Birleştirilen dosyayı bul ve taşı
                merged_files = [f for f in os.listdir(temp_folder) if f.endswith('_b.pdf')]
                if merged_files:
                    merged_file = merged_files[0]
                    safe_name = self.safe_filename(merged_file, folder_path)
                    final_path = os.path.join(folder_path, safe_name)
                    
                    shutil.move(os.path.join(temp_folder, merged_file), final_path)
                    self.merge_output_label.setText(f"📍 Birleştirilmiş dosya konumu: {final_path}")
                    
                    QMessageBox.information(self, "Başarılı", 
                        f"PDF'ler başarıyla birleştirildi!\nKonum: {final_path}")
                
                self.merge_drop.setText("PDF dosyalarını buraya sürükleyin")
                list_widget.clear()
                
            finally:
                self.cleanup_temp_files(temp_folder)
                
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Birleştirme hatası: {error_msg}", exc_info=True)
            if "iptal edildi" in error_msg:
                QMessageBox.information(self, "Bilgi", "İşlem iptal edildi")
            else:
                QMessageBox.critical(self, "Hata", 
                    f"PDF'ler birleştirilirken hata oluştu:\n{error_msg}")
        finally:
            self.set_processing(False)

    def select_split_location(self):
        """Bölünen dosyaların kaydedileceği konumu seç"""
        folder = QFileDialog.getExistingDirectory(self, "Kayıt Konumu Seç")
        if folder:
            self.split_location.setText(folder)
            self.split_output_label.setText(f"📍 Bölünen dosyaların konumu: {folder}")

    def split_pdfs(self):
        """PDF'leri böl"""
        if self.is_processing:
            return
            
        try:
            self.set_processing(True)
            list_widget = self.split_list
            if list_widget.count() == 0:
                QMessageBox.warning(self, "Uyarı", "Lütfen PDF dosyaları sürükleyin!")
                return

            # Konum kontrolü
            output_folder = self.split_location.text()
            if not output_folder:
                QMessageBox.warning(self, "Uyarı", "Lütfen kayıt konumu seçin!")
                return
            
            # Çıktı klasörünün varlığını kontrol et ve oluştur
            try:
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                elif not os.path.isdir(output_folder):
                    raise Exception("Seçilen konum bir klasör değil!")
            except Exception as e:
                raise Exception(f"Çıktı klasörü oluşturulamadı: {str(e)}")
            
            # Dosya yollarını topla
            file_paths = []
            for i in range(list_widget.count()):
                file_path = list_widget.item(i).data(Qt.ItemDataRole.UserRole)
                if os.path.exists(file_path):
                    file_paths.append(file_path)
            
            # Disk alanı kontrolü
            required_space = self.estimate_required_space(file_paths)
            if not self.check_disk_space(required_space, output_folder):
                raise Exception("Yeterli disk alanı yok!")
            
            # İlerleme çubuğunu göster
            total_steps = len(file_paths)
            self.split_progress.setVisible(True)
            self.split_progress.setMaximum(total_steps)
            self.split_progress.setValue(0)
            
            # Her dosyayı böl
            for i, file_path in enumerate(file_paths):
                if self.cancel_requested:
                    raise Exception("İşlem kullanıcı tarafından iptal edildi")
                    
                try:
                    self.logger.info(f"Dosya bölünüyor: {file_path}")
                    self.logger.info(f"Hedef klasör: {output_folder}")
                    
                    # Dosyayı böl
                    success = split_pdf(file_path, output_folder)
                    if success:
                        self.split_progress.setValue(i + 1)
                        self.logger.info(f"Dosya başarıyla bölündü: {file_path}")
                    else:
                        self.logger.error(f"Dosya bölme başarısız: {file_path}")
                    
                except Exception as e:
                    self.logger.error(f"Dosya bölme hatası: {str(e)}")
                    self.logger.error(f"Hata detayı: {traceback.format_exc()}")
                    continue
            
            # Çıktı klasörünü kontrol et
            if os.path.exists(output_folder):
                files = os.listdir(output_folder)
                if not any(f.endswith('.pdf') for f in files):
                    raise Exception("Hiçbir PDF dosyası oluşturulamadı!")
            
            self.split_output_label.setText(f"📍 Bölünen dosyaların konumu: {output_folder}")
            
            QMessageBox.information(self, "Başarılı", 
                f"PDF'ler başarıyla bölündü!\nKonum: {output_folder}")
            
            self.split_drop.setText("PDF dosyalarını buraya sürükleyin")
            list_widget.clear()
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Bölme hatası: {error_msg}", exc_info=True)
            if "iptal edildi" in error_msg:
                QMessageBox.information(self, "Bilgi", "İşlem iptal edildi")
            else:
                QMessageBox.critical(self, "Hata", 
                    f"PDF'ler bölünürken hata oluştu:\n{error_msg}")
        finally:
            self.split_progress.setVisible(False)
            self.set_processing(False)

    def keyPressEvent(self, event):
        """Klavye kısayollarını yakala"""
        # Ctrl+V kombinasyonunu kontrol et
        if event.key() == Qt.Key.Key_V and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Eğer odaktaki widget ModernLineEdit değilse dosya yapıştır
            focused_widget = QApplication.focusWidget()
            if not isinstance(focused_widget, ModernLineEdit):
                self.handle_paste(self.current_tab)

    def on_tab_changed(self, index):
        """Sekme değiştiğinde çağrılır"""
        tab_map = {
            0: "rename",
            1: "merge",
            2: "split"
        }
        self.current_tab = tab_map.get(index, "rename")

    def mousePressEvent(self, event):
        """Mouse tıklama olayını yakala"""
        super().mousePressEvent(event)
        # Aktif widget'ı bul
        focused_widget = QApplication.focusWidget()
        # Eğer aktif widget ModernLineEdit ise odağı kaldır
        if isinstance(focused_widget, ModernLineEdit):
            focused_widget.clearFocus()
        # Ana pencereye odağı ver
        self.setFocus()

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        
        # Stil ayarları
        app.setStyle('Fusion')
        
        window = PDFGUI()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Program hatası: {str(e)}")
        print("Hata detayı:")
        traceback.print_exc() 