# Z11 版本与哈希清单

> 用途：提交版冻结与完整性校验。  
> 生成时间：2026-04-29（本地）  
> 建议冻结标签：`z11-submit-v1`

## 一、仓库版本

- Git HEAD: `ceaccf17d907751eb20b65eaddb1da127646d65c`

## 二、A组主证据 SHA256（A01-A16）

| 文件路径 | SHA256 |
|---|---|
| `z11版权/版权申请总纲_合并版.md` | `978940201ce7ae907a38848607035e661fa8a28d058814e4d418b98e886bbbad` |
| `z11版权/人工智能协作原创性声明.md` | `b689382dd2e556f8dea23b9b6360d7a979d3a2b1a30aa296e81c4d47ae6c8ff2` |
| `z11版权/认知基础附录-V1.0.md` | `11ee7929b950e65359b3219c4cc4bd6c7805bc43da35b6226d1605c289234fb8` |
| `scripts/explore/explore_ncc_singles_coincidence_bridge.py` | `498947f523cccca24064ce9fa10e989e6e599479a42b298f8ceb3e3f8ec09a00` |
| `scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v6_joint.py` | `27ac23eb7028e0cf003f68528b7b0d720ac346ad825e39236be8b81af4d7871d` |
| `scripts/explore/ripple_quantum_tests/ripple_triplet_fullband_transparency_audit.py` | `9d5ca2c6fb8f9759eabeeeb06ea7253967db800da6eb861b26d9c679872180e6` |
| `scripts/explore/ripple_quantum_tests/ripple_thermal_triplet_preregistered_audit.py` | `71a86d869f0a03c77e9361a0da1c92c7a6e03416e98cd650dfcb4b1ff0069682` |
| `scripts/explore/ripple_quantum_tests/ripple_v6_identifiability_audit.py` | `28ed22d4a51f7aed011353490e4aef9d71cb0b8f01211338861f46b918e9c224` |
| `artifacts/ripple_v6_identifiability_audit_expanded/RIPPLE_V6_IDENTIFIABILITY_AUDIT_SUMMARY.md` | `0ab0c9a5c017f043c32419fb7e8aa18ea00fec00a9a3030e970921f69af11d84` |
| `artifacts/ripple_v6_identifiability_audit/RIPPLE_V6_IDENTIFIABILITY_AUDIT_SUMMARY.md` | `bc19ca5f372e528abf47cf7a39da21e11faa934de1cc60d524ca1a9b407f7c02` |
| `scripts/explore/ghz_threshold/explore_ghz_threshold_pipeline.py` | `da044d73f217ebc9e4be1f7b982b5e99523af4c9870d32c7925e9e876f4f3147` |
| `artifacts/ghz_threshold_experiment/GHZ_THRESHOLD_SUMMARY.md` | `0e30e5b3d0fd988f6d692cc9c0f0a1cfe323c4624b0d7fdf3d517bdbde6f144d` |
| `artifacts/ripple_quantum_tests_v8_unify/RIPPLE_V8_UNIFY_SUMMARY.md` | `bccafdb9de411584140349c8808bcc65c526d3d7ddeff9f2cbb0ce713a19b564` |
| `artifacts/public_validation_pack/PUBLIC_DATA_VALIDATION_SUMMARY.md` | `10c16f32de3ed3ebb351cedfc83fc17451146387791277de8f1d903b98c8eb6e` |
| `scripts/explore/bell_honest_window_scan_v1.py` | `f38a9cee4188a283c8779fdce84987cf0565e0abd552d7eafe3b5c8a99d13081` |
| `prepare_nist_bell_data.py` | `7b7b49a8fad01fba721965a25eb2c5ce2f7fc7022dfa5dbea4dcd11473d63ff8` |

## 三、建议补充（提交前）

- 若新增/替换 A 组文件，需同步更新本表并标注更新时间。
- 若更新文档或脚本，需重新计算对应哈希并同步本清单。
- 在提交说明中写入“本次提交对应 HEAD + HASH 清单版本”。

## 四、复算命令（Windows）

```powershell
git rev-parse HEAD
certutil -hashfile "z11版权\版权申请总纲_合并版.md" SHA256
certutil -hashfile "z11版权\人工智能协作原创性声明.md" SHA256
certutil -hashfile "z11版权\认知基础附录-V1.0.md" SHA256
```
