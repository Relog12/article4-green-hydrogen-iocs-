# Article 4 - Paris-aligned Green Hydrogen Pathways for European Oil Majors

PhD thesis (Ernesto Relogio, Universidade de Aveiro).
Multi-firm energy system optimisation framework with stochastic LCOH and
real options analysis under climate budget constraints.

## Folder structure

    Article4/
    |-- notebooks/              Jupyter notebooks
    |-- data/                   Excel workbook + raw downloads
    |-- results/                Model outputs
    |-- refs/                   Reference PDFs
    |-- requirements.txt        Frozen Python dependencies
    |-- environment.yml         Conda environment specification
    `-- README.md

## Environment

Python 3.11, PyPSA 0.35.1, HiGHS solver. To rebuild:

    conda create -n tese-h2 python=3.11 -y
    conda activate tese-h2
    pip install -r requirements.txt

## Methodology in three layers

L1: Deterministic capacity expansion (5 firms by 3 climate scenarios by 2 foresight modes = 30 runs). PyPSA + HiGHS.
L2: Stochastic LCOH on fixed capacities (10000 MC). NumPy / pandas.
L3: Real options analysis (Longstaff-Schwartz). NumPy.

## Investment horizon

2025-2050 in 5-year steps. Discount rate 5 percent. Vintages with lifetime decommissioning.

## Climate scenarios (from IEA WEO)

- STEPS - Stated Policies
- APS - Announced Pledges
- NZE - Net Zero Emissions by 2050

## Firms

Shell plc, TotalEnergies SE, BP plc, Eni S.p.A., Repsol S.A.

## Status

- [x] Environment frozen (PyPSA 0.35.1, pandas 2.2.3, numpy 1.26.4)
- [x] PyPSA multi-period model running (1554 vars, optimal in under 2s)
- [x] Excel data template (12 sheets, defensive loaders)
- [x] CO2 budget constraint per firm (GlobalConstraint, primary_energy)
- [x] MACC pipeline (budget sweep + shadow prices + cost-emissions trade-off)
- [ ] Data collection in workbook (in progress)
- [ ] Typical days via tsam
- [ ] Couple load_cost_params to PyPSA (replace placeholder CAPEX_TRAJ)
- [ ] Full 30-run pipeline (5 firms x 3 scenarios x 2 foresight modes)
- [ ] L2 Monte Carlo LCOH
- [ ] L3 Longstaff-Schwartz real options
- [ ] Manuscript draft

## Key results so far (synthetic data, placeholder costs)

- Unconstrained baseline: 2.62 MtCO2 cumulative 2025-2050, NPV 741 M Eur
- 50 percent CO2 budget: NPV +26.5 percent, shadow price 114 Eur/tCO2
- MACC knee at ~95 percent decarbonisation, last 5 percent costs above 2000 Eur/tCO2

## Reproducibility note

Versions are pinned because PyPSA 1.0 (released early 2026) introduced a
regression in multi_investment_periods. Last working stable version is 0.35.1.
Do not upgrade PyPSA mid-project.