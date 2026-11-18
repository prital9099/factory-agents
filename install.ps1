# Installs the factory agents and the /factory skill into your Claude Code user folder.
# Usage:  powershell -ExecutionPolicy Bypass -File install.ps1
param([string]$Target = (Join-Path $env:USERPROFILE ".claude"))
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
foreach ($item in @(@{src="agents"; dst="agents"}, @{src="skills\factory"; dst="skills\factory"})) {
  $src = Join-Path $here $item.src
  $dst = Join-Path $Target $item.dst
  if (Test-Path $dst) {
    # keep anything that already exists, so nothing is lost
    $bak = "$dst.backup-$stamp"
    if ($item.src -eq "agents") {
      New-Item -ItemType Directory -Force $bak | Out-Null
      Get-ChildItem $src -Filter *.md | ForEach-Object {
        $old = Join-Path $dst $_.Name
        if (Test-Path $old) { Copy-Item $old $bak -Force }
      }
    } else { Copy-Item $dst $bak -Recurse -Force }
  }
  New-Item -ItemType Directory -Force $dst | Out-Null
  Copy-Item "$src\*" $dst -Recurse -Force
}
Write-Host "Installed into $Target"
Write-Host "Existing files with the same names were backed up next to them as *.backup-$stamp"
Write-Host "Next: pip install -r requirements.txt, then start a NEW Claude Code session."
