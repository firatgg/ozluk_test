import os
import re
from PyPDF2 import PdfMerger, PdfReader
from pathlib import Path

def extract_number(filename):
    """
    Dosya adından parantez içindeki sayıyı çıkarır.
    Örnek: 'belirli sureli is sozlesmesi (2)' -> 2
    """
    match = re.search(r'\((\d+)\)', filename)
    if match:
        return int(match.group(1))
    return 0  # Eğer parantez içinde sayı yoksa en başa koy

def get_base_filename(pdf_files):
    """
    Sayı içermeyen PDF dosyasının adını bulur.
    """
    for pdf in pdf_files:
        if not re.search(r'\(\d+\)', pdf.name):
            # .pdf uzantısını kaldır
            return pdf.stem + "_b.pdf"
    return "birlesik.pdf"  # Eğer bulunamazsa varsayılan isim

def merge_pdfs(input_directory, output_filename=None):
    """
    Belirtilen dizindeki tüm PDF dosyalarını dosya isimlerindeki sayılara göre sıralayarak birleştirir.
    
    Args:
        input_directory (str): PDF'lerin bulunduğu dizin
        output_filename (str, optional): Oluşturulacak birleştirilmiş PDF'in adı
    """
    try:
        # PDF'lerin bulunduğu dizini kontrol et
        if not os.path.exists(input_directory):
            print(f"Hata: {input_directory} dizini bulunamadı!")
            return
        
        # PDF dosyalarını bul ve sayılarına göre sırala
        pdf_files = list(Path(input_directory).glob("*.pdf"))
        pdf_files.sort(key=lambda x: extract_number(x.name))
        
        if not pdf_files:
            print(f"Uyarı: {input_directory} dizininde PDF dosyası bulunamadı!")
            return
        
        # Çıktı dosyası adını belirle
        if output_filename is None:
            output_filename = get_base_filename(pdf_files)
        
        print(f"\nToplam {len(pdf_files)} PDF dosyası bulundu.")
        print(f"Çıktı dosyası: {output_filename}")
        print("\nBirleştirme sırası:")
        for i, pdf in enumerate(pdf_files, 1):
            print(f"{i}. {pdf.name}")
        
        # PDF birleştirici oluştur
        merger = PdfMerger()
        
        # Her PDF dosyasını birleştir
        for pdf_path in pdf_files:
            try:
                print(f"\nİşleniyor: {pdf_path.name}")
                
                # PDF'i oku
                reader = PdfReader(pdf_path)
                
                # PDF'i birleştiriciye ekle
                merger.append(reader)
                print(f"Başarıyla eklendi: {pdf_path.name}")
                
            except Exception as e:
                print(f"Hata: {pdf_path.name} dosyası işlenirken bir sorun oluştu: {str(e)}")
        
        # Birleştirilmiş PDF'i kaydet
        output_path = os.path.join(input_directory, output_filename)
        merger.write(output_path)
        merger.close()
        
        print(f"\nBirleştirilmiş PDF kaydedildi: {output_path}")
        
    except Exception as e:
        print(f"Beklenmeyen bir hata oluştu: {str(e)}")

def main():
    # PDF'lerin bulunduğu dizin
    input_directory = "pdf_files"
    
    # PDF'leri birleştir
    merge_pdfs(input_directory)

if __name__ == "__main__":
    main() 