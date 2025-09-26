# Marnak PDF Araçları - Windows Setup Oluşturucu (PowerShell)
Write-Host "Marnak PDF Araçları - Windows Setup Oluşturucu" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

Write-Host ""
Write-Host "1. Virtual environment aktifleştiriliyor..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "2. Gerekli paketler yükleniyor..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "3. PyInstaller ile executable oluşturuluyor..." -ForegroundColor Yellow
pyinstaller marnak_pdf_tools.spec --clean

Write-Host ""
Write-Host "4. Inno Setup ile installer oluşturuluyor..." -ForegroundColor Yellow
Write-Host "   (Inno Setup'un yüklü olduğundan emin olun)" -ForegroundColor Cyan

# Inno Setup'un farklı konumlarını kontrol et
$innoSetupPaths = @(
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe",
    "C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
    "C:\Program Files\Inno Setup 5\ISCC.exe"
)

$innoSetupFound = $false
foreach ($path in $innoSetupPaths) {
    if (Test-Path $path) {
        Write-Host "Inno Setup bulundu: $path" -ForegroundColor Green
        & $path setup.iss
        $innoSetupFound = $true
        break
    }
}

if (-not $innoSetupFound) {
    Write-Host "HATA: Inno Setup bulunamadı!" -ForegroundColor Red
    Write-Host "Lütfen Inno Setup'ı şu adresten indirin: https://jrsoftware.org/isinfo.php" -ForegroundColor Yellow
    Write-Host "Kurulum tamamlandıktan sonra bu scripti tekrar çalıştırın." -ForegroundColor Yellow
    Read-Host "Devam etmek için Enter'a basın"
    exit 1
}

Write-Host ""
Write-Host "5. Temizlik yapılıyor..." -ForegroundColor Yellow

# Temizlik işlemleri
$cleanupPaths = @(
    "build",
    "__pycache__",
    "marnak_pdf_tools\__pycache__",
    "marnak_pdf_tools\core\__pycache__",
    "marnak_pdf_tools\services\__pycache__",
    "marnak_pdf_tools\ui\__pycache__",
    "marnak_pdf_tools\ui\components\__pycache__",
    "marnak_pdf_tools\ui\windows\__pycache__",
    "marnak_pdf_tools\utils\__pycache__"
)

foreach ($path in $cleanupPaths) {
    if (Test-Path $path) {
        Remove-Item -Path $path -Recurse -Force
        Write-Host "Silindi: $path" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "Setup dosyası başarıyla oluşturuldu!" -ForegroundColor Green
Write-Host "Dosya konumu: dist\MarnakPDFAraclari_Setup.exe" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Green

# Setup dosyasının oluşturulup oluşturulmadığını kontrol et
$setupFile = "dist\MarnakPDFAraclari_Setup.exe"
if (Test-Path $setupFile) {
    $fileSize = (Get-Item $setupFile).Length
    $fileSizeMB = [math]::Round($fileSize / 1MB, 2)
    Write-Host "Setup dosyası boyutu: $fileSizeMB MB" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Setup dosyasını çalıştırmak ister misiniz? (Y/N)" -ForegroundColor Yellow
    $response = Read-Host
    if ($response -eq "Y" -or $response -eq "y") {
        Start-Process $setupFile
    }
} else {
    Write-Host "UYARI: Setup dosyası bulunamadı!" -ForegroundColor Red
}

Read-Host "Çıkmak için Enter'a basın"
