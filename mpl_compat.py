# Matplotlib < 3.3: Legend has no keyword "labelcolor".
# Chinese labels: default DejaVu Sans has no CJK glyphs → Glyph missing warnings on Windows.

import os
import sys
import warnings

import matplotlib

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


configure_matplotlib_cjk()
