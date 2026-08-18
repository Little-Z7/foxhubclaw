$root = Split-Path -Parent $PSScriptRoot
$env:FOXHUB_MODE = "desktop"
Set-Location "$root\backend"
python -m foxhubclaw.desktop
