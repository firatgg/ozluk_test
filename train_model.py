import os
import pdfplumber
from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, HashingVectorizer
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, StackingClassifier
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.metrics import classification_report, accuracy_score, f1_score, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.decomposition import TruncatedSVD
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
import joblib
import re
import numpy as np
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import lightgbm as lgb

def extract_text_from_pdf(pdf_path):
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

def prepare_training_data():
    """Eğitim verisini hazırla"""
    print("Eğitim verisi hazırlanıyor...")
    
    data = []
    training_dir = "training_data"
    
    # Tüm kişi klasörlerini işle
    for person_dir in os.listdir(training_dir):
        person_path = os.path.join(training_dir, person_dir)
        if not os.path.isdir(person_path):
            continue
            
        print(f"\n{person_dir} klasörü işleniyor...")
        pdf_files = [f for f in os.listdir(person_path) if f.endswith('.pdf')]
        print(f"{len(pdf_files)} PDF dosyası bulundu.")
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(person_path, pdf_file)
            try:
                text = extract_text_from_pdf(pdf_path)
                if text:
                    doc_type = get_doc_type_from_filename(pdf_file)
                    if doc_type:
                        data.append({
                            'text': text,
                            'doc_type': doc_type
                        })
                        print(f"Eklendi: {pdf_file} -> {doc_type}")
                    else:
                        print(f"Uyarı: {pdf_file} için belge tipi belirlenemedi")
                else:
                    print(f"Uyarı: {pdf_file} dosyasından metin çıkarılamadı, atlanıyor...")
            except Exception as e:
                print(f"Hata: {pdf_file} dosyası işlenirken hata oluştu: {str(e)}")
    
    if not data:
        raise ValueError("Hiç eğitim verisi bulunamadı!")
        
    df = pd.DataFrame(data)
    
    # Az örnekli sınıfları 'diger' kategorisine taşı
    class_counts = df['doc_type'].value_counts()
    rare_classes = class_counts[class_counts < 2].index.tolist()
    if rare_classes:
        print(f"\nAz örnekli sınıflar 'diger' kategorisine taşınıyor: {rare_classes}")
        df.loc[df['doc_type'].isin(rare_classes), 'doc_type'] = 'diger'
    
    print(f"\nToplam {len(df)} belge toplandı.")
    print("\nBelge tiplerinin dağılımı:")
    print(df['doc_type'].value_counts())
    
    return df

def evaluate_model(y_true, y_pred, model_name):
    """Model performansını detaylı değerlendir"""
    print(f"\n{model_name} Model Değerlendirmesi:")
    print("-" * 50)
    print(f"Accuracy: {accuracy_score(y_true, y_pred):.4f}")
    print(f"F1 Score (macro): {f1_score(y_true, y_pred, average='macro'):.4f}")
    print("\nSınıf Bazlı Sonuçlar:")
    print(classification_report(y_true, y_pred))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_true, y_pred))

def train_model():
    # Eğitim verilerini hazırla
    df = prepare_training_data()
    
    # Veri setini eğitim ve test olarak böl
    X = df['text']
    y = df['doc_type']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.2, 
        random_state=42,
        stratify=y
    )
    
    # Türkçe stop words
    turkish_stop_words = [
        'acaba', 'ama', 'aslında', 'az', 'bazı', 'belki', 'biri', 'birkaç', 'birşey',
        'biz', 'bu', 'çok', 'çünkü', 'da', 'daha', 'de', 'defa', 'diye', 'eğer', 'en',
        'gibi', 'hem', 'hep', 'hepsi', 'her', 'hiç', 'için', 'ile', 'ise', 'kez', 'ki',
        'kim', 'mı', 'mu', 'mü', 'nasıl', 'ne', 'neden', 'nerde', 'nerede', 'nereye',
        'niçin', 'niye', 'o', 'sanki', 'şey', 'siz', 'şu', 'tüm', 've', 'veya', 'ya',
        'yani'
    ]
    
    # Vektörizasyon parametreleri
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=3000,
        min_df=2,
        max_df=0.95,
        stop_words=turkish_stop_words
    )
    
    # Metinleri vektörize et
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # Veri dengesizliğini gider
    print("\nVeri dengesizliği gideriliyor...")
    smote = SMOTE(random_state=42, k_neighbors=2)
    under = RandomUnderSampler(random_state=42)
    
    try:
        X_train_balanced, y_train_balanced = smote.fit_resample(X_train_vec, y_train)
        X_train_balanced, y_train_balanced = under.fit_resample(X_train_balanced, y_train_balanced)
        print("Veri dengeleme başarılı!")
    except Exception as e:
        print(f"Veri dengeleme hatası: {str(e)}")
        print("Orijinal veri seti kullanılıyor...")
        X_train_balanced, y_train_balanced = X_train_vec, y_train
    
    # SGDClassifier için GridSearchCV
    print("\nSGDClassifier için hiperparametre optimizasyonu yapılıyor...")
    param_grid = {
        'loss': ['hinge', 'log_loss'],
        'penalty': ['l2', 'elasticnet'],
        'alpha': [1e-4, 1e-3, 1e-2],
        'class_weight': ['balanced', None]
    }
    
    sgd = SGDClassifier(max_iter=1000, random_state=42)
    grid_search = GridSearchCV(
        sgd,
        param_grid,
        cv=StratifiedKFold(n_splits=5),
        scoring='f1_weighted',
        n_jobs=-1
    )
    grid_search.fit(X_train_balanced, y_train_balanced)
    
    print("\nEn iyi parametreler:", grid_search.best_params_)
    print("En iyi skor:", grid_search.best_score_)
    
    # En iyi SGDClassifier modelini al
    best_sgd = grid_search.best_estimator_
    
    # Diğer modeller
    models = {
        'SGDClassifier (Optimized)': best_sgd,
        'MultinomialNB': MultinomialNB(),
        'LogisticRegression': LogisticRegression(max_iter=1000, class_weight='balanced'),
        'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'),
        'SVC': SVC(kernel='linear', probability=True, class_weight='balanced')
    }
    
    # Her modeli eğit ve değerlendir
    best_model = None
    best_score = 0
    
    for name, model in models.items():
        print(f"\n{name} modeli eğitiliyor...")
        
        try:
            # Modeli eğit
            model.fit(X_train_balanced, y_train_balanced)
            
            # Tahminler yap
            y_pred = model.predict(X_test_vec)
            
            # Modeli değerlendir
            evaluate_model(y_test, y_pred, name)
            
            # En iyi modeli kaydet (weighted F1 score kullan)
            current_score = f1_score(y_test, y_pred, average='weighted')
            if current_score > best_score:
                best_score = current_score
                best_model = model
                
        except Exception as e:
            print(f"Hata: {name} modeli eğitilemedi - {str(e)}")
    
    # En iyi modeli kaydet
    print(f"\nEn iyi model: {best_model.__class__.__name__} (Weighted F1 Score: {best_score:.4f})")
    
    # Vektörizasyonu ve en iyi modeli kaydet
    joblib.dump(vectorizer, 'vectorizer.joblib')
    joblib.dump(best_model, 'model.joblib')
    
    # Özellik önemini analiz et
    if hasattr(best_model, 'feature_importances_'):
        feature_importance = pd.DataFrame({
            'feature': vectorizer.get_feature_names_out(),
            'importance': best_model.feature_importances_
        })
        feature_importance = feature_importance.sort_values('importance', ascending=False)
        print("\nEn önemli 20 özellik:")
        print(feature_importance.head(20))
    
    # Veri seti dengesi analizi
    print("\nVeri seti dengesi:")
    print(y.value_counts())
    
    # Öneriler
    print("\nÖneriler:")
    print("1. Her sınıf için örnek sayısını 10-15'e çıkarın")
    print("2. BERT veya Sentence Transformers gibi embedding modellerini deneyin")
    print("3. Veri çoğaltma tekniklerini geliştirin")
    print("4. Daha fazla veri toplayın")
    print("5. Model performansını düzenli olarak değerlendirin")

if __name__ == "__main__":
    train_model() 