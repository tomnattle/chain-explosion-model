# V9 Realdata Gate Report

- final_pass: **False**
- optimum: mu=0.924882, rho=1.850000, eta=0.042232
- thresholds: val_r2>=0.9, blind_r2>=0.8, blind_nrmse<=fit_nrmse*2.0

| experiment | fit_nrmse | val_nrmse | blind_nrmse | fit_r2 | val_r2 | blind_r2 | gate_pass |
|---|---:|---:|---:|---:|---:|---:|:---:|
| dispersion_n_omega | 0.054461 | 0.214630 | 0.224349 | 0.966116 | 0.470311 | 0.421043 | N |
| absorption_alpha_omega | 0.118522 | 0.594984 | 0.841762 | 0.839557 | -3.071074 | -7.151070 | N |
| reflectance_r_theta | 0.135240 | 0.074623 | 0.115200 | 0.788628 | 0.936695 | 0.849103 | Y |
| group_delay_tau_omega | 0.289378 | 1.325824 | 1.535492 | 0.011416 | -19.229249 | -26.134138 | N |