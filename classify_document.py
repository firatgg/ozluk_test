import os
import pdfplumber
import pandas as pd
import joblib
from pathlib import Path
import re
from datetime import datetime
import shutil

def extract_text_from_pdf(pdf_path):
    """PDF dosyasından metin çıkar"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"Hata: {pdf_path} dosyası okunamadı - {str(e)}")
        return ""

def get_doc_type_from_filename(filename):
    """Dosya adından belge tipini belirle"""
    # Belge tiplerini ve ilgili anahtar kelimeleri tanımla
    doc_type_keywords = {
        "kimlik": ["kimlik", "tc", "t.c.", "nüfus cüzdanı", "tc kimlik", "tckn"],
        "ehliyet": ["ehliyet", "sürücü belgesi", "sürücü"],
        "diploma": ["diploma", "mezuniyet", "okul bitirme", "yüksekokul", "lise"],
        "ikametgah": ["ikametgah", "yerleşim yeri", "ikamet"],
        "saglik_raporu": [
            "sağlık", "sağlık raporu", "kan", "hemogram", "göz", "akciğer", 
            "odyometri", "psikoteknik", "tetanoz", "covid", "test", 
            "muayene", "checkup", "periyodik"
        ],
        "sertifika": [
            "sertifika", "katılım", "başarı", "eğitim", "kurs", 
            "seminer", "talimat", "isg", "iş güvenliği", 
            "yangın", "acil durum", "ilk yardım"
        ],
        "transkript": ["transkript", "not dökümü", "not belgesi"],
        "sgk": ["sgk", "hizmet dökümü", "ssk", "sgk dökümü", "4a", "4b", "emeklilik"],
        "sozlesme": ["sözleşme", "iş sözleşmesi", "kontrat", "anlaşma", "hizmet sözleşmesi"],
        "dilekce": ["dilekçe", "ibraname", "başvuru", "izin talebi"],
        "referans": ["referans", "öneri mektubu", "tavsiye mektubu"],
        "banka": ["banka", "iban", "hesap bilgisi", "banka bilgisi", "dekont"],
        "fotoğraf": ["fotoğraf", "vesikalık", "resim", "profil"],
        "adli_sicil": ["adli sicil", "sabıka", "temiz kağıdı", "sicil belgesi"],
        "ik": ["personel bilgi formu", "özgeçmiş", "cv", "kimlik fotokopisi", "nüfus kayıt örneği", "nüfus"],
        "aile": ["vukuatlı", "nüfus kayıt örneği", "aile bireyleri", "aile belgesi"],
        "askerlik": ["askerlik", "terhis", "askerlik durumu", "askerlik belgesi"],
        "src": ["src", "src2", "src4"],
        "dijital_imza": ["e-imza", "dijital imza", "mobil imza", "nitelikli", "imza belgesi"],
        "fatura": ["fatura", "ödeme", "makbuz"],
        "kıdem": ["kıdem", "kıdem tazminatı", "hizmet süresi", "kıdem belgesi"],
        "kkd": ["kkd", "kişisel koruyucu", "baret", "eldiven", "koruma ekipmanı"],
        "diger": ["belge", "doküman", "dosya", "ek", "evrak"]
    }
    
    # İlk olarak köşeli parantez içindeki tüm metinleri bul
    matches = re.findall(r'\[([^\]]+)\]', filename)
    if not matches:
        return None
    
    # Tüm eşleşmeleri birleştir ve küçük harfe çevir
    doc_type = ' '.join(matches).lower()
    
    # Belge tipini belirle
    for doc_type_name, keywords in doc_type_keywords.items():
        if any(keyword in doc_type for keyword in keywords):
            return doc_type_name
    
    return "diger"

def classify_document(pdf_path, person_name):
    """PDF belgesini sınıflandır"""
    try:
        # Model ve vektörizasyonu yükle
        vectorizer = joblib.load('vectorizer.joblib')
        model = joblib.load('model.joblib')
        
        # PDF'den metin çıkar
        text = extract_text_from_pdf(pdf_path)
        if not text:
            print(f"Uyarı: {pdf_path} dosyasından metin çıkarılamadı")
            return None
        
        # Metni vektörize et
        text_vec = vectorizer.transform([text])
        
        # Tahmin yap
        predicted_type = model.predict(text_vec)[0]
        probabilities = model.predict_proba(text_vec)[0]
        confidence = max(probabilities)
        
        # Sonuçları kaydet
        filename = os.path.basename(pdf_path)
        results = {
            'dosya_adi': filename,
            'tahmin_edilen_tip': predicted_type,
            'güven_skoru': confidence,
            'tarih': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'kişi': person_name
        }
        
        # Sonuçları Excel'e ekle
        try:
            df = pd.read_excel('belge_sonuclari.xlsx')
        except FileNotFoundError:
            df = pd.DataFrame()
        
        df = pd.concat([df, pd.DataFrame([results])], ignore_index=True)
        df.to_excel('belge_sonuclari.xlsx', index=False)
        
        return predicted_type
        
    except Exception as e:
        print(f"Hata: {pdf_path} dosyası sınıflandırılırken hata oluştu - {str(e)}")
        return None

def get_detailed_doc_name(doc_type, text):
    """Belge tipine göre detaylı dosya adı oluştur"""
    details = {
        'adli_sicil': '[adli sicil kaydı]',
        'banka': '[banka hesap IBAN belgesi]',
        'sozlesme': '[belirsiz süreli iş sözleşmesi]',
        'diploma': '[diploma]',
        'ehliyet': '[ehliyet]',
        'fotoğraf': '[fotoğraf]',
        'ikametgah': '[ikametgah]',
        'isg': '[isg eğitim katılım formu]',
        'kimlik': '[kimlik]',
        'nufus': '[nüfus kayıt örneği]',
        'personel': '[personel bilgi formu]',
        'saglik_raporu': {
            'akciğer': '[sağlık] [akciğer grafisi]',
            'kan': '[sağlık] [kan testi]',
            'odyometri': '[sağlık] [odyometri raporu]',
            'psikoteknik': '[sağlık] [psikoteknik]',
            'tetanoz': '[sağlık] [tetanoz aşı kartı]'
        },
        'sgk': '[sgk işe giriş bildirgesi]',
        'src': '[sürücü belgesi ve ceza sorgulama]',
        'tehlikeli': '[tehlikeli mal taşımacılığı sürücü eğitim sertifikası]'
    }
    
    if doc_type in details:
        if isinstance(details[doc_type], dict):
            # Özel durumlar için metin içeriğini kontrol et
            for key, value in details[doc_type].items():
                if key.lower() in text.lower():
                    return value
            return f'[{doc_type}]'  # Eğer özel durum bulunamazsa
        else:
            return details[doc_type]
    return f'[{doc_type}]'

def process_pdf_folder(input_folder, output_folder, person_name):
    """PDF dosyalarını işle ve sınıflandır"""
    try:
        # Çıktı klasörünü oluştur
        os.makedirs(output_folder, exist_ok=True)
        
        # Klasördeki her PDF dosyasını işle
        for filename in os.listdir(input_folder):
            if filename.endswith('.pdf'):
                pdf_path = os.path.join(input_folder, filename)
                
                # PDF'den metin çıkar
                text = extract_text_from_pdf(pdf_path)
                
                # Belgeyi sınıflandır
                doc_type = classify_document(pdf_path, person_name)
                
                if doc_type:
                    # Detaylı belge adı al
                    detailed_type = get_detailed_doc_name(doc_type, text)
                    
                    # Yeni dosya adı oluştur
                    new_filename = f"{person_name} {detailed_type}.pdf"
                    
                    # Dosyayı kopyala
                    target_path = os.path.join(output_folder, new_filename)
                    shutil.copy2(pdf_path, target_path)
                    print(f"Belge kopyalandı: {filename} -> {new_filename}")
                else:
                    print(f"Belge sınıflandırılamadı: {filename}")
                    
    except Exception as e:
        print(f"Hata: Klasör işlenirken hata oluştu - {str(e)}")

if __name__ == "__main__":
    # Klasör yollarını güncelle
    input_folder = "to_classify/ahmet_gezer"  # Sınıflandırılacak PDF'ler
    output_folder = "ahmet_gezer"  # Yeni klasör
    person_name = "Adem Barin"  # Kişi adı
    
    print("Belge sınıflandırma işlemi başlıyor...")
    print(f"Giriş klasörü: {input_folder}")
    print(f"Çıkış klasörü: {output_folder}")
    print(f"Kişi adı: {person_name}")
    
    process_pdf_folder(input_folder, output_folder, person_name)
    print("\nBelge sınıflandırma işlemi tamamlandı!")
    print("Sonuçlar 'belge_sonuclari.xlsx' dosyasına kaydedildi.")