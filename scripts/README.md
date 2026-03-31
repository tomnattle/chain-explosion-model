# Scripts Layout

This directory collects most runnable experiment scripts so that the repository root can stay focused on core modules, orchestration entry points, configuration, documentation, and archived results.

## Subdirectories

- `ce/`: foundational chain-explosion experiments and related CE variants
- `verify/`: verification-style scripts
- `discover/`: discovery and parameter-scan scripts
- `explore/`: exploratory, critique, and CHSH-oriented scripts
- `misc/`: small standalone or older auxiliary experiments

## Running

If you want the repository to resolve script names automatically after the reorganization, use the root-level runners:

- `python run_with_mpl_compat.py ce_00_double_slit_demo.py`
- `python run_unified_suite.py`
- `python run_all_simulations.py`

Those entry points can now locate moved scripts by filename, so old script names still work in the main workflow.
