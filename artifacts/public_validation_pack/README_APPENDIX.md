# Public Validation Pack Appendix

本附录用于补充 `index.html`，聚焦 NIST `E(Delta)` 三线对照结果与方法边界。

## 快速入口

- 附录页面：`artifacts/public_validation_pack/nist_e_delta_appendix.html`
- 主图（图5）：`artifacts/public_validation_pack/fig5_nist_e_delta_three_tracks.png`
- 主结果摘要：`artifacts/public_validation_pack/NIST_E_DELTA_THREE_TRACKS_SUMMARY.md`
- 映射敏感性：`artifacts/public_validation_pack/NIST_E_DELTA_MAPPING_SENSITIVITY.md`
- 严谨性补齐报告：`artifacts/public_validation_pack/NIST_E_DELTA_RIGOR_REPORT.md`

## 对外可引用结论（当前主映射）

在 `slot 0..7 => +1, slot 8..15 => -1` 的映射定义下，NIST completeblind 实测点对三条参考曲线的贴合度为：

- Bell 二值化折线 RMSE: `0.929737`
- 连续原始矮余弦 RMSE: `0.200994`
- 连续归一化高余弦 RMSE: `0.213850`

据此，实测点明显更贴近余弦轨道（尤其是连续原始矮余弦），而非 Bell 折线。

## 方法边界（必须一并声明）

- 该结论依赖 `slot -> ±1` 映射定义；映射变化会影响定量结果。
- 敏感性结果已在 `NIST_E_DELTA_MAPPING_SENSITIVITY.md` 展示。
- 对外陈述时建议使用“在当前映射定义下”这一定语，避免过度外推。

## 复现命令

```bash
python scripts/explore/explore_nist_e_delta_three_tracks.py
python scripts/explore/explore_nist_e_delta_mapping_sensitivity.py
python scripts/explore/explore_nist_e_delta_rigor_pack.py
```
