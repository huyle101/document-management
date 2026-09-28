$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)

$pythonVersion = $null
foreach ($version in @('3.14', '3.12')) {
    & py "-$version" --version *> $null
    if ($LASTEXITCODE -eq 0) {
        $pythonVersion = $version
        break
    }
}
if (-not $pythonVersion) { throw 'Can cai Python 3.14 hoac 3.12 de dong goi.' }

& py "-$pythonVersion" -m venv .venv
if ($LASTEXITCODE -ne 0) { throw 'Khong tao duoc moi truong Python.' }
& .\.venv\Scripts\python.exe -c 'import sysconfig; print("Build target: " + sysconfig.get_platform())'

& .\.venv\Scripts\python.exe -m pip install -r requirements.txt 'pyinstaller>=6.20,<7'
if ($LASTEXITCODE -ne 0) { throw 'Khong cai duoc thu vien.' }

& .\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed --name KhoVanBan --add-data 'templates:templates' --add-data 'static:static' launcher.py
if ($LASTEXITCODE -ne 0) { throw 'Dong goi khong thanh cong.' }

Write-Host 'Da tao dist\KhoVanBan.exe'
