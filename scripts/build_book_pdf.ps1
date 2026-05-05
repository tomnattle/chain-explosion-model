#Requires -Version 5.1
<#
.SYNOPSIS
  将 book/ 下书稿按阅读顺序合并为单册 PDF（Pandoc + XeLaTeX）。

.DESCRIPTION
  依赖（需自行安装并加入 PATH）：
  - Pandoc  https://pandoc.org/
  - MiKTeX 或 TeX Live（提供 xelatex；仓库内曾有 tectonic 用法，本脚本默认 xelatex）

  在仓库根目录执行：
    .\scripts\build_book_pdf.ps1

  输出默认： book/_build/假大象与泡泡-书稿.pdf

  若中文缺字，可改 -MainFont 为本机已装字体（如 "Source Han Serif SC", "SimSun"）。

.NOTES
  - 不含 02-contents.md（目录由 Pandoc --toc 生成）；不含 00-unified-writing-scheme.md（编者体例，避免正文膨胀）。
  - 图片路径依赖 --resource-path=book，以解析 cover.md 内 image/cover.jpg 等。
#>
[CmdletBinding()]
param(
    [string]$OutPdf = "",
    [string]$MainFont = "Microsoft YaHei"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RepoRoot

$Book = Join-Path $RepoRoot "book"
$BuildDir = Join-Path $Book "_build"
if (-not (Test-Path $BuildDir)) {
    New-Item -ItemType Directory -Path $BuildDir | Out-Null
}
if (-not $OutPdf) {
    $OutPdf = Join-Path $BuildDir "假大象与泡泡-书稿.pdf"
}

$rel = @(
    "book/cover.md",
    "book/00-preface.md",
    "book/01-appendix-three-phrasings.md",
    "book/04-chapter.md",
    "book/03-chapter.md",
    "book/05-chapter.md",
    "book/06-archive-bell.md",
    "book/07-archive-ghz.md",
    "book/08-chapter04.md",
    "book/09-chapter05.md",
    "book/10-chapter06.md",
    "book/11-chapter07.md",
    "book/12-chapter08.md",
    "book/13-chapter09.md",
    "book/14-chapter10.md",
    "book/15-chapter11.md",
    "book/16-chapter12.md",
    "book/17-chapter13.md",
    "book/18-chapter14.md",
    "book/19-chapter15.md",
    "book/20-chapter16.md",
    "book/21-chapter17.md",
    "book/22-chapter18.md",
    "book/23-afterword.md"
)

$inputs = @()
foreach ($f in $rel) {
    $p = Join-Path $RepoRoot $f
    if (-not (Test-Path $p)) {
        Write-Error "缺少文件: $p"
    }
    $inputs += $p
}

$pandoc = Get-Command pandoc -ErrorAction SilentlyContinue
if (-not $pandoc) {
    Write-Error "未找到 pandoc。请先安装 Pandoc 并加入 PATH。https://pandoc.org/installing.html"
}

$engine = "tectonic"
if (Get-Command xelatex -ErrorAction SilentlyContinue) {
    $engine = "xelatex"
} elseif (-not (Get-Command tectonic -ErrorAction SilentlyContinue)) {
    Write-Error "未找到 xelatex 或 tectonic。请在 conda base 安装: conda install -c conda-forge tectonic ；或安装 MiKTeX/TeX Live。"
}
Write-Host "PDF engine: $engine" -ForegroundColor Cyan

$rp = $Book + [IO.Path]::PathSeparator + (Join-Path $Book "image")
$pandocArgs = $inputs + @(
    "-o", $OutPdf
    "--pdf-engine=$engine"
    "-V", "mainfont=$MainFont"
    "-V", "CJKmainfont=$MainFont"
    "-V", "geometry:margin=2.5cm"
    "--resource-path", $rp
    "--toc"
    "--toc-depth=2"
    "-N"
    "--metadata", "title=假大象与泡泡"
    "--metadata", "subtitle=公开数据、Bell/GHZ 与读数规则的审计手记（书稿汇编）"
    "--metadata", "lang=zh-CN"
)

Write-Host "Pandoc -> $OutPdf"
& pandoc @pandocArgs
if ($LASTEXITCODE -ne 0) {
    Write-Error "pandoc 失败（退出码 $LASTEXITCODE）。可尝试 conda activate base 确保 tectonic 在 PATH，或安装 xelatex。"
}
Write-Host "完成: $OutPdf"
