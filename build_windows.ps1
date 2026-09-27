$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)

py -3.12 -m venv .venv
if ($LASTEXITCODE -ne 0) { throw 'Can cai Python 3.12 de dong goi.' }

& .\.venv\Scripts\python.exe -m pip install -r requirements.txt 'pyinstaller>=6.20,<7'
if ($LASTEXITCODE -ne 0) { throw 'Khong cai duoc thu vien.' }

& .\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed --name KhoVanBan --add-data 'templates:templates' --add-data 'static:static' launcher.py
if ($LASTEXITCODE -ne 0) { throw 'Dong goi khong thanh cong.' }

Write-Host 'Da tao dist\KhoVanBan.exe'
