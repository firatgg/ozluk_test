"""
PDF bölme penceresi.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QFileDialog, QMessageBox, QComboBox,
    QLabel, QSpinBox, QLineEdit, QFormLayout,
    QGroupBox, QRadioButton, QButtonGroup,
    QCheckBox, QPushButton, QFrame, QSplitter,
    QStackedWidget, QScrollArea
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
from ..styles import (
    SECTION_TITLE_STYLE, CARD_STYLE, FILE_LIST_STYLE,
    FORM_STYLE, CHECKBOX_STYLE, RADIO_STYLE,
    INFO_BOX_STYLE, STEP_INDICATOR_STYLE,
    ACTIVE_STEP_STYLE, INACTIVE_STEP_STYLE,
    ARROW_STYLE, SEPARATOR_STYLE, SCROLLBAR_STYLE,
    GREEN_BUTTON_STYLE
)

# Marnak Lojistik Kurumsal Renkleri
MARNAK_BLUE = "#0066B3"
MARNAK_GREEN = "#3AB54A"
MARNAK_LIGHT_BLUE = "#E5F1F9"
MARNAK_LIGHT_GREEN = "#E8F5EA"

class PDFSplitWindow(QWidget):
    """PDF bölme penceresi."""
    
    # Sinyaller
    split_requested = pyqtSignal(str, str)  # Dosya yolu, çıktı dizini
    
    # Bölme modları
    SPLIT_MODE_ALL_PAGES = "all_pages"  # Tüm sayfaları böl
    SPLIT_MODE_PAGE_RANGE = "page_range"  # Sayfa aralığına göre böl
    SPLIT_MODE_EVERY_N_PAGES = "every_n_pages"  # Her N sayfada bir böl
    SPLIT_MODE_ODD_EVEN = "odd_even"  # Tek/Çift sayfalara göre böl
    
    def __init__(self, pdf_service):
        super().__init__()
        self.pdf_service = pdf_service
        
        # Veri koruma özelliği (ekranlar arası geçişte veriyi silme)
        self.persistData = True
        
        # Responsive tasarım için boyut bilgisi
        self.is_compact_mode = False
        
        # UI bileşenlerini oluştur
        self.init_ui()
        
        # Çıktı dizini
        self.output_dir = None
        
        # İş parçacığı
        self.worker = None
        
        # Başlangıç UI durumunu ayarla
        self.update_options_ui()
        self.update_file_count()
        
        # Pencere açıldığında DragDropWidget'a odak ver (Kaldırıldı)
        # QTimer.singleShot(100, self.drag_drop.setFocus)
    
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
    
    def init_ui(self):
        """Kullanıcı arayüzünü oluşturur."""
        # Ana düzen
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlık
        header = HeaderLabel("PDF Bölme")
        main_layout.addWidget(header)
        
        # İşlem adımları
        steps_widget = QWidget()
        steps_widget.setStyleSheet(STEP_INDICATOR_STYLE)
        steps_layout = QHBoxLayout(steps_widget)
        steps_layout.setContentsMargins(10, 10, 10, 10)
        steps_layout.setSpacing(15)
        
        # Adım etiketleri oluştur
        self.step1_label = QLabel("1. Dosya Seçimi")
        self.step1_label.setStyleSheet(ACTIVE_STEP_STYLE)
        
        self.step2_label = QLabel("2. Bölme Seçenekleri")
        self.step2_label.setStyleSheet(INACTIVE_STEP_STYLE)
        
        self.step3_label = QLabel("3. Dizin Seçimi")
        self.step3_label.setStyleSheet(INACTIVE_STEP_STYLE)
        
        # Ok etiketleri
        arrow1 = QLabel("➔")
        arrow1.setStyleSheet(ARROW_STYLE)
        arrow1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        arrow2 = QLabel("➔")
        arrow2.setStyleSheet(ARROW_STYLE)
        arrow2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Adımları düzene ekle
        steps_layout.addWidget(self.step1_label)
        steps_layout.addWidget(arrow1)
        steps_layout.addWidget(self.step2_label)
        steps_layout.addWidget(arrow2)
        steps_layout.addWidget(self.step3_label)
        steps_layout.addStretch()
        
        main_layout.addWidget(steps_widget)
        
        # Ayırıcı çizgi
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(SEPARATOR_STYLE)
        main_layout.addWidget(separator)
        
        # Ana içerik - bölücü
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Sol panel - Dosya listesi container
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        # Dosya seçimi kart widget'ı
        file_card = QWidget()
        file_card.setStyleSheet(CARD_STYLE)
        file_layout = QVBoxLayout(file_card)
        file_layout.setSpacing(15)
        
        # Dosya seçimi başlığı
        files_header = QLabel("Dosya Seçimi")
        files_header.setStyleSheet(SECTION_TITLE_STYLE)
        file_layout.addWidget(files_header)
        
        # Sürükle-bırak alanı
        self.drag_drop = DragDropWidget(self, "split")
        self.drag_drop.files_dropped.connect(self.add_files)
        file_layout.addWidget(self.drag_drop)
        
        # Dosya işlemleri
        file_actions = QHBoxLayout()
        file_actions.setSpacing(10)
        
        # Dosya ekleme düğmesi
        self.add_file_btn = ModernButton("Dosya Ekle", primary=False)
        self.add_file_btn.clicked.connect(self.select_files)
        self.add_file_btn.setMinimumWidth(120)
        file_actions.addWidget(self.add_file_btn)
        
        # Dosya silme düğmesi
        self.remove_file_btn = ModernButton("Seçili Dosyaları Kaldır", primary=False)
        self.remove_file_btn.clicked.connect(self.remove_checked_files)
        self.remove_file_btn.setMinimumWidth(170)
        file_actions.addWidget(self.remove_file_btn)
        
        file_layout.addLayout(file_actions)
        
        # Seçim kontrolü
        check_control = QHBoxLayout()
        check_control.setContentsMargins(0, 5, 0, 5)
        
        # Tümünü seç/hiçbirini seçme
        self.select_all_checkbox = QCheckBox("Tümünü Seç")
        self.select_all_checkbox.setStyleSheet(CHECKBOX_STYLE)
        self.select_all_checkbox.setChecked(True)
        self.select_all_checkbox.stateChanged.connect(self.toggle_all_files)
        check_control.addWidget(self.select_all_checkbox)
        check_control.addStretch()
        
        # Seçili dosya sayısı
        self.selected_count_label = QLabel("0 dosya seçili")
        check_control.addWidget(self.selected_count_label)
        
        file_layout.addLayout(check_control)
        
        # Dosya listesi
        self.file_list = FileListWidget(selectable=True)
        self.file_list.setStyleSheet(FILE_LIST_STYLE)
        self.file_list.setMinimumHeight(400)  # PDF listesi için daha fazla alan
        self.file_list.files_changed.connect(self.update_file_count)
        # self.file_list.files_removed.connect(self.refocus_drag_drop) # Kaldırıldı
        self.file_list.itemChanged.connect(self.check_item_state)
        file_layout.addWidget(self.file_list)
        
        left_layout.addWidget(file_card)
        
        # Sağ panel - bölme seçenekleri kartı
        right_panel = QScrollArea()
        right_panel.setWidgetResizable(True)
        right_panel.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        right_panel.setFrameShape(QFrame.Shape.NoFrame)
        
        right_content = QWidget()
        right_layout = QVBoxLayout(right_content)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        # Bölme seçenekleri kartı
        options_card = QWidget()
        options_card.setStyleSheet(CARD_STYLE)
        options_layout = QVBoxLayout(options_card)
        options_layout.setSpacing(15)
        
        # Bölme seçenekleri başlığı
        options_header = QLabel("Bölme Seçenekleri")
        options_header.setStyleSheet(SECTION_TITLE_STYLE)
        options_layout.addWidget(options_header)
        
        # Bölme modu seçimi
        mode_widget = QWidget()
        mode_layout = QVBoxLayout(mode_widget)
        mode_layout.setContentsMargins(0, 0, 0, 0)
        mode_layout.setSpacing(10)
        
        mode_label = QLabel("Bölme Modunu Seçin:")
        mode_label.setStyleSheet(FORM_STYLE)
        mode_layout.addWidget(mode_label)
        
        # Bölme modu combobox'ı
        self.mode_combo = QComboBox()
        self.mode_combo.setStyleSheet(FORM_STYLE)
        self.mode_combo.addItem("Tüm Sayfaları Ayrı Ayrı Böl", self.SPLIT_MODE_ALL_PAGES)
        self.mode_combo.addItem("Sayfa Aralığını Böl", self.SPLIT_MODE_PAGE_RANGE)
        self.mode_combo.addItem("Her N Sayfada Bir Böl", self.SPLIT_MODE_EVERY_N_PAGES)
        self.mode_combo.addItem("Tek/Çift Sayfaları Böl", self.SPLIT_MODE_ODD_EVEN)
        self.mode_combo.currentIndexChanged.connect(self.update_options_ui)
        mode_layout.addWidget(self.mode_combo)
        
        # Mod açıklaması
        self.mode_description = QLabel()
        self.mode_description.setStyleSheet(INFO_BOX_STYLE)
        self.mode_description.setWordWrap(True)
        mode_layout.addWidget(self.mode_description)
        
        options_layout.addWidget(mode_widget)
        
        # Seçenek konteyner
        self.options_stack = QStackedWidget()
        
        # 1. Tüm Sayfaları Ayrı Ayrı Böl
        all_pages_widget = QWidget()
        all_pages_layout = QVBoxLayout(all_pages_widget)
        all_pages_layout.setContentsMargins(0, 0, 0, 0)
        all_pages_description = QLabel("Her sayfa ayrı bir PDF dosyası olarak bölünecektir.")
        all_pages_description.setStyleSheet(INFO_BOX_STYLE)
        all_pages_description.setWordWrap(True)
        all_pages_layout.addWidget(all_pages_description)
        all_pages_layout.addStretch()
        self.options_stack.addWidget(all_pages_widget)
        
        # 2. Sayfa Aralığını Böl
        range_widget = QWidget()
        range_layout = QVBoxLayout(range_widget)
        range_layout.setContentsMargins(0, 0, 0, 0)
        range_layout.setSpacing(10)
        
        range_label = QLabel("Sayfa Aralığı:")
        range_label.setStyleSheet(FORM_STYLE)
        range_layout.addWidget(range_label)
        
        self.range_input = ModernLineEdit()
        self.range_input.setPlaceholderText("Örn: 1-5, 8-10, 15")
        range_layout.addWidget(self.range_input)
        
        range_help = QLabel("Her aralık ayrı bir PDF olarak oluşturulacaktır. Virgülle ayırın.")
        range_help.setStyleSheet(INFO_BOX_STYLE)
        range_help.setWordWrap(True)
        range_layout.addWidget(range_help)
        
        range_layout.addStretch()
        self.options_stack.addWidget(range_widget)
        
        # 3. Her N Sayfada Bir Böl
        every_n_widget = QWidget()
        every_n_layout = QVBoxLayout(every_n_widget)
        every_n_layout.setContentsMargins(0, 0, 0, 0)
        every_n_layout.setSpacing(10)
        
        every_n_label = QLabel("Her Kaç Sayfada Bir Böl:")
        every_n_label.setStyleSheet(FORM_STYLE)
        every_n_layout.addWidget(every_n_label)
        
        self.every_n_spinbox = QSpinBox()
        self.every_n_spinbox.setStyleSheet(FORM_STYLE)
        self.every_n_spinbox.setMinimum(1)
        self.every_n_spinbox.setMaximum(100)
        self.every_n_spinbox.setValue(1)
        every_n_layout.addWidget(self.every_n_spinbox)
        
        every_n_help = QLabel("PDF, her X sayfada bir bölünecektir.")
        every_n_help.setStyleSheet(INFO_BOX_STYLE)
        every_n_help.setWordWrap(True)
        every_n_layout.addWidget(every_n_help)
        
        every_n_layout.addStretch()
        self.options_stack.addWidget(every_n_widget)
        
        # 4. Tek/Çift Sayfaları Böl
        odd_even_widget = QWidget()
        odd_even_layout = QVBoxLayout(odd_even_widget)
        odd_even_layout.setContentsMargins(0, 0, 0, 0)
        odd_even_layout.setSpacing(10)
        
        odd_even_label = QLabel("Tek/Çift Sayfa Seçenekleri:")
        odd_even_label.setStyleSheet(FORM_STYLE)
        odd_even_layout.addWidget(odd_even_label)
        
        self.odd_radio = QRadioButton("Tek Sayfaları Ayır")
        self.odd_radio.setStyleSheet(RADIO_STYLE)
        self.even_radio = QRadioButton("Çift Sayfaları Ayır")
        self.even_radio.setStyleSheet(RADIO_STYLE)
        self.odd_even_both_radio = QRadioButton("Tek ve Çift Sayfaları Ayrı PDF'lere Böl")
        self.odd_even_both_radio.setStyleSheet(RADIO_STYLE)
        
        self.odd_even_group = QButtonGroup(self)
        self.odd_even_group.addButton(self.odd_radio)
        self.odd_even_group.addButton(self.even_radio)
        self.odd_even_group.addButton(self.odd_even_both_radio)
        
        self.odd_radio.setChecked(True)
        
        odd_even_layout.addWidget(self.odd_radio)
        odd_even_layout.addWidget(self.even_radio)
        odd_even_layout.addWidget(self.odd_even_both_radio)
        
        odd_even_help = QLabel("Seçiminize göre tek, çift veya her ikisini içeren ayrı PDF'ler oluşturulacaktır.")
        odd_even_help.setStyleSheet(INFO_BOX_STYLE)
        odd_even_help.setWordWrap(True)
        odd_even_layout.addWidget(odd_even_help)
        
        odd_even_layout.addStretch()
        self.options_stack.addWidget(odd_even_widget)
        
        options_layout.addWidget(self.options_stack)
        
        # Çıktı dizini seçimi kartı
        output_card = QWidget()
        output_card.setStyleSheet(CARD_STYLE)
        output_layout = QVBoxLayout(output_card)
        output_layout.setSpacing(10)
        
        output_label = QLabel("Çıktı Dizini")
        output_label.setStyleSheet(SECTION_TITLE_STYLE)
        output_layout.addWidget(output_label)
        
        self.select_dir_btn = ModernButton("Dizin Seç", primary=False)
        self.select_dir_btn.clicked.connect(self.select_output_dir)
        output_layout.addWidget(self.select_dir_btn)
        
        self.output_dir_label = QLabel("Henüz dizin seçilmedi")
        self.output_dir_label.setStyleSheet(INFO_BOX_STYLE)
        self.output_dir_label.setWordWrap(True)
        output_layout.addWidget(self.output_dir_label)
        
        # İşleme düğmesi
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.split_btn = ModernButton("Böl")
        self.split_btn.setStyleSheet(GREEN_BUTTON_STYLE)  # Özel stil uygula
        self.split_btn.setEnabled(False)
        self.split_btn.clicked.connect(self.start_splitting)
        button_layout.addWidget(self.split_btn)
        
        right_layout.addWidget(options_card)
        right_layout.addWidget(output_card)
        right_layout.addLayout(button_layout)
        
        # İlerleme çubuğu ve bilgi paneli
        progress_card = QWidget()
        progress_card.setStyleSheet(CARD_STYLE)
        progress_layout = QVBoxLayout(progress_card)
        progress_layout.setSpacing(10)
        
        # İlerleme çubuğu
        self.progress = ModernProgressBar()
        self.progress.hide()
        progress_layout.addWidget(self.progress)
        
        # Bilgi etiketi
        self.info_label = InfoLabel()
        self.info_label.hide()
        progress_layout.addWidget(self.info_label)
        
        # Hata etiketi
        self.error_label = ErrorLabel()
        self.error_label.hide()
        progress_layout.addWidget(self.error_label)
        
        right_layout.addWidget(progress_card)
        right_layout.addStretch()
        
        # Scroll alanını ayarla
        right_panel.setWidget(right_content)
        
        # Panelleri splitter'a ekle
        self.splitter.addWidget(left_panel)
        self.splitter.addWidget(right_panel)
        self.splitter.setSizes([400, 500])  # Panel boyutlarını ayarla - PDF listesi için daha fazla alan
        
        main_layout.addWidget(self.splitter, 1)  # 1 stretch factor ile ekle
        
        # Pencere ayarları
        self.setMinimumSize(1000, 700)
        self.setWindowTitle("PDF Bölme")
    
    def create_step_label(self, number, text):
        """Adım etiketi oluşturur."""
        label = QLabel(f"{number}. {text}")
        label.setStyleSheet(f"""
            background-color: {MARNAK_BLUE};
            color: white;
            padding: 8px 12px;
            border-radius: 5px;
            font-weight: bold;
        """)
        return label
    
    def create_arrow_label(self):
        """Adımlar arası ok oluşturur."""
        label = QLabel(" → ")
        label.setStyleSheet(f"""
            color: {MARNAK_BLUE};
            font-size: 18px;
            font-weight: bold;
        """)
        return label
        
    def update_options_ui(self):
        """Seçilen moda göre UI'ı güncelle"""
        current_mode = self.mode_combo.currentData()
        current_index = self.mode_combo.currentIndex()
        
        # Adım durumlarını güncelle
        self.step1_label.setStyleSheet(INACTIVE_STEP_STYLE)
        self.step2_label.setStyleSheet(ACTIVE_STEP_STYLE)
        self.step3_label.setStyleSheet(INACTIVE_STEP_STYLE)
        
        # Açıklama metinlerini ayarla
        descriptions = [
            "Bu mod, PDF'in her sayfasını ayrı bir PDF dosyası olarak kaydeder. Uzun bir belgeyi sayfalara ayırmak için idealdir.",
            "Bu mod, belirlediğiniz sayfa aralıklarını ayrı PDF'ler olarak kaydeder. Belirli bölümleri ayırmak için kullanışlıdır.",
            "Bu mod, belgeyi belirlediğiniz sayfa sayısına göre böler. Örneğin, her 5 sayfada bir yeni PDF oluşturur.",
            "Bu mod, belgenin tek veya çift sayfalarını ayrı PDF'ler olarak kaydeder. Çift yönlü taranmış belgeleri ayırmak için idealdir."
        ]
        
        if 0 <= current_index < len(descriptions):
            self.mode_description.setText(descriptions[current_index])
        
        # Seçenek panelini göster
        self.options_stack.setCurrentIndex(current_index)
    
    def update_file_count(self):
        """Seçili dosya sayısını ve Tümünü Seç kutusunun durumunu günceller."""
        total_files = self.file_list.count()
        selected_files = len(self.get_selected_files())
        
        # Adım durumlarını güncelle
        if total_files > 0:
            self.step1_label.setStyleSheet(INACTIVE_STEP_STYLE)
            self.step2_label.setStyleSheet(ACTIVE_STEP_STYLE)
        else:
            self.step1_label.setStyleSheet(ACTIVE_STEP_STYLE)
            self.step2_label.setStyleSheet(INACTIVE_STEP_STYLE)
        
        # Seçili dosya sayısını göster
        if total_files == 0:
            self.selected_count_label.setText("Dosya yok")
            # Liste boşaldığında DragDropWidget'a odak ver
            # self.refocus_drag_drop() # Kaldırıldı
        else:
            self.selected_count_label.setText(f"{selected_files}/{total_files} dosya seçili")
            
        # "Tümünü Seç" kutusu için sinyal tuzağından kaçınmak için blockSignals kullan
        self.select_all_checkbox.blockSignals(True)
        
        # Tümünü Seç kutusunun durumunu güncelle
        if total_files == 0:
            # Liste boşsa, varsayılan olarak işaretli
            self.select_all_checkbox.setChecked(True)
        elif selected_files == 0:
            # Hiçbir dosya seçili değilse, işaretsiz
            self.select_all_checkbox.setChecked(False)
        elif selected_files == total_files:
            # Tüm dosyalar seçiliyse, işaretli
            self.select_all_checkbox.setChecked(True)
        else:
            # Bazı dosyalar seçiliyse, işaretsiz
            self.select_all_checkbox.setChecked(False)
            
        # Sinyalleri tekrar etkinleştir
        self.select_all_checkbox.blockSignals(False)
        
        # Bölme butonunu güncelle
        if total_files > 0 and self.output_dir:
            self.split_btn.setEnabled(True)
        else:
            self.split_btn.setEnabled(False)
    
    def toggle_all_files(self, state):
        """Tüm dosyaları seç/işaretle veya seçimleri/işaretleri kaldır."""
        try:
            if state == Qt.CheckState.Checked.value:
                self.file_list.check_all()
            else:
                self.file_list.uncheck_all()
            self.update_file_count()
        except Exception as e:
            self.show_error(f"Dosyaların işaretlenme durumu değiştirilirken hata oluştu: {str(e)}")
    
    def add_files(self, file_paths):
        """Sürükle-bırak ile dosya ekler."""
        try:
            # PDF dosyalarını filtrele
            pdf_files = [f for f in file_paths if f.lower().endswith('.pdf')]
            
            if pdf_files:
                # Dosyaları ekle
                for pdf_file in pdf_files:
                    self.file_list.add_file(pdf_file)
                self.update_file_count() # Dosya sayısı güncellendi

        except Exception as e:
            self.show_error(f"Dosya eklenirken hata oluştu: {str(e)}")
    
    def get_selected_files(self):
        """Seçili/işaretli dosyaların listesini alır."""
        # PDFListWidget sınıfındaki get_checked_files metodunu kullan
        return self.file_list.get_checked_files()
    
    def remove_checked_files(self):
        """İşaretli dosyaları listeden kaldırır."""
        try:
            self.file_list.remove_checked_files()
            self.update_file_count()
            # self.refocus_drag_drop() # Kaldırıldı
        except Exception as e:
            self.show_error(f"İşaretli dosyalar kaldırılırken hata oluştu: {str(e)}")
                
    def select_files(self):
        """Dosya seçme dialogunu açar."""
        try:
            files, _ = QFileDialog.getOpenFileNames(
                self,
                "PDF Dosyası Seç",
                "",
                "PDF Dosyaları (*.pdf)"
            )
            
            if files:
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
                self.output_dir_label.setText(dir_path)
                self.output_dir_label.setStyleSheet(INFO_BOX_STYLE)
                
                # Adım durumlarını güncelle
                self.step1_label.setStyleSheet(INACTIVE_STEP_STYLE)
                self.step2_label.setStyleSheet(INACTIVE_STEP_STYLE)
                self.step3_label.setStyleSheet(ACTIVE_STEP_STYLE)
                
                # Dosya ve dizin seçildiyse, butonları etkinleştir
                if self.file_list.count() > 0:
                    self.split_btn.setEnabled(True)
                else:
                    self.split_btn.setEnabled(False)
        except Exception as e:
            self.show_error(f"Çıktı dizini seçilirken hata oluştu: {str(e)}")
        
    def get_split_options(self):
        """Kullanıcının seçtiği bölme seçeneklerini alır."""
        options = {
            "mode": self.mode_combo.currentData()
        }
        
        # Seçilen moda göre ek bilgileri ekle
        if options["mode"] == self.SPLIT_MODE_PAGE_RANGE:
            options["page_range"] = self.range_input.text()
        elif options["mode"] == self.SPLIT_MODE_EVERY_N_PAGES:
            options["pages_per_split"] = self.every_n_spinbox.value()
        elif options["mode"] == self.SPLIT_MODE_ODD_EVEN:
            if self.odd_radio.isChecked():
                options["odd_even_mode"] = "odd"
            elif self.even_radio.isChecked():
                options["odd_even_mode"] = "even"
            else:
                options["odd_even_mode"] = "both"
                
        return options
    
    def start_splitting(self):
        """Bölme işlemini başlatır."""
        # Seçili dosyaları al
        selected_files = self.get_selected_files()
        
        # Girdileri kontrol et
        if not selected_files:
            self.show_error("Lütfen en az bir PDF dosyası seçin.")
            return
            
        if not self.output_dir:
            self.show_error("Lütfen çıktı dizini seçin.")
            return
            
        # Doğrulama mesajı göster
        current_mode = self.mode_combo.currentText()
        confirm = QMessageBox.question(
            self,
            "Bölme İşlemini Onayla",
            f"<b>{len(selected_files)}</b> PDF dosyası, <b>{current_mode}</b> modunda bölünecek.\n\n"
            f"Çıktı dizini: <b>{self.output_dir}</b>\n\n"
            f"İşleme devam etmek istiyor musunuz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            # Bölme seçeneklerini al
            options = self.get_split_options()
            
            # İşlem başla
            self.process_files(selected_files, options)
            
    def process_files(self, files, options):
        """Birden fazla dosyayı işler."""
        self.total_files = len(files)
        self.processed_files = 0
        self.current_file_index = 0
        self.file_queue = files
        self.split_options = options
        self.success_count = 0
        self.error_count = 0
        
        # Arayüzü güncelle
        self.progress.setValue(0)
        self.progress.show()
        self.info_label.setText("Bölme işlemi başlatılıyor...")
        self.info_label.show()
        self.error_label.hide()
        self.split_btn.setEnabled(False)
        
        # İlk dosyayı işle
        QTimer.singleShot(100, self.process_next_file)
    
    def process_next_file(self):
        """Sıradaki dosyayı işler."""
        if self.current_file_index < len(self.file_queue):
            current_file = self.file_queue[self.current_file_index]
            
            # Dosya yolunu kontrol et
            if not os.path.exists(current_file):
                # Dosya bulunamadı, sonraki dosyaya geç
                self.error_count += 1
                file_name = os.path.basename(current_file)
                self.error_label.setText(f"Hata: {file_name} bulunamadı")
                self.error_label.show()
                print(f"Dosya bulunamadı: {current_file}")
                
                self.processed_files += 1
                self.current_file_index += 1
                QTimer.singleShot(100, self.process_next_file)
                return
                
            # Dosya adını mesaj olarak göster
            try:
                file_name = os.path.basename(current_file)
                self.info_label.setText(f"İşleniyor: {file_name} ({self.current_file_index+1}/{self.total_files})")
                self.info_label.show()
            except Exception as e:
                # Dosya adı işlenirken hata, dosya adını güvenli şekilde göster
                safe_name = str(current_file).encode('utf-8', errors='replace').decode('utf-8', errors='replace')
                self.info_label.setText(f"İşleniyor: Dosya {self.current_file_index+1}/{self.total_files}")
                self.info_label.show()
                print(f"Dosya adı işlenirken hata: {safe_name}, {str(e)}")
            
            # İş parçacığını başlat
            try:
                self.worker = self.pdf_service.create_split_worker(
                    current_file,
                    self.output_dir,
                    self.split_options
                )
                
                # Sinyalleri bağla
                self.worker.progress.connect(self.update_file_progress)
                self.worker.finished.connect(self.handle_file_finished)
                
                # İş parçacığını başlat
                self.worker.start()
            except Exception as e:
                # İş parçacığı oluşturma hatası, sonraki dosyaya geç
                self.error_count += 1
                try:
                    file_name = os.path.basename(current_file)
                except:
                    file_name = f"Dosya {self.current_file_index+1}"
                    
                self.error_label.setText(f"Hata: {file_name} işleme hazırlanamadı - {str(e)}")
                self.error_label.show()
                print(f"Dosya işleme hazırlama hatası: {str(e)}")
                
                self.processed_files += 1
                self.current_file_index += 1
                QTimer.singleShot(100, self.process_next_file)
        else:
            # Tüm dosyalar işlendi
            self.handle_all_files_completed()
    
    def update_file_progress(self, value):
        """Dosya ilerleme durumunu günceller."""
        # Dosya başına ilerleme + toplam ilerleme
        file_weight = 100 / self.total_files
        total_progress = int((self.processed_files * file_weight) + (value * file_weight / 100))
        self.progress.setValue(total_progress)
    
    def handle_file_finished(self, success, message):
        """Bir dosya işlendiğinde çağrılır."""
        try:
            current_file = self.file_queue[self.current_file_index]
            try:
                file_name = os.path.basename(current_file)
            except:
                file_name = f"Dosya {self.current_file_index+1}"
            
            # Başarı/hata sayısını güncelle
            if success:
                self.success_count += 1
            else:
                self.error_count += 1
                error_message = f"Hata: {file_name} işlenemedi - {message}"
                self.error_label.setText(error_message)
                self.error_label.show()
                print(f"Dosya işleme hatası: {message}")
            
            # Dosya işleme sonucunu kaydet
            self.processed_files += 1
            self.current_file_index += 1
            
            # Sonraki dosyayı işle
            QTimer.singleShot(100, self.process_next_file)
        except Exception as e:
            # İşlem tamamlama hatası, güvenli bir şekilde sonraki dosyaya geç
            print(f"Dosya işleme tamamlama hatası: {str(e)}")
            self.processed_files += 1
            self.current_file_index += 1
            self.error_count += 1
            QTimer.singleShot(100, self.process_next_file)
    
    def handle_all_files_completed(self):
        """Tüm dosyalar işlendiğinde çağrılır."""
        self.progress.hide()
        self.split_btn.setEnabled(True)
        
        # Sonuç mesajını göster
        if self.success_count == self.total_files:
            self.info_label.setText(f"Bölme işlemi tamamlandı. {self.success_count} dosya başarıyla işlendi.")
            
            # Başarılı sonuç mesajı
            QMessageBox.information(
                self,
                "İşlem Tamamlandı",
                f"PDF bölme işlemi başarıyla tamamlandı.\n\n"
                f"Toplam {self.success_count} dosya işlendi.\n"
                f"Çıktı dizini: {self.output_dir}"
            )
            
            # Dizini aç seçeneği
            reply = QMessageBox.question(
                self, 
                "Dizini Aç", 
                "Bölünmüş PDF dosyalarının bulunduğu dizini açmak ister misiniz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    from ...utils.file_utils import open_file
                    open_file(self.output_dir)
                except Exception as e:
                    QMessageBox.warning(
                        self, 
                        "Uyarı", 
                        f"Dizin açılamadı: {str(e)}"
                    )
        else:
            self.info_label.setText(f"Bölme işlemi tamamlandı. {self.success_count} başarılı, {self.error_count} başarısız.")
            
            # Uyarı mesajı
            QMessageBox.warning(
                self,
                "İşlem Sonuçları",
                f"PDF bölme işlemi tamamlandı, ancak bazı hatalar oluştu.\n\n"
                f"Başarılı: {self.success_count} dosya\n"
                f"Başarısız: {self.error_count} dosya\n\n"
                f"Lütfen hata mesajlarını kontrol edin."
            )
        
        self.info_label.show()
            
    def show_error(self, message):
        """Hata mesajını gösterir."""
        self.error_label.setText(message)
        self.error_label.show()
        self.info_label.hide()
        
        # Daha ciddi hatalar için mesaj kutusu da göster
        QMessageBox.warning(self, "Hata", message)
    
    def clear(self):
        """Pencereyi temizler."""
        # persistData true ise sadece etiketleri temizle, false ise tam temizlik yap
        if not self.persistData:
            self.file_list.clear()
            self.output_dir = None
            self.output_dir_label.setText("Henüz dizin seçilmedi")
            
            # Adım durumlarını sıfırla
            self.step1_label.setStyleSheet(ACTIVE_STEP_STYLE)
            self.step2_label.setStyleSheet(INACTIVE_STEP_STYLE)
            self.step3_label.setStyleSheet(INACTIVE_STEP_STYLE)
            
            # Seçenekleri sıfırla
            self.mode_combo.setCurrentIndex(0)
            self.update_file_count()
        
        # Her durumda temizlenmesi gereken öğeler
        self.error_label.hide()
        self.info_label.hide()
        self.progress.hide()
        self.split_btn.setEnabled(False)
    
    def showEvent(self, event):
        """Pencere gösterildiğinde çağrılır."""
        super().showEvent(event)
        # Pencere her gösterildiğinde DragDropWidget'a odak ver
        # QTimer.singleShot(200, lambda: self.drag_drop.setFocus()) # Kaldırıldı
        
        # Dosya sayısı durumunu güncelle
        self.update_file_count()

    # def refocus_drag_drop(self):
    #     """DragDropWidget'a yeniden odak verir."""
    #     # Eğer DragDropWidget görünür durumdaysa odak ver
    #     if self.isVisible() and self.drag_drop.isVisible():
    #         self.drag_drop.setFocus(Qt.FocusReason.OtherFocusReason)
    #         print("PDF Split Window: DragDrop set focus")
        
    # def _set_focus_to_drag_drop(self):
    #     """DragDropWidget'a odak verme işlemi."""
    #     if self.isVisible() and self.drag_drop.isVisible():
    #         self.drag_drop.setFocus(Qt.FocusReason.OtherFocusReason)
    #         print("PDF Split Window: DragDrop set focus (delayed)")

    def check_item_state(self, item):
        """Öğe işaretlendiğinde/işaret kaldırıldığında güncelle"""
        # Öğe değişikliklerini sadece dinle, "Tümünü Seç" durumunu güncelle
        self.update_file_count() 