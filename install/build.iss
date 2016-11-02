; This file generates the installer for {#AppName}
; This game was created and published by {#DevName}

#expr Exec("C:\Python27\python.exe", "../src/setup.py build",'.',1,SW_HIDE)

#define AppName "Take It Back"
#define DevName "Jake Thurman"

; Define the Entry Points
[Files]
Source: "build\exe.win-amd64-2.7\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs      
Source: "..\src\images\*"; DestDir: "{app}\images"; Flags: ignoreversion recursesubdirs createallsubdirs                    
Source: "..\src\fonts\*"; DestDir: "{app}\fonts"; Flags: ignoreversion
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

; Create a start menu shorcut
[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\TakeItBack.exe"; IconFilename: "{app}\src\images\logo.ico"

; Run the game when the user has completed the install process.
[Run]
Filename: "{app}\TakeItBack.exe"; Flags: postinstall; Description: "Play Now!";