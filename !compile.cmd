@ECHO OFF
REM Компиляция проекта.

SET pythonDir=c:\Python27
SET installerDir=D:\Install\_pyinstaller-2.0
SET upxDir=D:\Install\_upx308w
SET outDir=D:\Install\ArchiveAnalizer\bin
SET projectName=ArchiveAnalizer
SET CurrentDir=%CD%
SET console=noconsole
SET one=onedir

rmdir /S /Q %outDir%

start /B /WAIT /D "%installerDir%" %pythonDir%\python.exe pyinstaller.py --%console% --%one% --out=%outDir% --name=%projectName% --version-file=%CurrentDir%\version.py --icon=%CurrentDir%\icon.ico %CurrentDir%\%projectName%.py

ECHO.
PAUSE
REM c:\Python27\python pyinstaller.py --console --onedir --name=ArchiveAnalizer --version-file=D:\Install\ArchiveAnalizer\version.py --upx-dir=D:\Install\_upx308w --icon=D:\Install\ArchiveAnalizer\icon.ico D:\Install\ArchiveAnalizer\ArchiveAnalizer.py
