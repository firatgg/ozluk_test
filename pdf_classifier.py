import os
import pdfplumber
import pandas as pd
from pathlib import Path

def main():
    try:
        # PDF'lerin bulunduğu dizini belirtin
        pdf_directory = "pdf_files"
        
        if not os.path.exists(pdf_directory):
            print(f"Hata: {pdf_directory} dizini bulunamadı!")
            return
        
        # PDF dosyalarını bul
        pdf_files = list(Path(pdf_directory).glob("*.pdf"))
        
        if not pdf_files:
            print(f"Uyarı: {pdf_directory} dizininde PDF dosyası bulunamadı!")
            return
        
        print(f"\nToplam {len(pdf_files)} PDF dosyası bulundu.")
        
        # Sonuçları tutacak liste
        results = []
        
        # Her PDF dosyasını işle
        for pdf_path in pdf_files:
            print(f"\nİşleniyor: {pdf_path.name}")
            
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    total_pages = len(pdf.pages)
                    print(f"Toplam sayfa sayısı: {total_pages}")
                    
                    for page_num, page in enumerate(pdf.pages, 1):
                        print(f"Sayfa {page_num}/{total_pages} işleniyor...")
                        
                        try:
                            # Metni çıkar
                            text = page.extract_text()
                            
                            # Belge tipini belirle
                            doc_type = "Diğer"
                            text_lower = text.lower()
                            
                            if "kimlik" in text_lower or "t.c." in text_lower:
                                doc_type = "Kimlik Kartı"
                            elif "sürücü" in text_lower or "ehliyet" in text_lower:
                                doc_type = "Sürücü Belgesi"
                            elif "diploma" in text_lower:
                                doc_type = "Diploma"
                            elif "ikametgah" in text_lower:
                                doc_type = "İkametgah"
                            elif "sağlık" in text_lower:
                                doc_type = "Sağlık Raporu"
                            elif "sertifika" in text_lower:
                                doc_type = "Sertifika"
                            elif "transkript" in text_lower:
                                doc_type = "Transkript"
                            elif "sgk" in text_lower:
                                doc_type = "SGK"
                            elif "sözleşme" in text_lower:
                                doc_type = "Sözleşme"
                            elif "dilekçe" in text_lower:
                                doc_type = "Dilekçe"
                            elif "referans" in text_lower:
                                doc_type = "Referans Mektubu"
                            elif "banka" in text_lower:
                                doc_type = "Banka Belgesi"
                            
                            # Sonucu kaydet
                            results.append({
                                'Dosya Adı': pdf_path.name,
                                'Sayfa Numarası': page_num,
                                'Belge Tipi': doc_type
                            })
                            
                            print(f"Sayfa {page_num}: {doc_type} olarak sınıflandırıldı.")
                            
                        except Exception as e:
                            print(f"Sayfa {page_num} işlenirken hata oluştu: {str(e)}")
                            results.append({
                                'Dosya Adı': pdf_path.name,
                                'Sayfa Numarası': page_num,
                                'Belge Tipi': "Hata"
                            })
            
            except Exception as e:
                print(f"PDF dosyası işlenirken hata oluştu: {str(e)}")
        
        # Sonuçları kaydet
        if results:
            df = pd.DataFrame(results)
            output_file = os.path.join(pdf_directory, "belge_siniflandirma_sonuclari.xlsx")
            df.to_excel(output_file, index=False)
            print(f"\nSonuçlar kaydedildi: {output_file}")
        else:
            print("\nHiç sonuç üretilemedi!")
            
    except Exception as e:
        print(f"Beklenmeyen bir hata oluştu: {str(e)}")

if __name__ == "__main__":
    main() 