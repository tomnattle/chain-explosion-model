# Zenodo Metadata: Bell Audit v5 (Professional CN)

## Title / 标题

[EN] Bell Audit v5: How Binarization and Pairing Semantics Shape CHSH Headlines  
[中] Bell 审计 v5：二值化与配对语义如何塑造 CHSH 头条数值

## Authors / 作者

- wang, hui

## Description / 描述

[EN]
This deposit provides a professional Bell audit rewrite based on the Apr-29 v4 evidence package and is designed for reviewer-level traceability.

Key quantitative findings on a fixed event stream:

- Binarization shift: `S_raw(continuous) = 1.117683` vs `S_raw(quant_2) = 2.297779`.
- Semantic premium staircase: `same_index = 2.329417`, `external_bucket_all = 2.775687` (`+0.446270`), `event_anchor_nearest = 2.834670` (`+0.058983`).
- Closure checks: `same_index_not_near_2p82 = True`, `pure_bucket_in_2p8_zone = True`, `anchor_asymmetry_small = True` (`delta_abs = 0.001356`), `edge_sensitivity_bounded = True`.

Experimental principle and method:

- Principle: CHSH headline values can be altered by representation and inclusion rules even when the underlying row/event stream is unchanged.
- Method chain: same data -> quantization choice -> pairing semantics -> denominator inclusion policy -> CHSH report.
- Scope: methodological reproducibility and protocol sensitivity audit.
- Not claimed: ontology-final conclusion or direct falsification of all competing theories.

Primary manuscripts:

- `papers_final/05_Bell_Audit/version_01/【0】_Bell_Audit/files/01_Bell_Audit_Professional_CN.md`
- `papers_final/05_Bell_Audit/version_01/【0】_Bell_Audit/files/02_Bell_Audit_Professional_EN.md`

[中]
本归档基于 4 月 29 日 v4 证据包，提供 Bell 审计专业重写稿，目标是让审稿人可直接追踪数字、方法与边界。

核心量化结果（固定事件流）：

- 二值化跃迁：`S_raw(continuous) = 1.117683`，`S_raw(quant_2) = 2.297779`。
- 语义溢价阶梯：`same_index = 2.329417`，`external_bucket_all = 2.775687`（`+0.446270`），`event_anchor_nearest = 2.834670`（`+0.058983`）。
- 闭环检查：`same_index_not_near_2p82 = True`、`pure_bucket_in_2p8_zone = True`、`anchor_asymmetry_small = True`（`delta_abs = 0.001356`）、`edge_sensitivity_bounded = True`。

实验原理与方法：

- 原理：在底层事件不变时，表示层与纳入规则可显著改变 CHSH 头条值。
- 方法链：同一数据 -> 量化策略 -> 配对语义 -> 分母纳入策略 -> CHSH 报告值。
- 主张范围：方法学可复现性与协议敏感性审计。
- 非主张范围：本体层终局结论，或对全部竞争理论的一步到位否定。

主稿文件：

- `papers_final/05_Bell_Audit/version_01/【0】_Bell_Audit/files/01_Bell_Audit_Professional_CN.md`
- `papers_final/05_Bell_Audit/version_01/【0】_Bell_Audit/files/02_Bell_Audit_Professional_EN.md`

## Reproducibility / 可复现

Run from repository root:

`python scripts/explore/nist_same_index_quantization_sweep_v4.py`

`python scripts/explore/nist_unified_semantics_audit_v4.py`

`python scripts/explore/nist_revival_20pct_closure_v4.py`

## Keywords / 关键词

- Bell audit
- CHSH
- Binarization sensitivity
- Pairing semantics
- Denominator transparency
- Reproducibility

## License note / 许可说明

- Software code: AGPL-3.0-or-later (`LICENSE`, `NOTICE`).
- Narrative docs/manuscripts: CC BY-NC-ND 4.0 (`LICENSE-DOCS.md`).

