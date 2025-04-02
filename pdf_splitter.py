import os
from PyPDF2 import PdfReader, PdfWriter
import glob

def split_pdf(pdf_path):
    try:
        # PDF dosyasının adını al (uzantısız)
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        # PDF dosyasını oku
        reader = PdfReader(pdf_path)
        
        # PDF adıyla yeni bir klasör oluştur
        output_dir = pdf_name
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Her sayfayı ayrı bir PDF olarak kaydet
        for page_num in range(len(reader.pages)):
            writer = PdfWriter()
            writer.add_page(reader.pages[page_num])
            
            # Çıktı dosya adını oluştur (örn: klasor_adi/sayfa_1.pdf)
            output_path = os.path.join(output_dir, f'sayfa_{page_num + 1}.pdf')
            
            # PDF'i kaydet
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            print(f'{pdf_name} - Sayfa {page_num + 1} kaydedildi: {output_path}')
        
        print(f'✓ {pdf_name} başarıyla işlendi.')
        return True
    except Exception as e:
        print(f'✗ {pdf_name} işlenirken hata oluştu: {str(e)}')
        return False

def process_all_pdfs(directory_path):
    # Belirtilen dizindeki tüm PDF dosyalarını bul
    pdf_files = glob.glob(os.path.join(directory_path, '*.pdf'))
    
    if not pdf_files:
        print(f'"{directory_path}" dizininde PDF dosyası bulunamadı!')
        return
    
    print(f'Toplam {len(pdf_files)} PDF dosyası bulundu.')
    print('İşlem başlıyor...\n')
    
    # Başarılı ve başarısız işlem sayılarını takip et
    successful = 0
    failed = 0
    
    # Her PDF dosyasını işle
    for pdf_file in pdf_files:
        if split_pdf(pdf_file):
            successful += 1
        else:
            failed += 1
    
    print('\nİşlem tamamlandı!')
    print(f'Toplam işlenen: {len(pdf_files)}')
    print(f'Başarılı: {successful}')
    print(f'Başarısız: {failed}')

if __name__ == '__main__':
    # Kullanıcıdan dizin yolunu al
    directory_path = input('PDF dosyalarının bulunduğu dizinin yolunu girin: ')
    
    # Dizin yolunun geçerli olup olmadığını kontrol et
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        process_all_pdfs(directory_path)
    else:
        print('Geçersiz dizin yolu! Lütfen var olan bir dizin yolu girin.') 