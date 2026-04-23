# Submission Text Pack

基于当前仓库结果的一次性投稿文本包（可直接复制改名使用）。

---

## Version A: Foundations / Methods 风格

### Title Candidates

1. **A Reproducible Shape-Level Reanalysis of NIST Bell Data with Definition-Traceable `E(Δ)` Modeling**  
2. **Open Bell-Test Data Reanalysis: Cosine-vs-Polyline `E(Δ)` Comparison with Assumption Auditing**  
3. **From Point Violations to Shape Evidence: A Transparent `E(Δ)` Framework on NIST Completeblind Data**

### Abstract (Methods-Forward)

We present a reproducible shape-level reanalysis of the NIST completeblind Bell-test public dataset by constructing an explicit correlation profile `E(Δ)` from one-hot time-slot clicks. Three reference families are compared on a common angle-difference axis: a Bell-style binary polyline baseline, a raw low-cosine model `a cos(Δ)+b`, and a normalized cosine model `sign(a)cos(Δ)`. Under a preregistered binary mapping (`slot 0..7 -> +1`, `slot 8..15 -> -1`), the best-fit low-cosine is `E_low(Δ)=0.907410 cos(Δ)+0.092241`, with markedly lower weighted RMSE than the Bell polyline (`0.014459` vs `0.058318`; normalized cosine `0.016552`).  
Statistical robustness is quantified by parametric bootstrap (`n=3000`), yielding a 95% CI for `wRMSE(LowCos)-wRMSE(Bell)` of `[-0.049243, -0.036555]` and `P[wRMSE(LowCos)<wRMSE(Bell)]=1.0`, and by exact paired-swap permutation testing across 9 `Δ` bins (one-sided `p=0.0117188`, two-sided `p=0.0234375`).  
To prevent interpretive overreach, we explicitly separate officially aligned definitions (one-hot slot decoding) from engineering choices (`Δ` folding) and assumption-dependent steps (`slot -> ±1` mapping). The resulting claim is conditional but precise: under the declared mapping, the empirical `E(Δ)` shape is closer to cosine-family trajectories than to a piecewise-linear Bell baseline. Beyond this specific finding, we provide a transparent framework for open Bell-data model comparison with assumption traceability and reproducible inferential evidence.

### Keywords

- Bell test reanalysis  
- NIST completeblind  
- reproducibility  
- model comparison  
- permutation test  
- bootstrap confidence interval  
- assumption traceability

### Cover Letter (Methods-Forward)

Dear Editor,

Please find enclosed our manuscript on a reproducible reanalysis of the NIST completeblind Bell-test public dataset. The manuscript targets a methodological question: how to compare competing correlation-shape hypotheses on open Bell data while keeping every assumption auditable.

Our contribution is threefold:

1. We construct `E(Δ)` directly from public one-hot slot streams with explicit preprocessing definitions.
2. We compare Bell-style piecewise-linear and cosine-family trajectories on the same axis with weighted error metrics.
3. We report robustness using both bootstrap confidence intervals and exact permutation testing, and provide an explicit legality matrix that separates officially documented steps from assumption-dependent ones.

Under the declared preregistered mapping, the empirical profile is significantly closer to cosine-family trajectories than to the Bell polyline baseline. We deliberately frame this as a conditional result and include sensitivity analysis to prevent overstatement.

We believe this manuscript fits a methods-oriented readership interested in Bell-test data analysis, reproducibility standards, and assumption-aware inference in foundational experiments. All key artifacts are organized for independent verification.

Thank you for your consideration.

Sincerely,  
[Your Name]  
[Affiliation]  
[Email]

---

## Version B: Physics Letters 风格（更短、更结果导向）

### Title Candidates

1. **NIST `E(Δ)` Data Favor Cosine-Family Shapes over a Bell-Style Polyline Baseline**  
2. **Shape-Level Evidence in NIST Bell Data: Low-Cosine Outperforms Piecewise Linear Baseline**  
3. **A Compact `E(Δ)` Test on NIST Completeblind Data with Bootstrap and Exact Permutation Evidence**

### Abstract (Compact / Results-First)

We perform a compact shape-level test on NIST completeblind Bell-test public data by reconstructing `E(Δ)` from one-hot click slots and comparing three reference trajectories: Bell-style binary polyline, raw low-cosine `a cos(Δ)+b`, and normalized cosine `sign(a)cos(Δ)`. With preregistered mapping (`slot 0..7 -> +1`, `slot 8..15 -> -1`), the fitted model is `E_low(Δ)=0.907410 cos(Δ)+0.092241`. Weighted RMSE values are `0.058318` (Bell), `0.014459` (LowCos), and `0.016552` (HighCos). Bootstrap (`n=3000`) yields a 95% CI for `wRMSE(LowCos)-wRMSE(Bell)` of `[-0.049243, -0.036555]` with probability `1.0` that LowCos is better. Exact paired-swap permutation across 9 `Δ` bins gives one-sided `p=0.0117188` (two-sided `0.0234375`).  
The conclusion is explicit and conditional: under the declared mapping, empirical `E(Δ)` is closer to cosine-family trajectories than to the piecewise-linear Bell baseline.

### Keywords

- Bell-test public data  
- correlation shape  
- NIST completeblind  
- cosine fit  
- permutation p-value

### Cover Letter (Compact / Results-First)

Dear Editor,

We submit a short report on a shape-level reanalysis of NIST completeblind Bell-test data. Instead of relying on isolated scalar summaries, we compare the full `E(Δ)` profile against a Bell-style polyline and two cosine-family trajectories.

Under a declared preregistered mapping, the low-cosine model strongly outperforms the Bell polyline (`wRMSE 0.014459` vs `0.058318`), with support from bootstrap confidence intervals and exact paired-swap permutation testing (`p=0.0117188`, one-sided). The manuscript is concise, fully reproducible, and explicit about assumption boundaries.

We believe the result is suitable for a brief communication format focused on quantitative model discrimination in open Bell-test data.

Sincerely,  
[Your Name]  
[Affiliation]  
[Email]

---

## 可直接替换区（提交前手动改）

- `[Your Name]`
- `[Affiliation]`
- `[Email]`
- 目标期刊名称（若要定制抬头）
- 如需双盲：删除作者与机构信息

---

## 投稿前检查清单（一次过）

1. 数字一致性：`wRMSE`、CI、p 值与 `NIST_E_DELTA_RIGOR_REPORT.md` 一致。  
2. 口径一致性：都写“under the declared/preregistered mapping”。  
3. 图文一致性：图5标题、图注、正文结论同向。  
4. 边界披露：必须保留定义合法性分层（官方一致/工程定义/假设定义）。  
5. 复现路径：保留核心脚本路径与输出路径。  

---

## 门禁状态与边界声明（建议并入正文/附录）

为避免过度承诺，建议在投稿版本中加入以下统一口径：

- 当前项目采用 `MAPPING_POLICY_2D` 门禁体系，先以 2D（仅 `Δ` 轴）进行严格无泄漏外推评估，再决定是否进入 3D 扩展。
- 在主映射 `half_split` 下，主模型可通过主门槛；但在压力映射 `parity` 与 `quadrant_split` 下出现赢家切换。
- 因此当前总体门禁状态为 `FAIL`（见 `NIST_MAPPING_POLICY_CHECK.md`），结论应表述为条件性结论，而非映射无关结论。
- 推荐对外表述模板：**“在预注册主映射定义下，观察到稳定的形状层证据；跨映射稳健性仍在加固中。”**

建议在文末增加“下一步工作”一句：

- `Next-step statement`: *Before 3D expansion, we will finalize mapping policy and pass the 2D robustness gate across stress mappings.*

---

## 对应证据文件

- `artifacts/public_validation_pack/fig5_nist_e_delta_three_tracks.png`
- `artifacts/public_validation_pack/NIST_E_DELTA_THREE_TRACKS_SUMMARY.md`
- `artifacts/public_validation_pack/NIST_E_DELTA_MAPPING_SENSITIVITY.md`
- `artifacts/public_validation_pack/NIST_E_DELTA_RIGOR_REPORT.md`
- `artifacts/public_validation_pack/NIST_E_DELTA_CV_BOOTSTRAP_MULTIMAPPING.md`
- `artifacts/public_validation_pack/NIST_MAPPING_POLICY_CHECK.md`
- `artifacts/public_validation_pack/MAPPING_POLICY_2D.md`
