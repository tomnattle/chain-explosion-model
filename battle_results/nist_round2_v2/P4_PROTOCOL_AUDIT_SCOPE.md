# P4 Protocol Audit Scope
# P4 协议审计范围说明

## Purpose

这个文件的目的，是明确区分两条不能混为一谈的研究线：一条是协议审计线，另一条是基于公开 NIST 数据的对齐与归档线。  
The purpose of this file is to clearly separate two research lines that must not be merged casually: the protocol-audit line, and the alignment-and-archival line based on public NIST data.

协议审计线讨论的是：在一个显式局域模型中，配对窗口、阈值、筛选规则和 coincidence 协议怎样系统地改变 CHSH 统计量 \(S\)。  
The protocol-audit line asks: within an explicit local model, how do pairing windows, thresholds, retention rules, and coincidence protocols systematically change the CHSH statistic \(S\)?

NIST 对齐线讨论的是：在既定公开数据与既定读取管道下，最终观察到的 \(S\) 是多少，以及某个预注册门槛是否通过。  
The NIST alignment line asks: under a given public dataset and a given reading pipeline, what \(S\) is ultimately observed, and does a particular preregistered threshold pass?

## Core Distinction

协议审计线的回答是“在给定代码模型下，\(S\) 对协议细节有多敏感”。  
The protocol-audit line answers “how sensitive \(S\) is to protocol details under the given coded model.”

NIST 对齐线的回答是“在给定公开数据和给定转换管道下，得到的数值是多少”。  
The NIST alignment line answers “what numerical value is obtained under the given public data and the given conversion pipeline.”

这两者可以并存，但不能相互替代。  
These two lines can coexist, but they cannot substitute for one another.

## Why This Matters

如果把协议审计线直接当成对 NIST 数据的实验性裁决，那么会出现一个逻辑跳跃：你会把“模型中协议敏感性很强”误读成“真实外部实验结果必然说明某种本体结论”。  
If the protocol-audit line is treated directly as an experimental ruling on the NIST data, a logical leap appears: one misreads “the model is highly protocol-sensitive” as “the real external experiment must therefore imply a certain ontological conclusion.”

反过来，如果把 NIST 对齐结果直接拿来替代协议审计线，也会出问题，因为那会忽略“协议本身是否已经在代码中决定了结果分叉”这一层。  
Conversely, if the NIST alignment result is used to replace the protocol-audit line, one also loses an essential layer, namely whether the protocol itself already determines the branching of results in code.

## Representative Scripts

协议审计线的代表脚本包括：  
Representative scripts on the protocol-audit line include:

- `explore_chsh_strict_protocol.py`
- `explore_chsh_operation_audit.py`
- `explore_chsh_strict_vs_postselected_compare.py`
- `explore_chsh_closure_protocol.py`
- `explore_chsh_local_wave_closure_full.py`
- `run_battle_plan.py`

这些脚本回答的是“在显式模型与显式协议下，结果怎样随协议开关变化”。  
These scripts answer “how results change with protocol switches under an explicit model and an explicit protocol.”

NIST 对齐线的代表文件则包括：  
Representative files on the NIST alignment line include:

- `run_nist_round2_compare.py`
- `ROUND2_ENGINEERING_BATTLE_REPORT.json`
- `ROUND2_UNDER_ROUND1_GATE.json`
- `p3_compare_report.json`

这些文件回答的是“在公开数据与锁定转换路径下，最终落地的数值和门槛判断是什么”。  
These files answer “what the final realized numbers and threshold judgments are under public data and locked conversion paths.”

## Safe External Wording

在当前仓库框架下，较安全的外部表达是：  
Within the current repository framework, the safer external wording is:

> 在本仓库实现的显式模型中，CHSH 统计量会随配对、筛选与 coincidence 协议系统变化，因此任何 `S > 2` 的解释都应与协议细节绑定，而不能自动上升为单一的本体结论。  
> In the explicit model implemented in this repository, the CHSH statistic varies systematically with pairing, filtering, and coincidence protocols; therefore any interpretation of `S > 2` should remain bound to protocol detail rather than being automatically elevated to a single ontological conclusion.

## Not Allowed

以下两种跳跃式说法应被避免：  
The following two leap-like formulations should be avoided:

1. 用协议审计线的结果直接替代对 NIST 数据本身的实验判断。  
   Using the protocol-audit line as a direct substitute for experimental judgment on the NIST data itself.
2. 用 NIST 对齐结果反向证明协议敏感性问题已经自动解决。  
   Using the NIST alignment result to retroactively claim that the protocol-sensitivity problem has automatically been solved.

## Final Note

这个文件存在的目的，不是削弱项目，而是保护项目。只有把协议问题、数据问题和解释问题分层写清楚，整个仓库才会显得成熟、可信、并且值得被认真讨论。  
The purpose of this file is not to weaken the project, but to protect it. Only by writing protocol issues, data issues, and interpretive issues as clearly separated layers can the whole repository appear mature, credible, and worthy of serious discussion.
