$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)

& py -3 -m venv --clear .venv
if ($LASTEXITCODE -ne 0) { throw 'Khong tao duoc moi truong Python.' }
$buildTarget = & .\.venv\Scripts\python.exe -c 'import sysconfig;print(sysconfig.get_platform())'
if ($LASTEXITCODE -ne 0) { throw 'Khong xac dinh duoc kien truc Python.' }
Write-Host "Build target: $buildTarget"

& .\.venv\Scripts\python.exe -m pip install -r requirements.txt 'pyinstaller>=6.20,<7'
if ($LASTEXITCODE -ne 0) { throw 'Khong cai duoc thu vien.' }

& .\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed --name KhoVanBan --add-data 'templates:templates' --add-data 'static:static' launcher.py
if ($LASTEXITCODE -ne 0) { throw 'Dong goi khong thanh cong.' }

Write-Host 'Da tao dist\KhoVanBan.exe'
