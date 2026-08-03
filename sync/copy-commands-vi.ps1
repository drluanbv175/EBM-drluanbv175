# =============================================================
# copy-commands-vi.ps1  (Windows)
# Chép bộ LỆNH TIẾNG VIỆT từ hub OneDrive -> %USERPROFILE%\.claude\commands\
# Idempotent: chạy lại bao nhiêu lần cũng an toàn.
# =============================================================
$ErrorActionPreference = 'Stop'
$Src  = Join-Path $PSScriptRoot 'commands-vi'
$Dest = Join-Path $env:USERPROFILE '.claude\commands'
if (-not (Test-Path $Src)) { Write-Host "✗ Không thấy thư mục nguồn: $Src"; exit 1 }
New-Item -ItemType Directory -Force -Path $Dest | Out-Null
$moi=0; $capnhat=0; $giu=0
Get-ChildItem "$Src\*.md" | ForEach-Object {
    $dich = Join-Path $Dest $_.Name
    if (-not (Test-Path $dich)) { Copy-Item $_.FullName $dich; $moi++; Write-Host "  + $($_.Name) (mới)" }
    elseif ((Get-FileHash $_.FullName).Hash -eq (Get-FileHash $dich).Hash) { $giu++ }
    else {
        $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
        Copy-Item $dich "$dich.bak-$ts" -Force
        Copy-Item $_.FullName $dich -Force; $capnhat++
        Write-Host "  ↻ $($_.Name) (cập nhật, bản cũ lưu .bak-$ts)"
    }
}
Write-Host "✓ Xong: $moi mới · $capnhat cập nhật · $giu không đổi → $Dest"
Write-Host "  Mở lại phiên Claude Code rồi gõ / để thấy các lệnh tiếng Việt."
