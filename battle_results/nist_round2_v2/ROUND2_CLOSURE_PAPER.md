---
title: 第二场工程向 CHSH 评估工作收束说明
subtitle: 预注册协议下的结果归档与解释边界（非 NIST 官方复现声明）
date: 2026-03-31
lang: zh-CN
---

## 摘要

本文档对仓库内「第二场」（Round 2）工程向 CHSH 评估作**温和、有限**的收束叙述：在预注册的配置锁、指标公式锁与无走私（no-smuggling）审计范围内，报告离线管道所得数值；明确**不**声称等同 NIST 官方实验复现，**不**以单次管线结论仲裁量子理论基础。目的在于整理可复核工件、划定可陈述与不可陈述的边界，并使相关工作在文档层面告一段落。

**关键词：** CHSH；预注册；工程敏感性；解释边界；可重复性

---

## 1. 背景与动机

贝尔型实验文献中，`S` 统计量常被用作讨论局域实在与量子相关性的枢纽。与此同时，从原始记录到 `±1` 符号、时间窗与配对规则的实现链条较长，**工程选择与解释框架**会影响读数与可推广结论。第二场工作的定位是：在已声明的假设与审计约束下，完成一轮**可归档、可复查**的离线评估，并以克制措辞记录结果——而非扩张为对广理论的裁决。

## 2. 范围与非声称

下列边界由项目内预注册文件与工程报告共同约定，本文档予以重申：

- **工程/假设性质：** 评估在「局域经典波前、显式测量依赖」等**建模前提**下展开；不宣称量子理论为假或为真。
- **与 NIST 官方流程的关系：** 本工作为**工程向双映射与窗分级**管道，**不是** NIST 官方 CHSH 实验的逐项复现；任何「与公开描述对齐」的陈述均以仓库内单独报告为限。
- **对 `S > 2` 的含义：** 即便在锁定公式下出现 `S > 2`，亦**不等同**于在一般哲学意义上「证明非局域本体」或「否定局域实在」；预注册解释类 B 仅在与审计通过与范围说明同时成立时，才在**本协议内**记为有效类别（参见协议级 `result_class` 定义）。

## 3. 方法概要（读者可据工件复核）

- **配置：** 工程对齐使用 `chsh_preregistered_config_nist_round2_engineering.json`；同一批事件另以第一场（Round 1）论文式门限配置 `chsh_preregistered_config_nist_index.json` 作**对照回放**（不改变当年第一场已冻结结论，仅作数值并列）。
- **CHSH：** 采用锁定的标准代数形式（各设置单元格内 `E = (N_{++}+N_{--}-N_{+-}-N_{-+})/N_{总}`，总统计量 `S = E_{ab}+E_{ab'}+E_{a'b}-E_{a'b'}`）；跑程中不改公式。
- **双映射：** 「legacy」与「parity」两种工程映射用于敏感性对照（具体定义见转换配置与 NIST 映射报告）。
- **窗分级：** 第二场工程报告中「strict」与「standard」对应不同配对时间窗（strict：0；standard：10 ns 量级，以锁定配置为准）；Round 1 门限回放中 standard 窗为索引配置中的 15 ns 档位。
- **审计：** 对约定执行路径执行无走私检查清单（共享状态、全局后选、隐蔽同步、局部时间线、确定性重算、指标不变性等），结论带 **scope note**：**仅适用于该确定性离线 CSV 管线**，不扩展为对新型模拟器实装或未审计代码路径的证明。

## 4. 主要数值结果（归档摘要）

下列数字摘自 `round2_second_sudden_death_run/run_summary.json` 与 `ROUND2_ENGINEERING_BATTLE_REPORT.json`（2026-03-31 运行摘要），供独立复核；四舍五入请以原始 JSON 为准。

**第二场工程门（fork_only：要求 `S_standard > S_strict`，且不启用 Round 1 的 `strict_max_S` 等阈值）：**

| 映射 | `S_strict`（window 0） | `S_standard`（window 10） | strict 对数 | standard 对数 |
|------|------------------------|-----------------------------|-------------|----------------|
| legacy | 2.336276 | 2.844568 | 136632 | 144790 |
| parity | 2.327428 | 2.836171 | 136632 | 144790 |

parity 相对 legacy：`ΔS_strict ≈ -0.00885`，`ΔS_standard ≈ -0.00840`（工程报告内双精度值）。

**Round 1 门限回放（同一 CSV，`strict_max_S = 2.02` 等）：** legacy 与 parity 的 **thesis_pass 均为否**，因 strict 侧 `S` 高于预注册上限；standard（window 15）侧 `S` 仍约为 2.84 量级，但**整体验证**按 Round 1 锁死规则未通过。该并列旨在 transparency：不同门限讲述不同「通过/不通过」故事，读者应始终回到**当时冻结**的那一份配置来理解归档结论。

**协议层归类（第二场锁定规则）：** `result_class = B`，`audit_status = pass_with_scope_note`（审计通过限于上文 scope）。

## 5. 温和解释与收束

在以上边界内，可以**谨慎**表述为：

1. 在第二场预注册工程配置与通过审计的离线管道下，报告了 **strict 与 standard 均大于 2** 的 CHSH 组合值，且 parity/legacy 对照显示**量级稳定、存在小幅差异**——后者对工程映射敏感度给出了可报告的量级。
2. 将这些结果**外推**为实验物理学、设备层或 NIST 官方结论，**超出本文档与仓库已声明范围**。
3. 哲学与基础解释上的分歧（例如测量介入与本体论断）宜保留为**开放讨论**；本仓库以**可重复工件**为优先，不以修辞替代推导。

**结语：** 第二场工程向评估在约定协议下已完成归档；主要工件集中于 `battle_results/nist_round2_v2/`。若日后有必要延续，应以**新协议版本号**与**新预注册文件**另起一行，而非retroactively 修改本场冻结叙述。本文档标志本场工作在作者侧的**文档层面的收束**，并邀请读者依路径自行复算、独立判断。

---

## 参考文献与工件（仓库内）

- `ROUND2_RUN_PROTOCOL.md`、`ROUND2_HYPOTHESIS.md`、`ROUND2_RESULT_INTERPRETATION.md`
- `ROUND2_ENGINEERING_BATTLE_REPORT.json`、`round2_second_sudden_death_run/run_summary.json`
- `round2_second_sudden_death_run/NO_SMUGGLING_AUDIT_RESULT.md`
- `ROUND2_UNDER_ROUND1_GATE.json`、`NIST_OFFICIAL_MAPPING_AND_WINDOWS_REPORT.md`

---

## 附录：生成 PDF 的简要方式

以下为常见做法，择一即可；中文字体需本机已安装相应字体。

**A. Pandoc + LaTeX（推荐结构控制）**

```bash
cd battle_results/nist_round2_v2
pandoc ROUND2_CLOSURE_PAPER.md -o ROUND2_CLOSURE_PAPER.pdf --pdf-engine=xelatex -V mainfont="Microsoft YaHei" -V geometry:margin=2.5cm
```

若缺 `mainfont` 可改为本机存在的宋体/黑体名称；无 LaTeX 时可安装 TeX Live 或 MiKTeX。

**B. Pandoc + wkhtmltopdf / 浏览器打印**

先将 Markdown 转为 HTML，再用浏览器「打印 → 另存为 PDF」。

**C. VS Code / Typora**

用自带 Markdown 预览导出 PDF（需在软件中启用对应扩展或导出功能）。

---

*文稿性质：工作区收束说明，非期刊投稿版本。*
