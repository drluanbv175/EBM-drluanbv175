# =============================================================
# link-skills.ps1  (Windows, PowerShell)
# Tro tung skill EBM trong hub -> %USERPROFILE%\.claude\skills\<ten>
#                              VA %USERPROFILE%\.codex\skills\<ten>
# bang JUNCTION (khong can quyen admin).
#
#   sync\skills\<ten>   --(junction)-->   ~\.claude\skills\<ten>
#                         \-(junction)-->  ~\.codex\skills\<ten>
#
# Idempotent: chay lai nhieu lan deu an toan.
# Cach chay: bam dup link-skills.cmd, hoac trong PowerShell:
#   powershell -ExecutionPolicy Bypass -File link-skills.ps1
#
# SUA 21/08/2026: them ~\.codex\skills. Ban cu chi noi ~\.claude\skills nen tren
# may Windows, Codex KHONG thay mot skill nao cua bac si - trong khi SYNC-README va
# AGENTS.md deu noi ca hai runtime dung chung nguon sync/skills. Dung dung ca:
# `os.symlink` cua Python nem WinError 1314 khi may chua bat Developer Mode (da do
# tren chinh may nay 17/08/2026), con junction thi tao duoc ma khong can quyen gi.
# =============================================================
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Hub  = Join-Path $ScriptDir "skills"

Write-Host "==> Hub : $Hub`n"

$tong = 0
foreach ($rel in @(".claude\skills", ".codex\skills")) {
    $Dest   = Join-Path $env:USERPROFILE $rel
    $Backup = "$Dest-backup"                # NGOAI vung Claude/Codex quet skill
    New-Item -ItemType Directory -Force -Path $Dest | Out-Null
    Write-Host "==> Dich: $Dest"

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
                Write-Host "    [!] $name (da co san -> sao luu vao $(Split-Path $Backup -Leaf)\$name.bak-$ts)"
            }
        } else {
            cmd /c mklink /J "$target" "$($_.FullName)" | Out-Null
            Write-Host "    [+] $name (junction moi)"
        }
        $count++
    }
    Write-Host "    -> $count skill`n"
    $tong += $count
}

Write-Host "HOAN TAT: da lien ket $tong luot (skill x 2 runtime)."
Write-Host "Kiem tra: dir `"$env:USERPROFILE\.claude\skills`" ; dir `"$env:USERPROFILE\.codex\skills`""
