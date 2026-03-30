# -*- coding: utf-8 -*-
"""
结构化「实验档案」输出，供人审与 AI 审阅、挑错、质疑数据与假设。

用法（每个测试脚本末尾）:
    from experiment_dossier import emit_case_dossier
    emit_case_dossier(__file__, constants={...}, observed={...}, artifacts=[...])

stdout 中会包含 EXPERIMENT_DOSSIER_JSON ... END 块，便于 grep/解析进 suite_report.json。
"""
import json
import os
import time

MARK_JSON_BEGIN = "======== EXPERIMENT_DOSSIER_JSON_BEGIN ========"
MARK_JSON_END = "======== EXPERIMENT_DOSSIER_JSON_END ========"
MARK_HDR = "======== EXPERIMENT_DOSSIER_FOR_AI_REVIEW ========"


# 与 run_unified_suite 中 Job.script 主文件名一致；缺省时 emit 仍会用文件名生成最小档案。
DOSSIER_BASE = {
    "ce_00_double_slit_demo.py": {
        "purpose_zh": "双缝几何下展示离散链式传播能否形成类干涉屏上分布。",
        "purpose_en": "Demo double-slit-like screen pattern under discrete neighbor propagation.",
        "code_principle_zh": "Numba 核 `chain_explosion_numba.propagate_double_slit`：每步将格点能量按 A/S/B 权重分到邻格并乘 λ；挡板布尔掩模开孔。",
        "code_principle_en": "JIT neighbor split with directional A,S,B and λ; boolean barrier slits.",
        "assumptions_zh": [
            "二维矩形网格足够大，边界效应未单独建模。",
            "单点源初始化；未引入色散/色散关系。",
            "干涉可读性依赖人为选取的 A,S,B,λ 与缝几何。",
        ],
        "expected_zh": "屏上出现多峰结构或条纹趋势；峰数与对比度随参数可变。",
        "expected_en": "Multi-peak or fringe-like screen profile.",
        "procedure_zh": [
            "初始化网格与双缝挡板",
            "重复调用 propagate_double_slit",
            "取挡板右侧固定 X 列 screen，绘图",
        ],
        "engine": "chain_explosion_numba.propagate_double_slit",
    },
    "ce_01_visibility_vs_screen_distance.py": {
        "purpose_zh": "扫描屏距（传播步数proxy），记录干涉对比度 V 是否随距离变化。",
        "purpose_en": "Scan effective screen distance vs fringe visibility V.",
        "code_principle_zh": "同一双缝设置，多个 SCREEN_X；每距离同步长传播；本地计算 V。",
        "code_principle_en": "Same slit/barrier; vary screen column index and steps.",
        "assumptions_zh": [
            "对比度定义与脚本内 compute_visibility 一致。",
            "总能量未归一化时数值量级会爆涨；V 仍基于相对起伏。",
        ],
        "expected_zh": "模型常给出 V 随距离下降（内禀扩散叙事）；需与均匀衰减类解释区分。",
        "expected_en": "Often decreasing V with distance (model-specific).",
        "procedure_zh": ["多 screen_x 循环", "每列传播", "汇总 V 并绘图"],
        "engine": "chain_explosion_numba.propagate_double_slit",
    },
    "ce_02_double_slit_screen_statistics.py": {
        "purpose_zh": "单次长跑后做屏上峰谷统计、对称性、对比度，定量描述条纹质量。",
        "purpose_en": "Single-run screen statistics: peaks, symmetry, visibility.",
        "code_principle_zh": "与 ce_00 同核；额外在 Python 层找局部极大与简化的 V。",
        "code_principle_en": "Same kernel; peak finding & visibility in Python.",
        "assumptions_zh": ["主峰判定用阈值 mean*0.5；启发式非唯一。"],
        "expected_zh": "多主峰且 V>某阈值则打印「明显干涉」类信息。",
        "expected_en": "Several peaks and non-trivial V.",
        "procedure_zh": ["传播 STEPS 步", "取屏列", "峰谷与对称性输出", "保存屏列曲线图"],
        "engine": "chain_explosion_numba.propagate_double_slit",
    },
    "ce_03_visibility_vs_side_coupling_S.py": {
        "purpose_zh": "在固定几何下扫侧向耦合 S，观察 V–S 关系。",
        "purpose_en": "Scan lateral coupling S vs visibility.",
        "code_principle_zh": "对每个 S 重跑传播至 SCREEN_X，计算 V。",
        "code_principle_en": "Repeat propagation per S value.",
        "assumptions_zh": [
            "S 列表离散；未做连续外推。",
            "其余 A,B,λ 固定。",
        ],
        "expected_zh": "V 通常随 S 变化；具体单调性依赖网格与距离。",
        "expected_en": "V varies with S; monotonicity not guaranteed a priori.",
        "procedure_zh": ["for S in S_values", "传播", "算 V", "plot & savefig"],
        "engine": "chain_explosion_numba.propagate_double_slit",
    },
    "ce_04_measurement_absorption_at_slit.py": {
        "purpose_zh": "缝后不同吸收强度对屏条纹的对比示意（测量/路径信息 toy）。",
        "purpose_en": "Slit-side absorption strength vs fringe pattern (toy measurement).",
        "code_principle_zh": "使用 `propagate_double_slit_slit_absorb`（缝邻域按比率抽走能量）。",
        "code_principle_en": "Slit-region absorption variant kernel.",
        "assumptions_zh": ["吸收率离散档位", "未建模探测器量子效率谱"],
        "expected_zh": "强吸收下条纹对比下降或形态改变。",
        "expected_en": "Contrast changes with absorption scenario.",
        "procedure_zh": ["多场景循环", "传播", " subplot 对比"],
        "engine": "chain_explosion_numba.propagate_double_slit_slit_absorb",
    },
    "ce_05_finite_absorber_detector.py": {
        "purpose_zh": "有限圆形吸收体（路径探测）对场的扰动示意。",
        "purpose_en": "Finite circular absorber mask perturbation.",
        "code_principle_zh": "`propagate_double_slit_absorber_mask` + 圆掩模。",
        "code_principle_en": "Absorber boolean mask + kernel.",
        "assumptions_zh": ["圆域吸收简化为每步乘法抽能"],
        "expected_zh": "吸收体存在时屏分布相对基线不对称或减弱。",
        "expected_en": "Pattern differs from baseline with absorber.",
        "procedure_zh": ["设圆掩模", "传播", "成像"],
        "engine": "chain_explosion_numba.propagate_double_slit_absorber_mask",
    },
    "ce_06_delayed_choice_absorber.py": {
        "purpose_zh": "中途开启/插入吸收影响的 thought-experiment 风格模拟。",
        "purpose_en": "Mid-run absorber insertion (delayed-choice style).",
        "code_principle_zh": "分阶段传播参数或掩模变更。",
        "code_principle_en": "Multi-phase propagation / mask change.",
        "assumptions_zh": ["时间步与「延迟」仅为离散步数隐喻"],
        "expected_zh": "后期插入改变后续场演化结果。",
        "expected_en": "Late insertion alters downstream field.",
        "procedure_zh": ["前半传播", "变更吸收/掩模", "后半传播"],
        "engine": "chain_explosion_numba (absorber variant)",
    },
    "ce_07_measurement_phase_diagram_scan.py": {
        "purpose_zh": "多参数格子扫描测量「相图」式拼图。",
        "purpose_en": "Multi-parameter scan panels.",
        "code_principle_zh": "嵌套循环改变吸收体位置/尺度/率并成像。",
        "code_principle_en": "Nested loops over measurement-like parameters.",
        "assumptions_zh": ["扫描网格稀疏；非物理参数空间完备搜索"],
        "expected_zh": "拼图展示不同区域内条纹/强度形态差异。",
        "expected_en": "Panel map of qualitative pattern changes.",
        "procedure_zh": ["嵌套扫描", "每格成像子图"],
        "engine": "chain_explosion_numba",
    },
    "ce_08_entanglement_split_wavepackets.py": {
        "purpose_zh": "分裂波包 + 双探测器几何，示意「纠缠风格」能量分配。",
        "purpose_en": "Split packets & detector geometry (illustrative).",
        "code_principle_zh": "`propagate_split_energy` 将能量分到两条支路格点。",
        "code_principle_en": "split_energy kernel branches energy.",
        "assumptions_zh": [
            "「纠缠」仅为同一网格上演化规则，非希尔伯特张量积形式。",
        ],
        "expected_zh": "两路相关结构出现在能量场上。",
        "expected_en": "Correlated structure in two branches (energy view).",
        "procedure_zh": ["初始化", "split 传播", "双探测器统计/绘图"],
        "engine": "chain_explosion_numba.propagate_split_energy",
    },
    "ce_09_entanglement_with_phase_field.py": {
        "purpose_zh": "在能量之外维护相位场，观察相干/相关可视化。",
        "purpose_en": "Phase field + energy on lattice.",
        "code_principle_zh": "`propagate_split_phase` 同时更新相位。",
        "code_principle_en": "Phase-carrying split propagation.",
        "assumptions_zh": ["相位离散更新规则为模型定义，非推导自 QM 相位手册"],
        "expected_zh": "相位与强度图样共同展示。",
        "expected_en": "Combined phase-intensity visualization.",
        "procedure_zh": ["split+phase 传播", "成像"],
        "engine": "chain_explosion_numba.propagate_split_phase",
    },
    "ce_10_entanglement_distance_scan.py": {
        "purpose_zh": "纠缠支路参数随等效距离扫描，看趋势曲线。",
        "purpose_en": "Distance-like scan for split-phase setup.",
        "code_principle_zh": "多 WIDTH 或距离 proxy 循环 + 每 run 指标。",
        "code_principle_en": "Loop over distance proxy; record metric.",
        "assumptions_zh": ["步内/路径上若做归一则须读脚本内具体实现"],
        "expected_zh": "曲线展示随距离衰减或振荡类趋势（模型依赖）。",
        "expected_en": "Trend curve vs distance proxy.",
        "procedure_zh": ["距离列表", "多次完整模拟", "savefig 曲线"],
        "engine": "chain_explosion_numba.propagate_split_phase",
    },
    "verify_born_rule.py": {
        "purpose_zh": "比较「连续场屏分布」与「蒙特卡洛光子累计屏分布」是否相似，讨论波恩规则类比。",
        "purpose_en": "Compare continuous field screen vs MC photon histogram.",
        "code_principle_zh": "ce_engine_v2: `propagate_double_slit_n_steps` + `run_monte_carlo`；皮尔逊 r。",
        "code_principle_en": "Fused steps field vs random walk photons; Pearson r.",
        "assumptions_zh": [
            "光子随机游走权重与连续分裂比例一致化假设。",
            "有限光子数与随机种子引入统计涨落。",
            "r 高不代表已在测度论意义上证明 Born。",
        ],
        "expected_zh": "二者分布形状高度相关则叙事上支持「|ψ|² 类比」；阈值见 runner strict/relaxed。",
        "expected_en": "High Pearson r between two screen vectors.",
        "procedure_zh": ["连续场", "固定种子 MC", "corrcoef", "画图"],
        "engine": "ce_engine_v2",
    },
    "verify_uncertainty.py": {
        "purpose_zh": "通过缝宽扫描与角展宽拟合，记录幂律指数 α（现象层），不与 -1 做硬等式门禁。",
        "purpose_en": "Slit width scan; fit exponent alpha (phenomenological).",
        "code_principle_zh": "ce_engine_v2 传播 + 屏上宽度指标 + log-log 拟合。",
        "code_principle_en": "Same engine; extract width metric; polyfit log-log.",
        "assumptions_zh": [
            "σ_θ 的操作定义来自脚本几何。",
            "α 拟合受离散与近场影响。",
        ],
        "expected_zh": "得到有限 α 与内图；用于描述「趋势」而非封印式定理。",
        "expected_en": "Finite alpha and diagnostic figure.",
        "procedure_zh": ["多缝宽", "传播", "拟合", "拼图保存"],
        "engine": "ce_engine_v2",
    },
    "discover_visibility_decay.py": {
        "purpose_zh": "强调模型预言：对比度可随传播距离下降，并与叙事「QM 不衰减需退相干」对照。",
        "purpose_en": "Visibility vs distance as model prediction / narrative.",
        "code_principle_zh": "多 SCREEN（或距离）扫描 V，可选指数拟合特征长度。",
        "code_principle_en": "Scan V(d); optional exp fit.",
        "assumptions_zh": ["特征长度 d0 依赖当前 A,S,B,λ 与网格"],
        "expected_zh": "V 末端低于初值；runner 硬检查该单调方向。",
        "expected_en": "End V < start V (suite gate).",
        "procedure_zh": ["距离列表", "每点完整传播", "衰减率总结图"],
        "engine": "ce_engine_v2",
    },
    "discover_measurement_continuity.py": {
        "purpose_zh": "吸收率缓慢增加时可见度轨迹是否呈现突变阈（坍缩叙事对照）。",
        "purpose_en": "Visibility vs absorption ratio continuity check.",
        "code_principle_zh": "带吸收掩模多步传播 + 扫描 ratio 序列。",
        "code_principle_en": "Absorber mask kernel; scan absorption ratio.",
        "assumptions_zh": ["[OK]/[警告] 判据阈值 0.15 为脚本常数"],
        "expected_zh": "stdout 出现 [OK] 或 [警告]；后者 suite 仍可能 PASS（软通过）。",
        "expected_en": "Threshold verdict line for suite parser.",
        "procedure_zh": ["扫描吸收率", "记录 V", "第二扫描（若存在）"],
        "engine": "ce_engine_v2 + chain_explosion set_circle_mask等",
    },
    "discover_coupling_constant.py": {
        "purpose_zh": "在参数空间粗扫/细扫 S（或 S/A），找「最优」耦合以示 toy 标定。",
        "purpose_en": "Coupling scan / argmax illustrative.",
        "code_principle_zh": "重复双缝运行 + 目标函数（如可见度）。",
        "code_principle_en": "Repeated runs; objective on visibility or similar.",
        "assumptions_zh": ["最优值依赖目标定义与搜索网格"],
        "expected_zh": "给出最优 S/A 数值与曲线；非基本常数宣称。",
        "expected_en": "Best S/A under scripted objective.",
        "procedure_zh": ["粗扫", "细扫", "保存相图/曲线"],
        "engine": "ce_engine_v2",
    },
    "explore_lorentz_selfcheck.py": {
        "purpose_zh": "与格点无关：检验代码中使用的洛伦兹速度合成公式数值自洽。",
        "purpose_en": "Off-lattice algebraic SR composition sanity check.",
        "code_principle_zh": "一元函数 add / inv_boost_velocity 浮点误差界内检查。",
        "code_principle_en": "Pure float Einstein addition and inverse boost.",
        "assumptions_zh": ["一维同向；c=1", "不与离散光锥因果混淆"],
        "expected_zh": "交换/结合近零误差；v'=1；并保存误差条形图。",
        "expected_en": "Commute/assoc ~0; vprime~1.",
        "procedure_zh": ["代数样点", "判定 VERDICT", "savefig"],
        "engine": "pure Python / numpy scalars",
    },
    "explore_visibility_vs_uniform_loss.py": {
        "purpose_zh": "区分「几何导致的 V 变化」与「每步全局标度 loss」：V 应对后者近似不变，总强度应下降。",
        "purpose_en": "Uniform per-step loss vs visibility (scale invariance of V).",
        "code_principle_zh": "ce_engine_v2 propagate；可选每步 grid*= (1-η)。",
        "code_principle_en": "Optional global damping after each step.",
        "assumptions_zh": ["η 常数；无空间关联噪声"],
        "expected_zh": "median(loss/base) < 1；V 两曲线贴近。",
        "expected_en": "Intensity ratio <1; V overlap.",
        "procedure_zh": ["多屏距", "有/无 loss 双轨", "对比 V 与 sum I"],
        "engine": "ce_engine_v2",
    },
    "explore_energy_budget.py": {
        "purpose_zh": "审计 sum(E) 逐步是否增长（未全局归一核的常见行为）。",
        "purpose_en": "Total grid sum growth audit.",
        "code_principle_zh": "每步 propagate_double_slit 后记录 sum。",
        "code_principle_en": "Track sum(E) stepwise.",
        "assumptions_zh": ["总和非概率守恒量；与 |ψ|² 守恒不是同一对象"],
        "expected_zh": "步间中位比 >1（与当前文档一致）。",
        "expected_en": "Median ratio >1 (suite gate).",
        "procedure_zh": ["双缝设置", "MAX_STEPS 循环", "画图"],
        "engine": "ce_engine_v2",
    },
    "explore_causal_front.py": {
        "purpose_zh": "无障碍点源：最右激活列速度是否约为 1 格/步（离散光锥隐喻）。",
        "purpose_en": "Causal front dx/dt ~ 1 cell/step.",
        "code_principle_zh": "每步 1 次 propagate；找 max x where E>thresh。",
        "code_principle_en": "Thresholded rightmost active column.",
        "assumptions_zh": ["THRESH 选取影响前缘检测"],
        "expected_zh": "dx/dt 中位数 ~1（带宽式门禁）。",
        "expected_en": "Median front speed ~1.",
        "procedure_zh": ["点源", "逐步推进", "记录 front 序列"],
        "engine": "ce_engine_v2 propagate_double_slit_n_steps",
    },
    "explore_fringe_spacing_vs_slit.py": {
        "purpose_zh": "扫缝距 d，测屏上主条纹间隔 Δy；log-log 斜率与远场 1/d 类比对照。",
        "purpose_en": "Fringe spacing vs slit gap; log-log slope.",
        "code_principle_zh": "每 d 双缝几何重配，传播，峰值/FFT 估周期。",
        "code_principle_en": "Peak spacing or FFT dominant period.",
        "assumptions_zh": ["近场/离散使斜率不必为 -1"],
        "expected_zh": "可解析斜率；与 -1 偏离为备注非硬失败（主 suite）。",
        "expected_en": "Finite fitted slope.",
        "procedure_zh": ["D_LIST 循环", "传播", "拟合 log d vs log Δy"],
        "engine": "ce_engine_v2",
    },
    "explore_causal_cone_anisotropy.py": {
        "purpose_zh": "比较 L1 菱形前缘与轴向+前向因果比 R，落在仓库 GOLD 公差内。",
        "purpose_en": "Anisotropy ratio R_L1/R_ax vs gold tolerance.",
        "code_principle_zh": "多方向推进测最远激活曼哈顿/轴向步。",
        "code_principle_en": "Directional front metrics (script-specific).",
        "assumptions_zh": ["GOLD 随内核版本固化；变更核须改常量"],
        "expected_zh": "比值落入 run_unified_suite 公差；图非空。",
        "expected_en": "Ratio within tolerance + substantive PNG.",
        "procedure_zh": ["初始化点源", "传播", "比 R", "savefig"],
        "engine": "ce_engine_v2 或专用循环",
    },
    "explore_relativity_light_speed_invariant.py": {
        "purpose_zh": "公式层逆变 v' 是否给出 c（与格点光锥叙述分离）。",
        "purpose_en": "Formula-layer v' equals c check.",
        "code_principle_zh": "显式洛伦兹逆变数值代入。",
        "code_principle_en": "Explicit inverse boost numbers.",
        "assumptions_zh": ["与 relativity_final 格子演示互不替代"],
        "expected_zh": "stdout [OK] + v'≈1；图非空。",
        "expected_en": "OK line + vprime~1.",
        "procedure_zh": ["计算", "打印标记", "简单图"],
        "engine": "formula + matplotlib",
    },
    "explore_double_slit_mirror_parity.py": {
        "purpose_zh": "对称双缝几何下屏分布镜像残差 asym 与相关系数落在回归带。",
        "purpose_en": "Mirror parity residual bands.",
        "code_principle_zh": "双缝 + 屏列翻转对比 + 相关。",
        "code_principle_en": "flip screen column compare.",
        "assumptions_zh": ["离散核破坏完美对称；带宽为经验非物理证明"],
        "expected_zh": "asym、r_mirror 在 MIRROR_* 常量带内。",
        "expected_en": "Metrics within regression bands.",
        "procedure_zh": ["跑双缝", "镜像比较", "savefig"],
        "engine": "ce_engine_v2",
    },
    "explore_critique_01_unification_scope.py": {
        "purpose_zh": "文档/宣称边界：何为可审计「统一」对标。",
        "purpose_en": "Checklist for auditable unification claims.",
        "code_principle_zh": "纯文字排版成图 + 固定 [OK] 行。",
        "code_principle_en": "Text figure + marker line.",
        "assumptions_zh": ["不运行物理格点传播"],
        "expected_zh": "图非空且含 critique_01 标记。",
        "expected_en": "PNG + OK marker.",
        "procedure_zh": ["打印行", "matplotlib text", "savefig"],
        "engine": "matplotlib only",
    },
    "explore_critique_02_bell_hypothesis_boundary.py": {
        "purpose_zh": "Bell/坍缩相关假说的表述边界提醒。",
        "purpose_en": "Bell/collapse hypothesis boundary note.",
        "code_principle_zh": "叙事图 + 标记行。",
        "code_principle_en": "Doc figure.",
        "assumptions_zh": [],
        "expected_zh": "critique_02 标记 + 图。",
        "expected_en": "Marker + PNG.",
        "procedure_zh": ["文本", "savefig"],
        "engine": "matplotlib",
    },
    "explore_critique_03_analogy_vs_mechanism.py": {
        "purpose_zh": "类比 vs 同一机制措辞区分。",
        "purpose_en": "Analogy vs mechanism language.",
        "code_principle_zh": "叙事图 + 标记。",
        "code_principle_en": "Doc figure.",
        "assumptions_zh": [],
        "expected_zh": "critique_03 标记。",
        "expected_en": "OK line.",
        "procedure_zh": ["savefig"],
        "engine": "matplotlib",
    },
    "explore_critique_04_sr_not_derived_from_lattice.py": {
        "purpose_zh": "强调格点前缘 ~1 格/步与公式层 SR 不是同一条推导链。",
        "purpose_en": "Lattice front vs SR formula separation.",
        "code_principle_zh": "可能含简短格点模拟 + 公式 v' 输出。",
        "code_principle_en": "Combined narrative + numbers.",
        "assumptions_zh": ["v_grid 与 v' 双通道汇报"],
        "expected_zh": "critique_04 标记 + 两速度落入检查窗。",
        "expected_en": "Two-speed checks in window.",
        "procedure_zh": ["模拟/公式", "print OK", "fig"],
        "engine": "ce_engine_v2 / formula",
    },
    "explore_critique_05_decay_nonuniqueness.py": {
        "purpose_zh": "干涉衰减可用均匀 η 通道部分模仿；r_V 门禁。",
        "purpose_en": "Decay channel non-uniqueness; r_V gate.",
        "code_principle_zh": "CE vs uniform loss correlation on V series。",
        "code_principle_en": "Compare V traces.",
        "assumptions_zh": ["r_V 阈值 relaxed/strict"],
        "expected_zh": "高 r_V 提示难区分；非否定几何衰减。",
        "expected_en": "r_V above floor.",
        "procedure_zh": ["双轨迹 V", "corrcoef", "fig"],
        "engine": "ce_engine_v2",
    },
    "explore_critique_06_energy_growth_explosion.py": {
        "purpose_zh": "总能量暴增量级 R_E 与步间比叙事；对「相对论式守恒」误读的反驳材料。",
        "purpose_en": "Energy growth R_E and step ratio narrative.",
        "code_principle_zh": "长步数 sum(E) 曲线。",
        "code_principle_en": "sum(E) trace.",
        "assumptions_zh": ["R_E 门禁量级极大以防数值误判"],
        "expected_zh": "R_E 与 median step ratio 过线。",
        "expected_en": "Huge R_E; median>1.",
        "procedure_zh": ["长跑", "指标", "fig"],
        "engine": "ce_engine_v2",
    },
    "explore_critique_07_fringe_spacing_theory_gap.py": {
        "purpose_zh": "log-log 斜率拟合相对仓库 GOLD；提醒与远场 -1 的理论间隙。",
        "purpose_en": "Fringe slope vs GOLD; theory gap note.",
        "code_principle_zh": "类似 explore_fringe_spacing 的拟合 +  tighter 公差。",
        "code_principle_en": "Fitted slope gold tolerance.",
        "assumptions_zh": ["GOLD 固化于当前内核"],
        "expected_zh": "fitted slope within CRITIQUE07 tolerance. ",
        "expected_en": "Slope near gold.",
        "procedure_zh": ["扫 d", "拟合", "fig"],
        "engine": "ce_engine_v2",
    },
    "verify_interference_decay.py": {
        "purpose_zh": "扩展套件：干涉对比随距离衰减的独立脚本（命名 verify_）。",
        "purpose_en": "Extended: interference decay verify script.",
        "code_principle_zh": "ce_engine_v2 多距离 V。",
        "code_principle_en": "V vs distance.",
        "assumptions_zh": ["与 discover_visibility_decay 叙事可能重叠"],
        "expected_zh": "生成 verify_interference_decay.png。",
        "expected_en": "PNG.",
        "procedure_zh": ["扫描", "plot"],
        "engine": "ce_engine_v2",
    },
    "verify_delayed_choice.py": {
        "purpose_zh": "扩展：延迟选择类几何的一组验证图。",
        "purpose_en": "Extended delayed-choice style figure.",
        "code_principle_zh": "专用屏障/步进。",
        "code_principle_en": "Script-specific barrier schedule.",
        "assumptions_zh": [],
        "expected_zh": "verify_delayed_choice.png。",
        "expected_en": "PNG.",
        "procedure_zh": ["运行", "savefig"],
        "engine": "ce_engine_v2",
    },
    "verify_which_way.py": {
        "purpose_zh": "扩展：which-way 吸收几何对比。",
        "purpose_en": "Extended which-way style.",
        "code_principle_zh": "吸收/双缝组合。",
        "code_principle_en": "Absorption + slits.",
        "assumptions_zh": [],
        "expected_zh": "verify_which_way.png。",
        "expected_en": "PNG.",
        "procedure_zh": ["运行", "savefig"],
        "engine": "ce_engine_v2",
    },
    "chain_explosion_numba.py": {
        "purpose_zh": "为各 `ce_*` 仿真提供共享的二维格点传播核（Numba JIT）。",
        "purpose_en": "Shared 2D lattice propagation kernels (Numba JIT) for ce_* scripts.",
        "code_principle_zh": "每步：格点能量乘衰减 λ，再按轴向权重 A/B 与侧向/对角 S 分配到邻格；`barrier` 布尔挡板禁止向被挡格转移；变体在缝列或布尔掩模上对能量做乘法吸收；另有 `propagate_split_energy` / `propagate_split_phase` 分支与相位更新。",
        "code_principle_en": "Per step: λ damping, A/B/S neighbor split, barrier mask; variants absorb on slit column or mask; split and phase kernels.",
        "assumptions_zh": [
            "场量为非负标量「能量」而非量子振幅；不宣称等价于含时薛定谔方程。",
            "耦合权重 A,S,B,λ 由调用脚本给定；无量纲格点单位。",
            "具体几何（缝位、屏列）由各 `ce_*` 脚本与 barrier 矩阵定义。",
        ],
        "expected_zh": "被 `ce_*` 逐步调用后得到与参数一致的离散演化。",
        "expected_en": "Stepwise calls yield consistent discrete evolution.",
        "procedure_zh": ["由仿真脚本逐步调用各 `propagate_*` 函数"],
        "engine": "numba @jit (this module)",
    },
}


def dossier_fields_for_readme(script_name):
    """
    供 README / suite 报告注入：目的、实现机制、假设列表（与 emit 档案一致）。
    script_name: 例如 'ce_00_double_slit_demo.py'
    """
    base = DOSSIER_BASE.get(script_name) or _default_base(script_name)
    return {
        "purpose_zh": base.get("purpose_zh") or "",
        "code_principle_zh": base.get("code_principle_zh") or "",
        "assumptions_zh": list(base.get("assumptions_zh") or []),
    }


def _default_base(script_name):
    return {
        "purpose_zh": "（未在 DOSSIER_BASE 注册）自动档案：请补全 experiment_dossier.DOSSIER_BASE。",
        "purpose_en": "Auto dossier; extend DOSSIER_BASE.",
        "code_principle_zh": "见脚本正文。",
        "code_principle_en": "See script body.",
        "assumptions_zh": ["未逐项列出"],
        "expected_zh": "脚本末尾自行补充 observed。",
        "expected_en": "Fill observed.",
        "procedure_zh": ["执行 __main__"],
        "engine": "unknown",
    }


def emit_case_dossier(
    script_file,
    constants=None,
    observed=None,
    artifacts=None,
    steps_executed=None,
    extra_assumptions=None,
    reviewer_prompts=None,
):
    """
    script_file: 传入 __file__
    constants: dict 脚本中主要数字参数（原样 JSON 序列化）
    observed: dict 运行结果（数、字符串、verdict）
    artifacts: 产出文件 basename 列表
    steps_executed: 若给定则覆盖 BASE 的 procedure_zh
    extra_assumptions / reviewer_prompts: 额外列表，拼到输出
    """
    script_name = os.path.basename(script_file)
    base = dict(DOSSIER_BASE.get(script_name, _default_base(script_name)))
    assumptions = list(base.get("assumptions_zh") or [])
    if extra_assumptions:
        assumptions.extend(extra_assumptions)

    proc = steps_executed or base.get("procedure_zh") or []

    invites = list(reviewer_prompts or [])
    invites.extend(
        [
            "上述 constants 是否与物理文献标准符号一一对应？若不对应，混淆点在哪里？",
            "observed 中的量是否对网格分辨率/边界条件敏感？能否做一个粗收敛性实验？",
            "assumptions 中哪一条若违背后会推翻结论？",
            "engine 调用链是否可能在某次重构中被悄悄替换？如何冻结回归？",
        ]
    )

    payload = {
        "schema": "experiment_dossier_v1",
        "generated_at_iso": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "case_id": script_name.replace(".py", ""),
        "script_path_hint": script_name,
        "purpose": {"zh": base.get("purpose_zh"), "en": base.get("purpose_en")},
        "code_principle": {
            "zh": base.get("code_principle_zh"),
            "en": base.get("code_principle_en"),
        },
        "engine_module_hint": base.get("engine"),
        "constants_declared": constants or {},
        "assumptions_zh": assumptions,
        "expected_outcome": {
            "zh": base.get("expected_zh"),
            "en": base.get("expected_en"),
        },
        "steps_executed_zh": proc,
        "artifacts_produced": artifacts or [],
        "observed_outcome": observed or {},
        "invited_critiques_for_ai_zh": invites,
    }

    # Human-readable header for log tail readers
    print("\n%s" % MARK_HDR)
    print("[目的] %s" % payload["purpose"]["zh"])
    print("[引擎] %s" % payload["engine_module_hint"])
    print("[假设条目数] %d  |  [邀请质疑条目数] %d" % (len(assumptions), len(invites)))
    if constants:
        print("[常量键] %s" % (", ".join(sorted(constants.keys())[:40]),))
    if observed:
        print(
            "[观测摘要] %s"
            % (json.dumps(observed, ensure_ascii=False, default=str)[:800],)
        )
    print("%s\n" % MARK_HDR.replace("=", "-"))

    print(MARK_JSON_BEGIN)
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    print(MARK_JSON_END)
