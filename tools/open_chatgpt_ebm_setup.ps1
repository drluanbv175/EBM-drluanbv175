$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$PromptPath = Join-Path $Root "CHATGPT_EXPORT\CHATGPT_EBM_AGENT_SYSTEM_PROMPT.md"
$ZipPath = Join-Path $Root "CHATGPT_EXPORT\EBM_Copilot_ChatGPT_20260618.zip"
$ReadmePath = Join-Path $Root "CHATGPT-TICH-HOP.md"
$BuilderUrl = "https://chatgpt.com/gpts/editor"

if (-not (Test-Path -LiteralPath $PromptPath)) {
    throw "Thiếu prompt tích hợp ChatGPT: $PromptPath"
}
if (-not (Test-Path -LiteralPath $ZipPath)) {
    throw "Thiếu gói upload ChatGPT: $ZipPath"
}

$Prompt = Get-Content -LiteralPath $PromptPath -Raw -Encoding UTF8
Set-Clipboard -Value $Prompt

Start-Process $BuilderUrl
Start-Process explorer.exe -ArgumentList "/select,`"$ZipPath`""
Start-Process notepad.exe -ArgumentList "`"$ReadmePath`""

Write-Host ""
Write-Host "Đã chuẩn bị tự động:"
Write-Host "1. Prompt hệ thống đã nằm trong clipboard."
Write-Host "2. Đã mở trang tạo GPT: $BuilderUrl"
Write-Host "3. Đã mở Explorer và chọn sẵn file zip để upload:"
Write-Host "   $ZipPath"
Write-Host "4. Đã mở hướng dẫn nhanh."
Write-Host ""
Write-Host "Trong ChatGPT: đặt tên GPT là EBM Copilot, dán clipboard vào Instructions, upload file zip ở Knowledge."
