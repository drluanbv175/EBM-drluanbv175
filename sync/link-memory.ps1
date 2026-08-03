# =============================================================
# link-memory.ps1  (Windows)
# Tro thu muc memory cua Claude CLI -> hub chung trong OneDrive,
# de "tri nho" dong bo lien mach giua Windows va Mac.
#
#   %USERPROFILE%\.claude\projects\<encoded>\memory  --(Junction)-->  sync\memory
#
# Dung JUNCTION nen KHONG can quyen admin. Idempotent.
# Chay:  bam dup link-memory.cmd  (hoac)
#        powershell -ExecutionPolicy Bypass -File link-memory.ps1
# =============================================================
$ErrorActionPreference = "Stop"

$scriptDir = $PSScriptRoot
$projRoot  = (Resolve-Path (Join-Path $scriptDir "..")).Path     # ...\Claude AI
$hub       = Join-Path $scriptDir "memory"                        # ...\Claude AI\sync\memory
New-Item -ItemType Directory -Force -Path $hub | Out-Null

# 1) Tim project dir cuc bo: uu tien *Claude-AI co san, neu khong thi tu tinh ten ma hoa
$projectsRoot = Join-Path $env:USERPROFILE ".claude\projects"
New-Item -ItemType Directory -Force -Path $projectsRoot | Out-Null
$existing = Get-ChildItem $projectsRoot -Directory -Filter "*Claude-AI" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($existing) {
    $localParent = $existing.FullName
} else {
    $enc = ($projRoot -replace '[^a-zA-Z0-9]','-')
    $localParent = Join-Path $projectsRoot $enc
    New-Item -ItemType Directory -Force -Path $localParent | Out-Null
    Write-Host "==> Tao project dir moi: $localParent"
}
$local = Join-Path $localParent "memory"
Write-Host "==> Hub  : $hub"
Write-Host "==> Local: $local"

# 2) Dong bo noi dung 1 lan truoc khi link (khong mat du lieu cua may nao)
$hubMd = Get-ChildItem $hub -Filter *.md -ErrorAction SilentlyContinue
$localItem = Get-Item $local -ErrorAction SilentlyContinue
$localIsReal = ($localItem) -and (-not ($localItem.Attributes -band [IO.FileAttributes]::ReparsePoint))
if (-not $hubMd) {
    if ($localIsReal -and (Get-ChildItem $local -Filter *.md -ErrorAction SilentlyContinue)) {
        Write-Host "==> Hub trong -> seed tu local"
        Copy-Item "$local\*.md" $hub -Force
    }
} elseif ($localIsReal) {
    Get-ChildItem $local -Filter *.md -ErrorAction SilentlyContinue | ForEach-Object {
        $dest = Join-Path $hub $_.Name
        if (-not (Test-Path $dest)) { Write-Host "==> Bo sung file local con thieu vao hub: $($_.Name)"; Copy-Item $_.FullName $dest }
    }
}

# 3) Tao junction
$localItem = Get-Item $local -ErrorAction SilentlyContinue
if ($localItem -and ($localItem.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
    Write-Host "==> Da la junction/symlink: $local"
} else {
    if (Test-Path $local) {
        $ts = Get-Date -Format "yyyyMMdd-HHmmss"
        Write-Host "==> Sao luu $local -> memory.bak-$ts"
        Rename-Item $local "memory.bak-$ts"
    }
    New-Item -ItemType Junction -Path $local -Target $hub | Out-Null
    Write-Host "==> Da tao junction: $local -> $hub"
}

Write-Host ""
Write-Host "HOAN TAT. Noi dung hub:"
Get-ChildItem $hub -Filter *.md | Select-Object Name, Length | Format-Table -AutoSize
