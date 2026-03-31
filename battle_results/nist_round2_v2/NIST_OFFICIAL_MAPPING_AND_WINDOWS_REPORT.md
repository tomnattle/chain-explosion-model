# NIST 官方文档对齐：槽位映射与时间窗（completeblind HDF5）

**依据**：NIST *Description of Data*（Bell Test），页面标注 last updated December 23, 2015。  
**完整 URL**：https://www.nist.gov/document/bell-test-data-file-folder-descriptions  

**执行性说明**：本文档只使用**公开页面 + 本仓库 HDF5 内实测结构**；**不**宣称已取得 `bell_analysis_code` / yaml，故凡依赖 yaml 的量（例如 sync 相对 delay → 网格步长）一律标为 **缺口**，不得冒充官方数值。

**机器可读日志**：同目录 `NIST_OFFICIAL_ALIGNMENT_RUN_LOG.json`（由 `nist_official_compliance_report.py` 生成，含前 2500 万行 clicks 的 one-hot 校验结果）。

---

## 1. 槽位（slot）映射——与公开文档 **一致** 的部分

### 1.1 cw45 / processed HDF5 的语义（文档原文要点）

- 处理管线中 **5 字节事件** 里，**字节 2–3（Alice）与 4–5（Bob）** 为 **无符号 16 位整数**。
- 该字表示：在 **Pockels 窗内**，光子可能落在 **16 个 laser cycle / 时间槽** 中的哪一个；**以按位 one-hot 形式编码**。
- 文档表述：**slot 1 对应 bit 0**，…，**slot 16 对应 bit 15**（即 **bit 索引** \(k\in\{0,\ldots,15\}\) 与「第几个槽」差 1）。

### 1.2 本 HDF5 中 `clicks` 的 **官方一致** 解码规则

对 `uint16` 取值 `v`：

| 条件 | 含义 |
|------|------|
| `v == 0` | 该网格行无点击（16 槽皆未置位） |
| `v > 0` 且 `v == 2^k`（单一比特为 1） | **合法 one-hot**：点击落在 **bit 索引 `k`**（文档意义下的 slot \(k+1\)） |
| `v > 0` 且非 2 的幂 | **与公开 one-hot 定义冲突**（应视为数据/解码错误） |

**bit 索引**：`k = log2(v)`（整数），**不得**对非 2 的幂做强行槽位解释。

### 1.3 我们在本文件上做的编码校验（执行结果）

- 已对 **前 25,000,000 行** `alice/clicks` 与 `bob/clicks` 扫描：**所有非零点击均满足 one-hot（2 的幂）**。
- 结论写入 `NIST_OFFICIAL_ALIGNMENT_RUN_LOG.json` → `click_encoding_validation.conforms_to_one_hot_slot_rule: true`。

---

## 2. 槽位 → CHSH 二元 `±1` ——公开文档 **未给出** 的部分（必须单独冻结）

公开页面 **没有** 规定：「bit 索引 \(k\) 如何映射到某一方的 `outcome ∈ {+1,-1}`」。

文档在 **Peter 数据计算** 一节给出的是 **16 列联合结果** 的排序（`++ab`, `+0ab`, `0+ab`, `00ab`，再在 \(ab'\)、\(a'b\)、\(a'b'\) 上重复）——这是 **含「无点击 0」的联合 (Alice,Bob) 粗粒度**，**不是**「单边半个 Pockels 时间窗 = 探测器 +、另半个 = −」的先天性定义。

因此：

- **任何**「例如 \(k\in\{0,\ldots,7\}\Rightarrow +1\)，\(k\in\{8,\ldots,15\}\Rightarrow -1\)」的划分，在本报告依据下均归为 **非官方占位**，不得称为 NIST 文档映射。
- 若要坚持「与论文/官方分析 100% 一致」的 CHSH **二元**口径，**必须**补入：论文补充材料、或 `build_file_txt.py` / yaml 中的读出定义，并 **新开一轮预注册（v2+）**。

---

## 3. Settings（测量设定）——HDF5 与 cw45 字节 **不是同一编码层**

- **cw45 5 字节格式** 字节 1：用 **比特 0–3** 标记 Alice/Bob 的 RNG 设定（「哪一位为 1 表示哪一个设定发生」的 **one-hot 风格**）。
- **本 completeblind HDF5**：`alice/settings`、`bob/settings` 为与 `clicks` **等长**的 `uint8` 流；实测主要取值为 **1 与 2**（工程上常映射为 CHSH 的 `0/1`）。

**结论**：将 `1→0`、`2→1` 用于现有 CHSH 脚本，是 **工程约定**；与 cw45 **字节 1** 的位定义 **不在同一压缩层**。若要做到比特级一致，需对照 **生成该 HDF 的** 程序说明（yaml），而非仅凭公开描述页单行推断。

---

## 4. 时间轴与 trial：**不得**把「扁平网格索引」擅自等同于「官方脉冲 trial」

### 4.1 HDF5 实测事实（completeblind）

- `alice/clicks` 与 `alice/settings` **等长**：`356464574`。
- `alice/laserPulseNumber` 与 `alice/syncNumber` 长度为 **`17656721`**；Bob 侧 `laserPulseNumber` 为 **`15191573`**（与 Alice **不等长**）。
- `grid / len(alice laserPulseNumber) ≈ 20.189`（**非整数**）。
- **本文件未包含** 文档文字里提到的「**每一次点击相对 sync 的原始 delay 数组**」等逐事件物理量（当前目录下列表仅有 clicks/settings/lpn/phase/syncNumber/badSyncInfo 及 config/offsets）。

### 4.2 设置流在网格上的行为（辅助理解，非官方 trial 定义）

对前 500 万行：`settings` 在行与行之间 **频繁变化**（最常见间隔 1 行即变）。说明 **HDF5 行** 至少是 **细于「一次激光脉冲持稳」** 的一个数字化刻度；**不能**未经 yaml 就说「一行 = 一次脉冲 trial」。

### 4.3 与公开文档一致的 **最小** 对齐原则（时间窗层级）

在 **不引入 yaml** 的前提下，文档唯一无争议的双方对齐是：

- **同一 HDF5 行索引 \(i\)**：`alice/*[i]` 与 `bob/*[i]` 属于 **同一对并列采样**（因文档说明 Alice/Bob 合并于 **同一 build 文件、并列流**）。

因此：

- **「严格同期」在网格层的可陈述定义**：配对窗口在 **行索引差** 上取 **0**（`explore_chsh_experiment_alignment` 里以同一 `t = float(i)` 注入 A/B 时自然满足）。这是 **并列流内部一致性**，**不等于** 文档中 **radius 围绕 sync** 的 **物理** coincidence（后者缺数值换算）。

---

## 5. 时间窗（coincidence）配置——按官方逻辑应 **分级**

| 层级 | 定义 | 与公开文档关系 | 本仓库可用性 |
|------|------|------------------|--------------|
| **A. 并列流行内** | 行索引差 `Δi = 0` | 符合「合并后并列数组」结构 | **可用**；对应此前 `strict` `window=0`（以 `t`=行索引解释）。 |
| **B. radius / sync 物理窗** | cw45: Alice radius 4、Bob 5；**相对 sync 的 delay** 由 **yaml** 决定 | 文档 **明确** 写出需 yaml / `build_file_txt.py` | **本 HDF5 + 公开页 alone** → **无法** 唯一换算成 `Δi`；**不得**称为官方给定 15 行。 |
| **C. v1 探索 `window=15`** | 行索引单位 | **无任何** 公开公式支持该整数 | 标为 **HEURISTIC_ONLY**（见 JSON 日志）。 |

---

## 6. 与第一场（v1）管道的关系（避免 silently 偏差）

| 项目 | v1 做法 | 本官方对齐审查结论 |
|------|---------|----------------------|
| 槽位 one-hot | 使用 2 的幂 | **与文档一致**（已批量验证） |
| 槽位→±1 | 0–7 / 8–15 | **非**公开文档内容 → **不得称官方** |
| `t` | 行索引 | **并列流自洽**；**非**经 yaml 证明的脉冲相位时间 |
| `standard` 窗 15 | 行索引 | **探索启发式**；**非** radius 官方换算 |

---

## 7. 你需要二次核对时的检查清单

1. `NIST_OFFICIAL_ALIGNMENT_RUN_LOG.json` 中 `click_encoding_validation` 是否为 `true`（你本地可重跑 `python nist_official_compliance_report.py`）。
2. 是否接受：**在未取得 yaml/论文读出定义前，CHSH 二元 outome 无「官方唯一映射」**。
3. 若必须继续算 `S`：**请书面冻结**「二元 outome 来自何处」（论文定理式、SI 表、或自有 v2 假设），并 **新开归档**，勿与「官方文档唯一来源」混称。
4. 若必须 **radius 级** coincidence：**优先**取得 `bell_analysis_code` / yaml，再把 **delay→网格步长** 写进 `chsh_preregistered_config_nist_v2` 的定稿。

---

## 8. 命令（可复现）

```bash
python nist_official_compliance_report.py ^
  --hdf5 data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5 ^
  --out-json battle_results/nist_round2_v2/NIST_OFFICIAL_ALIGNMENT_RUN_LOG.json
```

（Linux/macOS 将 `^` 换为 `\`。）

---

*本报告为「第二场」对官方公开描述的合规拆解；数值 CHSH 结论在未补全二元 outcome 与物理窗换算前，不作为「与论文逐比特等价」的断言。*
