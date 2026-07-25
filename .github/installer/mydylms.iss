; ============================================================
; MYDY LMS — Inno Setup Installer Script
; ============================================================

#define MyAppName "MYDY LMS"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "viraj-sh"
#define MyAppURL "https://github.com/viraj-sh/MYDYLMS"
#define MyAppExeName "MYDYLMS.exe"

; This GUID is permanent — generate it ONCE (Tools > Generate GUID inside
; the Inno Setup IDE) and never change it again. Changing it makes Inno
; Setup treat every future release as a totally different application
; (side-by-side install instead of an upgrade). Committing it to git now.
#define MyAppId "{{7C30C73C-3C6E-43E9-84D7-4C24EEF1B173}}"

[Setup]
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases

; Per-user install by default: no UAC prompt, installs under the user's
; own profile. Change to "admin" + DefaultDirName={autopf}\{#MyAppName}
; if you need machine-wide installs later.
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=commandline dialog

DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
DisableWelcomePage=no

; 64-bit only — Nuitka compiled a 64-bit interpreter, so we require and
; target 64-bit Program Files.
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

OutputDir=Output
OutputBaseFilename=MYDYLMSSetup-{#MyAppVersion}
SetupIconFile=..\assets\icon.ico
Compression=lzma2/max
SolidCompression=yes

WizardStyle=modern
WizardImageFile=..\assets\installer\wizard-large.bmp
WizardSmallImageFile=..\assets\installer\wizard-small.bmp

; Uncomment once you add a real license file:
; LicenseFile=assets\license.txt

UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=MYDY LMS Setup
VersionInfoProductName={#MyAppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
; Pulls in the ENTIRE Nuitka standalone output folder recursively.
; Update the Source path if your Nuitka --output-dir differs.
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Removes locally-created logs/cache on uninstall. Config/user data under
; %LOCALAPPDATA%\MYDYLMS is intentionally NOT deleted here — see Part 7
; for why, and how to offer the user a choice instead.
Type: filesandordirs; Name: "{app}\logs"