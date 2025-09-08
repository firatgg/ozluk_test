"""
Core modülleri için birim testler.
"""
import os
import tempfile
import shutil
import pytest
from pathlib import Path

from marnak_pdf_tools.core.merger import PdfMerger
from marnak_pdf_tools.core.splitter import PdfSplitter
from marnak_pdf_tools.core.renamer import PdfRenamer
from marnak_pdf_tools.core.extractor import PdfExtractor


class TestPdfMerger:
    """PdfMerger sınıfı testleri."""
    
    def setup_method(self):
        """Her test öncesi çalışır."""
        self.merger = PdfMerger()
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Her test sonrası çalışır."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_merger_creation(self):
        """PdfMerger nesnesi doğru oluşturuluyor mu?"""
        assert self.merger is not None
        assert hasattr(self.merger, 'merge_pdfs')
    
    def test_merge_empty_list(self):
        """Boş dosya listesi ile birleştirme testi."""
        output_path = os.path.join(self.temp_dir, "output.pdf")
        success, message, output_files = self.merger.merge_pdfs([], output_path)
        
        # Boş liste ile success olur ve boş PDF oluşturulur
        assert isinstance(success, bool)
        assert isinstance(message, str)
        assert isinstance(output_files, list)
        # Boş bile olsa merger bir dosya oluşturabilir
    
    def test_merge_nonexistent_files(self):
        """Var olmayan dosyalarla birleştirme testi."""
        files = ["nonexistent1.pdf", "nonexistent2.pdf"]
        output_path = os.path.join(self.temp_dir, "output.pdf")
        
        success, message, output_files = self.merger.merge_pdfs(files, output_path)
        
        assert not success
        assert len(output_files) == 0


class TestPdfSplitter:
    """PdfSplitter sınıfı testleri."""
    
    def setup_method(self):
        """Her test öncesi çalışır."""
        self.splitter = PdfSplitter()
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Her test sonrası çalışır."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_splitter_creation(self):
        """PdfSplitter nesnesi doğru oluşturuluyor mu?"""
        assert self.splitter is not None
        assert hasattr(self.splitter, 'split_pdf')
    
    def test_split_nonexistent_file(self):
        """Var olmayan dosya ile bölme testi."""
        file_path = "nonexistent.pdf"
        
        success, message, output_files = self.splitter.split_pdf(file_path, self.temp_dir)
        
        assert not success
        assert len(output_files) == 0


class TestPdfRenamer:
    """PdfRenamer sınıfı testleri."""
    
    def setup_method(self):
        """Her test öncesi çalışır."""
        self.renamer = PdfRenamer()
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Her test sonrası çalışır."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_renamer_creation(self):
        """PdfRenamer nesnesi doğru oluşturuluyor mu?"""
        assert self.renamer is not None
        assert hasattr(self.renamer, 'rename_pdfs')
    
    def test_rename_empty_list(self):
        """Boş dosya listesi ile yeniden adlandırma testi."""
        options = {"new_name": "test"}
        success, message, output_files = self.renamer.rename_pdfs([], self.temp_dir, options)
        
        # Boş liste ile success olabilir (hiç dosya yok ama başarılı)
        assert isinstance(success, bool)
        assert isinstance(message, str)
        assert len(output_files) == 0
    
    def test_rename_no_new_name(self):
        """Yeni isim belirtilmediğinde hata testi."""
        files = ["nonexistent1.pdf", "nonexistent2.pdf"]
        
        success, message, output_files = self.renamer.rename_pdfs(files, self.temp_dir)
        
        assert not success
        assert "yeni dosya adı" in message.lower()
        assert len(output_files) == 0


class TestPdfExtractor:
    """PdfExtractor sınıfı testleri."""
    
    def setup_method(self):
        """Her test öncesi çalışır."""
        self.extractor = PdfExtractor()
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Her test sonrası çalışır."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_extractor_creation(self):
        """PdfExtractor nesnesi doğru oluşturuluyor mu?"""
        assert self.extractor is not None
        assert hasattr(self.extractor, 'extract_pages')
    
    def test_extract_nonexistent_file(self):
        """Var olmayan dosya ile çıkarma testi."""
        file_path = "nonexistent.pdf"
        
        success, message, output_files = self.extractor.extract_pages(file_path, self.temp_dir)
        
        assert not success
        assert len(output_files) == 0


class TestCoreIntegration:
    """Core modülleri entegrasyon testleri."""
    
    def test_all_classes_have_consistent_interface(self):
        """Tüm core sınıfları tutarlı interface'e sahip mi?"""
        merger = PdfMerger()
        splitter = PdfSplitter()
        renamer = PdfRenamer()
        extractor = PdfExtractor()
        
        # Tüm sınıflar ana metodlarına sahip olmalı
        assert hasattr(merger, 'merge_pdfs')
        assert hasattr(splitter, 'split_pdf')
        assert hasattr(renamer, 'rename_pdfs')
        assert hasattr(extractor, 'extract_pages')
        
        # Return değerleri tutarlı olmalı (success, message, output_files)
        temp_dir = tempfile.mkdtemp()
        try:
            # Test calls with valid parameters
            merger_result = merger.merge_pdfs([], os.path.join(temp_dir, "test.pdf"))
            renamer_result = renamer.rename_pdfs([], temp_dir, {"new_name": "test"})
            
            assert len(merger_result) == 3
            assert len(renamer_result) == 3
            
            # İlk element bool (success)
            assert isinstance(merger_result[0], bool)
            assert isinstance(renamer_result[0], bool)
            
            # İkinci element str (message)
            assert isinstance(merger_result[1], str)
            assert isinstance(renamer_result[1], str)
            
            # Üçüncü element list (output_files)
            assert isinstance(merger_result[2], list)
            assert isinstance(renamer_result[2], list)
            
        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__]) 