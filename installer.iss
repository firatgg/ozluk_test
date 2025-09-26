; Marnak PDF Araçları - Inno Setup Kurulum Betiği
; Bu betik, Marnak PDF Araçları uygulaması için Windows kurulum dosyası oluşturur

#define MyAppName "Marnak PDF Araçları"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Marnak Lojistik"
#define MyAppURL "https://www.marnak.com.tr"
#define MyAppExeName "MarnakPDFAraclari.exe"

[Setup]
; Uygulama bilgileri
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Kurulum dizini
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes

; Lisans ve bilgi dosyaları
LicenseFile=LICENSE
InfoBeforeFile=MAIL_ICERIGI.txt
InfoAfterFile=KURULUM_REHBERI.md

; Çıktı dosyası
OutputDir=dist
OutputBaseFilename=Marnak_PDF_Araclari_Kurulum
SetupIconFile=marnak_pdf_tools\icons\favicon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; Sistem gereksinimleri
MinVersion=6.1sp1
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Dil desteği
; Languages=Turkish,English

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"
Name: "english"; MessagesFile: "compiler:Languages\English.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
; Ana uygulama dosyası
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Çeviri dosyaları
Source: "marnak_pdf_tools\translations\*"; DestDir: "{app}\translations"; Flags: ignoreversion recursesubdirs createallsubdirs

; Test dosyaları (isteğe bağlı)
Source: "tests\assets\*"; DestDir: "{app}\tests\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

; Dokümantasyon
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "KURULUM_REHBERI.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Başlat menüsü kısayolu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Masaüstü kısayolu (isteğe bağlı)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\{#MyAppExeName}"

; Hızlı başlat kısayolu (Windows 7 ve öncesi)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Kurulum tamamlandıktan sonra uygulamayı çalıştır
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Kullanıcı ayarlarını silme (isteğe bağlı)
Type: filesandordirs; Name: "{localappdata}\MarnakPDFTools"

[Code]
// Kurulum öncesi kontroller
function InitializeSetup(): Boolean;
begin
  Result := True;
  
  // .NET Framework kontrolü (gerekirse)
  // if not IsDotNetDetected('v4.0', 0) then begin
  //   MsgBox('Bu uygulama .NET Framework 4.0 veya üstü gerektirir.', mbError, MB_OK);
  //   Result := False;
  // end;
end;

// Kurulum sonrası işlemler
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then begin
    // Kurulum tamamlandı mesajı
    MsgBox('Marnak PDF Araçları başarıyla kuruldu!' + #13#10 + 
           'Uygulamayı başlatmak için masaüstündeki kısayolu kullanabilirsiniz.', 
           mbInformation, MB_OK);
  end;
end;

// Kaldırma işlemi öncesi
function InitializeUninstall(): Boolean;
begin
  Result := True;
  
  // Kullanıcıya onay sor
  if MsgBox('Marnak PDF Araçları kaldırılacak. Devam etmek istiyor musunuz?', 
            mbConfirmation, MB_YESNO) = IDNO then
    Result := False;
end;
