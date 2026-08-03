# =============================================================
# fix-medsci-root.ps1  (Windows) — bản song song của fix-medsci-root.sh
# Trỏ %USERPROFILE%\workspace\medsci-skills về bản medsci-skills đang cài.
#
# VÌ SAO CẦN: các script bên trong skill medsci gọi nhau bằng đường dẫn
#     "${MEDSCI_SKILLS_ROOT:-$HOME/workspace/medsci-skills}/skills/..."
# Khi cài qua Claude Code, skill nằm ở
#     ~\.claude\plugins\cache\medsci-skills\<plugin>\<hash>\skills\...
# nên mặc định trỏ vào thư mục KHÔNG TỒN TẠI → skill vẫn hiện khi gõ `/`
# nhưng chạy tới lệnh nào cũng gãy. tools/check_plugin_health.py bắt lỗi này (N2).
#
# Hash phiên bản đổi sau mỗi lần cập nhật plugin → chạy lại script này khi đó.
# Dùng JUNCTION nên KHÔNG cần quyền quản trị. Idempotent.
# =============================================================
$ErrorActionPreference = "Stop"

$Cache = Join-Path $env:USERPROFILE ".claude\plugins\cache\medsci-skills"
$Dich  = Join-Path $env:USERPROFILE "workspace\medsci-skills"

if (-not (Test-Path $Cache)) {
    Write-Host "X Chua cai bo medsci-skills (khong thay $Cache)"
    exit 1
}

# Chọn bản cài có ĐỦ skill nhất; mọi plugin medsci đều chứa trọn bộ, nhưng
# nếu một bản đang tải dở thì bản khác vẫn cứu được.
$Nguon = ""; $Nhieu = 0
Get-ChildItem $Cache -Directory | ForEach-Object {
    Get-ChildItem $_.FullName -Directory | ForEach-Object {
        $sk = Join-Path $_.FullName "skills"
        if (Test-Path $sk) {
            $n = (Get-ChildItem $sk -Directory).Count
            if ($n -gt $Nhieu) { $Nhieu = $n; $Nguon = $_.FullName }
        }
    }
}
if (-not $Nguon) { Write-Host "X Khong thay thu muc skills nao trong $Cache"; exit 1 }

New-Item -ItemType Directory -Force -Path (Split-Path $Dich) | Out-Null

if (Test-Path $Dich) {
    $item = Get-Item $Dich -Force
    if ($item.LinkType) {
        cmd /c rmdir "$Dich" | Out-Null
        cmd /c mklink /J "$Dich" "$Nguon" | Out-Null
        Write-Host "~ Cap nhat lien ket"
    } else {
        # Có thư mục thật ở đó — KHÔNG đè, để bác sĩ tự quyết
        Write-Host "! $Dich dang la thu muc that, khong phai lien ket."
        Write-Host "  Khong dung vao. Muon dung ban cai cua Claude Code thi doi ten no roi chay lai."
        exit 2
    }
} else {
    cmd /c mklink /J "$Dich" "$Nguon" | Out-Null
    Write-Host "+ Tao lien ket moi"
}

Write-Host "OK $Dich -> $Nguon"
Write-Host "  ($Nhieu skill dung duoc)"

$probe = Join-Path $Dich "skills\self-review\scripts\check_classical_style.py"
if (Test-Path $probe) {
    Write-Host "  OK script trong skill da co the doc toi"
} else {
    Write-Host "  ! Khong thay script mau - xem lai ban cai"
}
