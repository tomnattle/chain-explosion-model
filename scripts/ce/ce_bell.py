import logging
import time

import numpy as np
import matplotlib.pyplot as plt
from numba import jit

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ============================================================
# 参数配置
# ============================================================

HEIGHT = 101
WIDTH = 400
A = 1.0
S = 0.4
B = 0.05
LAMBDA = 0.95
SOURCE_X = 10
SOURCE_Y = HEIGHT // 2
STEPS = 800
SPLIT_X = WIDTH // 4
SPLIT_ANGLE = 8
DETECTOR_X = 300

# 偏振片角度扫描
ANGLES = np.linspace(0, 90, 10)  # 0° 到 90°，10个点

# ============================================================
# 初始化（加入偏振）
# ============================================================

def init_grids(*, quiet=False):
    energy_grid = np.zeros((HEIGHT, WIDTH))
    phase_grid = np.zeros((HEIGHT, WIDTH))
    polarization_grid = np.zeros((HEIGHT, WIDTH))  # 偏振方向（0-360度）

    for y in range(HEIGHT):
        dy = y - SOURCE_Y
        energy_grid[y, SOURCE_X] = 100.0 * np.exp(-dy**2 / 50)
        polarization_grid[y, SOURCE_X] = 0.0  # 初始偏振为0°

    if not quiet:
        e0 = float(np.sum(energy_grid))
        ymax = int(np.argmax(energy_grid[:, SOURCE_X]))
        logger.info(
            "init_grids: grid=%dx%d, source=(%d,%d), sum(energy)=%.6g, peak_row_y=%d",
            HEIGHT,
            WIDTH,
            SOURCE_X,
            SOURCE_Y,
            e0,
            ymax,
        )
    return energy_grid, phase_grid, polarization_grid

def create_split_mask(*, quiet=False):
    split_mask = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)
    for y in range(HEIGHT):
        for x in range(SPLIT_X, min(SPLIT_X + 20, WIDTH)):
            target_y_up = SOURCE_Y - int((x - SPLIT_X) * np.tan(np.radians(SPLIT_ANGLE)))
            if 0 <= target_y_up < HEIGHT:
                split_mask[target_y_up, x] = True
            target_y_down = SOURCE_Y + int((x - SPLIT_X) * np.tan(np.radians(SPLIT_ANGLE)))
            if 0 <= target_y_down < HEIGHT:
                split_mask[target_y_down, x] = True
    if not quiet:
        n_split = int(np.count_nonzero(split_mask))
        logger.info(
            "create_split_mask: SPLIT_X=%d, span_x<=20 cells, True_cells=%d",
            SPLIT_X,
            n_split,
        )
    return split_mask

# ============================================================
# 传播函数（带偏振）
# ============================================================

@jit(nopython=True)
def propagate_numba(energy_grid, phase_grid, polarization_grid, split_mask, 
                    lambda_val, A_val, S_val, B_val):
    h, w = energy_grid.shape
    new_energy = np.zeros((h, w))
    new_phase = np.zeros((h, w))
    new_polarization = np.zeros((h, w))
    
    for y in range(h):
        for x in range(w):
            energy = energy_grid[y, x]
            if energy <= 0:
                continue
            
            phase = phase_grid[y, x]
            polarization = polarization_grid[y, x]
            energy *= lambda_val
            
            if split_mask[y, x]:
                if y - 1 >= 0 and x + 1 < w:
                    new_energy[y-1, x+1] += energy * A_val * 0.5
                    new_phase[y-1, x+1] = phase
                    new_polarization[y-1, x+1] = polarization
                if y + 1 < h and x + 1 < w:
                    new_energy[y+1, x+1] += energy * A_val * 0.5
                    new_phase[y+1, x+1] = phase
                    new_polarization[y+1, x+1] = polarization
            else:
                if x + 1 < w:
                    new_energy[y, x+1] += energy * A_val
                    new_phase[y, x+1] = phase
                    new_polarization[y, x+1] = polarization
                if x - 1 >= 0:
                    new_energy[y, x-1] += energy * B_val
                    new_phase[y, x-1] = phase
                    new_polarization[y, x-1] = polarization
                if y - 1 >= 0:
                    new_energy[y-1, x] += energy * S_val
                    new_phase[y-1, x] = phase
                    new_polarization[y-1, x] = polarization
                if y + 1 < h:
                    new_energy[y+1, x] += energy * S_val
                    new_phase[y+1, x] = phase
                    new_polarization[y+1, x] = polarization
                # 对角方向
                if x-1>=0 and y-1>=0:
                    new_energy[y-1, x-1] += energy * S_val * 0.5
                    new_phase[y-1, x-1] = phase
                    new_polarization[y-1, x-1] = polarization
                if x+1<w and y-1>=0:
                    new_energy[y-1, x+1] += energy * S_val * 0.5
                    new_phase[y-1, x+1] = phase
                    new_polarization[y-1, x+1] = polarization
                if x-1>=0 and y+1<h:
                    new_energy[y+1, x-1] += energy * S_val * 0.5
                    new_phase[y+1, x-1] = phase
                    new_polarization[y+1, x-1] = polarization
                if x+1<w and y+1<h:
                    new_energy[y+1, x+1] += energy * S_val * 0.5
                    new_phase[y+1, x+1] = phase
                    new_polarization[y+1, x+1] = polarization
    
    total = np.sum(new_energy)
    if total > 1e-9:
        new_energy /= total
    
    return new_energy, new_phase, new_polarization

# ============================================================
# 测量函数（模拟偏振片）
# ============================================================

def measure_with_polarizer(energy, polarization, polarizer_angle):
    """偏振片测量：只有偏振方向与偏振片夹角为0°的光子能完全通过"""
    # 计算偏振方向与偏振片的夹角（0-90度）
    delta = abs(polarization - polarizer_angle)
    delta = min(delta, 180 - delta)  # 取锐角
    # 透过率 = cos²(delta)（马吕斯定律）
    transmission = np.cos(np.radians(delta))**2
    # 返回测量到的能量（模拟探测器）
    return energy * transmission

# ============================================================
# 单次模拟（测量两个探测器的符合计数）
# ============================================================

def run_bell_test(angle1, angle2, log_propagation_summary=False, quiet_geometry=False):
    energy_grid, phase_grid, polarization_grid = init_grids(quiet=quiet_geometry)
    split_mask = create_split_mask(quiet=quiet_geometry)

    detector_y1 = SOURCE_Y - int(DETECTOR_X * np.tan(np.radians(SPLIT_ANGLE)))
    detector_y2 = SOURCE_Y + int(DETECTOR_X * np.tan(np.radians(SPLIT_ANGLE)))

    if detector_y1 < 0 or detector_y1 >= HEIGHT or detector_y2 < 0 or detector_y2 >= HEIGHT:
        logger.warning(
            "run_bell_test: detector rows out of bounds (y1=%d, y2=%d, HEIGHT=%d), return 0",
            detector_y1,
            detector_y2,
            HEIGHT,
        )
        return 0.0, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), float("nan")

    t0 = time.perf_counter()
    for step in range(STEPS):
        energy_grid, phase_grid, polarization_grid = propagate_numba(
            energy_grid, phase_grid, polarization_grid, split_mask,
            LAMBDA, A, S, B
        )
    elapsed = time.perf_counter() - t0

    e_sum = float(np.sum(energy_grid))
    e_max = float(np.max(energy_grid))
    if log_propagation_summary:
        logger.info(
            "run_bell_test: %d steps in %.3fs | post sum(E)=%.6g max(E)=%.6g",
            STEPS,
            elapsed,
            e_sum,
            e_max,
        )

    e1 = energy_grid[detector_y1, DETECTOR_X]
    e2 = energy_grid[detector_y2, DETECTOR_X]
    p1 = polarization_grid[detector_y1, DETECTOR_X]
    p2 = polarization_grid[detector_y2, DETECTOR_X]

    m1 = measure_with_polarizer(e1, p1, angle1)
    m2 = measure_with_polarizer(e2, p2, angle2)

    coincidence = m1 * m2

    logger.debug(
        "  detectors (x,y)=(%d,%d) & (%d,%d) | e1,e2=(%.6g,%.6g) p1,p2=(%.4g,%.4g) "
        "m1,m2=(%.6g,%.6g) coin=%.6g",
        DETECTOR_X,
        detector_y1,
        DETECTOR_X,
        detector_y2,
        e1,
        e2,
        p1,
        p2,
        m1,
        m2,
        coincidence,
    )

    return coincidence, e1, e2, m1, m2, p1, p2

# ============================================================
# 主程序：扫描角度差，画相关性曲线
# ============================================================

logger.info("=" * 70)
logger.info("Bell Test Simulation — Polarization Correlation (ce_bell)")
logger.info(
    "Lattice: HEIGHT=%d WIDTH=%d | couplings A=%.4g S=%.4g B=%.4g lambda=%.4g | STEPS=%d",
    HEIGHT,
    WIDTH,
    A,
    S,
    B,
    LAMBDA,
    STEPS,
)
logger.info(
    "Source: (%d,%d) | SPLIT_X=%d SPLIT_ANGLE=%g deg | DETECTOR_X=%d",
    SOURCE_X,
    SOURCE_Y,
    SPLIT_X,
    SPLIT_ANGLE,
    DETECTOR_X,
)
logger.info("Angle scan: %d points from 0 to 90 deg (det1 fixed 0 deg)", len(ANGLES))
logger.info("=" * 70)

_det_y1 = SOURCE_Y - int(DETECTOR_X * np.tan(np.radians(SPLIT_ANGLE)))
_det_y2 = SOURCE_Y + int(DETECTOR_X * np.tan(np.radians(SPLIT_ANGLE)))
logger.info(
    "Nominal detector pixels: arm1 (x,y)=(%d,%d), arm2 (x,y)=(%d,%d)",
    DETECTOR_X,
    _det_y1,
    DETECTOR_X,
    _det_y2,
)

correlations = []
_first = True
for i, angle2 in enumerate(ANGLES):
    angle1 = 0
    corr, e1, e2, m1, m2, p1, p2 = run_bell_test(
        angle1,
        angle2,
        log_propagation_summary=_first,
        quiet_geometry=not _first,
    )
    _first = False
    correlations.append(corr)
    logger.info(
        "[%d/%d] angle1=%g angle2=%g deg | e1,e2=(%.6g,%.6g) p1,p2=(%.4g,%.4g) "
        "Malus m1,m2=(%.6g,%.6g) coincidence=%.6g",
        i + 1,
        len(ANGLES),
        angle1,
        angle2,
        e1,
        e2,
        p1,
        p2,
        m1,
        m2,
        corr,
    )

correlations = np.asarray(correlations, dtype=np.float64)
baseline = float(correlations[0])
if baseline <= 0 or not np.isfinite(baseline):
    logger.error(
        "Baseline coincidence at 0 deg is invalid (corr[0]=%r); normalization skipped",
        baseline,
    )
else:
    logger.info(
        "Normalize correlations by coincidence at angle2=0 (baseline=%.6g)",
        baseline,
    )
    correlations = correlations / baseline

angles_rad = np.radians(ANGLES)
qm_curve = np.cos(angles_rad) ** 2

rmse = float(np.sqrt(np.mean((correlations - qm_curve) ** 2)))
max_abs = float(np.max(np.abs(correlations - qm_curve)))
logger.info(
    "vs QM cos^2(theta): RMSE=%.6g max|Δ|=%.6g close(0.1)=%s",
    rmse,
    max_abs,
    np.allclose(correlations, qm_curve, atol=0.1),
)

# ============================================================
# 绘图
# ============================================================

plt.figure(figsize=(8, 6))
plt.plot(ANGLES, correlations, 'bo-', linewidth=2, markersize=8, label='Your Model')
plt.plot(ANGLES, qm_curve, 'r--', linewidth=2, label='Quantum Mechanics (cos²θ)')
plt.xlabel('Polarizer Angle Difference (degrees)', fontsize=12)
plt.ylabel('Normalized Correlation (Coincidence)', fontsize=12)
plt.title('Bell Test: Polarization Correlation\nYour Model vs Quantum Mechanics', fontsize=14)
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('bell_test_result.png', dpi=150)
plt.show()

logger.info("Figure written: bell_test_result.png")

if np.allclose(correlations, qm_curve, atol=0.1):
    logger.info(
        "[RESULT] Normalized coincidence vs angle2 tracks cos^2 within atol=0.1 "
        "(curve comparison only; not a full Bell-test certification)."
    )
else:
    logger.info(
        "[RESULT] Deviation from cos^2(theta) beyond atol=0.1 — review polarization "
        "propagation / Malus / coincidence definition."
    )