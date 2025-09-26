# Marnak PDF Araçları - Windows Setup Oluşturma Rehberi

Bu rehber, Marnak PDF Araçları uygulamasını Windows setup dosyası haline getirmek için gerekli adımları açıklar.

## Gereksinimler

### 1. Python ve Virtual Environment
- Python 3.8 veya üzeri
- Virtual environment desteği

### 2. Inno Setup
- [Inno Setup](https://jrsoftware.org/isinfo.php) indirin ve kurun
- Kurulum sonrası `C:\Program Files (x86)\Inno Setup 6\ISCC.exe` konumunda olmalı

### 3. Gerekli Python Paketleri
- PyQt6
- PyPDF2
- PyMuPDF
- PyInstaller

## Kurulum Adımları

### Otomatik Kurulum (Önerilen)

#### Windows Batch Script ile:
```cmd
build_setup.bat
```

#### PowerShell Script ile:
```powershell
.\build_setup.ps1
```

### Manuel Kurulum

#### 1. Virtual Environment Oluşturma
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

#### 2. Gerekli Paketleri Yükleme
```cmd
pip install -r requirements.txt
```

#### 3. PyInstaller ile Executable Oluşturma
```cmd
pyinstaller marnak_pdf_tools.spec --clean
```

#### 4. Inno Setup ile Installer Oluşturma
```cmd
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
```

## Dosya Yapısı

Kurulum sonrası aşağıdaki dosyalar oluşturulur:

```
dist/
├── MarnakPDFAraclari.exe          # Ana executable dosya
└── MarnakPDFAraclari_Setup.exe    # Windows installer
```

## Kurulum Özellikleri

### Setup Dosyası Özellikleri:
- **Uygulama Adı**: Marnak PDF Araçları
- **Versiyon**: 1.0.0
- **Dil**: Türkçe
- **Mimari**: 64-bit
- **İkon**: favicon.ico
- **Lisans**: LICENSE dosyası dahil

### Kurulum Seçenekleri:
- Masaüstü kısayolu (isteğe bağlı)
- Hızlı başlatma kısayolu (Windows 7 ve öncesi)
- Başlat menüsü kısayolu
- Otomatik başlatma (kurulum sonrası)

### Dosya Konumları:
- **Kurulum Dizini**: `C:\Program Files\Marnak PDF Araçları`
- **Kısayollar**: Masaüstü ve Başlat Menüsü
- **Log Dosyası**: `Documents\MarnakPDFAraclari\app.log`

## Sorun Giderme

### PyInstaller Hataları
- Virtual environment'ın aktif olduğundan emin olun
- Tüm gerekli paketlerin yüklü olduğunu kontrol edin
- `--clean` parametresi ile temiz kurulum yapın

### Inno Setup Hataları
- Inno Setup'ın doğru konumda kurulu olduğunu kontrol edin
- `setup.iss` dosyasının mevcut dizinde olduğundan emin olun
- Yönetici yetkileri ile çalıştırmayı deneyin

### Executable Çalışmıyor
- Windows Defender'ın dosyayı engellemediğini kontrol edin
- Gerekli Visual C++ Redistributable'ların yüklü olduğundan emin olun
- Log dosyasını kontrol edin: `Documents\MarnakPDFAraclari\app.log`

## Geliştirici Notları

### Spec Dosyası Özelleştirme
`marnak_pdf_tools.spec` dosyasını düzenleyerek:
- Ek dosyalar ekleyebilirsiniz
- Gizli import'ları belirtebilirsiniz
- Executable özelliklerini değiştirebilirsiniz

### Inno Setup Özelleştirme
`setup.iss` dosyasını düzenleyerek:
- Kurulum seçeneklerini değiştirebilirsiniz
- Ek dosyalar ekleyebilirsiniz
- Kurulum sürecini özelleştirebilirsiniz

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.
