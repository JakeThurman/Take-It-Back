; Define the Entry Poins

#define AppName "Take It Back"
#define DevName "Jake Thurman"

[Files]
Source: "..\src\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dependencies\*"; DestDir: "{tmp}"; Flags: ignoreversion deleteafterinstall
Source: "appdata\*"; DestDir: "{userappdata}/{#AppName}"; Flags: ignoreversion

; Settings
[Setup]
SetupIconFile="..\src\images\logo.ico"
AppName={#AppName}
AppVerName={#AppName}
AppVersion="1.0.0.12"
DefaultDirName="C:\Program Files\{#DevName}\{#AppName}"
AppPublisherURL="jakethurman.github.io"
AppPublisher="{#DevName}"
DefaultGroupName="{#DevName}"
OutputBaseFilename="{#AppName} Installer"

; Install Python 3.2
[Run]                                                                       
Filename: "msiexec.exe"; Parameters: "/i ""{tmp}\python-3.2.5.msi"; Flags: hidewizard; StatusMsg:"Installing Python Interpreter";

; Install Pygame
[Run]
Filename: "msiexec.exe"; Parameters: "/i ""{tmp}\pygame-1.9.2a0.win32-py3.2.msi"; Flags: hidewizard; StatusMsg:"Installing Pygame Framework";

; Create a start menu shorcut
[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\main.pyw"; IconFilename: "{app}\images\logo.ico"

; Run the game when the user has completed the install process.
[Run]
Filename: "python"; Parameters:"{app}\main.pyw"" > {userappdata}\run.log"; Flags: postinstall; Description: "Play Now!";