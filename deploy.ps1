# Push device/*.py and data files to the ESP32 and reset it. Usage: .\deploy.ps1 [-Port COM7]
param([string]$Port = "COM7")
$mp = Join-Path $PSScriptRoot ".venv\Scripts\mpremote.exe"
$files = Get-ChildItem (Join-Path $PSScriptRoot "device") -File | Where-Object { $_.Extension -in ".py", ".b64", ".txt", ".html" }
foreach ($f in $files) {
    Write-Host "-> $($f.Name)"
    & $mp connect $Port fs cp $f.FullName ":$($f.Name)"
}
& $mp connect $Port reset
