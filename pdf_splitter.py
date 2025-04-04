import os
from PyPDF2 import PdfReader, PdfWriter
import traceback

def split_pdf(input_path, output_dir):
    """PDF dosyasını sayfalara böler"""
    try:
        print(f"PDF bölme işlemi başlıyor...")
        print(f"Girdi dosyası: {input_path}")
        print(f"Çıktı klasörü: {output_dir}")
        
        # Girdi dosyasının varlığını kontrol et
        if not os.path.exists(input_path):
            raise Exception(f"Girdi dosyası bulunamadı: {input_path}")
            
        # Çıktı klasörünün varlığını kontrol et
        if not os.path.exists(output_dir):
            raise Exception(f"Çıktı klasörü bulunamadı: {output_dir}")
            
        # PDF dosyasını aç
        reader = PdfReader(input_path)
        num_pages = len(reader.pages)
        print(f"Toplam sayfa sayısı: {num_pages}")
        
        # Her sayfayı ayrı PDF olarak kaydet
        for page_num in range(num_pages):
            writer = PdfWriter()
            writer.add_page(reader.pages[page_num])
            
            # Çıktı dosya adını oluştur
            pdf_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(output_dir, f'{pdf_name}_sayfa_{page_num + 1}.pdf')
            print(f"Sayfa {page_num + 1} kaydediliyor: {output_path}")
            
            # PDF'i kaydet
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
                
            # Dosyanın başarıyla oluşturulduğunu kontrol et
            if not os.path.exists(output_path):
                raise Exception(f"Sayfa {page_num + 1} kaydedilemedi: {output_path}")
                
            print(f"Sayfa {page_num + 1} başarıyla kaydedildi")
        
        print("PDF bölme işlemi tamamlandı")
        return True
        
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")
        print(f"Hata detayı: {traceback.format_exc()}")
        return False

if __name__ == '__main__':
    # Kullanıcıdan dizin yolunu al
    directory_path = input('PDF dosyalarının bulunduğu dizinin yolunu girin: ')
    output_dir = input('Bölünen dosyaların kaydedileceği dizinin yolunu girin: ')
    
    # Dizin yollarının geçerli olup olmadığını kontrol et
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        if os.path.exists(output_dir) and os.path.isdir(output_dir):
            split_pdf(directory_path, output_dir)
        else:
            print('Geçersiz çıktı dizin yolu! Lütfen var olan bir dizin yolu girin.')
    else:
        print('Geçersiz giriş dizin yolu! Lütfen var olan bir dizin yolu girin.') 