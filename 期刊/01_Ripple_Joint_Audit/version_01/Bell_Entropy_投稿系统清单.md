# Bell -> Entropy 投稿系统清单（可直接照填）

> 目标稿件：`papers/bell-deconstruction-paper-v3/BELL_DECONSTRUCTION_V3_FULL.md`  
> 投稿策略：先方法学审计，不碰“推翻量子力学”叙事。

---

## 1) 标题与摘要（系统字段）

- **Title（建议）**  
  `Denominator-Audit Robustness Analysis for Bell/CHSH Statistics: A Reconciliation Study of Strict vs Standard Protocols`

- **Running Title（可选）**  
  `Protocol Sensitivity Audit for Bell/CHSH`

- **Abstract（要点必须包含）**
  - 同一真实数据源（NIST completeblind）
  - strict 与 standard 并行比较
  - 核心数字：`2.336276 -> 2.839387`，`ΔS=+0.503111`
  - bootstrap 区间：`[2.295151,2.378669]` 与 `[2.820420,2.857413]`
  - 明确边界：不主张 Tsirelson violation，不做本体论裁决

---

## 2) 关键词（建议 5-7 个）

- Bell test
- CHSH
- protocol audit
- bootstrap confidence interval
- reproducibility
- NIST completeblind
- negative results

---

## 3) 学科分类（按 Entropy 常见风格）

- Statistical Physics / Complex Systems
- Information Theory in Physical Measurement
- Reproducibility and Methodology

---

## 4) 上传文件建议（按优先级）

必传：
- [ ] 主稿 PDF（Bell）
- [ ] 图表文件（主文引用图）
- [ ] 补充材料（方法细节、更多表格）

建议同时上传：
- [ ] 机器可读结果（JSON/CSV）
- [ ] 复现实验命令清单（README 或附录）
- [ ] 数据可用性声明（含 NIST 来源链接）

若系统支持“附加材料 DOI”：
- [ ] 填入 Zenodo 记录：`10.5281/zenodo.19784937`

---

## 5) Cover Letter 粘贴模板

- 使用文件：`期刊/01_Ripple_Joint_Audit/version_01/Bell_Entropy_首投投稿信.md`
- 提交前替换：
  - [ ] 通讯作者
  - [ ] 单位与邮箱
  - [ ] 仓库链接
  - [ ] 利益冲突声明

---

## 6) 必填声明（逐项核对）

- [ ] 非一稿多投
- [ ] 全体作者同意投稿
- [ ] 数据与代码可获得（或说明限制）
- [ ] 利益冲突已声明
- [ ] 伦理审批（如不涉及人体/动物，填写 Not applicable）

---

## 7) 审稿人可能首问 & 预设回答

1. **问：你这是不是在宣称“量子力学错了”？**  
   答：不是。本文是统计协议审计，结论限定为“协议定义显著影响 CHSH 报告值”。

2. **问：为什么会出现不同 S 值？**  
   答：同一事件流下，不同配对/分母定义导致统计量不同；本文通过并行 strict/standard 与 bootstrap 区间进行量化。

3. **问：是否声称超越 Tsirelson？**  
   答：不声称。标准流程下 `2√2` 落在 CI 内，论文明确保留边界与负结果。

4. **问：可复现吗？**  
   答：可复现。提供机器可读结果、命令和归档数据路径。

---

## 8) 提交后 7 天动作

- D+0：完成首投
- D+1：整理“审稿问答版”补充文档
- D+3：准备二投期刊适配包（FoP / EPJ Plus）
- D+7：根据编辑部回执决定是否改题/改摘要后转投

