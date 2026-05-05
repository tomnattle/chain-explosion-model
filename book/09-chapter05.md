# 第五章 · Chapter 5

**栅格涟漪：缝口吸收、有限吸收体与探测器**  
*Ripple grid: slit absorption and finite absorber–detector*

> **【给普通读者 · 这幅图在说什么】**
>
> - **人话词解**：把「测量」暂时翻译成**在某一格抠走一部分能量**——像海绵挡在波纹路上**吸掉一截**。
> - **这章解决什么**：**哪里吸、吸多狠**，条纹会怎样变淡或变形？这是**几何 + 损耗**问题，不是玄学。
> - **教科书常识**：量子叙述里常用**坍缩、路径信息**；经典波动里**吸收/探测**也会破坏干涉。**本书用经典式损耗在格子上演示**，不自称替代量子测量理论。
> - **本书在干什么**：`ce_04`–`ce_05` 给出**可对照的曲线**；书中快照告诉你**同一指标也可能误读**，要结合图看。
> - **和物理学家们**：现象方向（**有吸收常削弱对比**）与常识一致；**定量**只对本仓库参数负责。

> **本章任务**  
> 把「探测器读到一点」落实为**可扫参数**：缝后吃多少、吸收片多大、多狠——看条纹与可见度**如何被洗掉**。

## 5.1　承接：测量 = 局域干预

专论里写过 **Ê = (1−η)E** 式的吸收。`ce_04` 起，脚本把 **η**、**吸收列**、**缝行区间**写进传播循环：你在传播链上**显式抠走**一部分场，再进入下一步。这里没有「口头坍缩」，只有**乘子与几何**。

## 5.2　`ce_04`：缝口吸收

`scripts/ce/ce_04_measurement_absorption_at_slit.py`（及同系列变体）扫描：**就在缝口**吃掉一部分能量时，下游条纹如何劣化。直觉与第三章一致：**多吞一口，就少一份能干涉的份额**；定量由曲线说话。

### 一次运行快照（`ce_04` 三联对照，模型内）

下列数值来自 **2026-05-05**、仓库根目录、`PYTHONPATH` 指向仓库根、`MPLBACKEND=Agg`、建议 `PYTHONIOENCODING=utf-8` 下的一次运行。脚本对**上缝**邻列施加分档吸收（`ABSORB_RATIO` 默认 **0.5**），在 **`SCREEN_X = WIDTH - 10`** 取列并计算脚本内 **`compute_visibility`**。

| 项目 | 内容 |
| :--- | :--- |
| **命令** | `python scripts/ce/ce_04_measurement_absorption_at_slit.py` |
| **图文件** | **`scripts/ce/measurement_effect.png`**（三联屏曲线） |

| 场景 | `emit_case_dossier` 键 | 可见度 V（快照） |
| :--- | :--- | ---: |
| 无吸收（双缝基线） | `visibility_none_absorb` | ≈ **0.8065** |
| 上缝 50% 吸收 | `visibility_partial_absorb` | ≈ **0.7719** |
| 上缝 100% 吸收（等效单缝叙事） | `visibility_one_slit_gone` | ≈ **0.8431** |

**读法**：**部分吸收**相对基线 **V 下降**，与「吃掉相干份额」一致。第三行 **V 未跌近零**——因脚本的 **V** 是**峰谷启发式**，单缝式包络仍可有起伏；**不能**把该标量单独当「干涉是否消失」的终审，应结合 **`measurement_effect.png`** 与峰位对称性判断。下一节 **`ce_05`** 把吸收块做成**二维几何**，同一类「读数定义敏感」仍会出现。

## 5.3　`ce_05`：有限吸收体 / 探测器块

把吸收从「一条缝列」推广到**二维小块**：模拟**有限大探测器**或**挡在半路的海绵**。参数包括位置、宽度、**η**。你会看到：不是只有「全有或全无」，**半大不小的吸收体**就能显著改统计形状——这对后面谈「符合窗」「有效探测区」是同一类**几何敏感**。

### 一次运行快照（`ce_05` 默认圆吸收体，模型内）

下列数值来自 **2026-05-05**、仓库根目录、`PYTHONPATH` 指向仓库根、`MPLBACKEND=Agg`、建议 `PYTHONIOENCODING=utf-8` 下的一次运行。**`ENABLE_ABSORBER=True`**（默认）：圆心约在缝后 **(BARRIER_X+5, 上缝中心)**，**半径 10**，**ABSORB_RATIO=0.8**，**STEPS=500**，屏列 **`SCREEN_X = WIDTH - 10`**。

| 项目 | 内容 |
| :--- | :--- |
| **命令** | `python scripts/ce/ce_05_finite_absorber_detector.py` |
| **图文件** | **`scripts/ce/finite_absorber.png`**（屏曲线 + 全场对数图 + 局部放大） |
| **`emit_case_dossier` 摘要** | `visibility_final` = **0.0**（脚本内 **`compute_visibility`**：无有效峰谷时返回 0） |

**读法**：与 **`ce_04`** 的「部分吃一条缝列」不同，**二维圆斑 + 高吸收** 在本组默认参下把屏上曲线压成**启发式 V 读不出来**的形态——脚本会走「对比度低于 0.1」分支。这**不**自动等价于实验室里的 which-way 结论；只说明 **几何与 η 联调** 能强烈改变**同一套 V 定义**下的输出。务必另跑 **`ENABLE_ABSORBER=False`** 对照，并把两幅 **`finite_absorber.png`**（或导出 CSV）并排归档。

> **本章边界**  
> 吸收仍是**经典式损耗**在格点上的实现；**不**声称单独解决 Bell/GHZ 的赋值矛盾（见 **`07-archive-ghz.md`**）。

## 5.4　小结

同一泡泡内核上，你多了**两把旋钮**：哪里吃、吃多狠。下一章引入**延迟插入吸收**、**测量相图**与更复杂的**纠缠扫描**脚本（`ce_06`–`ce_10`）：问「**何时**吃」与「**多种测量设定**」会怎样改变图样与相关曲线。

---

# Chapter 5 · Ripple grid: slit absorption and finite absorber–detector

**栅格涟漪：缝口吸收、有限吸收体与探测器**  
*Ripple grid: slit absorption and finite absorber–detector*

> **For general readers — what this picture is about**
>
> - **In plain words**: Treat “measurement” temporarily as **scraping away part of the energy at a cell** — a sponge on the ripple path **drinks a slice**.
> - **What this chapter does**: **Where** you absorb and **how hard** — how fringes fade or distort? This is **geometry + loss**, not mysticism.
> - **Textbook baseline**: Quantum language uses **collapse, which-path information**; classical waves also lose interference under **absorption / detection**. **This book demos classical-style loss on a grid**, not a replacement for quantum measurement theory.
> - **What the book is doing**: `ce_04`–`ce_05` give **comparable curves**; snapshots warn that **the same scalar can mislead** — read with the figure.
> - **For working physicists**: Qualitative direction (**absorption often weakens contrast**) matches intuition; **quantitative** claims bind to this repo’s parameters only.

> **This chapter’s job**  
> Turn “the detector touches a point” into **scannable knobs**: how much is eaten past the slit, how big and how hungry the absorber — watch fringes and visibility **wash out**.

## 5.1 Bridge: measurement = local intervention

Reviews use **Ê = (1−η)E**-style absorption. From `ce_04` on, scripts bake **η**, **absorption columns**, **slit row ranges** into the propagation loop: you **explicitly scrape** part of the field before the next step. No verbal collapse — only **multipliers and geometry**.

## 5.2 `ce_04`: absorption at the slit

`scripts/ce/ce_04_measurement_absorption_at_slit.py` (and variants) scans: when you **eat energy right at the slit**, how downstream fringes degrade. Intuition matches Chapter 3: **more swallowed, less coherent share to interfere**; the curves carry the quantity.

### One-run snapshot (`ce_04` triptych, in-model)

Numbers from **2026-05-05**, repo root, `PYTHONPATH` at root, `MPLBACKEND=Agg`, `PYTHONIOENCODING=utf-8` recommended. The script applies stepped absorption to **upper-slit** neighbor columns (`ABSORB_RATIO` default **0.5**), reads column **`SCREEN_X = WIDTH - 10`**, uses in-script **`compute_visibility`**.

| Item | Content |
| :--- | :--- |
| **Command** | `python scripts/ce/ce_04_measurement_absorption_at_slit.py` |
| **Figure** | **`scripts/ce/measurement_effect.png`** (triptych) |

| Case | `emit_case_dossier` key | Visibility V (snapshot) |
| :--- | :--- | ---: |
| No absorption (double-slit baseline) | `visibility_none_absorb` | ≈ **0.8065** |
| 50% absorption on upper slit | `visibility_partial_absorb` | ≈ **0.7719** |
| 100% absorption on upper slit (single-slit narrative) | `visibility_one_slit_gone` | ≈ **0.8431** |

**Readout**: **partial absorption** drops **V** vs baseline — consistent with eating coherent share. The third row **does not** fall near zero — the script’s **V** is a **peak–valley heuristic**; single-slit envelopes can still undulate; **do not** treat that scalar alone as final word on “interference gone” — use **`measurement_effect.png`** and peak symmetry. Next, **`ce_05`** moves absorption into **2D geometry** — the same “readout-definition sensitivity” returns.

## 5.3 `ce_05`: finite absorber / detector patch

Generalize absorption from “one slit column” to a **2D patch**: finite detector or sponge mid-path. Parameters: position, width, **η**. You see it is not only all-or-nothing — **middling absorbers** can reshape statistics — the same **geometry sensitivity** that later meets **coincidence windows** and **effective sensitive areas**.

### One-run snapshot (`ce_05` default circular absorber, in-model)

From **2026-05-05**, repo root, `PYTHONPATH`, `MPLBACKEND=Agg`, `PYTHONIOENCODING=utf-8`. **`ENABLE_ABSORBER=True`** (default): circle near **(BARRIER_X+5, upper-slit center)**, **radius 10**, **ABSORB_RATIO=0.8**, **STEPS=500**, screen **`SCREEN_X = WIDTH - 10`**.

| Item | Content |
| :--- | :--- |
| **Command** | `python scripts/ce/ce_05_finite_absorber_detector.py` |
| **Figure** | **`scripts/ce/finite_absorber.png`** (screen curve + log field + zoom) |
| **`emit_case_dossier` summary** | `visibility_final` = **0.0** (in-script **`compute_visibility`**: returns 0 when no valid peaks/valleys) |

**Readout**: unlike **`ce_04`**’s “partially eat one slit column,” **2D blob + strong absorption** under these defaults **flattens** the screen curve so the heuristic **V** reads zero — the script takes the “contrast < 0.1” branch. This **does not** auto-equal a lab which-way verdict; it shows **geometry × η** can strongly move output under **one V definition**. Always run **`ENABLE_ABSORBER=False`** control and archive **`finite_absorber.png`** (or CSV) side by side.

> **Chapter boundary**  
> Absorption is still **classical-style loss** on lattice sites; it **does not** claim to settle Bell/GHZ assignment tensions alone (see **`07-archive-ghz.md`**).

## 5.4 Close

On the same bubble kernel you gained **two knobs**: where to eat, how hard. Next chapter adds **delayed insertion of absorption**, **measurement phase diagrams**, and richer **entanglement scans** (`ce_06`–`ce_10`): **when** you eat and **many measurement settings** — how patterns and correlation curves move.
