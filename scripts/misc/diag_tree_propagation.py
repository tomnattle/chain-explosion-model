import os
import numpy as np

from tree_propagation import bfs_tree_double_slit


def main():
    HEIGHT = 201
    WIDTH = 400
    SOURCE_X = 10
    SOURCE_Y = HEIGHT // 2
    INIT_ENERGY = 100.0

    A, S, B = 1.0, 0.3, 0.05
    LAM = 0.97
    THRESHOLD = 1e-4

    BARRIER_X = 150
    SLIT1_Y = HEIGHT // 2 - 30
    SLIT2_Y = HEIGHT // 2 + 30
    SLIT_WIDTH = 8

    energy, generation, steps, barrier = bfs_tree_double_slit(
        SOURCE_Y,
        SOURCE_X,
        INIT_ENERGY,
        A,
        S,
        B,
        LAM,
        THRESHOLD,
        HEIGHT,
        WIDTH,
        BARRIER_X,
        SLIT1_Y,
        SLIT2_Y,
        SLIT_WIDTH,
        max_steps=None,
        verbose=False,
    )

    nonzero = energy[energy > 0]
    print("steps", steps)
    print("nonzero_count", int(nonzero.size))
    print("energy_sum", float(energy.sum()))
    if nonzero.size:
        print("max_energy", float(nonzero.max()))
        print("min_nonzero", float(nonzero.min()))
        for q in [50, 75, 90, 95, 99, 99.5, 99.9]:
            print(f"q{q:g}", float(np.percentile(nonzero, q)))
        x = np.log1p(nonzero)
        print("log1p_max", float(x.max()))
        print("log1p_q99.9", float(np.percentile(x, 99.9)))

    png = "tree_double_slit.png"
    if os.path.exists(png):
        from PIL import Image

        im = np.asarray(Image.open(png).convert("RGB"), dtype=np.float32) / 255.0
        print("png_exists", True)
        print("png_mean", float(im.mean()))
        print("png_std", float(im.std()))
        print("png_max", float(im.max()))
    else:
        print("png_exists", False)


if __name__ == "__main__":
    main()

