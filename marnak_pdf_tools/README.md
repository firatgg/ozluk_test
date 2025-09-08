# 📄 Marnak PDF Araçları

Modern ve kullanıcı dostu PDF işlem araçları - PDF dosyalarınızı kolayca yönetin!

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6.1-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Özellikler

- **🔄 PDF Birleştirme**: Birden fazla PDF dosyasını tek dosyada birleştirin
- **✂️ PDF Bölme**: PDF dosyalarını sayfa sayfa veya aralıklara göre bölün
- **📝 PDF Yeniden Adlandırma**: Toplu PDF yeniden adlandırma işlemleri
- **📤 Sayfa Çıkarma**: PDF dosyalarından belirli sayfaları çıkarın
- **🖱️ Sürükle-Bırak**: Kolay dosya yönetimi için sürükle-bırak desteği
- **🎨 Modern Arayüz**: PyQt6 tabanlı şık ve kullanıcı dostu arayüz
- **⚡ CLI Desteği**: Komut satırından da kullanabilirsiniz
- **🔧 Hata Yönetimi**: Kapsamlı hata kontrolleri ve kullanıcı bildirimleri

## 🚀 Kurulum

### Gereksinimler

- Python 3.8 veya üzeri
- Windows 10/11, macOS, veya Linux

### Adım 1: Projeyi İndirin

```bash
git clone https://github.com/your-username/marnak_pdf_tools.git
cd marnak_pdf_tools
```

### Adım 2: Virtual Environment Oluşturun

```bash
python -m venv venv
```

### Adım 3: Virtual Environment'ı Aktifleştirin

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### Adım 4: Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

## 📖 Kullanım

### GUI Modu (Varsayılan)

Uygulamayı grafik arayüzü ile başlatmak için:

```bash
python -m marnak_pdf_tools
```

veya

```bash
python -m marnak_pdf_tools --gui
```

### CLI Modu

Komut satırından PDF işlemlerini gerçekleştirin:

#### PDF Birleştirme
```bash
python -m marnak_pdf_tools merge dosya1.pdf dosya2.pdf dosya3.pdf -o birlestirilmis.pdf
```

#### PDF Bölme
```bash
# Tüm sayfaları böl
python -m marnak_pdf_tools split dosya.pdf -o output_klasoru/

# Belirli sayfa aralıklarını böl
python -m marnak_pdf_tools split dosya.pdf -o output_klasoru/ --pages "1-5,10,15-20"
```

#### PDF Yeniden Adlandırma
```bash
python -m marnak_pdf_tools rename dosya1.pdf dosya2.pdf -o output_klasoru/ --prefix "yeni_" --suffix "_v2"
```

#### Sayfa Çıkarma
```bash
python -m marnak_pdf_tools extract dosya.pdf -o cikti.pdf --pages "1-3"
```

#### Yardım
```bash
python -m marnak_pdf_tools --help
python -m marnak_pdf_tools merge --help
```

## 🏗️ Proje Yapısı

```
marnak_pdf_tools/
├── __init__.py                 # Paket başlatması
├── __main__.py                 # CLI entry point
├── app.py                      # Ana uygulama
├── core/                       # Temel PDF işlem sınıfları
│   ├── __init__.py
│   ├── merger.py              # PDF birleştirme
│   ├── splitter.py            # PDF bölme
│   ├── renamer.py             # PDF yeniden adlandırma
│   └── extractor.py           # Sayfa çıkarma
├── ui/                        # Kullanıcı arayüzü
│   ├── __init__.py
│   ├── styles.py              # UI stilleri
│   ├── components/            # UI bileşenleri
│   │   ├── __init__.py
│   │   ├── buttons.py
│   │   ├── labels.py
│   │   ├── inputs.py
│   │   ├── drag_drop.py
│   │   └── list_widget.py
│   └── windows/               # Ana pencereler
│       ├── __init__.py
│       ├── main_window.py
│       ├── pdf_merge_window.py
│       ├── pdf_split_window.py
│       ├── pdf_rename_window.py
│       └── pdf_extract_window.py
├── services/                  # İş mantığı katmanı
│   ├── __init__.py
│   └── pdf_service.py
├── icons/                     # Uygulama ikonları
├── requirements.txt           # Python bağımlılıkları
└── README.md                 # Bu dosya
```

## 🧪 Testler

Proje kapsamlı birim testler içerir.

### Testleri Çalıştırma

```bash
# Tüm testleri çalıştır
python -m pytest tests/ -v

# Belirli test dosyasını çalıştır
python -m pytest tests/test_core.py -v

# Test kapsamı raporu
python -m pytest tests/ --cov=marnak_pdf_tools
```

### Test Yapısı

```
tests/
├── __init__.py
└── test_core.py              # Core sınıfları için testler
```

## 📦 Tek .exe Dosyası Oluşturma

Windows için tek çalıştırılabilir dosya oluşturmak için:

```bash
# PyInstaller ile derleme
pyinstaller marnak_pdf_tools.spec

# Oluşturulan dosya
dist/MarakPDFAraclari.exe
```

## 🛠️ Geliştirici Notları

### Mimari

Proje 3 katmanlı mimari kullanır:

1. **Core Layer** (`core/`): PDF işlem mantığı
2. **Service Layer** (`services/`): İş mantığı ve worker thread'ler
3. **UI Layer** (`ui/`): Kullanıcı arayüzü

### Kod Standartları

- Tüm core sınıfları tutarlı interface kullanır: `(success: bool, message: str, output_files: List[str])`
- Kapsamlı hata yönetimi ve loglama
- Type hints kullanımı
- Türkçe dokümantasyon ve hata mesajları

### Katkıda Bulunma

1. Fork'layın
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit'leyin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push'layın (`git push origin feature/yeni-ozellik`)
5. Pull Request oluşturun

### CI/CD

Her commit'te otomatik olarak:
- ✅ Birim testler çalıştırılır
- 🔍 Kod kalitesi kontrol edilir
- 📦 Build işlemi gerçekleştirilir

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🤝 Destek

- 🐛 **Bug Report**: [Issues](https://github.com/your-username/marnak_pdf_tools/issues)
- 💡 **Feature Request**: [Issues](https://github.com/your-username/marnak_pdf_tools/issues)
- 📧 **İletişim**: your-email@example.com

## 📝 Changelog

### v1.0.0
- ✨ İlk sürüm yayınlandı
- 🔄 PDF birleştirme özelliği
- ✂️ PDF bölme özelliği
- 📝 PDF yeniden adlandırma özelliği
- 📤 Sayfa çıkarma özelliği
- 🖥️ GUI ve CLI desteği
- 🧪 Kapsamlı test altyapısı

---

💫 **Marnak PDF Araçları** ile PDF işlemlerinizi kolaylaştırın! 