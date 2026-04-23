# 本仓库作者的写作方式与认知模型
# Writing Style and Cognitive Model Reflected in This Repository

> **性质：** 对仓库内文档、注释与工程结构的可读证据所作的归纳；不是心理诊断，也不能替代本人自述。任何关于“性格”的表述均指文本中所呈现的稳定行为倾向，读者可用下文路径逐项核对。  
> **Nature:** This is an evidence-based synthesis drawn from readable traces in the repository’s documents, comments, and engineering structure. It is not a psychological diagnosis and cannot replace the author’s own self-description. Any statement about “personality” refers only to stable behavioral tendencies reflected in the writing and project structure, and can be checked against the paths listed below.

---

## 1. 证据与方法
## 1. Evidence and Method

| 依据类型 | 示例路径（可打开核对） |
|----------|------------------------|
| 总览与自动报告 | `README.md`、`run_unified_suite.py` 文首说明、`test_artifacts/README_TEST_REPORT.md` |
| 实验叙事基础设施 | `experiment_dossier.py`、`DOSSIER_BASE` 内各脚本的 purpose / assumptions |
| Bell / CHSH 表述边界 | `BELL_PROTOCOL_NOTE.md`、`battle_results/nist_round2_v2/P4_PROTOCOL_AUDIT_SCOPE.md` |
| 第一场数据归档注记 | `battle_results/nist_completeblind_2015-09-19/INTERPRETATION_NOTE.md` |
| 第二场组织与收束 | `ROUND2_KICKOFF.md`、`ROUND2_HYPOTHESIS.md`、`ROUND2_RESULT_INTERPRETATION.md`、`ROUND2_CLOSURE_PAPER.md`、`ROUND2_FINAL_DECLARATION.md` |

| Evidence Type | Example Paths |
|---------------|---------------|
| Overview and automated reporting | `README.md`, the opening notes of `run_unified_suite.py`, `test_artifacts/README_TEST_REPORT.md` |
| Experimental narrative infrastructure | `experiment_dossier.py`, and the purpose / assumptions fields inside `DOSSIER_BASE` |
| Bell / CHSH boundary statements | `BELL_PROTOCOL_NOTE.md`, `battle_results/nist_round2_v2/P4_PROTOCOL_AUDIT_SCOPE.md` |
| Notes around the first data archive | `battle_results/nist_completeblind_2015-09-19/INTERPRETATION_NOTE.md` |
| Round 2 organization and closure | `ROUND2_KICKOFF.md`, `ROUND2_HYPOTHESIS.md`, `ROUND2_RESULT_INTERPRETATION.md`, `ROUND2_CLOSURE_PAPER.md`, `ROUND2_FINAL_DECLARATION.md` |

**归纳原则：** 只陈述在多处重复出现、或与代码结构一致的模式；单点夸张表述若已被后续文档明确撤回或覆盖，则记入“演变”而非当作稳定特征。  
**Principle of inference:** Only patterns that recur across multiple files or align with the code structure are treated as stable. A single exaggerated statement, if later withdrawn or structurally overridden by newer documents, is recorded as part of the project’s evolution rather than as a lasting trait.

---

## 2. 话术与文体（表层）
## 2. Surface Style and Rhetoric

### 2.1 中英双语与技术混排
### 2.1 Bilingual Technical Mixing

- **现象：** 同一文档内常见英文标识符（`strict` / `postselected` / `S`）与中文解释并存；预注册与工程管线类文件尤甚。
- **功能：** 便于国际读者与脚本字段对齐；同时用中文承担“边界说明”与“伦理/范围”叙述。
- **可核对：** `README.md` 双栏表格；`ROUND2_KICKOFF.md` 中英命令与文件名混排。

- **Observed pattern:** The same document frequently mixes English identifiers such as `strict`, `postselected`, and `S` with Chinese explanatory prose; this is especially visible in preregistration and engineering-pipeline documents.
- **Function:** It helps international readers align with script fields while letting Chinese prose carry boundary statements and scope/ethics discussion.
- **Check paths:** bilingual tables in `README.md`; mixed Chinese/English commands and filenames in `ROUND2_KICKOFF.md`.

### 2.2 军事化与游戏化隐喻
### 2.2 Militarized and Game-Like Metaphors

- **现象：** “战斗”“战线”“Kickoff”“工程战”“门禁”“统一战线”等词汇高频出现。
- **功能：** 把长周期、多分支任务打成可执行的战役结构；降低叙事涣散风险。
- **副作用（客观）：** 在情绪激动时，同一隐喻体系容易生产出与科学克制相冲突的句子；仓库后半段用“收束说明”“非声称”“解释边界”对此做了制度性拉回。

- **Observed pattern:** Terms such as “battle,” “front,” “Kickoff,” “engineering battle,” “gate,” and “unified line” appear frequently.
- **Function:** They convert long, branching work into a campaign-like executable structure and reduce narrative drift.
- **Side effect:** Under emotional intensity, the same metaphor system can produce sentences that conflict with scientific restraint; the later part of the repository compensates for this through closure notes, non-claims language, and explicit interpretive boundaries.

### 2.3 表格、清单与阶段书
### 2.3 Tables, Checklists, and Phase Documents

- **现象：** Phase 0–3、P1–P7、检查清单、目录约定表密集。
- **功能：** 把口头决心转成可审计步骤；与 preregistration 话语天然相合。
- **可核对：** `ROUND2_KICKOFF.md`、`ROUND2_NO_SMUGGLING_CHECKLIST.md`、`README.md` 中 Battle Plan 段。

- **Observed pattern:** Phase 0–3, P1–P7, checklists, and directory-contract tables appear densely across the project.
- **Function:** They translate verbal intention into auditable steps and fit naturally with preregistration logic.
- **Check paths:** `ROUND2_KICKOFF.md`, `ROUND2_NO_SMUGGLING_CHECKLIST.md`, and the Battle Plan section of `README.md`.

### 2.4 “邀请质疑”模板
### 2.4 The “Invite Critique” Template

- **现象：** `experiment_dossier.py` 会向 stdout 注入 `invited_critiques_for_ai_zh`；问题高度模式化，如分辨率敏感、符号是否与文献一一对应、门禁是否被重构偷换等。
- **功能：** 主动占位常见反对意见，使报告呈现“已知会被挑错”的形态。
- **可核对：** `README.md` 自动补丁段内各实验下方的质疑列表；`experiment_dossier.py` 模块说明。

- **Observed pattern:** `experiment_dossier.py` injects `invited_critiques_for_ai_zh` into stdout; the questions are highly patterned, for example about resolution sensitivity, symbol alignment with literature, and whether gates could be silently changed by refactoring.
- **Function:** It proactively reserves space for common objections and gives reports the shape of something that already expects scrutiny.
- **Check paths:** the critique prompts shown under experiments in the README-generated sections; the module description in `experiment_dossier.py`.

---

## 3. 方法与工程观（中层）
## 3. Method and Engineering Outlook

### 3.1 预注册 + 冻结叙事
### 3.1 Preregistration + Frozen Narrative

- **核心做法：** 假设、指标公式、通过/不通过条件尽量先固定在 JSON / Markdown 中；事后改口需要新版本文件。
- **可核对：** `chsh_preregistered_config*.json`、`INTERPRETATION_NOTE.md` 中“只补充边界、不改判决”的做法。

- **Core practice:** Hypotheses, metric formulas, and pass/fail conditions are written into JSON or Markdown as early as possible; any later reinterpretation requires a new versioned file.
- **Check paths:** the `chsh_preregistered_config*.json` files and the boundary-only style of `INTERPRETATION_NOTE.md`.

### 3.2 门禁（gating）思维
### 3.2 Gating Mindset

- **核心做法：** `run_unified_suite.py` 明确区分“进程退出 0”和“物理/解释正确”；大量数值阈值与 strict / relaxed 双轨。
- **认知含义：** 接受可自动化反驳；把“我相信”降级为“当前版本在阈值下是否过线”。
- **可核对：** `run_unified_suite.py` 文首说明与 gate 字段；`BELL_PROTOCOL_NOTE.md` 中类似 `chsh_strict_S <= 2.02` 的约定。

- **Core practice:** `run_unified_suite.py` clearly distinguishes “process exited with 0” from “physics/interpretation is valid,” and uses many numerical thresholds and strict/relaxed dual tracks.
- **Cognitive implication:** It accepts automated falsifiability and demotes “I believe” into “does the current version pass under the threshold.”
- **Check paths:** the opening comments of `run_unified_suite.py` and gate-style statements such as `chsh_strict_S <= 2.02` in `BELL_PROTOCOL_NOTE.md`.

### 3.3 战线分离（scope firewall）
### 3.3 Separated Fronts (Scope Firewall)

- **核心做法：** P4 协议审计线与 NIST 数据复现线被刻意拆开，文档明确写出“不要合并 claim”。
- **功能：** 防止“局域模型里 S 对协议敏感”被误说成“某实验室数据已经给出本体论结论”。
- **可核对：** `battle_results/nist_round2_v2/P4_PROTOCOL_AUDIT_SCOPE.md`。

- **Core practice:** The P4 protocol-audit line and the NIST data-alignment line are deliberately separated, and documents explicitly say not to merge claims.
- **Function:** This prevents “S is protocol-sensitive in a local model” from being overstated into “a laboratory dataset already decides ontology.”
- **Check path:** `battle_results/nist_round2_v2/P4_PROTOCOL_AUDIT_SCOPE.md`.

### 3.4 可机读档案与可 grep 的诚实
### 3.4 Machine-Readable Archives and Grep-Friendly Honesty

- **核心做法：** `EXPERIMENT_DOSSIER_JSON_BEGIN ... END` 块、`suite_report.json` 和 battle JSON 报告并存。
- **功能：** 人类叙事与机器摘要同源；减少“报告写得漂亮而结果跑不出来”的漂移。

- **Core practice:** The repository keeps `EXPERIMENT_DOSSIER_JSON_BEGIN ... END` blocks, `suite_report.json`, and battle JSON reports side by side.
- **Function:** Human narrative and machine summary share the same source, reducing drift between “beautiful reporting” and actually reproducible outputs.

---

## 4. 认知倾向（从行为模式推断，非定论）
## 4. Cognitive Tendencies (Behavioral Inference, Not Diagnosis)

下列每条都对应可观察行为；是否映射到更深层性格，由读者自行判断。  
Each item below corresponds to observable behavior; whether it maps to a deeper personality structure is left to the reader.

| 倾向 | 文本中的稳定行为 | 说明 |
|------|------------------|------|
| 规范主义 | 预注册、清单、 Freeze Rule | 相信规则先于结论，结论争议应通过新版本规则重跑而不是事后改口。 |
| 对抗性自我审查 | dossier 邀请质疑、`INTERPRETATION_NOTE.md` 主动限缩解释 | 在叙述中预留反对者席位，接近交叉询问结构。 |
| 分层实在论（方法论上） | “现象层记录”“不对理论极限做硬门禁”等措辞 | 区分脚本可读层与理论主张层，避免一步跳到哲学判决。 |
| 控制感需求 | 长 README、统一套件、并行研究路线总览 | 通过给不确定性命名并分区来管理复杂度。 |
| 强叙事冲动与强纠错机制并存 | 一侧是宣言与战役语言，另一侧是非声称、收束、边界 | 张力持续存在，但后期文档会主动回收冲动性措辞。 |

| Tendency | Stable textual behavior | Meaning |
|----------|------------------------|---------|
| Normativism | preregistration, checklists, Freeze Rules | Rules are treated as prior to conclusions; disputed results should be rerun under new rules rather than explained away afterward. |
| Adversarial self-audit | dossier critique prompts, self-limiting interpretation notes | The writing reserves a seat for the critic and structurally resembles cross-examination. |
| Layered realism at the methodological level | distinction between phenomenon-level records and theory-level claims | Script-readable outputs are separated from higher theoretical claims so that the text does not jump too quickly into philosophy. |
| Need for control | long READMEs, unified suites, battle plans | Complexity is managed by naming, segmenting, and freezing uncertainty. |
| Strong narrative drive coexisting with strong correction mechanisms | battle/manifesto language on one side, non-claims and closure notes on the other | A visible tension remains, but later documentation actively absorbs the more impulsive rhetoric. |

---

## 5. 理论立场在文档中的表达
## 5. How Theoretical Position Appears in the Documents

- 局域/经典波前 + 测量依赖经常作为建模对象出现，但同时又反复附带 Non-Claims 列表。  
  Local/classical wavefronts plus measurement dependence appear repeatedly as modeling objects, but are accompanied again and again by explicit Non-Claims lists.
- CHSH 的读法被多次固定为“必须绑定协议细节”；`S > 2` 不能直接等同于一般哲学意义上的非局域判决。  
  The reading of CHSH is repeatedly locked into “must remain tied to protocol detail”; `S > 2` is not allowed to become an automatic philosophical verdict of nonlocality.
- 文档中的成熟，不表现在结论变强，而表现在边界变清楚。  
  Maturity in the documents appears not when conclusions become stronger, but when boundaries become clearer.

---

## 6. 时间线上的演变
## 6. Evolution Across Time

1. **体系搭建期：** 仿真脚本、`ce_*` 统一、`experiment_dossier`、`run_unified_suite`，重点是可重复与可反驳。  
   **Infrastructure-building phase:** simulation scripts, `ce_*` unification, `experiment_dossier`, and `run_unified_suite`; the priority is repeatability and falsifiability.
2. **NIST 与盲测期：** `INTERPRETATION_NOTE.md` 开始更明显地区分工程通过、论点未通过与哲学不裁决。  
   **NIST and blind-test phase:** `INTERPRETATION_NOTE.md` begins to distinguish more clearly between engineering success, thesis failure, and refusal of philosophical overreach.
3. **Round 2 组织期：** `ROUND2_KICKOFF`、engineering battle、layout blocker 文档，把未完成条件明文阻塞。  
   **Round 2 organizational phase:** `ROUND2_KICKOFF`, engineering battle documents, and layout blockers make incompleteness explicit rather than hidden.
4. **收束期：** closure paper、README 免责链、声明指针化，表现为制度化地减少外部误读和内部修辞外溢。  
   **Closure phase:** the closure paper, README disclaimer chains, and declaration-as-pointer style show an institutionalized effort to reduce external misreading and internal rhetorical spillover.

这一时间线表明，项目的写作目标正在从“推进战线”迁移到“把战线关进档案馆”。  
This timeline suggests that the project’s writing goal is shifting from “advancing a front” toward “archiving the front within fixed boundaries.”

---

## 7. 盲点与代价
## 7. Blind Spots and Costs

- **认知负荷转移给读者：** 极长文档提高了单文件可审计性，但牺牲了新读者友好度。  
  **Cognitive load shifted to the reader:** very long documents improve single-file auditability, but reduce newcomer friendliness.
- **隐喻成本：** 对抗性话语对外部读者有时会像 advocacy 而不是 research。
  **Metaphor cost:** adversarial language may appear as advocacy rather than research to outside readers.
- **情感与制度的缝隙：** 宣言式句子若不被 closure 文档回收，就会在历史记录中形成张力。  
  **Gap between emotion and institution:** manifesto-like lines, if not absorbed by closure documents, remain as tension in the historical record.

---

## 8. 一句话模型
## 8. One-Sentence Model

如果需要一个高度压缩的描述，这个项目可以被概括为：  
If a highly compressed description is needed, the project may be summarized as:

> **预注册的对抗性工程写作**：用版本化规则与门禁代替一次性激情判断；用双语表格与 JSON 锚定语义；用多条并行研究线隔离不同类型结论；并在周期末用闭包文档明确可说与不可说的话。
> **Preregistered adversarial engineering writing**: replacing one-shot passionate judgment with versioned rules and gates; anchoring meaning with bilingual tables and JSON; isolating different conclusions behind distinct fronts; and finally using closure documents to freeze what may and may not be claimed.

---

## 9. 如何使用本文件
## 9. How To Use This File

- **自荐 / 答辩：** 可引用第 3、5、6 节说明方法论与演变。  
  **For self-presentation or defense:** cite Sections 3, 5, and 6 to explain method and evolution.
- **他人审稿：** 可把本文件当作作者一致性的检查表。  
  **For external review:** treat this file as a consistency checklist for the repository’s authorial method.
- **未来回看：** 它也可以作为一面镜子，让多年后的自己重新看见当时是如何组织焦虑、约束冲动、并把不确定性写成结构的。  
  **For the future self:** it can also serve as a mirror, letting an older self see again how uncertainty, urgency, and self-restraint were once turned into structure.

---

*文件说明：本文件根据当前仓库树与公开文档归纳整理，并根据一次外部评价的文本内容保存成档。若未来仓库叙事发生显著变化，应同步更新证据路径与演变部分。*  
*File note: this document is synthesized from the current repository tree and public documents, and preserves the substance of an external evaluation as a long-term project artifact. If the repository narrative changes significantly in the future, the evidence paths and evolution sections should be updated accordingly.*
