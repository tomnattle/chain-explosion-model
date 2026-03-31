# NIST Completeblind Archive
# NIST Completeblind 第一轮归档

这个目录保存的是第一次严肃实验的冻结快照。它记录了一条完整链路：从公开 HDF5 数据，到事件 CSV，再到双协议 CHSH 对齐、数值结果和解释说明。  
This directory preserves the frozen snapshot of the first serious experiment. It records a full chain: from public HDF5 data to event CSV, then to dual-protocol CHSH alignment, numerical results, and interpretive notes.

这个归档的研究价值不在于它给出了“成功故事”，而在于它把一次清楚的失败结论也固定保存了下来。  
The research value of this archive does not lie in offering a “success story,” but in preserving a clear failed conclusion in fixed form.

## Archive Position

这是一份固定归档，不应被后续叙事反向修改。如果未来产生新实验，应新建目录，而不是覆盖这里的文件。  
This is a fixed archive and should not be retroactively altered by later narratives. If future experiments are produced, they should be placed in new directories rather than overwriting the files here.

## Core Judgment

这轮归档的结论可以压缩成两句：工程通过，论点未通过。  
The conclusion of this archive can be compressed into two sentences: the engineering passed, and the thesis did not.

更具体地说：  
More specifically:

- `engineering_pass = true`
- `thesis_pass = false`

失败原因是 strict 协议下的 \(S\) 没有落入锁定阈值之内。  
The failure reason is that the value of \(S\) under the strict protocol did not fall within the locked threshold.

\[
S_{\mathrm{strict}} = 2.336275858171887 > 2.02.
\]

## Numerical Summary

根据归档结果文件 [battle_result.json](D:/workspace/golang/nakama/chain-explosion-model/battle_results/nist_completeblind_2015-09-19/battle_result.json)，关键数值如下。  
According to the archival result file [battle_result.json](D:/workspace/golang/nakama/chain-explosion-model/battle_results/nist_completeblind_2015-09-19/battle_result.json), the key numbers are as follows.

### Strict Protocol

- `window = 0.0`
- `pair_count = 136632`
- `Eab = 0.9989774338237003`
- `Eabp = 0.9980977239045323`
- `Eapb = 0.9979612207190944`
- `Eapbp = 0.65876052027544`
- `S = 2.336275858171887`

### Standard Protocol

- `window = 15.0`
- `pair_count = 148670`
- `Eab = 0.9918413278942186`
- `Eabp = 0.9703577587147753`
- `Eapb = 0.9473404037508701`
- `Eapbp = 0.07015227532787607`
- `S = 2.8393872150319877`

这说明同一批数据在不同配对窗口下给出了显著不同的 \(S\) 量级，但在本次归档锁定的门槛下，strict 结果仍然不满足 thesis gate。  
This shows that the same data produced significantly different \(S\)-levels under different pairing windows, but under the thresholds locked for this archive, the strict result still did not satisfy the thesis gate.

## Protocol Context

本轮归档所使用的关键配置快照包括：  
The key configuration snapshots used in this archive include:

- `nist_convert_config.snapshot.json`
- `chsh_preregistered_config_nist_index.snapshot.json`

它们定义了事件转换方式、配对窗口和 thesis gate，因此构成了这次归档结论的真正条件边界。  
They define the event-conversion method, the pairing windows, and the thesis gate, and therefore constitute the actual boundary conditions of the conclusion in this archive.

## Important Files

建议优先查看以下文件：  
The following files are recommended as primary reading:

- [battle_result.json](D:/workspace/golang/nakama/chain-explosion-model/battle_results/nist_completeblind_2015-09-19/battle_result.json)  
  核心数值结果。  
  Core numerical result.
- [INTERPRETATION_NOTE.md](D:/workspace/golang/nakama/chain-explosion-model/battle_results/nist_completeblind_2015-09-19/INTERPRETATION_NOTE.md)  
  对解释边界的补充说明。  
  Supplementary note on interpretive boundaries.
- [BATTLE_ARCHIVE.json](D:/workspace/golang/nakama/chain-explosion-model/battle_results/nist_completeblind_2015-09-19/BATTLE_ARCHIVE.json)  
  归档元数据、来源和命令记录。  
  Archive metadata, sources, and command records.
- [figure_chsh_alignment.png](D:/workspace/golang/nakama/chain-explosion-model/battle_results/nist_completeblind_2015-09-19/figure_chsh_alignment.png)  
  当时输出的关键对齐图。  
  The key alignment figure produced in that run.

## Interpretation

这一轮结果最值得保留的，不是 wide-window 下出现了较高的 \(S\)，而是仓库明确拒绝把它直接包装成“自动成功”。文档保留了这样一个更成熟的姿态：同一批数据可以支持协议敏感性讨论，但并不因此自动满足当时预注册的 thesis gate。  
What is most worth preserving in this round is not simply that a relatively high \(S\) appeared under the wide-window protocol, but that the repository explicitly refused to package that as an “automatic success.” The documentation preserves a more mature posture: the same data may support a discussion of protocol sensitivity, but do not thereby automatically satisfy the preregistered thesis gate in force at that time.

从研究方法论角度说，这个归档的重要性很高，因为它说明项目并不是通过删除失败结果来维持叙事。  
From a methodological standpoint, this archive is highly important because it shows that the project does not maintain its narrative by deleting failed results.

## Source Note

关于 NIST 数据结构的公开说明，可参见：  
For public documentation of the NIST data structure, see:

[NIST Bell Test Data File/Folder Descriptions](https://www.nist.gov/document/bell-test-data-file-folder-descriptions)
