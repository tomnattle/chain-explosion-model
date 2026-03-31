# P4：协议审计战线 — 独立结论范围

## 目标

用仓库内 **closure / 严格 vs 后筛选 / 局域波闭包** 等脚本，在**显式模型**下复现：**同一套局域假设，变换协议（阈值、coincidence、配对）可使 CHSH 组合 `S` 穿过或不穿过经典界限**。

## 不与 NIST 共用的一句话结论

- **审计线**回答：在**给定代码里的局域机制**下，`S` 对**协议开关**有多敏感。  
- **NIST 线**回答：在**给定公开 HDF5 + 给定读出管道**下，观测到的 `S` 是多少、预注册预言是否通过。

二者可并存；**禁止**用审计线的结果直接代替 NIST 盲测判辞，除非在新预注册里**合并假设**并重新开盲。

## 代表脚本（可随 battle plan 跑）

- `explore_chsh_strict_protocol.py` — 严格二值、无后筛选基线  
- `explore_chsh_operation_audit.py` — 后筛选/效率扫描  
- `explore_chsh_closure_protocol.py` / `explore_chsh_local_wave_closure_full.py` — 更重的时序与探测器模型  
- `run_battle_plan.py` — 聚合与看板  

## 可对外陈述的「独立成果」模板

> 在本仓库实现的显式局域模型下，CHSH 统计量随**测量协议**（配对与筛选）系统变化；因此仅凭某一实验流程给出的 `S > 2`，在解释上必须与协议细节绑定，不能无条件升格为单一本体论结论。

（具体数值以 `battle_plan_summary.json` 与各脚本图为准。）
