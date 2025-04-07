# Marnak Belge Sınıflandırma Sistemi

Bu proje, makine öğrenmesi kullanarak PDF belgelerini otomatik olarak sınıflandıran bir sistemdir.

## Özellikler

- PDF belgelerini otomatik sınıflandırma
- Belge içeriği ve ismine göre sınıflandırma
- Model eğitimi ve değerlendirme
- Detaylı sınıflandırma raporları
- Excel formatında sonuç raporları

## Kurulum

1. Python 3.8 veya üzeri sürümü yükleyin
2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

## Kullanım

### Model Eğitimi
```bash
python train_model.py
```

### Belge Sınıflandırma
```bash
python classify_document.py
```

## Dosya Yapısı

- `train_model.py`: Model eğitim kodları
- `classify_document.py`: Belge sınıflandırma kodları
- `document_types.py`: Belge türleri ve yapılandırma
- `model.joblib`: Eğitilmiş model
- `content_vectorizer.joblib`: İçerik vektörleştirici
- `name_vectorizer.joblib`: İsim vektörleştirici
- `requirements.txt`: Gerekli Python kütüphaneleri

## Klasörler

- `training_data/`: Eğitim verileri
- `to_classify/`: Sınıflandırılacak belgeler
- `classified_documents/`: Sınıflandırılmış belgeler 