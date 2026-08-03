# =============================================================
# link-skills.ps1  (Windows, PowerShell)
# Trỏ từng skill EBM trong hub OneDrive -> %USERPROFILE%\.claude\skills\<tên>
# bằng JUNCTION (không cần quyền admin).
#
#   sync\skills\<tên>   --(junction)-->   ~\.claude\skills\<tên>
#
# Idempotent: chạy lại nhiều lần đều an toàn.
# Cách chạy: bấm đúp link-skills.cmd, hoặc trong PowerShell:
#   powershell -ExecutionPolicy Bypass -File link-skills.ps1
# =============================================================
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Hub  = Join-Path $ScriptDir "skills"
$Dest = Join-Path $env:USERPROFILE ".claude\skills"
$Backup = Join-Path $env:USERPROFILE ".claude\skills-backup"
New-Item -ItemType Directory -Force -Path $Dest | Out-Null

Write-Host "==> Hub : $Hub"
Write-Host "==> Dich: $Dest`n"

$count = 0
Get-ChildItem -Path $Hub -Directory | ForEach-Object {
    $name = $_.Name
    if ($name.StartsWith("_")) { return }                       # bo thu muc noi bo
    if (-not (Test-Path (Join-Path $_.FullName "SKILL.md"))) { return }  # chi skill that

    $target = Join-Path $Dest $name
    if (Test-Path $target) {
        $item = Get-Item $target -Force
        if ($item.LinkType) {
            # da la junction/symlink -> tao lai cho chac
            cmd /c rmdir "$target" | Out-Null
            cmd /c mklink /J "$target" "$($_.FullName)" | Out-Null
            Write-Host "    [~] $name (cap nhat junction)"
        } else {
            # Sao luu RA NGOAI thu muc skills: de .bak ngay tai cho thi Claude Code
            # van nap no thanh mot skill rieng -> menu "/" hien 2 ban cung ten, ban
            # cu mo ta cu (03/08/2026 da xay ra voi kham-ngoai-tru-ebm, tuan-thu-dieu-tri).
            $ts = Get-Date -Format "yyyyMMdd-HHmmss"
            New-Item -ItemType Directory -Force -Path $Backup | Out-Null
            Move-Item $target (Join-Path $Backup "$name.bak-$ts")
            cmd /c mklink /J "$target" "$($_.FullName)" | Out-Null
            Write-Host "    [!] $name (da co san -> sao luu vao skills-backup\$name.bak-$ts, tao junction moi)"
        }
    } else {
        cmd /c mklink /J "$target" "$($_.FullName)" | Out-Null
        Write-Host "    [+] $name (junction moi)"
    }
    $count++
}

Write-Host "`nHOAN TAT: da lien ket $count skill."
Write-Host "Kiem tra: dir `"$Dest`""
