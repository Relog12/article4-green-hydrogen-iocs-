# Article 4 - Paris-Aligned Green Hydrogen Pathways for European Oil Majors

**Manuscript:** APEN-D-26-12979 | **Journal:** Applied Energy

PhD thesis — Ernesto Relogio, Universidade de Aveiro
ORCID: 0000-0002-3784-2848 | relog12@ua.pt

## Title
Paris-Aligned Green Hydrogen Pathways for European Oil Majors:
Multi-Period Optimisation, Stochastic LCOH, Hydrogen Storage,
Renewable Profile Sensitivity, and Real Options Analysis

---

## Methodological corrections (revision v2)

Three corrections were applied following peer review:

1. **Storage formulation (e_cyclic)**: Changed from `e_cyclic=True`
   to `e_cyclic=False` in the PyPSA Store component, enabling
   inter-period energy transfer for seasonal salt cavern storage.
   Following Kotzur et al. (2018). Result: baseline CO2 falls
   to zero (not 97%) with correct seasonal buffering.

2. **LSM terminal condition**: Applied `max(payoff_2050, 0)` at
   the terminal date, bounding option values at zero as required
   by option theory. Corrected values: STEPS +3.1, APS +5.0,
   NZE +7.1 MEur per 100 MW PEM.

3. **Monte Carlo electrolyser CF**: Changed from fixed CF=0.45 to
   endogenous CF_elec = min(CF_renov x 1.5, 1.0). Wind CF is now
   the dominant LCOH driver (Spearman rho = -0.47). P50 LCOH =
   4.85 EUR/kg (corrected from 5.32 EUR/kg).

---

## Repository structure

    Article4/
    |-- notebooks/
    |   |-- 01_smoke_test.ipynb              Main model notebook
    |   |-- article4_style.py               Figure style module
    |   |-- layer2_monte_carlo_lcoh_fixed.py Layer 2 MC (corrected)
    |   `-- layer3_real_options_fixed.py     Layer 3 LSM (corrected)
    |-- data/
    |   |-- oil_majors_h2_data_collection.xlsx  Model parameters
    |   |-- real_profiles_DE_2019.csv           Solar/wind profiles
    |   |-- real_profiles_Rotterdam_2019.csv
    |   `-- real_profiles_Tarragona_2019.csv
    |-- results/
    |   |-- macc_sweep_v4_fixed.csv         MACC results (corrected)
    |   |-- lcoh_mc_v3_final.csv            MC LCOH (corrected)
    |   |-- real_options_ls_fixed.csv       LSM results (corrected)
    |   `-- figures/                         Publication figures
    |-- refs/                                Reference PDFs
    |-- requirements.txt                     Frozen dependencies
    |-- environment.yml                      Conda environment
    `-- README.md

---

## Environment

Python 3.11, PyPSA 0.35.1, HiGHS solver.

    conda create -n tese-h2 python=3.11 -y
    conda activate tese-h2
    pip install -r requirements.txt

**IMPORTANT**: Do not upgrade PyPSA beyond 0.35.1.
PyPSA 1.0 introduced a regression in multi_investment_periods.

---

## Three-layer methodology

**Layer 1 (PyPSA)**: Multi-period capacity expansion model.
5 firms x 8 CO2 budgets x 2 storage configurations.
14 representative days (12 typical + 2 extreme Dunkelflaute).
Real DE 2019 profiles from renewables.ninja MERRA-2.

**Layer 2 (Monte Carlo)**: Stochastic LCOH with endogenous
electrolyser CF. N=10,000, 11 triangular parameters.
Audited sources: IEA GHR 2024, IRENA RPGC 2024, CHM 2024.

**Layer 3 (Longstaff-Schwartz)**: Real options analysis.
Corrected terminal condition. N_paths=5,000.
State variables: EU ETS + TTF GBM (vol 35%/y, 45%/y, rho=0.30).

---

## Key results (revised)

| Finding | Result |
|---|---|
| MACC plateau | 13-16 EUR/tCO2 to ~85% abatement |
| Declared targets | All in flat zone (financially undemanding) |
| Storage (corrected) | 100% CO2 reduction, -3% NPV |
| LCOH P50 (corrected) | 4.85 EUR/kg |
| Primary LCOH driver | Wind CF (rho = -0.47) |
| Option value STEPS | +3.1 MEur/100 MW |
| Option value NZE | +7.1 MEur/100 MW |
| Investment barrier | Policy uncertainty > technology cost |

---

## Data sources

- IEA Global Hydrogen Review 2024
- IRENA Renewable Power Generation Costs 2023
- Clean Hydrogen Monitor 2024 (Hydrogen Europe)
- ENTSO-E DE/NL/ES 2019 electricity prices
- renewables.ninja MERRA-2 reanalysis (2019)
- OPSD DE solar/wind profiles 2019

---

## Citation

Relogio, E. (2026). Paris-Aligned Green Hydrogen Pathways for
European Oil Majors. Applied Energy. APEN-D-26-12979.

## Audit status
SHEET09_AUDIT_STATUS = AUDITED_IEA_IRENA_CHM_2024
