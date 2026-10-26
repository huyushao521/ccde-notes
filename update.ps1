# 一键更新笔记站点：构建 -> 提交 -> 推送
# 用法： .\update.ps1 "第7章：二层技术 精讲"
param(
    [Parameter(Position = 0)]
    [string]$Message
)

$ErrorActionPreference = 'Stop'
Set-Location -Path $PSScriptRoot

if (-not $Message) {
    $Message = "更新笔记 $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
}

Write-Host "[1/3] 构建站点 ..." -ForegroundColor Cyan
python build_site.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "构建失败，已中止（未提交、未推送）" -ForegroundColor Red
    exit 1
}

Write-Host "[2/3] 提交改动 ..." -ForegroundColor Cyan
git add -A
$pending = git status --porcelain
if (-not $pending) {
    Write-Host "没有需要提交的改动，跳过提交与推送" -ForegroundColor Yellow
    exit 0
}
git commit -q -m $Message
if ($LASTEXITCODE -ne 0) {
    Write-Host "提交失败，已中止" -ForegroundColor Red
    exit 1
}

Write-Host "[3/3] 推送到 GitHub ..." -ForegroundColor Cyan
git push origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "推送失败，请检查凭据或网络" -ForegroundColor Red
    exit 1
}

Write-Host "完成。约 1 分钟后生效： https://huyushao521.github.io/ccde-notes/" -ForegroundColor Green
