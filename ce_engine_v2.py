"""
Chain Explosion Engine v2
扩展核心内核，支持：
1. 相位真实演化（k·x 积累，不是复制）
2. 单次随机路径追踪（蒙特卡洛）
3. 能量守恒精确追踪
4. 衍射角计算辅助
5. propagate_*_n_steps：多步格点传播在单个 Numba 区完成，减少 Python 循环开销
"""

import numpy as np
try:
    from numba import jit
except Exception:  # no extra dependency required
    def jit(*args, **kwargs):
        def _wrap(func):
            return func
        return _wrap


# ============================================================
# 原始内核（保持兼容）
# ============================================================

@jit(nopython=True)
def _double_slit_step(grid, barrier, A, S, B, lam, new_grid):
    h, w = grid.shape
    for y in range(h):
        for x in range(w):
            new_grid[y, x] = 0.0
    for y in range(h):
        for x in range(w):
            energy = grid[y, x]
            if energy <= 0:
                continue
            energy *= lam
            if x + 1 < w and not barrier[y, x + 1]:
                new_grid[y, x + 1] += energy * A
            if x - 1 >= 0 and not barrier[y, x - 1]:
                new_grid[y, x - 1] += energy * B
            if y - 1 >= 0 and not barrier[y - 1, x]:
                new_grid[y - 1, x] += energy * S
            if y + 1 < h and not barrier[y + 1, x]:
                new_grid[y + 1, x] += energy * S
            if x - 1 >= 0 and y - 1 >= 0 and not barrier[y - 1, x - 1]:
                new_grid[y - 1, x - 1] += energy * S * 0.5
            if x + 1 < w and y - 1 >= 0 and not barrier[y - 1, x + 1]:
                new_grid[y - 1, x + 1] += energy * S * 0.5
            if x - 1 >= 0 and y + 1 < h and not barrier[y + 1, x - 1]:
                new_grid[y + 1, x - 1] += energy * S * 0.5
            if x + 1 < w and y + 1 < h and not barrier[y + 1, x + 1]:
                new_grid[y + 1, x + 1] += energy * S * 0.5


@jit(nopython=True)
def propagate_double_slit(grid, barrier, A, S, B, lam):
    h, w = grid.shape
    new_grid = np.zeros((h, w), dtype=np.float64)
    _double_slit_step(grid, barrier, A, S, B, lam, new_grid)
    return new_grid


@jit(nopython=True)
def propagate_double_slit_n_steps(grid, barrier, A, S, B, lam, n_steps):
    """多步传播一次完成，减少 Python↔Numba 往返。"""
    h, w = grid.shape
    buf0 = np.copy(grid)
    buf1 = np.zeros((h, w), dtype=np.float64)
    src = buf0
    dst = buf1
    for _ in range(n_steps):
        _double_slit_step(src, barrier, A, S, B, lam, dst)
        src, dst = dst, src
    return src


@jit(nopython=True)
def _absorber_mask_step(grid, barrier, absorber, absorb_ratio, A, S, B, lam, new_grid):
    h, w = grid.shape
    for y in range(h):
        for x in range(w):
            new_grid[y, x] = 0.0
    for y in range(h):
        for x in range(w):
            energy = grid[y, x]
            if energy <= 0:
                continue
            if absorber[y, x]:
                energy *= 1.0 - absorb_ratio
                if energy <= 0:
                    continue
            energy *= lam
            if x + 1 < w and not barrier[y, x + 1]:
                new_grid[y, x + 1] += energy * A
            if x - 1 >= 0 and not barrier[y, x - 1]:
                new_grid[y, x - 1] += energy * B
            if y - 1 >= 0 and not barrier[y - 1, x]:
                new_grid[y - 1, x] += energy * S
            if y + 1 < h and not barrier[y + 1, x]:
                new_grid[y + 1, x] += energy * S
            if x - 1 >= 0 and y - 1 >= 0 and not barrier[y - 1, x - 1]:
                new_grid[y - 1, x - 1] += energy * S * 0.5
            if x + 1 < w and y - 1 >= 0 and not barrier[y - 1, x + 1]:
                new_grid[y - 1, x + 1] += energy * S * 0.5
            if x - 1 >= 0 and y + 1 < h and not barrier[y + 1, x - 1]:
                new_grid[y + 1, x - 1] += energy * S * 0.5
            if x + 1 < w and y + 1 < h and not barrier[y + 1, x + 1]:
                new_grid[y + 1, x + 1] += energy * S * 0.5


@jit(nopython=True)
def propagate_double_slit_absorber_mask(grid, barrier, absorber, absorb_ratio, A, S, B, lam):
    h, w = grid.shape
    new_grid = np.zeros((h, w), dtype=np.float64)
    _absorber_mask_step(grid, barrier, absorber, absorb_ratio, A, S, B, lam, new_grid)
    return new_grid


@jit(nopython=True)
def propagate_double_slit_absorber_mask_n_steps(
    grid, barrier, absorber, absorb_ratio, A, S, B, lam, n_steps
):
    h, w = grid.shape
    buf0 = np.copy(grid)
    buf1 = np.zeros((h, w), dtype=np.float64)
    src = buf0
    dst = buf1
    for _ in range(n_steps):
        _absorber_mask_step(src, barrier, absorber, absorb_ratio, A, S, B, lam, dst)
        src, dst = dst, src
    return src


# ============================================================
# 新内核1：相位真实演化（路径积分累积）
# 每走一步，相位按方向累积 k·Δx
# 多路径到达同一点时，做复数叠加
# ============================================================

@jit(nopython=True)
def propagate_with_real_phase(energy_grid, phase_grid, barrier, A, S, B, lam, k_main, k_side):
    """
    相位真实演化版本。
    k_main: 主方向（X）的波数步长（弧度/格点）
    k_side: 侧向的波数步长
    多路径到达同一格点时，用复数叠加后取模平方作为能量。
    """
    h, w = energy_grid.shape
    # 用复数场做叠加
    new_complex = np.zeros((h, w), dtype=np.complex128)

    for y in range(h):
        for x in range(w):
            energy = energy_grid[y, x]
            if energy <= 0:
                continue
            amp = np.sqrt(energy) * (lam ** 0.5)
            phi = phase_grid[y, x]
            psi = amp * (np.cos(phi) + 1j * np.sin(phi))

            # 主方向前进 +x，相位积累 k_main
            if x + 1 < w and not barrier[y, x + 1]:
                new_phase = phi + k_main
                new_complex[y, x + 1] += np.sqrt(A) * amp * (np.cos(new_phase) + 1j * np.sin(new_phase))

            # 后向 -x
            if x - 1 >= 0 and not barrier[y, x - 1]:
                new_phase = phi - k_main
                new_complex[y, x - 1] += np.sqrt(B) * amp * (np.cos(new_phase) + 1j * np.sin(new_phase))

            # 侧向 ±y
            if y - 1 >= 0 and not barrier[y - 1, x]:
                new_phase = phi + k_side
                new_complex[y - 1, x] += np.sqrt(S) * amp * (np.cos(new_phase) + 1j * np.sin(new_phase))
            if y + 1 < h and not barrier[y + 1, x]:
                new_phase = phi + k_side
                new_complex[y + 1, x] += np.sqrt(S) * amp * (np.cos(new_phase) + 1j * np.sin(new_phase))

            # 对角
            diag_k = (k_main + k_side) * 0.5
            if x + 1 < w and y - 1 >= 0 and not barrier[y - 1, x + 1]:
                new_phase = phi + diag_k
                new_complex[y - 1, x + 1] += np.sqrt(S * 0.5) * amp * (np.cos(new_phase) + 1j * np.sin(new_phase))
            if x + 1 < w and y + 1 < h and not barrier[y + 1, x + 1]:
                new_phase = phi + diag_k
                new_complex[y + 1, x + 1] += np.sqrt(S * 0.5) * amp * (np.cos(new_phase) + 1j * np.sin(new_phase))
            if x - 1 >= 0 and y - 1 >= 0 and not barrier[y - 1, x - 1]:
                new_phase = phi - diag_k
                new_complex[y - 1, x - 1] += np.sqrt(S * 0.5) * amp * (np.cos(new_phase) + 1j * np.sin(new_phase))
            if x - 1 >= 0 and y + 1 < h and not barrier[y + 1, x - 1]:
                new_phase = phi - diag_k
                new_complex[y + 1, x - 1] += np.sqrt(S * 0.5) * amp * (np.cos(new_phase) + 1j * np.sin(new_phase))

    # 从复数场提取能量和相位
    new_energy = np.zeros((h, w), dtype=np.float64)
    new_phase = np.zeros((h, w), dtype=np.float64)
    for y in range(h):
        for x in range(w):
            c = new_complex[y, x]
            new_energy[y, x] = c.real ** 2 + c.imag ** 2
            if new_energy[y, x] > 1e-15:
                new_phase[y, x] = np.arctan2(c.imag, c.real)

    return new_energy, new_phase


# ============================================================
# 新内核2：单光子随机路径（蒙特卡洛单次追踪）
# 模拟"一个光子"从源到屏的随机游走
# 积累多次后应出现干涉图样（如果模型正确）
# ============================================================

@jit(nopython=True)
def single_photon_random_walk(height, width, source_x, source_y,
                               barrier, A, S, B, max_steps):
    """
    单次随机游走：从(source_x, source_y)出发，
    按A/S/B权重随机选择方向，直到到达右边界或超出步数。
    返回终止的(y, x)坐标，(-1,-1)表示被吸收/越界。
    """
    x = source_x
    y = source_y

    # 归一化权重
    total_w = A + B + 2 * S + 4 * (S * 0.5)
    w_right = A / total_w
    w_left = B / total_w
    w_up = S / total_w
    w_down = S / total_w
    w_ur = S * 0.5 / total_w
    w_ul = S * 0.5 / total_w
    w_dr = S * 0.5 / total_w
    w_dl = S * 0.5 / total_w

    for step in range(max_steps):
        if x >= width - 1:
            return y, x  # 到达右边界

        # 随机选方向
        r = np.random.random()
        cum = 0.0

        cum += w_right
        if r < cum:
            nx, ny = x + 1, y
        else:
            cum += w_left
            if r < cum:
                nx, ny = x - 1, y
            else:
                cum += w_up
                if r < cum:
                    nx, ny = x, y - 1
                else:
                    cum += w_down
                    if r < cum:
                        nx, ny = x, y + 1
                    else:
                        cum += w_ur
                        if r < cum:
                            nx, ny = x + 1, y - 1
                        else:
                            cum += w_ul
                            if r < cum:
                                nx, ny = x - 1, y - 1
                            else:
                                cum += w_dr
                                if r < cum:
                                    nx, ny = x + 1, y + 1
                                else:
                                    nx, ny = x - 1, y + 1

        # 边界检查
        if nx < 0 or nx >= width or ny < 0 or ny >= height:
            return -1, -1

        # 挡板检查
        if barrier[ny, nx]:
            return -1, -1

        x, y = nx, ny

    return -1, -1  # 超时


@jit(nopython=True)
def run_monte_carlo(n_photons, height, width, source_x, source_y,
                    barrier, A, S, B, max_steps, seed):
    """运行N个单光子，返回屏幕击中分布。"""
    # NOTE: Numba 的随机数状态不一定受 Python 层 np.random.seed 影响，
    # 在 nopython 内显式 seed，以保证测试可复现。
    np.random.seed(seed)
    screen = np.zeros(height, dtype=np.float64)
    hits = 0
    for _ in range(n_photons):
        fy, fx = single_photon_random_walk(
            height, width, source_x, source_y, barrier, A, S, B, max_steps
        )
        if fy >= 0 and fx >= width - 2:
            screen[fy] += 1.0
            hits += 1
    return screen, hits


@jit(nopython=True)
def monte_carlo_milestone_screens(
    n_photons, milestones, height, width, source_x, source_y,
    barrier, A, S, B, max_steps, seed,
):
    """
    milestones: 递增 int64，如 [100, 1000, 50000]；返回形状 (len(ms), height)。
    """
    nm = milestones.shape[0]
    out = np.zeros((nm, height), dtype=np.float64)
    screen = np.zeros(height, dtype=np.float64)
    next_m = 0
    np.random.seed(seed)
    for n in range(n_photons):
        fy, fx = single_photon_random_walk(
            height, width, source_x, source_y, barrier, A, S, B, max_steps
        )
        if fy >= 0 and fx >= width - 2:
            screen[fy] += 1.0
        if next_m < nm and n + 1 == milestones[next_m]:
            for i in range(height):
                out[next_m, i] = screen[i]
            next_m += 1
    return out


# ============================================================
# 工具函数：计算干涉对比度
# ============================================================

@jit(nopython=True)
def compute_visibility(screen):
    n = screen.shape[0]
    peak_vals = np.zeros(n, dtype=np.float64)
    valley_vals = np.zeros(n, dtype=np.float64)
    npk = 0
    nv = 0
    for i in range(1, n - 1):
        if screen[i] > screen[i - 1] and screen[i] > screen[i + 1]:
            peak_vals[npk] = screen[i]
            npk += 1
        elif screen[i] < screen[i - 1] and screen[i] < screen[i + 1]:
            valley_vals[nv] = screen[i]
            nv += 1
    if npk == 0 or nv == 0:
        return 0.0
    s_max = 0.0
    for i in range(npk):
        s_max += peak_vals[i]
    s_max /= npk
    s_min = 0.0
    for i in range(nv):
        s_min += valley_vals[i]
    s_min /= nv
    if s_max + s_min < 1e-12:
        return 0.0
    return (s_max - s_min) / (s_max + s_min)


def compute_energy_conservation(grid_before, grid_after):
    """返回能量保留比例（理想=lam，实际由耦合决定）"""
    e_before = np.sum(grid_before)
    e_after = np.sum(grid_after)
    if e_before < 1e-12:
        return 0.0
    return e_after / e_before
