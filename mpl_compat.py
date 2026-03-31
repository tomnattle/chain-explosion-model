# Matplotlib < 3.3: Legend has no keyword "labelcolor".
# Chinese labels: default DejaVu Sans has no CJK glyphs → Glyph missing warnings on Windows.

import os
import sys
import warnings
from pathlib import Path

import matplotlib
from matplotlib import animation as mpl_animation
from matplotlib.figure import Figure

from repo_layout import resolve_generated_output

_CJK_SANS = [
    "Microsoft YaHei",
    "Microsoft YaHei UI",
    "SimHei",
    "SimSun",
    "DengXian",
    "KaiTi",
    "FangSong",
    "PingFang SC",
    "Noto Sans CJK SC",
    "DejaVu Sans",
]


def _register_windows_cjk_font_files():
    if sys.platform != "win32":
        return
    windir = os.environ.get("WINDIR", r"C:\Windows")
    fonts_dir = os.path.join(windir, "Fonts")
    if not os.path.isdir(fonts_dir):
        return
    try:
        from matplotlib import font_manager
    except Exception:
        return
    addfont = getattr(font_manager.fontManager, "addfont", None)
    if addfont is None:
        return
    for fn in ("msyh.ttc", "msyhbd.ttc", "simhei.ttf", "simsun.ttc", "simsunb.ttf"):
        fp = os.path.join(fonts_dir, fn)
        if os.path.isfile(fp):
            try:
                addfont(fp)
            except (OSError, ValueError, TypeError, AttributeError):
                pass


def configure_matplotlib_cjk():
    _register_windows_cjk_font_files()
    matplotlib.rcParams["font.sans-serif"] = _CJK_SANS + list(
        matplotlib.rcParams.get("font.sans-serif", [])
    )
    matplotlib.rcParams["axes.unicode_minus"] = False
    warnings.filterwarnings(
        "ignore",
        message=r"Glyph \d+ missing from current font\.",
    )
    # 子进程常用 MPLBACKEND=Agg：plt.show() 会报「非 GUI 无法弹窗」，非错误。
    warnings.filterwarnings(
        "ignore",
        message=r".*[Nn]on-?GUI backend.*show the figure.*",
    )


def legend_kw(ax, labelcolor="white", **kwargs):
    leg = ax.legend(**kwargs)
    if leg is not None and labelcolor is not None:
        for t in leg.get_texts():
            t.set_color(labelcolor)
    return leg


def _patch_output_paths():
    repo = Path(__file__).resolve().parent

    original_figure_savefig = Figure.savefig

    def patched_figure_savefig(self, fname, *args, **kwargs):
        if isinstance(fname, (str, os.PathLike)):
            target = resolve_generated_output(repo, os.fspath(fname))
            target.parent.mkdir(parents=True, exist_ok=True)
            fname = str(target)
        return original_figure_savefig(self, fname, *args, **kwargs)

    Figure.savefig = patched_figure_savefig

    original_animation_save = mpl_animation.Animation.save

    def patched_animation_save(self, filename, *args, **kwargs):
        if isinstance(filename, (str, os.PathLike)):
            target = resolve_generated_output(repo, os.fspath(filename))
            target.parent.mkdir(parents=True, exist_ok=True)
            filename = str(target)
        return original_animation_save(self, filename, *args, **kwargs)

    mpl_animation.Animation.save = patched_animation_save


configure_matplotlib_cjk()
_patch_output_paths()
