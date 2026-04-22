# Claim Audit Tool

`claim_audit.py` 是一个面向真实审稿/报告流程的风险审计工具。  
它不判断“谁对谁错”，只审计一个结论是否存在**统计对象错配风险**。

## 1. 目标

给定同一批样本与一句结论声明（claim），并行计算三类指标：

- `E_binary`：二值 CHSH 对象（`A,B ∈ {±1}`）
- `E_raw`：连续原始相关
- `E_ncc`：归一化连续相关

再输出：

- 风险分数（0-100）
- 风险条目（高/中/低）
- 可执行的修正建议

## 2. 运行

```powershell
./activate_conda.ps1
python "scripts/explore/claim_audit.py" `
  --trials 300000 `
  --seed 20260422 `
  --angles "0,45,22.5,67.5" `
  --claim "S>2 implies nonlocality" `
  --out-json "docs/claim_audit_report.json" `
  --out-csv "docs/claim_audit_report.csv" `
  --out-markdown "docs/claim_audit_report.md"
```

### 2.1 审计外部 JSON 结果

如果你已有别处计算出的 `s_values`，可直接审计：

```json
{
  "s_values": {
    "binary": -2.0,
    "raw": -1.2,
    "ncc": -2.39
  }
}
```

```powershell
python "scripts/explore/claim_audit.py" `
  --input-json "path/to/s_values.json" `
  --claim "S>2 implies nonlocality"
```

### 2.2 审计外部 CSV 结果

支持两种 CSV 格式：

1) `metric,s` 纵表：

```csv
metric,s
binary,-2.0
raw,-1.2
ncc,-2.39
```

2) `binary,raw,ncc` 宽表（单行）：

```csv
binary,raw,ncc
-2.0,-1.2,-2.39
```

运行：

```powershell
python "scripts/explore/claim_audit.py" --input-csv "path/to/s_values.csv"
```

### 2.3 批量审计

批量配置示例：

```json
{
  "cases": [
    {
      "claim": "S>2 implies nonlocality",
      "angles": "0,45,22.5,67.5",
      "trials": 300000,
      "seed": 20260422
    },
    {
      "claim": "NCC>2 means Bell violation",
      "input_json": "docs/claim_audit_report.json"
    }
  ]
}
```

```powershell
python "scripts/explore/claim_audit.py" `
  --batch-json "path/to/batch_cases.json" `
  --out-json "docs/claim_audit_batch_report.json" `
  --out-csv "docs/claim_audit_batch_report.csv" `
  --out-markdown "docs/claim_audit_batch_report.md" `
  --out-html "docs/claim_audit_batch_report.html"
```

### 2.4 CI 失败阈值

可用 `--fail-on-risk-threshold` 把工具接入 CI：

```powershell
python "scripts/explore/claim_audit.py" `
  --batch-json "docs/claim_audit_batch_cases.json" `
  --fail-on-risk-threshold 50
```

如果任一 case 的风险分 `< 50`，进程会以 `exit code 2` 失败。

### 2.5 外置策略（Policy）

可通过 `--policy-json` 覆盖默认风险策略，便于团队按场景调权重。

示例：

```json
{
  "spread_high_threshold": 0.5,
  "binary_upper_guard": 2.001,
  "risk_penalty": {
    "high": 40,
    "medium": 20,
    "low": 10
  },
  "summary_cutoffs": {
    "high": 50,
    "medium": 80
  }
}
```

运行：

```powershell
python "scripts/explore/claim_audit.py" `
  --batch-json "docs/claim_audit_batch_cases.json" `
  --policy-json "docs/claim_audit_policy.json"
```

## 5. 一键运行

仓库根目录提供 `audit_all.ps1`，一次性输出 JSON/CSV/Markdown/HTML 并执行批量阈值检查：

```powershell
./audit_all.ps1
```

可选参数：

```powershell
./audit_all.ps1 -PolicyPath "docs/claim_audit_policy.json" -BatchConfig "docs/claim_audit_batch_cases.json" -FailThreshold 50
```

## 3. 核心规则（第一版）

- `RISK_METRIC_DIVERGENCE`：同一样本上多指标 \(|S|\) 分歧显著
- `RISK_OBJECT_MISMATCH`：二值 CHSH 未超界、NCC 超阈值，存在对象错配风险
- `RISK_CLAIM_OVERREACH`：结论外推超过当前指标支持范围

## 4. 输出口径

工具输出的是“审计风险”，不是“物理裁决”。  
建议在任何对外陈述中附上三指标并列结果，防止混用同一个 \(E\) 符号。

