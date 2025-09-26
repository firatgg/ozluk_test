@echo off
echo Marnak PDF Araçları - Windows Setup Oluşturucu
echo ================================================

echo.
echo 1. Virtual environment aktifleştiriliyor...
call venv\Scripts\activate.bat

echo.
echo 2. Gerekli paketler yükleniyor...
pip install -r requirements.txt

echo.
echo 3. PyInstaller ile executable oluşturuluyor...
pyinstaller marnak_pdf_tools.spec --clean

echo.
echo 4. Inno Setup ile installer oluşturuluyor...
echo    (Inno Setup'un yüklü olduğundan emin olun)
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss

echo.
echo 5. Temizlik yapılıyor...
if exist build rmdir /s /q build
if exist __pycache__ rmdir /s /q __pycache__
if exist marnak_pdf_tools\__pycache__ rmdir /s /q marnak_pdf_tools\__pycache__
if exist marnak_pdf_tools\core\__pycache__ rmdir /s /q marnak_pdf_tools\core\__pycache__
if exist marnak_pdf_tools\services\__pycache__ rmdir /s /q marnak_pdf_tools\services\__pycache__
if exist marnak_pdf_tools\ui\__pycache__ rmdir /s /q marnak_pdf_tools\ui\__pycache__
if exist marnak_pdf_tools\ui\components\__pycache__ rmdir /s /q marnak_pdf_tools\ui\components\__pycache__
if exist marnak_pdf_tools\ui\windows\__pycache__ rmdir /s /q marnak_pdf_tools\ui\windows\__pycache__
if exist marnak_pdf_tools\utils\__pycache__ rmdir /s /q marnak_pdf_tools\utils\__pycache__

echo.
echo ================================================
echo Setup dosyası başarıyla oluşturuldu!
echo Dosya konumu: dist\MarnakPDFAraclari_Setup.exe
echo ================================================
pause
