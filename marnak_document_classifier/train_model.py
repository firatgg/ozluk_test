import os
import pdfplumber
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score, precision_score, recall_score
import joblib
import re
from datetime import datetime
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.sparse
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

def prepare_training_data(training_folder):
    """Eğitim verilerini hazırla"""
    print("Eğitim verileri hazırlanıyor...")
    
    data = []
    for person_folder in os.listdir(training_folder):
        person_path = os.path.join(training_folder, person_folder)
        if os.path.isdir(person_path):
            print(f"Kişi klasörü işleniyor: {person_folder}")
            
            # Dosyaları grupla
            file_groups = {}
            for file_name in os.listdir(person_path):
                if file_name.endswith('.pdf'):
                    # Dosya adından belge tipini belirle
                    doc_type = get_doc_type_from_filename(file_name)
                    
                    # Dosya adını temizle (sayfa numarasını kaldır)
                    base_name = re.sub(r'_sayfa_\d+\.pdf$', '.pdf', file_name)
                    base_name = re.sub(r'_sayfa_\d+$', '', base_name)
                    
                    if base_name not in file_groups:
                        file_groups[base_name] = {'type': doc_type, 'files': []}
                    
                    file_groups[base_name]['files'].append(file_name)
            
            # Grupları işle
            for base_name, group_info in file_groups.items():
                doc_type = group_info['type']
                files = sorted(group_info['files'])
                
                # Tüm sayfaların içeriğini birleştir
                combined_text = ""
                for file_name in files:
                    file_path = os.path.join(person_path, file_name)
                    text = extract_text_from_pdf(file_path)
                    combined_text += text + " "
                
                # Veri setine ekle
                data.append({
                    'file_name': base_name,
                    'text': combined_text,
                    'label': doc_type,
                    'page_count': len(files)
                })
    
    # DataFrame oluştur
    df = pd.DataFrame(data)
    
    # Sınıf dağılımını göster
    label_counts = df['label'].value_counts()
    print("\nSınıf dağılımı:")
    for label, count in label_counts.items():
        print(f"- {label}: {count} dosya")
    
    # Sayfa sayısı dağılımını göster
    page_counts = df['page_count'].value_counts().sort_index()
    print("\nSayfa sayısı dağılımı:")
    for pages, count in page_counts.items():
        print(f"- {pages} sayfa: {count} belge")
    
    # CSV olarak kaydet
    df.to_csv('train_dataset.csv', index=False)
    print("\nEğitim verisi 'train_dataset.csv' dosyasına kaydedildi.")
    
    return df

def create_hybrid_features(filename_vectorizer, content_vectorizer, filenames, contents, is_training=True):
    # Dosya adı ve içerik özelliklerini oluştur
    if is_training:
        filename_features = filename_vectorizer.fit_transform(filenames)
        content_features = content_vectorizer.fit_transform(contents)
    else:
        filename_features = filename_vectorizer.transform(filenames)
        content_features = content_vectorizer.transform(contents)
    
    # İçerik özelliklerine daha fazla ağırlık ver (0.2 yerine 0.1)
    feature_weights = [0.1, 0.9]  # [filename_weight, content_weight]
    
    # Özellikleri ağırlıklandırılmış olarak birleştir
    weighted_filename_features = filename_features * feature_weights[0]
    weighted_content_features = content_features * feature_weights[1]
    
    # Özellikleri yatay olarak birleştir
    combined_features = scipy.sparse.hstack([weighted_filename_features, weighted_content_features])
    
    return combined_features

def train_model(X, y, name_vectorizer, content_vectorizer):
    """Modeli eğit ve değerlendir"""
    print("Model eğitiliyor...")
    
    # Az örnekli sınıfları birleştir
    rare_classes = ['askerlik', 'ik', 'transkript', 'kıdem', 'aile', 'fatura', 'kkd', 'dilekce', 'sgk', 'banka', 'fotoğraf']
    y_processed = y.copy()
    for rare_class in rare_classes:
        if rare_class in y_processed:
            y_processed = y_processed.replace(rare_class, 'diger')
    
    # Veriyi eğitim ve test setlerine ayır
    X_train, X_test, y_train, y_test = train_test_split(X, y_processed, test_size=0.2, random_state=42)
    
    # Veri dengesizliğini kontrol et
    print("\nEğitim seti sınıf dağılımı:")
    train_counts = Counter(y_train)
    for label, count in train_counts.items():
        print(f"- {label}: {count} örnek")
    
    # Veri dengesizliğini düzelt
    from imblearn.over_sampling import SMOTE
    from imblearn.under_sampling import RandomUnderSampler
    from imblearn.pipeline import Pipeline
    
    try:
        # SMOTE ve RandomUnderSampler'ı birlikte kullan
        over = SMOTE(sampling_strategy='auto', random_state=42, k_neighbors=2)
        under = RandomUnderSampler(sampling_strategy='auto', random_state=42)
        steps = [('over', over), ('under', under)]
        pipeline = Pipeline(steps=steps)
        
        # Dengeleme işlemini uygula
        X_train_balanced, y_train_balanced = pipeline.fit_resample(X_train, y_train)
        
        print("\nDengelenmiş eğitim seti sınıf dağılımı:")
        balanced_counts = Counter(y_train_balanced)
        for label, count in balanced_counts.items():
            print(f"- {label}: {count} örnek")
    except ValueError as e:
        print("\nUyarı: SMOTE ve RandomUnderSampler uygulanamadı, class_weight parametresi kullanılacak")
        print(f"Hata: {str(e)}")
        X_train_balanced, y_train_balanced = X_train, y_train
    
    # Model parametreleri
    param_grid = {
        'alpha': [0.0001, 0.001, 0.01],
        'eta0': [0.01, 0.1],
        'l1_ratio': [0.15, 0.3],
        'learning_rate': ['optimal', 'constant'],
        'loss': ['log_loss', 'modified_huber'],
        'max_iter': [3000],
        'penalty': ['elasticnet'],
        'class_weight': ['balanced']
    }
    
    # Model
    model = SGDClassifier(random_state=42)
    
    # GridSearchCV
    grid_search = GridSearchCV(
        estimator=model,
        param_grid=param_grid,
        cv=5,
        scoring='f1_weighted',
        n_jobs=-1,
        verbose=1
    )
    
    # Modeli eğit
    grid_search.fit(X_train_balanced, y_train_balanced)
    
    # En iyi parametreleri göster
    print("\nEn iyi parametreler:")
    for param, value in grid_search.best_params_.items():
        print(f"- {param}: {value}")
    
    # En iyi skoru göster
    print(f"\nEn iyi skor: {grid_search.best_score_:.4f}")
    
    # En iyi modeli al
    best_model = grid_search.best_estimator_
    
    # Test seti üzerinde değerlendir
    y_pred = best_model.predict(X_test)
    
    # Performans metriklerini hesapla
    accuracy = accuracy_score(y_test, y_pred)
    weighted_f1 = f1_score(y_test, y_pred, average='weighted')
    macro_f1 = f1_score(y_test, y_pred, average='macro')
    micro_f1 = f1_score(y_test, y_pred, average='micro')
    weighted_precision = precision_score(y_test, y_pred, average='weighted')
    weighted_recall = recall_score(y_test, y_pred, average='weighted')
    
    # Performans metriklerini göster
    print("\nModel Performans Metrikleri:")
    print(f"- Accuracy: {accuracy:.4f}")
    print(f"- Weighted F1: {weighted_f1:.4f}")
    print(f"- Macro F1: {macro_f1:.4f}")
    print(f"- Micro F1: {micro_f1:.4f}")
    print(f"- Weighted Precision: {weighted_precision:.4f}")
    print(f"- Weighted Recall: {weighted_recall:.4f}")
    
    # Sınıf bazlı performans metriklerini göster
    print("\nSınıf Bazlı Performans Metrikleri:")
    print(classification_report(y_test, y_pred))
    
    # Karmaşıklık matrisini göster
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Karmaşıklık Matrisi')
    plt.xlabel('Tahmin Edilen')
    plt.ylabel('Gerçek')
    plt.tight_layout()
    plt.savefig('confusion_matrix.png')
    print("\nKarmaşıklık matrisi 'confusion_matrix.png' dosyasına kaydedildi.")
    
    # Model ve vektörizerları kaydet
    joblib.dump(best_model, 'model.joblib')
    joblib.dump(name_vectorizer, 'name_vectorizer.joblib')
    joblib.dump(content_vectorizer, 'content_vectorizer.joblib')
    print("\nModel ve vektörizerlar kaydedildi.")
    
    # Değerlendirme sonuçlarını Excel'e kaydet
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_file = f'model_evaluation_{timestamp}.xlsx'
    
    # Performans metriklerini DataFrame'e dönüştür
    metrics_df = pd.DataFrame({
        'Metric': ['Accuracy', 'Weighted F1', 'Macro F1', 'Micro F1', 'Weighted Precision', 'Weighted Recall'],
        'Value': [accuracy, weighted_f1, macro_f1, micro_f1, weighted_precision, weighted_recall]
    })
    
    # Sınıf bazlı performans metriklerini DataFrame'e dönüştür
    class_report = classification_report(y_test, y_pred, output_dict=True)
    class_report_df = pd.DataFrame(class_report).transpose()
    
    # Excel'e kaydet
    with pd.ExcelWriter(excel_file) as writer:
        metrics_df.to_excel(writer, sheet_name='Detailed Metrics', index=False)
        class_report_df.to_excel(writer, sheet_name='Classification Report')
    
    print(f"\nDeğerlendirme sonuçları '{excel_file}' dosyasına kaydedildi.")
    
    return best_model, name_vectorizer, content_vectorizer

def analyze_filename_content_correlation(df):
    """Dosya adı ve içerik arasındaki korelasyonu analiz et"""
    print("\nDosya adı ve içerik korelasyonu analiz ediliyor...")
    
    # Dosya adından belge tipini belirle
    df['filename_doc_type'] = df['file_name'].apply(get_doc_type_from_filename)
    
    # Dosya adı ve içerik etiketleri arasındaki uyumu hesapla
    match_count = sum(df['filename_doc_type'] == df['label'])
    total_count = len(df)
    match_percentage = (match_count / total_count) * 100
    
    print(f"Dosya adı ve içerik etiketleri arasında uyum: {match_count}/{total_count} ({match_percentage:.2f}%)")
    
    # Uyumsuz örnekleri göster
    mismatches = df[df['filename_doc_type'] != df['label']]
    print(f"\nUyumsuz örnek sayısı: {len(mismatches)}")
    
    if len(mismatches) > 0:
        print("\nİlk 10 uyumsuz örnek:")
        for _, row in mismatches.head(10).iterrows():
            print(f"- Dosya: {row['file_name']}, Dosya Adı Etiketi: {row['filename_doc_type']}, İçerik Etiketi: {row['label']}")
    
    return match_percentage

def main():
    """Ana fonksiyon"""
    # Eğitim verilerini hazırla
    df = prepare_training_data('training_data')
    
    # Dosya adı ve içerik korelasyonunu analiz et
    match_percentage = analyze_filename_content_correlation(df)
    
    # Vektörizerları oluştur
    name_vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 4),
        analyzer='char',
        min_df=2,
        max_df=0.95
    )
    
    content_vectorizer = TfidfVectorizer(
        max_features=50000,
        ngram_range=(1, 5),
        analyzer='char',
        min_df=2,
        max_df=0.95
    )
    
    # Özellikleri oluştur
    X = create_hybrid_features(name_vectorizer, content_vectorizer, df['file_name'], df['text'], is_training=True)
    y = df['label']
    
    # Modeli eğit
    model, name_vectorizer, content_vectorizer = train_model(X, y, name_vectorizer, content_vectorizer)
    
    print("\nModel eğitimi tamamlandı.")

if __name__ == "__main__":
    main() 