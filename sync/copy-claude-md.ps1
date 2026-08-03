# =============================================================
# copy-claude-md.ps1  (Windows)
# Chép chỉ thị ngôn ngữ toàn cục từ hub OneDrive -> %USERPROFILE%\.claude\CLAUDE.md
#
#   sync\CLAUDE-user-global.md   --(copy)-->   ~\.claude\CLAUDE.md
#
# CỐ Ý dùng COPY chứ không junction/symlink: ~\.claude\CLAUDE.md là cấu hình nền,
# nếu OneDrive chưa tải file về (Files On-Demand) thì liên kết sẽ làm MẤT chỉ thị
# một cách im lặng. Bản chép thật luôn đọc được kể cả khi offline.
#
# Idempotent: chạy lại nhiều lần đều an toàn.
# =============================================================
$ErrorActionPreference = 'Stop'

$Src  = Join-Path $PSScriptRoot 'CLAUDE-user-global.md'
$Dest = Join-Path $env:USERPROFILE '.claude\CLAUDE.md'

if (-not (Test-Path $Src)) {
    Write-Host "✗ Không thấy bản nguồn: $Src"
    exit 1
}
New-Item -ItemType Directory -Force -Path (Split-Path $Dest) | Out-Null

if (Test-Path $Dest) {
    $hSrc  = (Get-FileHash $Src  -Algorithm SHA256).Hash
    $hDest = (Get-FileHash $Dest -Algorithm SHA256).Hash
    if ($hSrc -eq $hDest) {
        Write-Host "✓ Đã khớp, không cần chép: $Dest"
        exit 0
    }

    # Bản trên máy MỚI HƠN hub -> có thể là sửa tay chưa đưa lên hub. Không đè mù.
    if ((Get-Item $Dest).LastWriteTime -gt (Get-Item $Src).LastWriteTime -and $env:FORCE -ne '1') {
        Write-Host "⚠ Bản trên máy MỚI HƠN hub:"
        Write-Host "    máy: $Dest"
        Write-Host "    hub: $Src"
        Write-Host "  Nếu bản trên máy là bản đúng, hãy chép NGƯỢC lên hub rồi commit:"
        Write-Host "    Copy-Item `"$Dest`" `"$Src`" -Force"
        Write-Host "  Nếu muốn lấy bản hub đè lên: đặt biến môi trường FORCE=1 rồi chạy lại."
        exit 2
    }

    $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
    Copy-Item $Dest "$Dest.bak-$ts" -Force
    Write-Host "  ↳ đã sao lưu bản cũ: $Dest.bak-$ts"
}

Copy-Item $Src $Dest -Force
Write-Host "✓ Đã cập nhật: $Dest"
