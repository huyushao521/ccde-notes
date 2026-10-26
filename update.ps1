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

Write-Host "[1/4] 合并留言板导出（.json）..." -ForegroundColor Cyan
# 留言板把新留言存在浏览器本地，点「导出 .json」后会在下载目录生成 ccde-board.json
# 这里把它并入 docs/assets/board-data.json，随仓库推上去，换浏览器/换设备都能看到历史留言
$archivePath = Join-Path $PSScriptRoot 'docs\assets\board-data.json'
$downloadDir = Join-Path $env:USERPROFILE 'Downloads'
$exportFiles = @(
    Get-ChildItem -Path $downloadDir -Filter 'ccde-board*.json' -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime
)

if ($exportFiles.Count -eq 0) {
    Write-Host "  未发现 ccde-board*.json，跳过" -ForegroundColor DarkGray
}
else {
    $archive = @()
    if (Test-Path $archivePath) {
        $raw = Get-Content -Path $archivePath -Raw -Encoding UTF8
        if ($raw -and $raw.Trim()) {
            $parsed = $raw | ConvertFrom-Json
            if ($parsed -is [System.Array]) { $archive = @($parsed) }
            elseif ($parsed -and $parsed.PSObject.Properties.Name -contains 'items') { $archive = @($parsed.items) }
        }
    }

    $byId = [ordered]@{}
    foreach ($it in $archive) { if ($it.id) { $byId[[string]$it.id] = $it } }

    $added = 0; $updated = 0; $removed = 0
    foreach ($f in $exportFiles) {
        $data = Get-Content -Path $f.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
        foreach ($it in @($data.items)) {
            if (-not $it.id) { continue }
            $key = [string]$it.id
            if ($byId.Contains($key)) { $byId[$key] = $it; $updated++ }
            else { $byId[$key] = $it; $added++ }
        }
        foreach ($d in @($data.deleted)) {
            if ($d -and $byId.Contains([string]$d)) { $byId.Remove([string]$d); $removed++ }
        }
    }

    if (($added + $updated + $removed) -eq 0) {
        Write-Host "  导出文件没有新增内容，跳过" -ForegroundColor DarkGray
    }
    else {
        $merged = @($byId.Values | Sort-Object { [int64]$_.t })
        $parts = @()
        foreach ($it in $merged) { $parts += (ConvertTo-Json -InputObject $it -Depth 6 -Compress) }
        $json = if ($parts.Count -eq 0) { '[]' } else { "[`n  " + ($parts -join ",`n  ") + "`n]" }

        $utf8 = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($archivePath, $json, $utf8)

        foreach ($f in $exportFiles) {
            Rename-Item -Path $f.FullName -NewName ($f.Name + '.synced') -Force
        }
        Write-Host ("  新增 {0} 条 / 更新 {1} 条 / 删除 {2} 条，归档共 {3} 条" -f $added, $updated, $removed, $merged.Count) -ForegroundColor Green
    }
}

Write-Host "[2/4] 构建站点 ..." -ForegroundColor Cyan
python build_site.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "构建失败，已中止（未提交、未推送）" -ForegroundColor Red
    exit 1
}

Write-Host "[3/4] 提交改动 ..." -ForegroundColor Cyan
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

Write-Host "[4/4] 推送到 GitHub ..." -ForegroundColor Cyan
# git 会把进度写到 stderr，直接调用会被 PowerShell 当成错误中断，这里显式降级处理
$ErrorActionPreference = 'Continue'
git push origin main 2>&1 | Write-Host
$pushCode = $LASTEXITCODE
$ErrorActionPreference = 'Stop'
if ($pushCode -ne 0) {
    Write-Host "推送失败，请检查凭据或网络" -ForegroundColor Red
    exit 1
}

Write-Host "完成。约 1 分钟后生效： https://huyushao521.github.io/ccde-notes/" -ForegroundColor Green
