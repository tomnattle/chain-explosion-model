# Paper A Results Snippet (Δ Closure, Bilingual)

## 中文版（可直接粘贴到结果节）

在预注册 `Δ` 映射（`half_split`）与公开脚本下，我们对 NIST 数据的 `E(Δ)` 进行了定义闭合与统计严谨性检查。结果显示，`LowCos` 对实测点的拟合误差显著低于 Bell 折线基线：`wRMSE(Bell)=0.058318`，`wRMSE(LowCos)=0.014459`，`wRMSE(HighCos)=0.016552`。Bootstrap 给出 `wRMSE(LowCos)-wRMSE(Bell)` 的 95% CI 为 `[-0.049243, -0.036555]`，且 `P(wRMSE(LowCos) < wRMSE(Bell)) = 1.000000`。9-bin exact paired-swap 置换检验结果为单侧 `p=0.0117188`（双侧 `p=0.0234375`）。

闭合草判（自动汇总）为：Definition=`PASS`，Dimensional=`PASS`，Process=`PASS`，Statistical=`PASS`。上述结论限定在当前映射定义与样本处理流程下成立，不外推为对理论本体的裁决；其中 `slot->±1` 映射仍属于显式假设，应在讨论节保留边界声明。

### 结果表（中文）

| 项目 | 数值 |
|---|---:|
| 映射模式 | `half_split` |
| wRMSE(Bell) | 0.058318 |
| wRMSE(LowCos) | 0.014459 |
| wRMSE(HighCos) | 0.016552 |
| P(wRMSE(LowCos) < wRMSE(Bell)) | 1.000000 |
| permutation p(one-sided) | 0.0117188 |
| permutation p(two-sided) | 0.0234375 |

### 四闭合草判（中文）

| 闭合项 | 草判 |
|---|---|
| 定义闭合 | PASS |
| 量纲闭合 | PASS |
| 流程闭合 | PASS |
| 统计闭合 | PASS |

---

## English Version (Ready to Paste into Results)

Under a pre-registered `Δ` mapping (`half_split`) and open scripts, we evaluated NIST `E(Δ)` with closure and statistical-rigor checks. The empirical curve is better captured by `LowCos` than by the Bell polyline baseline: `wRMSE(Bell)=0.058318`, `wRMSE(LowCos)=0.014459`, and `wRMSE(HighCos)=0.016552`. Bootstrap yields a 95% CI of `[-0.049243, -0.036555]` for `wRMSE(LowCos)-wRMSE(Bell)`, with `P(wRMSE(LowCos) < wRMSE(Bell)) = 1.000000`. The 9-bin exact paired-swap permutation test gives one-sided `p=0.0117188` (two-sided `p=0.0234375`).

The automated draft closure status is Definition=`PASS`, Dimensional=`PASS`, Process=`PASS`, Statistical=`PASS`. These findings are restricted to the current mapping definition and preprocessing protocol and are not claimed as an ontological adjudication. The `slot->±1` assignment remains an explicit assumption and should be retained as a boundary statement in the Discussion section.

### Results Table (EN)

| Item | Value |
|---|---:|
| Mapping mode | `half_split` |
| wRMSE(Bell) | 0.058318 |
| wRMSE(LowCos) | 0.014459 |
| wRMSE(HighCos) | 0.016552 |
| P(wRMSE(LowCos) < wRMSE(Bell)) | 1.000000 |
| permutation p(one-sided) | 0.0117188 |
| permutation p(two-sided) | 0.0234375 |

### Four-Closure Draft (EN)

| Closure item | Draft status |
|---|---|
| Definition closure | PASS |
| Dimensional closure | PASS |
| Process closure | PASS |
| Statistical closure | PASS |

---

## 引用来源 / Source Files

- `artifacts/public_validation_pack/NIST_E_DELTA_RIGOR_REPORT.md`
- `artifacts/public_validation_pack/NIST_E_DELTA_VALIDATION_SANITY.md`
- `artifacts/public_validation_pack/DELTA_CLOSURE_SUMMARY.md`
