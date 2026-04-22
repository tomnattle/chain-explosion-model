# 最新成果文档：同一样本、不同统计量的 Bell 指标分歧

## 1. 文档目的

本文件用于固化当前阶段最关键成果：  
在**同一批隐变量样本**上，仅改变相关性统计定义，就会得到三种不同的 \(S\) 上限区间。  
这说明争议核心在“统计对象定义”，而不在“是否存在相关性”。

---

## 2. 本次使用的脚本与环境

- 脚本：`scripts/explore/explore_bell_metric_comparison.py`
- 环境激活：`activate_conda.ps1`（默认 `audit-api`）
- 运行命令：

```powershell
./activate_conda.ps1
python "scripts/explore/explore_bell_metric_comparison.py"
```

脚本会输出：
- 固定 CHSH 角组的三类 \(S\)
- 角度网格上的粗粒度全局 \(|S|\) 最大值（0..178，步长 2 度）
- `E(Δ)` 对照表
- 曲线图：`bell_metric_comparison_curves.png`

---

## 3. 三类指标定义（务必区分）

### 3.1 Binary（标准 CHSH 对象）

- 响应：\(A,B \in \{-1,+1\}\)
- 例：\(A=\mathrm{sign}(\cos(\lambda-a))\), \(B=-\mathrm{sign}(\cos(\lambda-b))\)
- 相关函数：\(E_{binary}(a,b)=\langle A\cdot B \rangle\)
- CHSH：
  \[
  S=E(a,b)-E(a,b')+E(a',b)+E(a',b')
  \]

这是 Bell-CHSH 原命题下的标准可比对象。

### 3.2 Continuous Raw（连续原始相关）

- 响应：\(A=\cos(\lambda-a)\), \(B=-\cos(\lambda-b)\)
- 相关函数：\(E_{raw}(a,b)=\langle A\cdot B\rangle\)

该指标是连续响应相关量，不是 dichotomic CHSH 的同一对象。

### 3.3 Continuous NCC（归一化连续相关）

- 定义：
  \[
  E_{ncc}(a,b)=\frac{\langle A\cdot B\rangle}{\sqrt{\langle A^2\rangle\langle B^2\rangle}}
  \]
- 在各向同性 + 余弦响应下，会把 `raw` 曲线按功率因子重标定。

该量可用于信号归一化分析，但不能自动等同于标准 CHSH 命题。

---

## 4. 当前实测结果（同一样本）

脚本一次运行得到（符号取决于约定，关注绝对值）：

- `|S_binary|max ≈ 2.000000`
- `|S_continuous_raw|max ≈ 1.414069`
- `|S_continuous_ncc|max ≈ 2.828065`

固定一组常见角度时，也可观测到对应层级：

- `S_binary ≈ -2.000000`
- `S_continuous_raw ≈ -1.194216`
- `S_continuous_ncc ≈ -2.389139`

---

## 5. 关键解释（当前最稳妥表述）

1. **同一隐变量样本**可以支持多种统计定义。  
2. 不同统计定义下 \(S\) 的数值规模可以显著不同。  
3. 因此，“是否达到 \(2\sqrt{2}\)”必须先绑定清楚：使用的是哪一个 \(E\) 与哪一种实验可观测定义。  
4. 这一步不是哲学争论，而是**统计对象一致性**问题。

---

## 6. 当前边界与风险提示

- 本项目尚未证明“哪种统计量才是唯一正确物理量”。  
- 当前结果证明的是：**定义差异足以解释数值分歧**。  
- 若将 NCC 结果用于 Bell 命题比较，必须先给出严格的实验可观测映射与公平采样条件论证。  
- 三体/GHZ 扩展尚未完成，不应超范围宣称。

---

## 7. 下一步计划（建议）

1. 增加“同一数据流、三统计管线”的交互可视化页面。  
2. 输出统一 `METRICS.md`，把 `E_binary / E_raw / E_ncc` 与适用命题逐项绑定。  
3. 增加对照实验：`no-chiral / random-phase / baseline`，验证指标辨识力。  
4. 后续若对外发布，附带最小复现实验脚本和固定随机种子。

---

## 8. 一句话结论（对外口径）

我们当前最可靠的成果不是“已经推翻某理论”，而是：  
**在同一样本上，不同相关性定义会系统地产生不同 \(S\) 数值区间；因此任何结论必须先锁定统计对象与实验映射。**

