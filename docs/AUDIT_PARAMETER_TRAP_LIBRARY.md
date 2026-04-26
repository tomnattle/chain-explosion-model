# 审计用参数陷阱库（v8，与锁定脚本一致）

**目的**：在**已冻结的 v8 脚本与门槛**下，公开一组“看起来仍像同一量级、但联合不通过”的三元组 \((\mu,\rho,\eta)\)，用于独立复现时的**对照表**。  
**非目的**：这不是法律意义上的“抄袭检测器”；不能单凭参数命中某一行推断来源。

**真值（canonical / 锁定通过点）**

| \(\mu\) | \(\rho\) | \(\eta\) | v8 `joint_pass` |
|--------:|---------:|---------:|:----------------|
| 1.5495 | 2.35 | 0.08 | `True` |

**机读归档**：`artifacts/ripple_quantum_tests_v8_unify/PARAMETER_TRAP_LIBRARY.json`  
（含各子项 `nrmse_y`、`R2`、`shape_ok`。）

**示例陷阱行（摘要）**

| id | \(\mu\) | \(\rho\) | \(\eta\) | 典型失败分支 |
|----|--------:|---------:|---------:|--------------|
| `trap_eta_0_03` | 1.5495 | 2.35 | 0.03 | `compton_shift` |
| `trap_eta_0_13` | 1.5495 | 2.35 | 0.13 | `compton_shift` |
| `trap_rho_3_35_eta_lock` | 1.5495 | 3.35 | 0.08 | `decoherence` |
| `trap_rho_1_35_eta_lock` | 1.5495 | 1.35 | 0.08 | `decoherence` |
| `trap_rho_2_85_eta_0_03` | 1.5495 | 2.85 | 0.03 | `decoherence`, `compton_shift` |
| `trap_swap_mu_rho` | 2.35 | 1.5495 | 0.08 | `compton_shift` |
| `trap_eta_probe_0_001` | 1.5495 | 2.35 | 0.001 | `compton_shift`（审计反事实探针） |

**复现命令**（与合并稿一致）：

`python scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v8_unify.py --rounds 100 --eta-probe 0.001`

**边界**：若他人修改模型方程、网格、参考曲线或门槛，本表**不再自动有效**；须重新生成陷阱库并改版本号。
