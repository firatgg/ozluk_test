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
    
    def test_merge_real_pdfs(self):
        """Gerçek PDF dosyaları ile birleştirme testi."""
        # Test varlıklarından dosyaları al
        sample_1_page = os.path.join("tests", "assets", "sample_1_page.pdf")
        sample_3_pages = os.path.join("tests", "assets", "sample_3_pages.pdf")
        
        # Dosyaların varlığını kontrol et
        if not os.path.exists(sample_1_page) or not os.path.exists(sample_3_pages):
            pytest.skip("Test PDF dosyaları bulunamadı")
        
        output_path = os.path.join(self.temp_dir, "merged_output.pdf")
        files = [sample_1_page, sample_3_pages]
        
        success, message, output_files = self.merger.merge_pdfs(files, output_path)
        
        assert success, f"Birleştirme başarısız: {message}"
        assert len(output_files) == 1
        assert os.path.exists(output_files[0])
        
        # Birleştirilmiş PDF'in 4 sayfa olduğunu kontrol et (1 + 3)
        import fitz
        merged_doc = fitz.open(output_files[0])
        assert len(merged_doc) == 4, f"Beklenen 4 sayfa, bulunan: {len(merged_doc)}"
        merged_doc.close()


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
    
    def test_split_all_pages(self):
        """3 sayfalık PDF'i tüm sayfaları böl moduyla bölme testi."""
        sample_3_pages = os.path.join("tests", "assets", "sample_3_pages.pdf")
        
        if not os.path.exists(sample_3_pages):
            pytest.skip("Test PDF dosyası bulunamadı")
        
        options = {"mode": self.splitter.SPLIT_MODE_ALL_PAGES}
        success, message, output_files = self.splitter.split_pdf(sample_3_pages, self.temp_dir, options)
        
        assert success, f"Bölme başarısız: {message}"
        assert len(output_files) == 3, f"Beklenen 3 dosya, bulunan: {len(output_files)}"
        
        # Tüm çıktı dosyalarının varlığını kontrol et
        for output_file in output_files:
            assert os.path.exists(output_file), f"Çıktı dosyası bulunamadı: {output_file}"


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
    
    def test_rename_real_pdf(self):
        """Gerçek PDF dosyası ile yeniden adlandırma testi."""
        sample_1_page = os.path.join("tests", "assets", "sample_1_page.pdf")
        
        if not os.path.exists(sample_1_page):
            pytest.skip("Test PDF dosyası bulunamadı")
        
        options = {"new_name": "yeni_isim"}
        success, message, output_files = self.renamer.rename_pdfs([sample_1_page], self.temp_dir, options)
        
        assert success, f"Yeniden adlandırma başarısız: {message}"
        assert len(output_files) == 1
        assert os.path.exists(output_files[0])
        
        # Dosya adının doğru olduğunu kontrol et
        expected_filename = "yeni_isim_1.pdf"
        actual_filename = os.path.basename(output_files[0])
        assert actual_filename == expected_filename, f"Beklenen: {expected_filename}, Bulunan: {actual_filename}"


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
    
    def test_extract_specific_pages(self):
        """3 sayfalık PDF'den belirli sayfaları çıkarma testi."""
        sample_3_pages = os.path.join("tests", "assets", "sample_3_pages.pdf")
        
        if not os.path.exists(sample_3_pages):
            pytest.skip("Test PDF dosyası bulunamadı")
        
        options = {
            "extract_all": False,
            "page_range": "1,3",
            "file_prefix": "test_"
        }
        
        success, message, output_files = self.extractor.extract_pages(sample_3_pages, self.temp_dir, options)
        
        assert success, f"Sayfa çıkarma başarısız: {message}"
        assert len(output_files) == 2, f"Beklenen 2 dosya, bulunan: {len(output_files)}"
        
        # Tüm çıktı dosyalarının varlığını kontrol et
        for output_file in output_files:
            assert os.path.exists(output_file), f"Çıktı dosyası bulunamadı: {output_file}"


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