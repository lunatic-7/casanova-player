; Casanova Player Installer Script

[Setup]
AppName=Casanova Player
AppVersion=1.0
AppPublisher=Wasif Nadeem
AppPublisherURL=https://github.com/lunatic-7/casanova-player
DefaultDirName={autopf}\CasanovaPlayer
DefaultGroupName=Casanova Player
OutputDir=installer_output
OutputBaseFilename=CasanovaPlayer_Setup_v1.0
SetupIconFile=assets\icons\app.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\CasanovaPlayer\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Casanova Player"; Filename: "{app}\CasanovaPlayer.exe"
Name: "{group}\Uninstall Casanova Player"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Casanova Player"; Filename: "{app}\CasanovaPlayer.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\CasanovaPlayer.exe"; Description: "{cm:LaunchProgram,Casanova Player}"; Flags: nowait postinstall skipifsilent