# Battle Archives
# Battle 实验归档总览

这个目录保存的是本仓库中最重要的两轮严肃实验归档。它们不是普通脚本运行输出的临时集合，而是围绕 CHSH / NIST 问题建立的可复核研究工件。  
This directory stores the two most important serious experiment archives in the repository. They are not temporary collections of ordinary script outputs, but reproducible research artifacts built around CHSH / NIST questions.

这些归档的意义在于，它们把“数据来源、配置、协议、数值结果、解释边界和最终结论”放进了同一个可追溯结构里。因此，它们应被视为本项目主线，而不是附属材料。  
The significance of these archives lies in the fact that they place “data source, configuration, protocol, numerical results, interpretive boundaries, and final judgment” into a single traceable structure. For that reason, they should be treated as the main line of the project rather than as supplementary material.

## Archive Index

### 1. `nist_completeblind_2015-09-19/`

这是第一轮严肃归档，围绕公开 completeblind 数据展开。它的核心结论是：工程链路已经打通，但按照当时锁定的 thesis gate，论点没有通过。  
This is the first serious archive, built around public completeblind data. Its central conclusion is that the engineering path was successfully established, but under the thesis gate locked at that time, the thesis itself did not pass.

建议先读：  
Suggested first reads:

- [README.md](D:/workspace/golang/nakama/chain-explosion-model/battle_results/nist_completeblind_2015-09-19/README.md)
- [battle_result.json](D:/workspace/golang/nakama/chain-explosion-model/battle_results/nist_completeblind_2015-09-19/battle_result.json)
- [INTERPRETATION_NOTE.md](D:/workspace/golang/nakama/chain-explosion-model/battle_results/nist_completeblind_2015-09-19/INTERPRETATION_NOTE.md)

### 2. `nist_round2_v2/`

这是第二轮严肃归档，重点不只是重复第一轮数值，而是进一步处理布局兼容性、工程映射敏感性、协议分叉以及收束叙述。它比第一轮更接近一份正式研究收束文档。  
This is the second serious archive. Its focus is not merely to repeat the first round numerically, but to further address layout compatibility, engineering-mapping sensitivity, protocol branching, and narrative closure. It is closer than the first round to a formal research-closure document.

建议先读：  
Suggested first reads:

- [README.md](D:/workspace/golang/nakama/chain-explosion-model/battle_results/nist_round2_v2/README.md)
- [ROUND2_CLOSURE_PAPER.md](D:/workspace/golang/nakama/chain-explosion-model/battle_results/nist_round2_v2/ROUND2_CLOSURE_PAPER.md)
- [ROUND2_ENGINEERING_BATTLE_REPORT.json](D:/workspace/golang/nakama/chain-explosion-model/battle_results/nist_round2_v2/ROUND2_ENGINEERING_BATTLE_REPORT.json)
- [P4_PROTOCOL_AUDIT_SCOPE.md](D:/workspace/golang/nakama/chain-explosion-model/battle_results/nist_round2_v2/P4_PROTOCOL_AUDIT_SCOPE.md)

## How To Read These Archives

阅读这些归档时，最重要的是分清三个层次：第一是工程层，第二是协议层，第三是解释层。工程层问的是流程能否跑通；协议层问的是换窗口、换映射、换筛选是否改变结果；解释层才讨论这些结果能否支持更强的叙述。  
When reading these archives, the most important thing is to distinguish three levels: first, the engineering level; second, the protocol level; third, the interpretive level. The engineering level asks whether the pipeline runs correctly; the protocol level asks whether changing windows, mappings, or selection changes the result; only the interpretive level discusses whether these results support stronger claims.

这两个 battle 目录都应被理解为“工程归档 + 研究判断”的组合，而不是任何外部机构官方实验流程的自动等价物。  
Both battle directories should be understood as combinations of “engineering archive + research judgment,” not as automatic equivalents of any external institution’s official experimental procedure.

## Documentation Note

后续如果继续优化文档，最优先的方向不是增加更多运行截图，而是继续统一 battle 子目录中的关键说明文件，使它们和顶层总文档保持同样的双语、结构化和可引用风格。  
If the documentation is further improved, the top priority should not be adding more screenshots, but continuing to normalize the key explanatory files inside the battle subdirectories so that they match the same bilingual, structured, and citation-ready style as the top-level monograph.
