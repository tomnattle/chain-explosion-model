# Paper A Methods Snippet (Δ Mapping, Bilingual)

## 中文版（可直接粘贴到方法节）

### 1. 研究目标与边界

本文的目标是审计 CHSH 分析中统计对象对结论的敏感性，而非裁决某一统计口径在本体论上的唯一正确性。具体而言，我们在同一输入样本上并行构建 `binary`、`continuous_raw` 与 `NCC` 三种统计对象，比较其对应 `S` 值差异，并要求所有结论受预注册流程约束。

### 2. 数据与预注册

分析使用逐次事件数据（NIST HDF5）。在执行前固定并记录以下要素：数据路径与校验、预处理顺序、`Δ` 映射定义、统计公式、bootstrap 次数与随机种。所有脚本与输出路径在仓库中公开，以保证可复现性。

### 3. `Δ` 映射与事件聚合

我们将 one-hot 槽位解码为离散 slot（`v=2^k -> slot k`），并以 Alice/Bob slot 的循环距离构造 `Δ`，将距离折叠到 `0..8` 并映射到 `0..180°`。  
该步骤属于工程可复现定义，不宣称为官方唯一定义。`slot->±1` 的二值赋值规则作为显式假设预先注册，并在映射敏感性实验中做替代测试。

### 4. 模型比较与误差指标

对 `E(Δ)` 曲线，比较以下三类基线：

- Bell 分段线性基线（局域对照曲线）
- `LowCos`: `a*cos(Δ)+b`（加权最小二乘拟合）
- `HighCos`: `sign(a)*cos(Δ)`（高对称余弦基线）

点估计使用加权 RMSE。统计不确定性通过 binomial parametric bootstrap（95% CI）给出，并使用 9-bin exact paired-swap permutation test 检验 `LowCos` 相对 Bell 基线的误差优势显著性。

### 5. 闭合判据与失败条件

我们采用四闭合检查：Definition、Dimensional、Process、Statistical。  
任一失败触发降格规则：NIST 段落标注为 `provisional evidence`，并在失败日志中保留复现命令、触发条件与处置记录。

### 6. 稳健性设计

除主映射 `half_split` 外，还执行 `parity` 与 `quadrant_split` 替代映射。  
验证逻辑采用 LOBO 与 L2O 双策略，并比较 raw 与 clipped 设定，以排除单一验证配置导致的伪优势。

### 7. 复现与执行路径

主执行入口：

- `scripts/explore/run_delta_validation_pack.ps1`
- `scripts/explore/summarize_delta_closure.py`

主输出文件：

- `artifacts/public_validation_pack/NIST_E_DELTA_RIGOR_REPORT.md`
- `artifacts/public_validation_pack/NIST_E_DELTA_VALIDATION_SANITY.md`
- `artifacts/public_validation_pack/DELTA_CLOSURE_SUMMARY.md`
- `artifacts/public_validation_pack/DELTA_CLOSURE_CHECKLIST.md`

---

## English Version (Ready to Paste into Methods)

### 1. Objective and Scope

This study audits the sensitivity of CHSH conclusions to statistical-object definitions, rather than claiming an ontologically unique metric. On the same sample pool, we compute `binary`, `continuous_raw`, and `NCC` tracks in parallel and compare the resulting `S` behavior under a pre-registered workflow.

### 2. Data and Preregistration

We use event-level NIST HDF5 data. Before execution, we lock and record: data path/hash, preprocessing order, `Δ` mapping definition, statistical formulas, bootstrap settings, and random seed. Scripts and artifact paths are repository-published for reproducibility.

### 3. `Δ` Mapping and Event Aggregation

One-hot click codes are decoded to slots (`v=2^k -> slot k`). `Δ` is constructed from circular Alice/Bob slot distance, folded to `0..8`, then mapped to `0..180°`.  
This is treated as an engineering-reproducible definition (not an officially unique physical definition). The `slot->±1` rule is explicitly declared as a preregistered assumption and tested via alternative mappings.

### 4. Model Comparison and Error Metrics

For `E(Δ)`, we compare:

- Bell piecewise-linear baseline (local-reference curve)
- `LowCos`: `a*cos(Δ)+b` (weighted least-squares fit)
- `HighCos`: `sign(a)*cos(Δ)` (symmetric cosine baseline)

Point performance is reported by weighted RMSE. Uncertainty is quantified by binomial parametric bootstrap (95% CI), and significance is assessed via an exact 9-bin paired-swap permutation test for the `LowCos` vs Bell error difference.

### 5. Closure Criteria and Failure Policy

We apply four closure checks: Definition, Dimensional, Process, and Statistical.  
Any failed item triggers downgrade policy: the NIST section is marked as `provisional evidence`, and a reproducible failure log is archived.

### 6. Robustness Design

Beyond the main `half_split` mapping, we run `parity` and `quadrant_split` alternatives.  
Validation logic is stress-tested with both LOBO and L2O, plus raw/clipped comparison, to reduce the risk of configuration-specific artifacts.

### 7. Reproducibility Entry Points

Primary runners:

- `scripts/explore/run_delta_validation_pack.ps1`
- `scripts/explore/summarize_delta_closure.py`

Primary artifacts:

- `artifacts/public_validation_pack/NIST_E_DELTA_RIGOR_REPORT.md`
- `artifacts/public_validation_pack/NIST_E_DELTA_VALIDATION_SANITY.md`
- `artifacts/public_validation_pack/DELTA_CLOSURE_SUMMARY.md`
- `artifacts/public_validation_pack/DELTA_CLOSURE_CHECKLIST.md`
