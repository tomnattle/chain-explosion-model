# 冻结版打包（2026-04-25）

用途：固定本轮 Bell 外发候选稿与关键证据，后续仅在“新反馈/新数据”触发下开新版本，不在本版本上滚动改写。

## 版本标识

- Freeze ID: `bell-freeze-2026-04-25`
- 范围：Bell 主稿、摘要、关键结果表、bootstrap 证据、NCC 桥接证据、外发邮件包
- 状态：`READY_TO_SEND`

## 冻结资产清单

1. `papers/bell-audit-paper/draft.en.md`
2. `papers/bell-audit-paper/draft.zh.md`
3. `papers/bell-audit-paper/ABSTRACT_FINAL.en.md`
4. `papers/bell-audit-paper/ABSTRACT_FINAL.zh.md`
5. `papers/bell-audit-paper/tables/table2_key_results.md`
6. `papers/READY_FOR_REVIEW.md`
7. `artifacts/reports/chsh_bootstrap_ci_standard15.json`
8. `artifacts/reports/chsh_bootstrap_ci_strict0.json`
9. `artifacts/reports/ncc_singles_bridge_real.json`
10. `artifacts/reports/ncc_singles_bridge_real.png`
11. `artifacts/reports/cnorm_e_delta_bridge_real.md`
12. `artifacts/reports/cnorm_e_delta_bridge_real.png`
13. `papers/open-review/outreach_quantum_pack/EMAILS_TOP3_QUANTUM_LEADS.en.md`
14. `papers/open-review/outreach_quantum_pack/SEND_CHECKLIST_FINAL.zh.md`

## 本版关键结论（冻结口径）

- 同一 NIST completeblind 事件流，二值 CHSH：
  - strict window `0.0`: `S=2.336276`
  - standard window `15.0`: `S=2.839387`
  - 差值 `Delta=+0.503111`（分析规则敏感性证据）
- Bootstrap (`n=2000`)：
  - strict CI95: `[2.295151, 2.378669]`
  - standard CI95: `[2.820420, 2.857413]`
- `2sqrt(2)=2.828427` 落在 standard CI95 内：**不主张 Tsirelson violation**

## 复现命令（冻结版）

```powershell
./scripts/explore/run_quantum_outreach_preflight.ps1 `
  -Hdf5Path "data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5"

python "scripts/explore/bootstrap_chsh_ci.py" `
  --events-csv "data/nist_completeblind_side_streams.csv" `
  --window 15.0 --n-boot 2000 --seed 42 `
  --out-json "artifacts/reports/chsh_bootstrap_ci_standard15.json"

python "scripts/explore/bootstrap_chsh_ci.py" `
  --events-csv "data/nist_completeblind_side_streams.csv" `
  --window 0.0 --n-boot 2000 --seed 42 `
  --out-json "artifacts/reports/chsh_bootstrap_ci_strict0.json"
```

## 完整性校验

- SHA256 列表见：`papers/open-review/FREEZE_PACKAGE_2026-04-25.sha256`
- 校验脚本：

```powershell
Get-Content "papers/open-review/FREEZE_PACKAGE_2026-04-25.sha256"
```

## 冻结规则

- 不在本批文件上做“无反馈驱动”的改写；
- 若收到外部技术反馈，开新版本：`bell-freeze-YYYY-MM-DD-rN`；
- 任何新版本都必须：
  - 保留本版结论与边界句；
  - 明确列出改动点与新增证据。
