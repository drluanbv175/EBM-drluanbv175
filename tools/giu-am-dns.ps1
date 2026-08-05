# -*- coding: utf-8 -*-
# ============================================================================
#  GIỮ ẤM CACHE DNS — làm mạng nhanh mà KHÔNG đổi DNS server của máy
# ============================================================================
#  Vì sao cần: DNS bệnh viện (192.1.1.214) hỏng khâu tra cứu đệ quy — mỗi tên
#  miền tra LẦN ĐẦU mất 3,7–12 giây, có khi thất bại hẳn. Nhưng tra LẠI chỉ
#  còn 2–4 ms nhờ cache. Script này chủ động tra sẵn các tên miền hay dùng
#  theo chu kỳ, để lúc bác sĩ cần thì kết quả đã nằm sẵn trong cache.
#
#  Hưởng lợi: MỌI chương trình trên máy (Claude Code, Python gọi PubMed/
#  Crossref, trình duyệt, OneDrive) vì tất cả dùng chung cache DNS của Windows.
#
#  KHÔNG sửa cài đặt hệ thống, KHÔNG cần quyền Administrator, dừng lúc nào
#  cũng được (Ctrl+C hoặc đóng cửa sổ). Không ảnh hưởng eHospital.
# ============================================================================

$ErrorActionPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Chu kỳ lặp (giây). Đặt 30 vì TTL của nhiều bản ghi chỉ ~56 giây —
# tra lại mỗi 30 giây thì cache gần như luôn còn hạn.
$chuKy = 30

# Các tên miền hệ EBM và công cụ thật sự gọi tới.
# Thêm/bớt tự do — mỗi dòng một tên miền.
$tenMien = @(
    # --- Claude / Anthropic ---
    'api.anthropic.com'
    'claude.ai'
    # --- PubMed / NCBI ---
    'eutils.ncbi.nlm.nih.gov'
    'pubmed.ncbi.nlm.nih.gov'
    'www.ncbi.nlm.nih.gov'
    # --- Europe PMC ---
    'www.ebi.ac.uk'
    'europepmc.org'
    # --- Crossref / DOI / OpenAlex ---
    'api.crossref.org'
    'doi.org'
    'api.openalex.org'
    # --- Nguồn chứng cứ khác ---
    'clinicaltrials.gov'
    'api.fda.gov'
    'api.semanticscholar.org'
    'www.cochranelibrary.com'
    # --- Guideline hay tra ---
    'www.nice.org.uk'
    'www.escardio.org'
    # --- Công cụ lập trình ---
    'github.com'
    'raw.githubusercontent.com'
    'pypi.org'
    'files.pythonhosted.org'
    # --- OneDrive ---
    'graph.microsoft.com'
)

Write-Host ""
Write-Host "  GIU AM CACHE DNS - dang chay" -ForegroundColor Green
Write-Host "  $($tenMien.Count) ten mien, lam moi moi $chuKy giay"
Write-Host "  Dong cua so nay hoac bam Ctrl+C de dung."
Write-Host ""

$vong = 0
while ($true) {
    $vong++
    $batDau = Get-Date
    $cham = 0
    $loi = 0

    foreach ($t in $tenMien) {
        $do = Measure-Command {
            try { Resolve-DnsName $t -Type A -ErrorAction Stop | Out-Null }
            catch { $script:coLoi = $true }
        }
        if ($script:coLoi) { $loi++; $script:coLoi = $false }
        elseif ($do.TotalMilliseconds -gt 500) { $cham++ }
    }

    $giay = [math]::Round(((Get-Date) - $batDau).TotalSeconds, 1)
    $gio = (Get-Date).ToString('HH:mm:ss')

    if ($vong -eq 1) {
        Write-Host "  [$gio] Vong dau (lam am lan dau, cham la binh thuong): $giay giay" -ForegroundColor Yellow
    } else {
        $mau = if ($giay -lt 2) { 'Green' } else { 'Yellow' }
        Write-Host "  [$gio] Vong $vong : $giay giay | phai tra moi: $cham | that bai: $loi" -ForegroundColor $mau
    }

    Start-Sleep -Seconds $chuKy
}
