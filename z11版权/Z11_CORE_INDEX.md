# Z11 核心证据总表（A组）

> 用途：提交时给审查员的一页式主证据索引。  
> 规则：每项必须包含「对应章节 / 文件路径 / 证据作用 / 对应结论」。

| 编号 | 对应章节 | 文件路径 | 证据作用 | 对应结论 |
|---|---|---|---|---|
| A01 | 0-总纲 | `z11版权/版权申请总纲_合并版.md` | 统一提交口径与边界总控 | 证明项目具备完整、可审计、可提交的结构化表达 |
| A02 | 0D-AI协作 | `z11版权/人工智能协作原创性声明.md` | 人机协作原创性与权属边界声明 | 证明“人设逻辑、机做验证”模式下作者主导成立 |
| A03 | 0C-动机附录 | `z11版权/认知基础附录-V1.0.md` | 记录认知来源与问题意识演化 | 证明模型动机链条清晰，且边界声明完备 |
| A04 | 2-Bell审计 | `scripts/explore/explore_ncc_singles_coincidence_bridge.py` | 关联算子与 singles/coincidences 映射重算 | 证明 Bell 节点可执行“阿喀琉斯之踵”补强审计 |
| A05 | 5-三元组推断 | `scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v6_joint.py` | 三元组联合求解核心脚本 | 证明 `mu/rho/eta` 由算法求得而非手工填写 |
| A06 | 5-全频域通透性 | `scripts/explore/ripple_quantum_tests/ripple_triplet_fullband_transparency_audit.py` | 玻璃参考 vs 涟漪介质全频域审计 | 证明“可通过”升级为“可辨识、可复核” |
| A07 | 6-热力学自洽 | `scripts/explore/ripple_quantum_tests/ripple_thermal_triplet_preregistered_audit.py` | 预注册+反事实+消融审计 | 证明三元组在热力学场景模型内自洽 |
| A08 | 8-可辨识性审计 | `scripts/explore/ripple_quantum_tests/ripple_v6_identifiability_audit.py` | expected-fail 与可辨识性校验 | 证明该失败时确实失败 |
| A09 | 8-身份区分 | `artifacts/ripple_v6_identifiability_audit_expanded/RIPPLE_V6_IDENTIFIABILITY_AUDIT_SUMMARY.md` | 可辨识性扩展审计摘要 | 证明介质身份区分有量化证据 |
| A10 | 5/8-基础审计摘要 | `artifacts/ripple_v6_identifiability_audit/RIPPLE_V6_IDENTIFIABILITY_AUDIT_SUMMARY.md` | 基础组审计摘要 | 证明基础口径与扩展口径一致 |
| A11 | 3-GHZ流程验证 | `scripts/explore/ghz_threshold/explore_ghz_threshold_pipeline.py` | GHZ门槛流程验证核心脚本 | 证明 GHZ 多条件验证链路可执行可复验 |
| A12 | 3-GHZ结果归档 | `artifacts/ghz_threshold_experiment/GHZ_THRESHOLD_SUMMARY.md` | GHZ 阈值实验摘要报告 | 证明 GHZ 审计结论有归档证据 |
| A13 | 4-光学场景扩展 | `artifacts/ripple_quantum_tests_v8_unify/RIPPLE_V8_UNIFY_SUMMARY.md` | 光学/多场景统一摘要 | 证明光学场景适配与统一口径 |
| A14 | 9-公共验证归档 | `artifacts/public_validation_pack/PUBLIC_DATA_VALIDATION_SUMMARY.md` | 公共数据验证摘要 | 证明跨数据源口径与流程一致性 |
| A15 | 2-Bell窗口协议 | `scripts/explore/bell_honest_window_scan_v1.py` | Bell 窗口审计专用脚本 | 证明时间窗口审计具备独立实现 |
| A16 | 2-数据准备链路 | `prepare_nist_bell_data.py` | NIST Bell 数据准备脚本 | 证明原始数据进入审计链条的前处理可复现 |

## 备注

- 建议每个 A 项在最终提交包中补充 1 条“运行命令”与 1 条“输出路径”。
- 本次提交文件集合以 `z11版权/提交版目录锁定页.md` 为最终准据。
