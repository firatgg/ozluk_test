import os
import pdfplumber
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import re
from datetime import datetime
from collections import Counter
import scipy.sparse
from PyPDF2 import PdfMerger
from document_types import (
    DOC_TYPE_KEYWORDS, 
    NON_PHOTO_KEYWORDS, 
    PHOTO_KEYWORDS, 
    RARE_CLASSES, 
    DOC_TYPE_DETAILS,
    get_doc_type_from_filename,
    is_photo_document,
    get_detailed_doc_name,
    merge_rare_classes
)
from scipy.sparse import hstack

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

def clean_text(text):
    """Metni temizle ve normalize et"""
    # Küçük harfe çevir
    text = text.lower()
    
    # Sayıları sil
    text = re.sub(r'\d+', '', text)
    
    # Noktalama işaretlerini sil
    text = re.sub(r'[^\w\s]', '', text)
    
    # Fazla boşlukları temizle
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def create_hybrid_features(name_vectorizer, content_vectorizer, filenames, contents, is_training=False):
    """Dosya adı ve içerik özelliklerini birleştir"""
    # Dosya adı ve içerik özelliklerini oluştur
    if is_training:
        filename_features = name_vectorizer.fit_transform(filenames)
        content_features = content_vectorizer.fit_transform(contents)
    else:
        filename_features = name_vectorizer.transform(filenames)
        content_features = content_vectorizer.transform(contents)
    
    # İçerik özelliklerine daha fazla ağırlık ver
    feature_weights = [0.1, 0.9]  # [filename_weight, content_weight]
    
    # Özellikleri ağırlıklandırılmış olarak birleştir
    weighted_filename_features = filename_features * feature_weights[0]
    weighted_content_features = content_features * feature_weights[1]
    
    # Özellikleri yatay olarak birleştir
    X = hstack([weighted_filename_features, weighted_content_features])
    
    return X

def classify_document(file_path, model, name_vectorizer, content_vectorizer, confidence_threshold=0.5):
    """Belgeyi sınıflandır"""
    try:
        # Dosya adını al
        file_name = os.path.basename(file_path)
        
        # PDF'den metin çıkar
        text = extract_text_from_pdf(file_path)
        
        # Metni temizle
        cleaned_text = clean_text(text)
        
        # Özellikleri oluştur
        X = create_hybrid_features(name_vectorizer, content_vectorizer, [file_name], [cleaned_text], is_training=False)
        
        # Sınıflandırma yap
        prediction = model.predict(X)[0]
        confidence = model.predict_proba(X).max()
        
        # Güven skoru eşik değerinin altındaysa "diger" olarak sınıflandır
        if confidence < confidence_threshold:
            prediction = "diger"
            confidence = 0.5  # Varsayılan güven skoru
        
        return prediction, confidence
    except Exception as e:
        print(f"Hata: {file_path} dosyası sınıflandırılamadı - {str(e)}")
        return "diger", 0.5

def process_folder(folder_path, model, name_vectorizer, content_vectorizer, output_folder, user_name):
    """Klasördeki tüm PDF dosyalarını işle"""
    print(f"\nKlasör işleniyor: {folder_path}")
    
    # Dosyaları grupla
    file_groups = {}
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.pdf'):
            # Dosya adını temizle (sayfa numarasını kaldır)
            base_name = re.sub(r'_sayfa_\d+\.pdf$', '.pdf', file_name)
            base_name = re.sub(r'_sayfa_\d+$', '', base_name)
            
            if base_name not in file_groups:
                file_groups[base_name] = []
            
            file_groups[base_name].append(file_name)
    
    # Sonuçları saklamak için liste
    results = []
    
    # Grupları işle
    for base_name, files in file_groups.items():
        files = sorted(files)
        
        # Tüm sayfaların içeriğini birleştir
        combined_text = ""
        for file_name in files:
            file_path = os.path.join(folder_path, file_name)
            text = extract_text_from_pdf(file_path)
            combined_text += text + " "
        
        # Belgeyi sınıflandır
        prediction, confidence = classify_document(
            os.path.join(folder_path, files[0]),  # İlk dosyayı kullan
            model,
            name_vectorizer,
            content_vectorizer
        )
        
        # Sonuçları kaydet
        results.append({
            'file_name': base_name,
            'prediction': prediction,
            'confidence': confidence,
            'page_count': len(files)
        })
        
        # Yeni dosya adını oluştur
        new_name = f"{prediction}_{len(results)}.pdf"
        new_path = os.path.join(output_folder, new_name)
        
        # Dosyaları birleştir ve kaydet
        merge_pdfs([os.path.join(folder_path, f) for f in files], new_path)
        
        print(f"Sınıflandırma: {base_name} -> {prediction} (Güven: {confidence:.2f}, Sayfa: {len(files)})")
    
    # İstatistikleri hesapla
    stats = {}
    for result in results:
        pred = result['prediction']
        if pred not in stats:
            stats[pred] = 0
        stats[pred] += 1
    
    print(f"\n{user_name} için sınıflandırma istatistikleri:")
    for pred, count in stats.items():
        print(f"- {pred}: {count} dosya")
    
    return results

def process_pdf_folder(input_folder, output_folder):
    """PDF klasörünü işle ve sınıflandırma sonuçlarını kaydet"""
    print(f"Belge sınıflandırma başlıyor...")
    print(f"Girdi klasörü: {input_folder}")
    print(f"Çıktı klasörü: {output_folder}")
    
    # Model ve vektörizerları yükle
    model = joblib.load('model.joblib')
    name_vectorizer = joblib.load('name_vectorizer.joblib')
    content_vectorizer = joblib.load('content_vectorizer.joblib')
    
    # Sonuçları saklamak için liste
    results = []
    
    # Sınıflandırma istatistikleri
    classification_stats = {}
    
    # Her kişi klasörü için
    for person_folder in os.listdir(input_folder):
        person_path = os.path.join(input_folder, person_folder)
        if os.path.isdir(person_path):
            print(f"\nKişi klasörü işleniyor: {person_folder}")
            
            # Çıktı klasörünü oluştur
            person_output_path = os.path.join(output_folder, person_folder)
            os.makedirs(person_output_path, exist_ok=True)
            
            # Kişi için istatistikleri sıfırla
            person_stats = Counter()
            other_counter = 1
            
            # PDF dosyalarını işle
            pdf_files = [f for f in os.listdir(person_path) if f.endswith('.pdf')]
            total_files = len(pdf_files)
            print(f"Toplam {total_files} PDF dosyası bulundu.")
            
            for i, pdf_file in enumerate(pdf_files, 1):
                print(f"\nDosya işleniyor ({i}/{total_files}): {pdf_file}")
                
                # PDF'den metin çıkar
                pdf_path = os.path.join(person_path, pdf_file)
                text = extract_text_from_pdf(pdf_path)
                
                # Belgeyi sınıflandır
                doc_type, confidence = classify_document(pdf_path, model, name_vectorizer, content_vectorizer)
                
                # Düşük güvenli sınıflandırmaları "diger" olarak işaretle
                if confidence < 0.5:  # Güven eşiği düşürüldü
                    doc_type = "diger"
                
                # Yeni dosya adını oluştur
                if doc_type == "diger":
                    new_filename = f"diger_{other_counter}.pdf"
                    other_counter += 1
                else:
                    new_filename = f"{doc_type}.pdf"
                
                # Dosyayı kopyala
                new_path = os.path.join(person_output_path, new_filename)
                os.system(f'copy "{pdf_path}" "{new_path}"')
                
                # Sonuçları kaydet
                results.append({
                    'person': person_folder,
                    'original_file': pdf_file,
                    'classified_as': doc_type,
                    'confidence': confidence,
                    'new_filename': new_filename
                })
                
                # İstatistikleri güncelle
                person_stats[doc_type] += 1
                
                print(f"Sınıflandırma: {doc_type} (Güven: {confidence:.2f})")
                print(f"Yeni dosya adı: {new_filename}")
            
            # Kişi istatistiklerini kaydet
            classification_stats[person_folder] = dict(person_stats)
            
            # Kişi istatistiklerini göster
            print(f"\n{person_folder} için sınıflandırma istatistikleri:")
            for doc_type, count in person_stats.items():
                print(f"- {doc_type}: {count} dosya")
    
    # Sonuçları Excel'e kaydet
    results_df = pd.DataFrame(results)
    results_df.to_excel('belge_sonuclari.xlsx', index=False)
    print("\nSınıflandırma sonuçları 'belge_sonuclari.xlsx' dosyasına kaydedildi.")
    
    # Sınıflandırma istatistiklerini Excel'e kaydet
    stats_df = pd.DataFrame(classification_stats).fillna(0)
    stats_df.to_excel('siniflandirma_istatistikleri.xlsx')
    print("Sınıflandırma istatistikleri 'siniflandirma_istatistikleri.xlsx' dosyasına kaydedildi.")
    
    # Genel istatistikleri hesapla ve göster
    total_processed = len(results)
    doc_type_distribution = Counter(r['classified_as'] for r in results)
    
    print("\nGenel Sınıflandırma İstatistikleri:")
    print(f"Toplam işlenen dosya: {total_processed}")
    print("\nBelge tipine göre dağılım:")
    for doc_type, count in doc_type_distribution.items():
        percentage = (count / total_processed) * 100
        print(f"- {doc_type}: {count} dosya ({percentage:.1f}%)")

def merge_pdfs(input_paths, output_path):
    """PDF dosyalarını birleştir"""
    merger = PdfMerger()
    
    try:
        for path in input_paths:
            merger.append(path)
        
        merger.write(output_path)
        merger.close()
        return True
    except Exception as e:
        print(f"Hata: PDF birleştirme başarısız - {str(e)}")
        return False

def main():
    """Ana fonksiyon"""
    input_folder = 'to_classify'
    output_folder = 'classified_documents'
    
    # Çıktı klasörünü oluştur
    os.makedirs(output_folder, exist_ok=True)
    
    # PDF klasörünü işle
    process_pdf_folder(input_folder, output_folder)

if __name__ == "__main__":
    main()