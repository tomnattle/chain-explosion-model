param(
    [switch]$Strict
)

Set-Location $PSScriptRoot

Write-Host "== 计算机探索: 启动 =="

# 在仓库根目录运行原有脚本
$repoRoot = Resolve-Path ".."
Set-Location $repoRoot

if ($Strict) {
    Write-Host "运行严格相图扫描..."
    python "ripple_computer_lab/ripple_phase_map_scan_strict.py"
} else {
    Write-Host "运行多映射彩色相图..."
    python "ripple_computer_lab/ripple_phase_map_multimapping_plot.py"
    Write-Host "运行论文风格图..."
    python "ripple_computer_lab/ripple_phase_map_paper_plots.py"
}

Write-Host "== 完成 =="
