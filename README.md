# 📄 Marnak PDF Araçları

<div align="center">

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║    ███╗   ███╗ █████╗ ██████╗ ███╗   ██╗ █████╗ ██╗  ██╗    ║
║    ████╗ ████║██╔══██╗██╔══██╗████╗  ██║██╔══██╗██║ ██╔╝    ║
║    ██╔████╔██║███████║██████╔╝██╔██╗ ██║███████║█████╔╝     ║
║    ██║╚██╔╝██║██╔══██║██╔══██╗██║╚██╗██║██╔══██║██╔═██╗     ║
║    ██║ ╚═╝ ██║██║  ██║██║  ██║██║ ╚████║██║  ██║██║  ██╗    ║
║    ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝    ║
║                                                               ║
║                    PDF ARAÇLARI v2.0                        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

<img src="marnak_pdf_tools/icons/android-chrome-512x512.png" alt="Marnak PDF Araçları Logo" width="128" height="128">

**Modern ve kullanıcı dostu PDF işlem araçları**  
*PDF dosyalarınızı kolayca yönetin!*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6.1-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Passing-green.svg)](tests/)

</div>

---

## ✨ Özellikler

- **🔄 PDF Birleştirme**: Birden fazla PDF dosyasını tek dosyada birleştirin
- **✂️ PDF Bölme**: PDF dosyalarını sayfa sayfa veya aralıklara göre bölün
- **📝 PDF Yeniden Adlandırma**: Toplu PDF yeniden adlandırma işlemleri
- **📤 Sayfa Çıkarma**: PDF dosyalarından belirli sayfaları çıkarın
- **🖱️ Sürükle-Bırak**: Kolay dosya yönetimi için sürükle-bırak desteği
- **🎨 Modern Arayüz**: PyQt6 tabanlı şık ve kullanıcı dostu arayüz
- **⚡ CLI Desteği**: Komut satırından da kullanabilirsiniz
- **🔧 Hata Yönetimi**: Kapsamlı hata kontrolleri ve kullanıcı bildirimleri

## 🚀 Hızlı Başlangıç

### Gereksinimler

- Python 3.8 veya üzeri
- Windows 10/11, macOS, veya Linux

### Kurulum

```bash
# Repository'yi klonlayın
git clone https://github.com/your-username/ozluk_test.git
cd ozluk_test

# Virtual environment oluşturun ve aktifleştirin
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

### Çalıştırma

```bash
# GUI modunda çalıştır
python -m marnak_pdf_tools

# CLI yardımı
python -m marnak_pdf_tools --help
```

## 📖 Kullanım Örnekleri

### GUI Modu
Uygulamayı başlatın ve sürükle-bırak ile PDF dosyalarınızı işleyin.

### CLI Modu

```bash
# PDF birleştirme
python -m marnak_pdf_tools merge dosya1.pdf dosya2.pdf -o birlestirilmis.pdf

# PDF bölme
python -m marnak_pdf_tools split dosya.pdf -o output_klasoru/

# PDF yeniden adlandırma
python -m marnak_pdf_tools rename *.pdf -o yeni_klasor/ --prefix "yeni_"

# Sayfa çıkarma
python -m marnak_pdf_tools extract dosya.pdf -o cikti.pdf --pages "1-3"
```

## 🏗️ Proje Yapısı

```
📁 proje_kök/
├── 📁 marnak_pdf_tools/     # Ana uygulama modülü
│   ├── 📁 core/             # PDF işlem sınıfları
│   ├── 📁 ui/               # Kullanıcı arayüzü
│   ├── 📁 services/         # İş mantığı katmanı
│   ├── 📁 utils/            # Yardımcı araçlar
│   └── 📁 icons/            # Uygulama ikonları
├── 📁 tests/                # Birim testler
├── 📁 unused_files/         # Temizlenen dosyalar (kategorize)
├── 📁 venv/                 # Virtual environment
├── 📄 requirements.txt      # Python bağımlılıkları
└── 📄 README.md            # Bu dosya
```

## 🧪 Testler

```bash
# Tüm testleri çalıştır
python -m pytest tests/ -v

# Test kapsamı raporu
python -m pytest tests/ --cov=marnak_pdf_tools
```

## 🛠️ Geliştirici Notları

### Mimari
- **Core Layer**: PDF işlem mantığı (`core/`)
- **Service Layer**: İş mantığı ve worker thread'ler (`services/`)
- **UI Layer**: PyQt6 tabanlı kullanıcı arayüzü (`ui/`)

### Kod Standartları
- Tutarlı interface: `(success: bool, message: str, output_files: List[str])`
- Kapsamlı hata yönetimi ve loglama
- Type hints kullanımı
- Türkçe dokümantasyon


## 🗂️ Proje Temizliği

Gereksiz dosyalar `unused_files/` klasöründe kategorize edilmiş şekilde saklanmaktadır:
- `build_files/` - Build ve derlenmiş dosyalar
- `installer_files/` - Installer script'leri
- `temp_files/` - Geçici dosyalar
- `code_files/` - Kullanılmayan kod dosyaları

Detaylı bilgi için `unused_files/TEMIZLEME_RAPORU.md` dosyasına bakınız.

## 🤝 Katkıda Bulunma

1. Fork'layın
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit'leyin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push'layın (`git push origin feature/yeni-ozellik`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakınız.

---

**Son Güncelleme:** 16 Temmuz 2025  
**Geliştirici:** Marnak Yazılım  Fırat Gültekin
**Versiyon:** 2.0.0 (Temizlenmiş) 
