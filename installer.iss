[Setup]
AppName=Sundry
AppVersion=1.0.1
VersionInfoVersion=1.0.1
AppPublisher=DuckStudio
VersionInfoCopyright=Copyright (c) 鸭鸭「カモ」
AppPublisherURL=https://duckduckstudio.github.io/yazicbs.github.io/
AppSupportURL=https://github.com/DuckDuckStudio/Sundry/issues
DefaultDirName={autopf}\Sundry
DefaultGroupName=Sundry
OutputDir=Release
OutputBaseFilename=Sundry_Setup
LicenseFile=LICENSE
Compression=lzma2
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"

[Files]
Source: "Release\pack\*"; DestDir: "{app}"; Flags: recursesubdirs

[Run]
Filename: "{sys}\cmd.exe"; Parameters: "/C setx PATH ""{app};%PATH%"" /M"; Flags: runhidden

[UninstallRun]
Filename: "{sys}\cmd.exe"; Parameters: "/C setx PATH ""%PATH:{app};=%"" /M"; Flags: runhidden; RunOnceId: UninstallSetPath
