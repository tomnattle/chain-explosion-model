"""Numba JIT kernels for chain-explosion lattice propagation."""
import numpy as np
from numba import jit


@jit(nopython=True)
def propagate_double_slit(grid, barrier, A, S, B, lam):
    """One step: double-slit barrier, diagonal couplings."""
    h, w = grid.shape
    new_grid = np.zeros((h, w), dtype=np.float64)
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
    return new_grid


@jit(nopython=True)
def propagate_double_slit_slit_absorb(
    grid, barrier, absorb_ratio, absorb_x, slit_y0, slit_y1, A, S, B, lam
):
    """Absorption on column absorb_x over slit rows [slit_y0, slit_y1)."""
    h, w = grid.shape
    new_grid = np.zeros((h, w), dtype=np.float64)
    for y in range(h):
        for x in range(w):
            energy = grid[y, x]
            if energy <= 0:
                continue
            if absorb_ratio > 0.0:
                if x == absorb_x and y >= slit_y0 and y < slit_y1:
                    energy *= 1.0 - absorb_ratio
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
    return new_grid


@jit(nopython=True)
def propagate_double_slit_absorber_mask(
    grid, barrier, absorber, absorb_ratio, A, S, B, lam
):
    """Boolean absorber mask: multiply energy by (1 - absorb_ratio) on True cells."""
    h, w = grid.shape
    new_grid = np.zeros((h, w), dtype=np.float64)
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
    return new_grid


@jit(nopython=True)
def propagate_split_energy(grid, split_mask, A, S, B, lam):
    """Beam splitter region: no barriers; split_mask steers energy."""
    h, w = grid.shape
    new_grid = np.zeros((h, w), dtype=np.float64)
    for y in range(h):
        for x in range(w):
            energy = grid[y, x]
            if energy <= 0:
                continue
            energy *= lam
            if split_mask[y, x]:
                if y - 1 >= 0:
                    new_grid[y - 1, x + 1] += energy * A * 0.5
                if y + 1 < h:
                    new_grid[y + 1, x + 1] += energy * A * 0.5
            else:
                if x + 1 < w:
                    new_grid[y, x + 1] += energy * A
                if x - 1 >= 0:
                    new_grid[y, x - 1] += energy * B
                if y - 1 >= 0:
                    new_grid[y - 1, x] += energy * S
                if y + 1 < h:
                    new_grid[y + 1, x] += energy * S
                if x - 1 >= 0 and y - 1 >= 0:
                    new_grid[y - 1, x - 1] += energy * S * 0.5
                if x + 1 < w and y - 1 >= 0:
                    new_grid[y - 1, x + 1] += energy * S * 0.5
                if x - 1 >= 0 and y + 1 < h:
                    new_grid[y + 1, x - 1] += energy * S * 0.5
                if x + 1 < w and y + 1 < h:
                    new_grid[y + 1, x + 1] += energy * S * 0.5
    return new_grid


@jit(nopython=True)
def propagate_split_phase(
    energy_grid, phase_grid, split_mask, A, S, B, lam, normalize_total
):
    """Energy + phase co-propagation; optional renorm of total energy to 1."""
    h, w = energy_grid.shape
    new_energy = np.zeros((h, w), dtype=np.float64)
    new_phase = np.zeros((h, w), dtype=np.float64)
    for y in range(h):
        for x in range(w):
            energy = energy_grid[y, x]
            if energy <= 0:
                continue
            phase = phase_grid[y, x]
            energy *= lam
            if split_mask[y, x]:
                if y - 1 >= 0 and x + 1 < w:
                    new_energy[y - 1, x + 1] += energy * A * 0.5
                    new_phase[y - 1, x + 1] = phase
                if y + 1 < h and x + 1 < w:
                    new_energy[y + 1, x + 1] += energy * A * 0.5
                    new_phase[y + 1, x + 1] = phase
            else:
                if x + 1 < w:
                    new_energy[y, x + 1] += energy * A
                    new_phase[y, x + 1] = phase
                if x - 1 >= 0:
                    new_energy[y, x - 1] += energy * B
                    new_phase[y, x - 1] = phase
                if y - 1 >= 0:
                    new_energy[y - 1, x] += energy * S
                    new_phase[y - 1, x] = phase
                if y + 1 < h:
                    new_energy[y + 1, x] += energy * S
                    new_phase[y + 1, x] = phase
                if x - 1 >= 0 and y - 1 >= 0:
                    new_energy[y - 1, x - 1] += energy * S * 0.5
                    new_phase[y - 1, x - 1] = phase
                if x + 1 < w and y - 1 >= 0:
                    new_energy[y - 1, x + 1] += energy * S * 0.5
                    new_phase[y - 1, x + 1] = phase
                if x - 1 >= 0 and y + 1 < h:
                    new_energy[y + 1, x - 1] += energy * S * 0.5
                    new_phase[y + 1, x - 1] = phase
                if x + 1 < w and y + 1 < h:
                    new_energy[y + 1, x + 1] += energy * S * 0.5
                    new_phase[y + 1, x + 1] = phase
    if normalize_total:
        total = 0.0
        for y in range(h):
            for x in range(w):
                total += new_energy[y, x]
        if total > 1e-9:
            inv = 1.0 / total
            for y in range(h):
                for x in range(w):
                    new_energy[y, x] *= inv
    return new_energy, new_phase


@jit(nopython=True)
def set_circle_mask(mask, cx, cy, radius):
    """Fill mask: True inside disk (inclusive radius^2). Clears entire mask first."""
    h, w = mask.shape
    for y in range(h):
        for x in range(w):
            mask[y, x] = False
    if radius <= 0:
        if 0 <= cy < h and 0 <= cx < w:
            mask[cy, cx] = True
        return
    r2 = radius * radius
    for y in range(h):
        for x in range(w):
            dx = x - cx
            dy = y - cy
            if dx * dx + dy * dy <= r2:
                mask[y, x] = True
