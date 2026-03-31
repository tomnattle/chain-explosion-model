# Round 2 Archive
# Round 2 第二轮归档

这个目录是第二轮严肃实验的工作区与归档区。它的意义不只是重复第一轮的数值流程，而是进一步处理布局兼容性、工程映射敏感性、协议分叉和解释收束问题。  
This directory is the workspace and archive zone of the second serious experiment. Its significance is not merely to repeat the first round numerically, but to further address layout compatibility, engineering-mapping sensitivity, protocol branching, and interpretive closure.

因此，第二轮的核心价值并不只是“产生一个新的 \(S\)”，而是把一整套更成熟的研究问题明确地写进了归档。  
For that reason, the core value of Round 2 is not simply “to produce a new \(S\),” but to explicitly write a more mature set of research questions into the archive.

## What Round 2 Adds

与第一轮相比，第二轮主要增加了三条线：  
Compared with Round 1, Round 2 mainly adds three lines of work:

1. P3 布局兼容性检查  
   P3 layout compatibility checking
2. engineering 映射敏感性对照  
   engineering mapping-sensitivity comparison
3. 收束文档与解释边界锁定  
   closure documents and interpretive-boundary locking

## P3: Layout Compatibility

第二轮首先确认一个基础事实：training HDF5 与 completeblind HDF5 并不能直接共用同一条 v1 grid-side-streams 转换路径。这个问题记录在 [p3_compare_report.json](D:/workspace/golang/nakama/chain-explosion-model/battle_results/nist_round2_v2/p3_compare_report.json) 中。  
Round 2 first confirms a basic fact: the training HDF5 and the completeblind HDF5 cannot directly share the same v1 grid-side-streams conversion path. This issue is recorded in [p3_compare_report.json](D:/workspace/golang/nakama/chain-explosion-model/battle_results/nist_round2_v2/p3_compare_report.json).

这一点很重要，因为它阻止了未经审计的横向类比。第二轮在这里表现出比第一轮更强的“工程自限”意识。  
This point is important because it prevents unaudited horizontal analogy. In this respect, Round 2 shows a stronger sense of engineering self-limitation than Round 1.

## Engineering Battle

第二轮的 engineering battle 允许两种映射并列比较：`legacy` 和 `parity`。对应的核心结果记录在 [ROUND2_ENGINEERING_BATTLE_REPORT.json](D:/workspace/golang/nakama/chain-explosion-model/battle_results/nist_round2_v2/ROUND2_ENGINEERING_BATTLE_REPORT.json)。  
The engineering battle of Round 2 allows two mappings to be compared side by side: `legacy` and `parity`. The corresponding core result is recorded in [ROUND2_ENGINEERING_BATTLE_REPORT.json](D:/workspace/golang/nakama/chain-explosion-model/battle_results/nist_round2_v2/ROUND2_ENGINEERING_BATTLE_REPORT.json).

### Legacy Mapping

- `S_strict = 2.336275858171887`
- `S_standard = 2.8445681666863845`
- `pair_count(strict) = 136632`
- `pair_count(standard) = 144790`

### Parity Mapping

- `S_strict = 2.3274283887643272`
- `S_standard = 2.83617087618962`
- `pair_count(strict) = 136632`
- `pair_count(standard) = 144790`

### Drift Between Mappings

- `delta_S_strict = -0.00884746940755976`
- `delta_S_standard = -0.008397290496764409`

这说明映射会改变数值，但在 Round 2 锁定的 engineering 框架下，这种改变是有限且可报告的。  
This shows that mapping does change the numerical result, but under the engineering framework locked in Round 2, that change is finite and reportable.

## Thesis Gate in Round 2

Round 2 使用的是 `fork_only` 模式，不再沿用第一轮的 `strict_max_S = 2.02` 作为主要 thesis gate。相反，它只要求在同一框架下满足 `S_standard > S_strict`。  
Round 2 uses `fork_only` mode and no longer treats the first-round `strict_max_S = 2.02` as the primary thesis gate. Instead, it only requires that `S_standard > S_strict` be satisfied within the same framework.

这意味着第二轮的 thesis 判断更像“方向性分叉确认”，而不是“经典上界压制确认”。  
This means the thesis judgment in Round 2 is closer to a “directional fork confirmation” than to a “classical-bound suppression confirmation.”

## Replay Under Round 1 Gate

第二轮没有抹掉第一轮的失败，而是把同一批数据重新放回第一轮门槛下检查。结果记录在 [ROUND2_UNDER_ROUND1_GATE.json](D:/workspace/golang/nakama/chain-explosion-model/battle_results/nist_round2_v2/ROUND2_UNDER_ROUND1_GATE.json)。  
Round 2 does not erase the first-round failure, but instead rechecks the same data under the first-round thresholds. The result is recorded in [ROUND2_UNDER_ROUND1_GATE.json](D:/workspace/golang/nakama/chain-explosion-model/battle_results/nist_round2_v2/ROUND2_UNDER_ROUND1_GATE.json).

在这个回放中，legacy 与 parity 依然都是 `thesis_pass = false`。这说明第二轮并不是用新的叙事去改写旧结论，而是在新框架中并列保留旧结论。  
In this replay, both legacy and parity remain `thesis_pass = false`. This means Round 2 does not rewrite the old conclusion with a new narrative, but preserves the old conclusion in parallel within the new framework.

## Suggested Reading Order

如果你第一次进入这个目录，建议按以下顺序阅读：  
If this is your first time entering this directory, the suggested reading order is:

1. [ROUND2_CLOSURE_PAPER.md](D:/workspace/golang/nakama/chain-explosion-model/battle_results/nist_round2_v2/ROUND2_CLOSURE_PAPER.md)
2. [ROUND2_ENGINEERING_BATTLE_REPORT.json](D:/workspace/golang/nakama/chain-explosion-model/battle_results/nist_round2_v2/ROUND2_ENGINEERING_BATTLE_REPORT.json)
3. [ROUND2_UNDER_ROUND1_GATE.json](D:/workspace/golang/nakama/chain-explosion-model/battle_results/nist_round2_v2/ROUND2_UNDER_ROUND1_GATE.json)
4. [p3_compare_report.json](D:/workspace/golang/nakama/chain-explosion-model/battle_results/nist_round2_v2/p3_compare_report.json)
5. [P4_PROTOCOL_AUDIT_SCOPE.md](D:/workspace/golang/nakama/chain-explosion-model/battle_results/nist_round2_v2/P4_PROTOCOL_AUDIT_SCOPE.md)

## Important Files

- `ROUND2_CLOSURE_PAPER.md`  
  第二轮收束文档。  
  The Round 2 closure paper.
- `ROUND2_ENGINEERING_BATTLE.md`  
  映射与窗口敏感性的叙述说明。  
  Narrative explanation of mapping and window sensitivity.
- `ROUND2_ENGINEERING_BATTLE_REPORT.json`  
  第二轮数值核心结果。  
  Core numerical result of Round 2.
- `ROUND2_UNDER_ROUND1_GATE.json`  
  在第一轮门槛下的回放结果。  
  Replay result under the Round 1 gate.
- `p3_compare_report.json`  
  P3 布局兼容性与阻塞说明。  
  P3 layout compatibility and blocker report.
- `P4_PROTOCOL_AUDIT_SCOPE.md`  
  协议审计线与 NIST 复现实验线的边界说明。  
  Boundary note between the protocol-audit line and the NIST reproduction line.

## Closing Note

第二轮的成熟之处，不在于它“更会说”，而在于它更明确地区分了哪些是数值结果，哪些是工程假设，哪些是解释边界。正因为如此，这个目录应被视为本仓库最重要的研究文档区之一。  
The maturity of Round 2 lies not in “speaking more boldly,” but in distinguishing more clearly what counts as numerical result, what counts as engineering assumption, and what counts as interpretive boundary. For that reason, this directory should be regarded as one of the most important research-document zones in the repository.
