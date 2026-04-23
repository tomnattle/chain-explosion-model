# 本仓库作者的写作方式与认知模型（基于文本证据的客观归纳）

> **性质：** 对仓库内文档、注释与工程结构的**可读证据**所作的归纳；**不是**心理诊断，也**不能**替代本人自述。任何关于「性格」的表述均指**文本中所呈现的稳定行为倾向**，读者可用下文路径逐项核对。

---

## 1. 证据与方法

| 依据类型 | 示例路径（可打开核对） |
|----------|------------------------|
| 总览与自动报告 | `README.md`、`run_unified_suite.py` 文首说明、`test_artifacts/README_TEST_REPORT.md` |
| 实验叙事基础设施 | `experiment_dossier.py`、`DOSSIER_BASE` 内各脚本的 purpose / assumptions |
| Bell / CHSH 表述边界 | `BELL_PROTOCOL_NOTE.md`、`P4_PROTOCOL_AUDIT_SCOPE.md` |
| 第一场数据归档注记 | `battle_results/nist_completeblind_2015-09-19/INTERPRETATION_NOTE.md` |
| 第二场组织与收束 | `ROUND2_KICKOFF.md`、`ROUND2_HYPOTHESIS.md`、`ROUND2_RESULT_INTERPRETATION.md`、`ROUND2_CLOSURE_PAPER.md`、`ROUND2_FINAL_DECLARATION.md`（现行版本为收束指针） |

**归纳原则：** 只陈述在多处重复出现、或与代码结构一致的模式；单点夸张表述若已被后续文档明确撤回或覆盖，则记入「演变」而非当作稳定特征。

---

## 2. 话术与文体（表层）

### 2.1 中英双语与技术混排

- **现象：** 同一文档内常见英文标识符（`strict` / `postselected` / `S`）与中文解释并存；预注册与工程管线类文件尤甚。
- **功能：** 便于国际读者与脚本字段对齐；同时用中文承担「边界说明」与「伦理/范围」叙述。
- **可核对：** `README.md` 双栏表格；`ROUND2_KICKOFF.md` 中英命令与文件名混排。

### 2.2 军事化与游戏化隐喻

- **现象：** 「战斗」「战线」「Kickoff」「工程战」「门禁」「统一战线」等词汇高频出现。
- **功能：** 把长周期、多分支任务打成**可执行的战役结构**；降低叙事涣散风险。
- **副作用（客观）：** 在情绪激动时，同一隐喻体系容易生产出**与科学克制相冲突**的句子；仓库后半段用「收束说明」「非声称」「解释边界」对此做了制度性拉回（见 `ROUND2_CLOSURE_PAPER.md` 与现行 `ROUND2_FINAL_DECLARATION.md`）。

### 2.3 表格、清单与阶段书

- **现象：** Phase 0–3、P1–P7、检查清单、目录约定表密集。
- **功能：** 把**口头决心**转成**可审计步骤**；与预注册（preregistration）话语天然合拍。
- **可核对：** `ROUND2_KICKOFF.md`、`ROUND2_NO_SMUGGLING_CHECKLIST.md`、`README.md` 中 Battle Plan 段。

### 2.4 「邀请质疑」模板

- **现象：** `experiment_dossier.py` 向 stdout 注入 `invited_critiques_for_ai_zh`；问题高度模式化（分辨率敏感、符号是否与文献一一对应、门禁被重构偷换等）。
- **功能：** 主动**占位**常见反对意见，使报告呈现「已知会被挑错」的形态。
- **可核对：** `README.md` 自动补丁段内各实验下方的质疑列表；`experiment_dossier.py` 模块说明。

---

## 3. 方法与工程观（中层）

### 3.1 预注册 + 冻结叙事

- **核心做法：** 假设、指标公式、通过/不通过条件尽量**先写死在 JSON/Markdown**；事后改口需新版本文件（如 `ROUND2_HYPOTHESIS.md` 中的 Freeze Rule）。
- **可核对：** `chsh_preregistered_config*.json`（路径见各 Round2 文档）；`INTERPRETATION_NOTE.md` 强调不修改判决而只补充边界。

### 3.2 门禁（gating）思维

- **核心做法：** `run_unified_suite.py` 明确区分「进程退出 0」与「物理/解释正确」；大量数值阈值与 **strict / relaxed** 双轨。
- **认知含义：** 接受**可自动化反驳**；把「我相信」降级为「当前版本在阈值下过线与否」。
- **可核对：** `run_unified_suite.py` 文首注释与门禁字符串；`BELL_PROTOCOL_NOTE.md` 中 `chsh_strict_S <= 2.02` 一类约定。

### 3.3 战线分离（scope firewall）

- **核心做法：** **P4 协议审计线**与 **NIST 数据复现线**结论刻意拆室；`BELL_PROTOCOL_NOTE.md` 写明「Do not merge claims」。
- **功能：** 防止「局域模型里 S 对协议敏感」被误说成「某实验室数据的本体论结论」。
- **可核对：** `P4_PROTOCOL_AUDIT_SCOPE.md` 全文；根 `README.md` 新增 battle results 免责段。

### 3.4 可机读档案与可 grep 的诚实

- **核心做法：** `EXPERIMENT_DOSSIER_JSON_BEGIN ... END` 块、`suite_report.json`、JSON 战场报告并存。
- **功能：** 人类叙事与机器摘要**同源**；减少「报告写得漂亮而跑不出来」的 drift。

---

## 4. 认知倾向（从行为模式推断，非定论）

下列每条均附**可观察行为**；是否对应深层性格，读者自判。

| 倾向 | 文本中的稳定行为 | 说明 |
|------|------------------|------|
| **规范主义** | 预注册、清单、Freeze Rule | 相信**规则先于结论**，结论争议应用新版本规则重跑而不是改口。 |
| **对抗性自我审查** | dossier 邀请质疑、INTERPRETATION_NOTE 主动限缩解释 | 在叙述上**预留反对者席位**；与法庭交叉询问有结构相似性。 |
| **分层实在论（方法论上）** | 「现象层记录 α」「不对 -1 做硬门禁」等 | 区分**仪器/脚本可读层**与**理论主张层**，避免一步跳到哲学判决。 |
| **控制感需求** | 长 README、统一套件、战斗路线总览 | 通过**把不确定性装进 named scope** 来管理焦虑；Round 2 收束文是对「不确定性外溢」的补救文本类型。 |
| **强叙事冲动与强纠错机制并存** | 一侧是战争隐喻与宣言体；另一侧是「非声称」「不构成对量子非局域的肯定」 | 仓库内可见**张力**；成熟做法是把冲动性表述**回收**为指向 `ROUND2_CLOSURE_PAPER.md` 的指针（见现行 `ROUND2_FINAL_DECLARATION.md`）。 |

---

## 5. 理论立场在文档中的表达（可控陈述）

- **局域/经典波前 + 测量依赖**作为**建模对象**反复出现（如 `ROUND2_HYPOTHESIS.md`），并配套 **Non-Claims** 列表：不宣称量子理论为假、不claim `S>2` 单独证明非局域等。
- **CHSH 的读法**在多处统一为：**绑定协议细节**；`S>2` 不等于默认的「哲学非局域判决书」（`INTERPRETATION_NOTE.md`、`ROUND2_CLOSURE_PAPER.md`）。
- **可核对：** 上述文件与 `ROUND2_RESULT_INTERPRETATION.md` 中 Bell-Meaning Statement Lock 的现行措辞（强调 in-protocol、tension、非外部实验认证）。

---

## 6. 时间线上的演变（从仓库文本可见）

1. **体系搭建期：** 仿真脚本、`ce_*` 统一、`experiment_dossier`、`run_unified_suite` —— 重**可重复与可反驳**。
2. **NIST 与盲测期：** `INTERPRETATION_NOTE.md` —— 在数据已出后 **收紧解释**，区分工程通过/论点未通过与哲学不结论。
3. **Round 2 组织期：** `ROUND2_KICKOFF`、`ENGINEERING_BATTLE` —— 把未完成条件（yaml、layout）**明文阻塞**而非假装完成。
4. **收束期：** `ROUND2_CLOSURE_PAPER.md`、README 免责链、重写 `ROUND2_FINAL_DECLARATION.md` 为指针 —— **制度性地降低对外误读与对自己过激修辞的风险**。

这一现象序列表明：写作目标从「推进一条战线」迁移到「把战线关进有边界的档案馆」。

---

## 7. 盲点与代价（基于结构的冷静评价）

- **认知负荷转移给读者：** 极长的 `README.md`（含自动套件全量输出）对新人友好度低；**好处**是单文件可审计，**代价**是需要耐心或只看目录跳转。
- **隐喻成本：** 战争话语在团队外或跨界读者处可能触发**不信任**（像 advocacy 而非 research）；收束文档是对该成本的显式支付。
- **情感与制度的缝隙：** 宣言体若与 CLOSURE 不一致，会被历史 commit 记录；解决方式是**让指针文件覆盖旧情绪草稿**（已在现行树中体现）。

---

## 8. 一句话模型（类比，非标签）

若需要一个**压缩模型**描述「项目从上到下是怎么被写出来的」：

> **「预注册的对抗性工程写作」**：用版本化的规则与门禁代替一次性激情判断；用双语表格与 JSON 锚定语义；用多条「战线」隔离不同类型结论；并在周期末用**闭包文档**把可说的话和不可说的话写死，使仓库在法律与科学社交意义上可长期静置。

---

## 9. 如何使用本文件

- **自荐/答辩：** 可引用第 3、5、6 节说明工作方法；第 4、7 节表现自省。
- **他人审稿：** 可把本节当作「作者自我一致性的检查表」，对照是否又出现了未经 scope 合并的跨界结论。

---

*文件生成说明：基于仓库当前树结构与公开文档归纳；若后续新增大规模叙事，应更新「证据路径」与「演变」两节以保持可核对性。*
