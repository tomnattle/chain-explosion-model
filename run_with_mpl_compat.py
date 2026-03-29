"""
在导入 matplotlib 之前加载 mpl_compat（中文字体 + 抑制缺字刷屏），再按 __main__ 执行目标脚本。

供 run_unified_suite / 本地需减少 Glyph missing 时使用：
  python run_with_mpl_compat.py ce_00_double_slit_demo.py
"""
import runpy
import sys
from pathlib import Path


def main():
    repo = Path(__file__).resolve().parent
    if len(sys.argv) < 2:
        sys.stderr.write("usage: python run_with_mpl_compat.py SCRIPT.py [args...]\n")
        return 2
    script_arg = sys.argv[1]
    target = Path(script_arg)
    if not target.is_file():
        target = repo / script_arg
    if not target.is_file():
        sys.stderr.write("not found: %s\n" % script_arg)
        return 2

    sys.path.insert(0, str(repo))
    import mpl_compat  # noqa: F401

    path_s = str(target.resolve())
    sys.argv = [path_s] + sys.argv[2:]
    try:
        runpy.run_path(path_s, run_name="__main__")
    except SystemExit as e:
        code = e.code
        if code is None:
            return 0
        if isinstance(code, int):
            return code
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
