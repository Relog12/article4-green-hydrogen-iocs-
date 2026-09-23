# Green hydrogen at European oil-major refineries

Code and data for the paper *Green hydrogen at European oil-major refineries: an
institutional barrier, not a technology problem* (E. Relogio, M. Robaina, L. A. C. Tarelho).

## Structure
- `code/`     analysis notebook and Layer 2 (Monte Carlo LCOH) / Layer 3 (Longstaff-Schwartz) scripts
- `data/`     renewable capacity-factor profiles and firm hydrogen-demand data
- `results/`  model output backing the figures; `results/tables/` are the supplementary tables
- `figures/`  final article figures (1-8)

## Reproduce
Python 3.11. `pip install -r requirements.txt` (PyPSA 0.35.1, pandas 2.2.3, numpy 1.26.4,
HiGHS solver, tsam, scipy). Random seed 42 throughout. Run the notebook in `code/`.

## Data sources / attribution
Renewable profiles derived from renewables.ninja (Pfenninger & Staffell, 2016;
Staffell & Pfenninger, 2016). Firm data from company disclosures. Third-party reports
(IEA, IRENA, company annual reports) are NOT redistributed here; see the paper's reference list.
