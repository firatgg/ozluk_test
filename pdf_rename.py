import os
from pathlib import Path

def rename_pdfs(folder_path, name):
    # Klasör yolunu Path nesnesine çevir
    folder = Path(folder_path)
    
    # Klasördeki tüm PDF dosyalarını bul
    pdf_files = list(folder.glob('*.pdf'))
    
    if not pdf_files:
        print("Belirtilen klasörde PDF dosyası bulunamadı!")
        return
    
    # Sağlık ile ilgili terimler listesi
    health_terms = [
        "odyometri", "psikoteknik","kan", "göz raporu", "akciğer grafisi", "tahlil", "test",
        "röntgen", "ultrason", "mr", "tomografi", "ekg", "ekg", "tansiyon",
        "şeker", "kolesterol", "hormon", "idrar", "dışkı", "mamografi", "pap smear",
        "aşı", "aşı kartı", "muayene", "kontrol", "check-up", "checkup",
        "diyet", "ilaç", "reçete", "randevu", "konsültasyon", "ameliyat", "operasyon",
        "tedavi", "terapi", "psikolog", "psikiyatrist", "diyetisyen", "fizik tedavi",
        "ortopedi", "kardiyoloji", "dermatoloji", "gastroenteroloji", "nöroloji",
        "göz", "kulak", "burun", "boğaz", "diş", "dişçi", "diş hekimi", "ortodonti",
        "çocuk doktoru", "kadın doğum", "jinekoloji", "üroloji", "endokrinoloji",
        "alerji", "astım", "bronşit", "grip", "covid", "korona", "enfeksiyon",
        "bulaşıcı", "virüs", "bakteri", "mikrop", "ateş", "öksürük", "nezle",
        "baş ağrısı", "migren", "bel ağrısı", "sırt ağrısı", "eklem ağrısı",
        "kanser", "tümör", "kist", "polip", "iltihap", "enfeksiyon", "yara",
        "yaralanma", "travma", "kaza", "acil", "ambulans", "hastane", "klinik",
        "laboratuvar", "laboratuvar", "analiz", "sonuç"
    ]
    
    # Her PDF dosyası için işlem yap
    for pdf_file in pdf_files:
        # Dosya adını ve uzantısını ayır
        old_name = pdf_file.stem.lower()  # Küçük harfe çevir
        extension = pdf_file.suffix
        
        # Sağlık terimlerini kontrol et
        is_health_related = any(term in old_name for term in health_terms)
        
        if is_health_related:
            new_name = f"{name} [sağlık] [{pdf_file.stem}]{extension}"
        else:
            new_name = f"{name} [{pdf_file.stem}]{extension}"
            
        new_path = pdf_file.parent / new_name
        
        try:
            # Dosyayı yeniden adlandır
            pdf_file.rename(new_path)
            print(f"Başarıyla yeniden adlandırıldı: {pdf_file.name} -> {new_name}")
        except Exception as e:
            print(f"Hata oluştu ({pdf_file.name}): {str(e)}")

def main():
    print("PDF Dosya Yeniden Adlandırma Aracı")
    print("-" * 30)
    
    # Kullanıcıdan klasör yolunu al
    folder_path = input("PDF dosyalarının bulunduğu klasör yolunu girin: ")
    
    # Klasörün var olup olmadığını kontrol et
    if not os.path.exists(folder_path):
        print("Hata: Belirtilen klasör bulunamadı!")
        return
    
    # Kullanıcıdan isim-soyisim al
    name = input("PDF dosyalarının başına eklenecek isim-soyisimi girin: ")
    
    # İşlemi başlat
    print("\nİşlem başlatılıyor...")
    rename_pdfs(folder_path, name)
    print("\nİşlem tamamlandı!")

if __name__ == "__main__":
    main() 