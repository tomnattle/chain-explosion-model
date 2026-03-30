"""
explore_directional_wave_animation.py
-------------------------------------
交互 + 导出双模式：
1) 交互模式（默认）:
   - 鼠标点击画布任意位置 -> 该位置注入一次激发
   - 不自动持续发射，完全由点击控制
2) GIF 导出模式:
   - 使用固定点击事件脚本自动注入，保存为 directional_wave_animation.gif
"""

import argparse
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

from ce_engine_v3_coherent import propagate_coherent
from ce_engine_v2 import compute_visibility


def make_double_slit_barrier(height, width, barrier_x, slit1_y0, slit2_y0, slit_w):
    barrier = np.zeros((height, width), dtype=np.bool_)
    barrier[:, barrier_x] = True
    barrier[slit1_y0 : slit1_y0 + slit_w, barrier_x] = False
    barrier[slit2_y0 : slit2_y0 + slit_w, barrier_x] = False
    return barrier


def build_scene():
    height, width = 181, 360
    source_x, source_y = 20, height // 2
    barrier_x = 145
    slit_w = 8
    slit1_y0 = height // 2 - 26
    slit2_y0 = height // 2 + 18
    screen_x = width - 12

    A = 1.0
    S = 0.18
    LAM = 0.995
    k = 2.0

    barrier = make_double_slit_barrier(height, width, barrier_x, slit1_y0, slit2_y0, slit_w)
    return {
        "height": height,
        "width": width,
        "source_x": source_x,
        "source_y": source_y,
        "barrier_x": barrier_x,
        "screen_x": screen_x,
        "barrier": barrier,
        "A": A,
        "S": S,
        "LAM": LAM,
        "k": k,
    }


def add_impulse(U, y, x, amp=1.0):
    h, w = U.shape
    if 0 <= y < h and 0 <= x < w:
        U[y, x] += complex(amp, 0.0)


def make_figure(scene, title):
    height = scene["height"]
    barrier_x = scene["barrier_x"]
    screen_x = scene["screen_x"]
    U = np.zeros((scene["height"], scene["width"]), dtype=np.complex128)

    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor("#0d1117")
    for ax in (ax0, ax1):
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="#8b949e")
        for sp in ax.spines.values():
            sp.set_color("#30363d")

    I0 = np.abs(U) ** 2
    im = ax0.imshow(np.log10(I0 + 1e-14), cmap="inferno", aspect="auto", origin="upper")
    ax0.axvline(barrier_x, color="cyan", linestyle="--", linewidth=1.0, alpha=0.8)
    ax0.axvline(screen_x, color="#58a6ff", linestyle="--", linewidth=1.0, alpha=0.8)
    ax0.set_title(title, color="white", fontsize=10)
    ax0.set_xlabel("x", color="#8b949e")
    ax0.set_ylabel("y", color="#8b949e")
    cbar = fig.colorbar(im, ax=ax0)
    cbar.ax.tick_params(colors="#8b949e")

    line, = ax1.plot(np.zeros(height), color="#58a6ff", linewidth=1.8)
    ax1.set_xlim(0, height - 1)
    ax1.set_ylim(0, 1.05)
    ax1.set_title("Screen profile", color="white", fontsize=10)
    ax1.set_xlabel("y", color="#8b949e")
    ax1.set_ylabel("I(y)/max", color="#8b949e")
    ax1.grid(True, alpha=0.25, color="#30363d")

    txt = ax1.text(
        0.02,
        0.95,
        "",
        transform=ax1.transAxes,
        va="top",
        ha="left",
        color="#c9d1d9",
        fontsize=9,
        family="monospace",
    )

    state = {"U": U, "frame": 0}
    return fig, ax0, im, line, txt, state


def step_once(scene, state, im, line, txt):
    state["U"] = propagate_coherent(
        state["U"], scene["barrier"], scene["A"], scene["S"], scene["LAM"], scene["k"]
    )
    state["frame"] += 1
    I = np.abs(state["U"]) ** 2
    im.set_data(np.log10(I + 1e-14))

    screen = I[:, scene["screen_x"]]
    smax = float(np.max(screen)) + 1e-18
    line.set_ydata(screen / smax)
    v = float(compute_visibility(screen.astype(np.float64)))
    txt.set_text(
        "t=%3d\nV=%.3f\nA=%.2f S=%.2f LAM=%.3f"
        % (state["frame"], v, scene["A"], scene["S"], scene["LAM"])
    )
    return im, line, txt


def run_gif_mode(scene, frames=220, out_gif="directional_wave_animation.gif"):
    fig, ax0, im, line, txt, state = make_figure(
        scene, "Directional coherent propagation (GIF mode)"
    )
    add_impulse(state["U"], scene["source_y"], scene["source_x"], amp=1.0)

    scripted_clicks = {
        1: [(scene["source_y"], scene["source_x"], 1.0)],
        70: [(scene["source_y"] - 20, scene["source_x"] + 5, 0.8)],
        120: [(scene["source_y"] + 22, scene["source_x"] + 5, 0.8)],
    }

    def update(frame_idx):
        if frame_idx in scripted_clicks:
            for y, x, amp in scripted_clicks[frame_idx]:
                add_impulse(state["U"], y, x, amp=amp)
        return step_once(scene, state, im, line, txt)

    ani = FuncAnimation(fig, update, frames=frames, interval=50, blit=False)
    ani.save(out_gif, writer=PillowWriter(fps=20))
    plt.close(fig)
    print("Directional wave animation complete.")
    print("saved:", out_gif)


def run_interactive_mode(scene):
    # interactive mode requires GUI backend
    if os.environ.get("MPLBACKEND", "").lower() == "agg":
        os.environ["MPLBACKEND"] = "TkAgg"

    fig, ax0, im, line, txt, state = make_figure(
        scene, "Directional coherent propagation (interactive click mode)"
    )
    ax0.text(
        0.01,
        0.02,
        "Click on left panel to inject one impulse",
        transform=ax0.transAxes,
        color="#c9d1d9",
        fontsize=8,
    )

    def on_click(event):
        if event.inaxes != ax0 or event.xdata is None or event.ydata is None:
            return
        add_impulse(state["U"], int(round(event.ydata)), int(round(event.xdata)), amp=1.0)

    timer = fig.canvas.new_timer(interval=40)

    def on_timer():
        step_once(scene, state, im, line, txt)
        fig.canvas.draw_idle()

    timer.add_callback(on_timer)
    timer.start()
    cid = fig.canvas.mpl_connect("button_press_event", on_click)
    print("Interactive mode started. Click in the left panel to inject impulses.")
    print("Close the window to exit.")
    plt.show()
    fig.canvas.mpl_disconnect(cid)


def main():
    parser = argparse.ArgumentParser(description="Directional wave animation (interactive / gif)")
    parser.add_argument(
        "--mode",
        choices=("interactive", "gif"),
        default="interactive",
        help="interactive: mouse click injection; gif: scripted export",
    )
    parser.add_argument("--frames", type=int, default=220, help="frame count in gif mode")
    args = parser.parse_args()

    scene = build_scene()
    if args.mode == "gif":
        run_gif_mode(scene, frames=max(20, int(args.frames)))
    else:
        run_interactive_mode(scene)


if __name__ == "__main__":
    main()

