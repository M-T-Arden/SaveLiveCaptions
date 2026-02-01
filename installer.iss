
#define MyAppName "Save Live Captions"
#define MyAppVersion "1.1.1"
#define MyAppPublisher "LiveCaptionsHelper"
#define MyAppURL "https://github.com/LiveCaptionsHelper/SaveLiveCaptions"
#define MyAppExeName "SaveLiveCaptions_Folder.exe"

[Setup]
AppId={{696FDCA2-CFAF-49EE-B803-EAE6FA86BA2D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes

OutputDir=installer_output
OutputBaseFilename=SaveLiveCaptions_Setup
SetupIconFile=assets\SaveLC.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Default.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; pack dist\SaveLiveCaptions_Folder 
Source: "dist\SaveLiveCaptions_Folder\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\SaveLiveCaptions_Folder\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Parameters: ""; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Filename: "{app}\{#MyAppExeName}"; Flags: nowait postinstall skipifsilent