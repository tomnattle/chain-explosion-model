# Zenodo Metadata: Ripple Reality Audit (v6+v7+v8)
# Zenodo 元数据：Ripple Reality 审计（v6+v7+v8）

## Title / 标题
[EN] Ripple Reality: A Rigid Parametric Unification Audit from Bell-Style Statistics to Compton-Style Shift (v6+v7+v8)
[中] Ripple Reality：从 Bell 样式统计到 Compton 样式位移的刚性参数统一审计（v6+v7+v8）

## Authors / 作者
- wang, hui

## Description / 描述
[EN]
This deposit reports a merged v6+v7+v8 audit under one locked parameter triplet `(mu, rho, eta)=(1.5495, 2.35, 0.08)`.

- v6 layer: four-benchmark baseline joint consistency (laser threshold, semiconductor cutoff, MRI Larmor, atomic-clock modes).
- v7 layer: three-benchmark consistency (double-slit, tunneling, spin-cos2), rigidity scans (`27/27` local, `18/20` random-global), counterfactual expected-fail suite, and 7-seed stability.
- v8 layer: radial levels, decoherence, and Compton-style shift at the same locked point, plus anti-cheat closure (eta counterfactual fail, negative controls fail, multi-round hardening `100/100`).

The claim is methodological and reproducibility-centered: auditable model-class consistency under declared gates.
Not claimed: completed SI mapping, ontology uniqueness, or direct falsification of standard quantum mechanics.

Primary manuscript files:
- `papers_final/04_Ripple_Rigidity_Audit/version_01/【0】_Ripple_Rigidity_Audit/files/07_Manuscript_Merged_v7_v8_Bilingual.md`
- `papers_final/04_Ripple_Rigidity_Audit/version_01/【0】_Ripple_Rigidity_Audit/files/08_Manuscript_Merged_v7_v8_Bilingual.html`

[中]
本归档给出 v6+v7+v8 合并审计，在单一锁定参数三元组 `(mu, rho, eta)=(1.5495, 2.35, 0.08)` 下完成证据闭环。

- v6 层：四项基线联合一致性（激光阈值、半导体截止、MRI Larmor、原子钟模态）。
- v7 层：三项基准（双缝、隧穿、自旋 cos2）联合一致性，刚性扫描（局部 `27/27`、全局随机 `18/20`）、反事实按预期失败、7 种子稳定性。
- v8 层：同锁定点下的径向能级、退相干、类 Compton 位移，并带反作弊闭环（eta 反事实失败、负对照失败、多轮加固 `100/100`）。

本文主张属于方法学与可复现性主张：在声明门槛下具备可审计一致性。
本文不主张：SI 映射已完成、唯一本体论成立、或可据此直接否定标准量子力学。

主要稿件文件：
- `papers_final/04_Ripple_Rigidity_Audit/version_01/【0】_Ripple_Rigidity_Audit/files/07_Manuscript_Merged_v7_v8_Bilingual.md`
- `papers_final/04_Ripple_Rigidity_Audit/version_01/【0】_Ripple_Rigidity_Audit/files/08_Manuscript_Merged_v7_v8_Bilingual.html`

## Reproducibility / 可复现
Run from repository root:

`python scripts/explore/ripple_quantum_tests/generate_v7_paper_figures.py`

`python scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v6_joint.py`

`python scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v8_unify.py --rounds 100 --eta-probe 0.001`

`python scripts/explore/ripple_quantum_tests/generate_v8_paper_figures.py`

`python scripts/explore/ripple_quantum_tests/build_merged_v7_v8_html.py`

## Keywords / 关键词
- Ripple medium model / 涟漪介质模型
- Joint consistency / 联合一致性
- Parameter rigidity / 参数刚性
- Anti-cheat audit / 反作弊审计
- Counterfactual controls / 反事实对照
- Reproducibility / 可复现性

## License note / 许可说明
- Software code: AGPL-3.0-or-later (`LICENSE`, `NOTICE`). Platform UI: search **GNU Affero** / **AGPL**; prefer **GNU Affero General Public License v3.0 or later** if listed. See `docs/HOW_TO_SELECT_AGPL.md`.
- Narrative docs/manuscripts: CC BY-NC-ND 4.0 (`LICENSE-DOCS.md`, SPDX `CC-BY-NC-ND-4.0`). Zenodo/GitHub often **do not** match the string `CC BY-NC-ND 4.0` or `LICENSE-DOCS.md` in search — browse **Creative Commons** and pick **Attribution-NonCommercial-NoDerivatives 4.0 International** (keywords: **NonCommercial**, **NoDerivatives**, **4.0**). Details: `docs/HOW_TO_SELECT_AGPL.md` (CC section).

