"""
Liste widget bileşenleri.
"""
import os
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QMenu, QScrollBar
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QKeyEvent, QAction, QFont, QCursor

# Marnak Lojistik Kurumsal Renkleri
MARNAK_BLUE = "#0066B3"
MARNAK_GREEN = "#3AB54A"
MARNAK_LIGHT_BLUE = "#E5F1F9"
MARNAK_LIGHT_GREEN = "#E8F5EA"
MARNAK_GRAY = "#F5F5F5"
MARNAK_DARK_GRAY = "#E0E0E0"

class PDFListWidget(QListWidget):
    """PDF dosyaları için liste widget'ı."""
    
    # Sinyaller
    files_changed = pyqtSignal()  # Dosya listesi değiştiğinde
    files_removed = pyqtSignal()  # Dosyalar kaldırıldığında özel sinyal
    pdf_selected = pyqtSignal(str)  # PDF seçildiğinde (dosya yolu)
    
    def __init__(self, parent=None, selectable=False):
        """
        Args:
            parent: Üst widget
            selectable: Öğelerin seçilebilir (checkbox) olup olmadığı
        """
        super().__init__(parent)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.setAcceptDrops(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Seçilebilir mi?
        self.selectable = selectable
        
        # PDF Önizleme sistemi - tıklama ile
        # Hover sistemi kaldırıldı, tıklama sistemi kullanılacak
        
        # Özel kaydırma çubuğu
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Kaydırma çubuğu stilini ayarla
        scrollbar = QScrollBar(Qt.Orientation.Vertical, self)
        scrollbar.setStyleSheet(f"""
            QScrollBar:vertical {{
                border: none;
                background: {MARNAK_GRAY};
                width: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {MARNAK_BLUE};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {MARNAK_GREEN};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        self.setVerticalScrollBar(scrollbar)
        
        # Liste widget stilini ayarla
        self.setStyleSheet(f"""
            QListWidget {{
                border: 2px solid {MARNAK_BLUE};
                border-radius: 8px;
                padding: 10px;
                background-color: white;
                font-size: 13px;
                outline: none;
            }}
            QListWidget::item {{
                border-bottom: 1px solid {MARNAK_LIGHT_BLUE};
                padding: 12px;
                margin: 4px 0;
                border-radius: 6px;
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

    def add_file(self, file_path: str, checked=True):
        """
        Listeye dosya ekler.
        
        Args:
            file_path: Dosya yolu
            checked: İşaretli mi (sadece selectable=True ise geçerli)
        """
        if file_path.lower().endswith('.pdf'):
            # Dosya adını kısalt
            display_name = os.path.basename(file_path)
            if len(display_name) > 30:
                display_name = display_name[:15] + "..." + display_name[-15:]
            
            item = QListWidgetItem("📄 " + display_name)
            item.setData(Qt.ItemDataRole.UserRole, file_path)
            item.setToolTip(file_path)  # Tam dosya yolunu tooltip olarak göster
            
            # Eğer seçilebilir ise, checkbox ekle
            if self.selectable:
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                if checked:
                    item.setCheckState(Qt.CheckState.Checked)
                else:
                    item.setCheckState(Qt.CheckState.Unchecked)
            
            self.addItem(item)
            self.files_changed.emit()
            
    def get_files(self):
        """Liste widget'ındaki tüm dosya yollarını döndürür."""
        return [self.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.count())]
    
    def get_checked_files(self):
        """İşaretlenmiş dosya yollarını döndürür (sadece selectable=True ise geçerli)."""
        if not self.selectable:
            return self.get_files()
        
        checked_files = []
        for i in range(self.count()):
            item = self.item(i)
            if item and item.checkState() == Qt.CheckState.Checked:
                # Güvenli bir şekilde dosya yolunu al
                file_path = item.data(Qt.ItemDataRole.UserRole)
                if file_path:
                    checked_files.append(file_path)
        
        return checked_files
        
    def keyPressEvent(self, event: QKeyEvent):
        """Klavye olaylarını yakala"""
        if event.key() == Qt.Key.Key_Delete:
            self.remove_selected()
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_A:  # Ctrl+A
                self.selectAll()
            elif event.key() == Qt.Key.Key_D:  # Ctrl+D
                self.remove_selected()
                
    def show_context_menu(self, position):
        """Sağ tık menüsünü göster"""
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: white;
                border: 1px solid {MARNAK_BLUE};
                border-radius: 5px;
                padding: 5px;
            }}
            QMenu::item {{
                padding: 8px 20px;
                border-radius: 4px;
                margin: 2px 0;
            }}
            QMenu::item:selected {{
                background-color: {MARNAK_LIGHT_BLUE};
                color: {MARNAK_BLUE};
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {MARNAK_DARK_GRAY};
                margin: 5px 0;
            }}
        """)
        
        # Seçili öğeleri sil
        if self.selectable:
            delete_action = QAction("🗑️ İşaretli Dosyaları Sil", self)
            delete_action.setFont(QFont("Segoe UI", 10))
            delete_action.triggered.connect(self.remove_checked_files)
            menu.addAction(delete_action)
        else:
            delete_action = QAction("🗑️ Seçili Dosyaları Sil", self)
            delete_action.setFont(QFont("Segoe UI", 10))
            delete_action.triggered.connect(self.remove_selected)
            menu.addAction(delete_action)
        
        menu.addSeparator()
        
        # Tümünü seç
        select_all_action = QAction("☑️ Tümünü Seç", self)
        select_all_action.setFont(QFont("Segoe UI", 10))
        select_all_action.triggered.connect(self.selectAll)
        menu.addAction(select_all_action)
        
        if self.selectable:
            menu.addSeparator()
            
            # Tüm öğeleri işaretle
            check_all_action = QAction("✓ Tüm Öğeleri İşaretle", self)
            check_all_action.setFont(QFont("Segoe UI", 10))
            check_all_action.triggered.connect(self.check_all)
            menu.addAction(check_all_action)
            
            # Tüm işaretleri kaldır
            uncheck_all_action = QAction("✗ Tüm İşaretleri Kaldır", self)
            uncheck_all_action.setFont(QFont("Segoe UI", 10))
            uncheck_all_action.triggered.connect(self.uncheck_all)
            menu.addAction(uncheck_all_action)
        
        # Menüyü göster
        menu.exec(self.mapToGlobal(position))
    
    def check_all(self):
        """Tüm öğeleri işaretle"""
        if not self.selectable:
            return
        
        for i in range(self.count()):
            self.item(i).setCheckState(Qt.CheckState.Checked)
        
        # Değişiklik gerçekleşti sinyali
        self.files_changed.emit()
    
    def uncheck_all(self):
        """Tüm işaretleri kaldır"""
        if not self.selectable:
            return
        
        for i in range(self.count()):
            self.item(i).setCheckState(Qt.CheckState.Unchecked)
            
        # Değişiklik gerçekleşti sinyali
        self.files_changed.emit()
        # Dosya kaldırıldı sinyali ile aynı davranışı göster - DragDropWidget'a odak verilmesi için
        self.files_removed.emit()
    
    def remove_selected(self):
        """Seçili dosyaları listeden kaldır"""
        for item in self.selectedItems():
            self.takeItem(self.row(item))
        self.files_changed.emit()
        self.files_removed.emit()
    
    def remove_selected_files(self):
        """Listeden seçili öğeleri kaldırır"""
        self.remove_selected()
        
    def remove_checked_files(self):
        """İşaretli dosyaları listeden kaldırır (sadece selectable=True ise geçerli)"""
        if not self.selectable:
            return
            
        # Sinyalleri geçici olarak kapat
        self.blockSignals(True)
        
        # İşaretli öğeleri bul ve kaldır
        # Sondan başlayarak kaldırmalıyız, aksi halde indeksler kayar
        for i in range(self.count() - 1, -1, -1):
            item = self.item(i)
            if item and item.checkState() == Qt.CheckState.Checked:
                self.takeItem(i)
        
        # Sinyalleri tekrar aç
        self.blockSignals(False)
        
        # Değişiklik sinyallerini yayınla
        self.files_changed.emit()
        self.files_removed.emit()
        
    def dropEvent(self, event):
        """Sürükle-bırak olayını yakala"""
        super().dropEvent(event)
        self.files_changed.emit()

    def clear(self):
        """Listeyi tamamen temizler."""
        # İçeriği temizle
        super().clear()
        
        # Sinyalleri yayınla
        self.files_changed.emit()
        self.files_removed.emit()
        
    def mousePressEvent(self, event):
        """Mouse tıklama - PDF önizleme için."""
        super().mousePressEvent(event)
        
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.position().toPoint())
            if item:
                # PDF dosya yolunu al
                file_path = item.data(Qt.ItemDataRole.UserRole)
                if file_path and os.path.exists(file_path):
                    # PDF önizleme sinyali gönder
                    self.pdf_selected.emit(file_path)
                    print(f"PDF seçildi: {os.path.basename(file_path)}")