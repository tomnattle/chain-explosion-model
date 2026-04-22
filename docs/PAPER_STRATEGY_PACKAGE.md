# Paper Strategy Package (Low-Rejection Track)

## 1) 投稿定位（不要偏）

本工作定位为**方法与可复现审计工具**，不是基础物理“推翻结论”论文。

- 目标命题：`结论风险控制`、`统计对象一致性审计`、`可复现分析流程`
- 非目标命题：`推翻 Bell`、`否定非局域`、`替代量子理论`

---

## 2) 标题候选（按稳健度排序）

1. **Auditing Metric-Object Consistency in Bell-Style Correlation Claims: A Reproducible Risk Pipeline**
2. **Claim Risk Auditing for Bell-Style Analyses: Reproducible Detection of Metric Mismatch**
3. **When the Same Data Yield Different S Values: A Practical Audit Framework for Metric Consistency**

---

## 3) 摘要（可直接用）

We present a reproducible claim-risk auditing pipeline for Bell-style correlation analyses, focusing on metric-object consistency rather than foundational interpretation. Using identical hidden-variable samples, we compare three correlation definitions frequently conflated in informal discussions: dichotomic CHSH-compatible correlation, continuous raw correlation, and normalized continuous correlation. The resulting S-value ranges differ systematically across definitions, demonstrating that claim validity depends critically on the metric-object mapping and reporting protocol.

To operationalize this issue, we implement a command-line auditor that outputs structured JSON/CSV/Markdown/HTML reports, computes risk scores, flags mismatch patterns, and supports CI-style fail thresholds for publication workflows. The tool also supports external result ingestion (JSON/CSV) and batch auditing for multi-claim review.

Our contribution is methodological: we provide an auditable, repeatable workflow for detecting overreach and object mismatch in correlation claims. We do not claim to refute existing physical theories; instead, we show that metric inconsistency alone can materially alter reported conclusions and therefore must be audited before interpretation.

---

## 4) 贡献点（投稿版）

1. **方法贡献**：提出 Bell 风格结论的指标一致性审计框架（metric-object consistency audit）。
2. **工程贡献**：实现可复现 CLI 工具链，支持单次、外部输入、批量审计与 CI 门禁。
3. **报告贡献**：统一输出 JSON/CSV/Markdown/HTML，便于审稿与组织流程接入。
4. **实证贡献**：在同一样本上并列比较三类指标，量化其 S 值分歧与风险触发模式。

---

## 5) 非主张声明（必须保留）

建议原文固定放置如下声明（可复制）：

> This work does not claim to falsify Bell’s theorem, deny nonlocality, or replace quantum theory.  
> Our scope is methodological: we audit whether a reported conclusion is consistent with the statistical object actually computed.

---

## 6) 审稿风险与应对

### 风险 A：被当作“基础物理推翻稿”
- **应对**：标题、摘要、结论全部改为“audit / consistency / reproducibility”语言。

### 风险 B：被质疑“只是模拟玩具”
- **应对**：增加外部公开数据再分析案例（至少 1 个），并附复现实验脚本。

### 风险 C：被质疑“混合对象比较”
- **应对**：单列 `E_binary / E_raw / E_ncc` 数学定义与适用范围，禁止混写符号 `E`。

### 风险 D：缺少负例与失败披露
- **应对**：保留 `fail-on-risk-threshold` 触发结果，展示工具如何拦截不稳健结论。

---

## 7) 两周补强清单（最小可投稿版）

### Week 1
- [ ] 增加外部数据输入案例（公开 Bell 风格结果 CSV/JSON）
- [ ] 生成三类基线：一致、错配、随机
- [ ] 输出误差/稳定性表（多 seed、多 trials）

### Week 2
- [ ] 增加“威胁与边界”章节
- [ ] 固化可复现实验脚本（单命令）
- [ ] 完成主文稿 + 附录 + 代码链接

---

## 8) 论文结构（建议）

1. Introduction  
2. Problem Definition: Metric-Object Consistency  
3. Audit Method and Risk Rules  
4. Implementation (CLI + Report Formats + CI Gate)  
5. Experiments (same-sample comparison + external case)  
6. Threats to Validity and Scope Limits  
7. Conclusion (methodological impact)

---

## 9) 当前仓库对应材料

- 核心审计工具：`scripts/explore/claim_audit.py`
- 对比实验：`scripts/explore/explore_bell_metric_comparison.py`
- 工具文档：`docs/CLAIM_AUDIT_TOOL.md`
- 最新结果说明：`docs/LATEST_RESULTS_METRIC_COMPARISON.md`

