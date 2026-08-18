$root = Split-Path -Parent $PSScriptRoot
$env:FOXHUB_MODE = "web"
Set-Location "$root\backend"
python -m foxhubclaw.main --mode web --host 0.0.0.0 --port 8787
