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

L1: Deterministic capacity expansion (5 firms x 3 climate scenarios x 2 foresight modes = 30 runs). PyPSA + HiGHS.
L2: Stochastic LCOH on fixed capacities (10000 MC). NumPy / pandas.
L3: Real options analysis (Longstaff-Schwartz). NumPy.

## Temporal representation

Time series aggregation via tsam: 12 representative days + 2 extreme days,
preserving annual means within 3 percent. Extreme days captured via addPeakMax
on price and addPeakMin on solar, ensuring Dunkelflaute events constrain the
capacity expansion decision. Resulting model: 2016 snapshots over 6 investment
periods (2025-2050).

## Climate scenarios (from IEA WEO)

- STEPS - Stated Policies
- APS - Announced Pledges
- NZE - Net Zero Emissions by 2050

## Firms

Shell plc, TotalEnergies SE, BP plc, Eni S.p.A., Repsol S.A.

## Status

- [x] Environment frozen (PyPSA 0.35.1, pandas 2.2.3, numpy 1.26.4)
- [x] PyPSA multi-period model running (typical days, ~5s/run)
- [x] Excel data template (12 sheets, defensive loaders)
- [x] CO2 budget constraint per firm (GlobalConstraint, primary_energy)
- [x] MACC pipeline (budget sweep + shadow prices + cost-emissions trade-off)
- [x] Typical days via tsam (12 typical + 2 extreme, 14-day representation)
- [x] Comparative analysis 24h synthetic vs typical days
- [ ] Data collection in workbook (in progress)
- [ ] Couple load_cost_params to PyPSA (replace placeholder CAPEX_TRAJ)
- [ ] Additional supply technologies (H2 storage, H2 imports, blue H2)
- [ ] Full 30-run pipeline (5 firms x 3 scenarios x 2 foresight modes)
- [ ] L2 Monte Carlo LCOH
- [ ] L3 Longstaff-Schwartz real options
- [ ] Manuscript draft

## Key results so far (synthetic data, placeholder costs)

- 24h synthetic baseline: 2.62 MtCO2 cumulative 2025-2050, NPV 741 M EUR
- Typical days baseline: 3.52 MtCO2 cumulative, NPV 750 M EUR (+34 percent CO2 for +1 percent NPV)
- 50 percent CO2 budget: shadow price 114 EUR/tCO2 (with 24h)
- Typical days expose technical infeasibility for budgets below 10 percent
  of baseline, indicating that >90 percent decarbonisation via supply-side
  alone requires technologies absent from current model (H2 imports, long
  duration storage, or blue H2).

## Methodology notes for paper

- tsam aggregation preserves annual means within 3 percent for solar CF,
  2 percent for wind CF, 0.1 percent for electricity price.
- Cluster 12 (2 days per year, wind CF 0.006, price 91 EUR/MWh) acts as
  Dunkelflaute event that materially constrains firm capacity sizing.
- Models that omit such extreme days systematically over-estimate the
  share of renewable supply that is economically rational, biasing
  decarbonisation pathways downwards.

## Reproducibility note

Versions are pinned because PyPSA 1.0 (released early 2026) introduced a
regression in multi_investment_periods. Last working stable version is 0.35.1.
Do not upgrade PyPSA mid-project.

tsam deprecation: TimeSeriesAggregation class will be removed in tsam v4.0.
Migrate to tsam.aggregate() before any future version upgrade.