# Marnak PDF İşlem Araçları

Bu proje, PDF dosyalarını toplu olarak yeniden adlandırma, birleştirme ve bölme işlemlerini gerçekleştiren bir masaüstü uygulamasıdır.

## Özellikler

- Toplu PDF yeniden adlandırma
- PDF dosyalarını birleştirme
- PDF dosyalarını sayfa sayfa bölme
- Sürükle-bırak desteği
- Modern ve kullanıcı dostu arayüz

## Kurulum

1. Python 3.8 veya üzeri sürümü yükleyin
2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

## Kullanım

Uygulamayı başlatmak için:
```bash
python pdf_gui.py
```

## Dosya Yapısı

- `pdf_gui.py`: Ana uygulama ve arayüz kodları
- `pdf_rename.py`: PDF yeniden adlandırma işlemleri
- `pdf_merger.py`: PDF birleştirme işlemleri
- `pdf_splitter.py`: PDF bölme işlemleri
- `requirements.txt`: Gerekli Python kütüphaneleri 