# 第八章 · Chapter 8

**公开数据：NIST complete-blind 上的 Bell/CHSH 分母与符合窗审计**  
*Public data: Bell/CHSH denominator and coincidence-window audit on NIST complete-blind*

> **【给普通读者 · 这幅图在说什么】**
>
> - **人话词解**：**公开数据**=别人已经测好、放在网上的表格；**分母**=「总共算了多少对」；**符合窗**=「多近算一次同步点击」。换分母、换窗宽，**就像换裁判规则**，比分会变。
> - **这章解决什么**：第二章里「1.1 vs 2.3」的戏剧，拆成**可检查的步骤**：我们到底在数什么？
> - **教科书常识**：Bell/CHSH 实验分析有**成熟规范**；本书做的是**对特定公开档案**的**审计式阅读**，不是替全世界实验下总判。
> - **本书在干什么**：把磁盘上的 **CSV/HDF5** 链路写清；**你不必会编程**，只要抓住「**统计对象是否被偷换**」。
> - **和物理学家们**：**不自动违背**；若发现的是**规则敏感**，那是**透明度问题**，不是骂战。

> **本章任务**  
> 把叙事从格子玩具**切到磁盘上的 CSV**：同一批 **NIST** 公开记录，**分母怎么取、符合怎么配对、窗宽怎么选**——会如何移动 **S 或 CHSH 代理量**。

## 8.1　为什么必须单独开一章

第二章只给你**一个戏剧性的数差**。本章（及后续数章）要做的是：**把戏剧拆成步骤**——哪一步对应仓库里哪条审计脚本、哪条归档 JSON。**complete-blind** 类档案有其**字段语义**；若把索引或权重误读，统计对象就悄悄换了。

## 8.2　分母与「有效对」：仓库从哪下手

Bell/CHSH 不是只有一个公式外壳，内里常藏：**哪些 trial 计入、哪些因丢失或无效被扔掉**。本书仓库在下列线索上**反复审计**（非穷尽列表，随仓库演进会增删）：

| 方向 | 示例脚本（`scripts/explore/`） |
| :--- | :--- |
| **字段/索引语义统一** | `nist_unified_semantics_audit_v1.py` … `v4.py` |
| **同一索引上的二值化/量化扫描** | `nist_same_index_quantization_sweep_v1.py`、`nist_same_index_quantization_sweep_v4.py` |
| **ρ–μ–η 或双指标桥** | `nist_same_index_rho_mu_eta_scan_v1.py`、`nist_same_index_dual_metric_bridge_v1.py` |
| **角度符号与符合构造** | `nist_same_index_angle_sign_scan_v1.py` |
| **closure / 复盘包** | `nist_revival_20pct_closure_v1.py`、`nist_revival_20pct_closure_v4.py` |
| **邮件/摘要打包** | `nist_email_summary_pack_v4.py`、`nist_semantics_contribution_summary_v1.py` |

归档常见根：**`battle_results/`**、**`papers_final/`**（以你本地克隆为准）。读法：**先打开具体 `*_audit*.py` 顶部的「事件定义」**，再对照 **CSV 列名**。

## 8.3　符合窗、时钟与「时间对齐」

光子实验中，**符合窗**决定哪些计数算「同时」；窗宽一变，偶然符合与真符合比例变——**S 会跟着动**。仓库中亦有**时钟参考/对齐**类审计（如 **`nist_clock_reference_audit_v1.py`**），用于检查**时间轴语义**是否与宣称一致。要点仍是：**把假设写进脚本**，再让数字说话。

> **本章边界**  
> 本章是**对公开记录与协议的审计式讨论**；**不是**对 NIST 或实验者的人身评价。任何 headline 数字以**本章引用的归档文件**中的定义为准。

## 8.4　小结

你应带走：**公开数据章节的硬度，来自分母与窗的显式化**。下一章进入**更几何的独立实验叙事**：在**同批数据**上拟合 Alice/Bob 偏振路径的**等效庞加莱坐标**——又一层「尺子」，可与 CHSH 管道**交叉检验**。

---

# Chapter 8 · Public data: Bell/CHSH denominator and coincidence-window audit on NIST complete-blind

**公开数据：NIST complete-blind 上的 Bell/CHSH 分母与符合窗审计**  
*Public data: Bell/CHSH denominator and coincidence-window audit on NIST complete-blind*

> **For general readers — what this picture is about**
>
> - **In plain words**: **Public data** is a table someone else measured and posted online; the **denominator** is “how many pairs we counted”; a **coincidence window** is “how close in time counts as one simultaneous click.” Change denominator or window width and **you change the refereeing rules** — scores move.
> - **What this chapter does**: Turn Chapter 2’s “1.1 vs 2.3” drama into **inspectable steps**: what exactly are we counting?
> - **Textbook baseline**: Bell/CHSH analysis has **mature practice**; this book offers **audit-style reading of one public archive**, not a global ruling on every experiment.
> - **What the book is doing**: Spell out the on-disk **CSV/HDF5** chain; **no coding required** — just watch whether **the statistical object is being swapped in silence**.
> - **For working physicists**: Nothing here **automatically contradicts** standard physics; if the finding is **rule sensitivity**, that is a **transparency** issue, not mudslinging.

> **This chapter’s job**  
> Move the story from lattice toys **to CSV on disk**: on one **NIST** public record, **how denominators are chosen, how coincidences pair, how window width is set** — and how those choices move **S** or a **CHSH proxy**.

## 8.1 Why this deserves its own chapter

Chapter 2 only showed a **dramatic gap**. This chapter (and neighbors) **unpack the drama into steps** — which step maps to which audit script, which archived JSON. **complete-blind** archives have **field semantics**; misread an index or weight and the statistical object quietly changes.

## 8.2 Denominators and “effective pairs”: where the repo digs in

Bell/CHSH is not just a formula shell; inside hides **which trials count, which are dropped for loss or invalidity**. The repo revisits these threads (non-exhaustive; evolves with the repo):

| Direction | Example scripts (`scripts/explore/`) |
| :--- | :--- |
| **Unified field / index semantics** | `nist_unified_semantics_audit_v1.py` … `v4.py` |
| **Same-index binarization / quantization sweeps** | `nist_same_index_quantization_sweep_v1.py`, `nist_same_index_quantization_sweep_v4.py` |
| **ρ–μ–η or dual-metric bridge** | `nist_same_index_rho_mu_eta_scan_v1.py`, `nist_same_index_dual_metric_bridge_v1.py` |
| **Angle sign and coincidence construction** | `nist_same_index_angle_sign_scan_v1.py` |
| **Closure / review packs** | `nist_revival_20pct_closure_v1.py`, `nist_revival_20pct_closure_v4.py` |
| **Email / summary bundles** | `nist_email_summary_pack_v4.py`, `nist_semantics_contribution_summary_v1.py` |

Archives often live under **`battle_results/`**, **`papers_final/`** (per your clone). Reading discipline: **open the chosen `*_audit*.py`, read the “event definition” header**, then line up **CSV column names**.

## 8.3 Coincidence windows, clocks, and “time alignment”

In photon work, the **coincidence window** decides which counts are “simultaneous”; change the width and the accidental vs true ratio shifts — **S moves with it**. The repo also has **clock reference / alignment** audits (e.g. **`nist_clock_reference_audit_v1.py`**) to check whether **time-axis semantics** match what is claimed. Same moral: **write assumptions into the script**, then let numbers speak.

> **Chapter boundary**  
> This is **audit-style discussion of public records and protocols** — **not** a personal judgment on NIST or the experimenters. Any headline number follows the **definition in the archived file cited in this chapter**.

## 8.4 Close

Take away: **public-data chapters get their rigor from explicit denominators and windows.** Next chapter opens a **more geometric, standalone experiment narrative**: fit **effective Poincaré coordinates** for Alice/Bob polarization paths on **the same batch** — another “yardstick” that can **cross-check** the CHSH pipeline.
