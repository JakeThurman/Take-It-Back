; Define the Entry Poins
[Files]
Source: "..\src\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dependencies\*"; DestDir: "{tmp}"; Flags: ignoreversion
Source: "appdata\*"; DestDir: "{userappdata}/Take It Back"; Flags: ignoreversion

; Settings
[Setup]
SetupIconFile="..\src\images\logo.ico"
AppName="Take It Back"
AppVerName="Take It Back"
AppVersion="1.0.0.12"
DefaultDirName="C:\Program Files\Jake Thurman\Take It Back"
AppPublisherURL="jakethurman.github.io"
AppPublisher="Jake Thurman"
DefaultGroupName="Jake Thurman"

; Install Python 3.2
[Run] 
Filename: "msiexec.exe"; Parameters: "/i ""{tmp}\python-3.2.5.msi";

; Install Pygame
[Run]
Filename: "msiexec.exe"; Parameters: "/i ""{tmp}\pygame-1.9.2a0.win32-py3.2.msi";

; Create a start menu shorcut
[Icons]
Name: "{group}\Take It Back"; Filename: "{app}\main.pyw"; IconFilename: "{app}\images\logo.ico"