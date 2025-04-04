import os
import shutil
from PyPDF2 import PdfReader
import traceback

def rename_pdfs(directory_path, output_dir, name):
    """PDF dosyalarını yeniden adlandır"""
    try:
        print(f"PDF yeniden adlandırma işlemi başlıyor...")
        print(f"Kaynak klasör: {directory_path}")
        print(f"Hedef klasör: {output_dir}")
        print(f"Yeni isim: {name}")
        
        # Kaynak klasörün varlığını kontrol et
        if not os.path.exists(directory_path):
            raise Exception(f"Kaynak klasör bulunamadı: {directory_path}")
            
        # Çıktı klasörünün varlığını kontrol et
        if not os.path.exists(output_dir):
            raise Exception(f"Çıktı klasörü bulunamadı: {output_dir}")
        
        # PDF dosyalarını bul
        pdf_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.pdf')]
        if not pdf_files:
            raise Exception(f"'{directory_path}' klasöründe PDF dosyası bulunamadı!")
        
        print(f"Toplam {len(pdf_files)} PDF dosyası bulundu.")
        
        # Her PDF dosyasını işle
        for i, pdf_file in enumerate(pdf_files):
            try:
                # Kaynak dosya yolu
                source_path = os.path.join(directory_path, pdf_file)
                
                # Yeni dosya adını oluştur
                new_name = f"{name}_{i+1}.pdf"
                
                # Hedef dosya yolunu oluştur
                target_path = os.path.join(output_dir, new_name)
                
                # Dosya zaten varsa yeni bir isim oluştur
                counter = 1
                while os.path.exists(target_path):
                    new_name = f"{name}_{i+1}_{counter}.pdf"
                    target_path = os.path.join(output_dir, new_name)
                    counter += 1
                
                # Dosyayı kopyala
                shutil.copy2(source_path, target_path)
                print(f"Dosya kopyalandı: {pdf_file} -> {new_name}")
                
            except Exception as e:
                print(f"Dosya işleme hatası ({pdf_file}): {str(e)}")
                print(f"Hata detayı: {traceback.format_exc()}")
                continue
        
        print("PDF yeniden adlandırma işlemi tamamlandı")
        return True
        
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")
        print(f"Hata detayı: {traceback.format_exc()}")
        return False

def main():
    # Kullanıcıdan dizin yolunu al
    directory_path = input('PDF dosyalarının bulunduğu dizinin yolunu girin: ')
    output_dir = input('Yeniden adlandırılan dosyaların kaydedileceği dizinin yolunu girin: ')
    name = input('Yeni dosya adını girin: ')
    
    # Dizin yollarını kontrol et
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        if os.path.exists(output_dir) and os.path.isdir(output_dir):
            rename_pdfs(directory_path, output_dir, name)
        else:
            print('Geçersiz çıktı dizin yolu! Lütfen var olan bir dizin yolu girin.')
    else:
        print('Geçersiz dizin yolu! Lütfen var olan bir dizin yolu girin.')

if __name__ == '__main__':
    main() 