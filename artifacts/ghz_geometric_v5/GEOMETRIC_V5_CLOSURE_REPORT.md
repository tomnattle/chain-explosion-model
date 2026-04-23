# Geometric V5 External-Closure Audit

## Goals
- External connector for real GHZ shot-level data
- 24x24 coarse exploration + focused local deep sampling
- New objective: density `D = F * R`

## Main Results
- coarse best F: 4.000000 at R=0.262555, D=1.050220
- coarse best D: 1.373068 with F=3.893187, R=0.352685
- focus best F: 3.997825 at R=0.229887, D=0.919050
- focus best D: 1.059039 with F=3.993320, R=0.265203
- count(F>3.5 and R>0.5): 0

## External Audit
- status: OK
- use `--external-shots <path>` with CSV/JSON shot file.