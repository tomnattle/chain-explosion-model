"""
explore_wave_particle_interaction_animation.py
----------------------------------------------
第2步 toy：在连续波传播里加入“稳定扰动团（类粒子）”交互。

机制（极简、局域、决定论）：
- 粒子是一个固定半径区域（可看作稳定扰动结的粗化表示）
- 每步吸收其区域内部分场强（局域吸收）
- 吸收能量累计到 particle_charge
- 当 charge 超过阈值时，从粒子中心触发一次再发射脉冲（回到场）

输出：
- wave_particle_interaction.gif
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

os.environ.setdefault("MPLBACKEND", "Agg")

from ce_engine_v3_coherent import propagate_coherent
from ce_engine_v2 import compute_visibility


def make_double_slit_barrier(height, width, barrier_x, slit1_y0, slit2_y0, slit_w):
    barrier = np.zeros((height, width), dtype=np.bool_)
    barrier[:, barrier_x] = True
    barrier[slit1_y0 : slit1_y0 + slit_w, barrier_x] = False
    barrier[slit2_y0 : slit2_y0 + slit_w, barrier_x] = False
    return barrier


def circle_mask(height, width, cx, cy, r):
    y, x = np.ogrid[:height, :width]
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r


def main():
    # Scene
    H, W = 181, 380
    src_x, src_y = 20, H // 2
    barrier_x = 150
    slit_w = 8
    slit1_y0 = H // 2 - 26
    slit2_y0 = H // 2 + 18
    screen_x = W - 12

    # Coherent propagation (forward strong, side weak)
    A, S, LAM, k = 1.0, 0.18, 0.995, 2.0
    n_frames = 260

    # Particle toy params
    p_x, p_y = 245, H // 2 + 3
    p_r = 6
    absorb_frac = 0.08     # per-step local absorption in particle area
    emit_threshold = 0.55  # trigger threshold in stored charge
    emit_amp = 0.75        # emitted impulse amplitude
    leak = 0.998           # charge slow leak for stability

    barrier = make_double_slit_barrier(H, W, barrier_x, slit1_y0, slit2_y0, slit_w)
    p_mask = circle_mask(H, W, p_x, p_y, p_r)

    U = np.zeros((H, W), dtype=np.complex128)
    U[src_y, src_x] = 1.0 + 0.0j  # single initial excitation

    # also inject a second pulse later to provoke interaction
    scripted_impulses = {
        1: [(src_y, src_x, 1.0)],
        90: [(src_y - 18, src_x + 4, 0.8)],
        150: [(src_y + 20, src_x + 4, 0.8)],
    }

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor("#0d1117")
    for ax in axes:
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="#8b949e")
        for sp in ax.spines.values():
            sp.set_color("#30363d")
    ax0, ax1 = axes

    I0 = np.abs(U) ** 2
    im = ax0.imshow(np.log10(I0 + 1e-14), cmap="inferno", aspect="auto", origin="upper")
    ax0.axvline(barrier_x, color="cyan", linestyle="--", linewidth=1.0, alpha=0.8)
    ax0.axvline(screen_x, color="#58a6ff", linestyle="--", linewidth=1.0, alpha=0.8)
    # particle overlay
    circ = plt.Circle((p_x, p_y), p_r, color="#7ee787", fill=False, linewidth=1.8, alpha=0.95)
    ax0.add_patch(circ)
    ax0.set_title("Wave + particle interaction (log10 |U|^2)", color="white", fontsize=10)
    ax0.set_xlabel("x", color="#8b949e")
    ax0.set_ylabel("y", color="#8b949e")
    cbar = fig.colorbar(im, ax=ax0)
    cbar.ax.tick_params(colors="#8b949e")

    line, = ax1.plot(np.zeros(H), color="#58a6ff", linewidth=1.8)
    ax1.set_xlim(0, H - 1)
    ax1.set_ylim(0, 1.05)
    ax1.set_title("Screen profile", color="white", fontsize=10)
    ax1.set_xlabel("y", color="#8b949e")
    ax1.set_ylabel("I(y)/max", color="#8b949e")
    ax1.grid(True, alpha=0.25, color="#30363d")

    txt = ax1.text(
        0.02, 0.95, "", transform=ax1.transAxes, va="top", ha="left",
        color="#c9d1d9", fontsize=9, family="monospace"
    )

    charge = 0.0
    emit_count = 0

    def add_impulse(y, x, amp):
        if 0 <= y < H and 0 <= x < W:
            U[y, x] += complex(amp, 0.0)

    def update(frame_idx):
        nonlocal charge, emit_count, U

        # scripted external excitations (still local, deterministic)
        if frame_idx in scripted_impulses:
            for yy, xx, aa in scripted_impulses[frame_idx]:
                add_impulse(yy, xx, aa)

        U = propagate_coherent(U, barrier, A, S, LAM, k)

        # particle absorption (local)
        local_amp2 = np.abs(U[p_mask]) ** 2
        absorbed = absorb_frac * float(np.sum(local_amp2))
        U[p_mask] *= np.sqrt(max(0.0, 1.0 - absorb_frac))

        # charge dynamics
        charge = charge * leak + absorbed
        fired = 0
        if charge >= emit_threshold:
            add_impulse(p_y, p_x + 1, emit_amp)  # tiny forward bias
            charge -= emit_threshold
            emit_count += 1
            fired = 1

        I = np.abs(U) ** 2
        im.set_data(np.log10(I + 1e-14))

        screen = I[:, screen_x]
        smax = float(np.max(screen)) + 1e-18
        line.set_ydata(screen / smax)
        v = float(compute_visibility(screen.astype(np.float64)))

        txt.set_text(
            "t=%3d\nV=%.3f\ncharge=%.3f\nemit_count=%d\nfired=%d"
            % (frame_idx + 1, v, charge, emit_count, fired)
        )
        return im, line, txt

    ani = FuncAnimation(fig, update, frames=n_frames, interval=45, blit=False)
    out_gif = "wave_particle_interaction.gif"
    ani.save(out_gif, writer=PillowWriter(fps=20))
    plt.close(fig)

    print("Wave-particle interaction animation complete.")
    print("saved:", out_gif)


if __name__ == "__main__":
    main()

