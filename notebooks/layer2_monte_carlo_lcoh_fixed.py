"""
layer2_monte_carlo_lcoh.py
==========================
Monte Carlo LCOH Analysis -- CORRECTED VERSION

Corrections applied vs prior version:
1. Electrolyser CF is now ENDOGENOUS:
   CF_elec = min(CF_renov x oversizing, 1.0)
   where CF_renov = weighted average of sampled solar/wind CFs
   Prior version fixed CF_elec = 0.45 independently of CFs.
2. Stack replacement correctly amortised over stack lifetime hours
   (not calendar hours of project lifetime).
3. Explicit LCOH equation documented.

Reference: IEA GHR 2024, IRENA RPGC 2024, CHM 2024.
"""

import numpy as np
import pandas as pd
from scipy.stats import triang, spearmanr
from pathlib import Path

# ── PARAMETERS ────────────────────────────────────────────────
N          = 10_000
SEED       = 42
RATIO_SOLAR   = 0.50   # 50% solar capacity
RATIO_WIND    = 0.50   # 50% wind capacity
OVERSIZING    = 1.50   # renewable capacity / PEM capacity
LHV_H2_KWH_KG = 33.33  # kWh/kg

# Triangular distributions (min, mode, max)
# Source: IEA GHR 2024, IRENA RPGC 2024, CHM 2024
PARAMS = {
    "PEM CAPEX (EUR/kW)":    (950,  1200, 1600),
    "PEM OPEX (%)":           (1.5,     3,    5),
    "PEM efficiency (%)":     (60,     67,   72),
    "Stack lifetime (kh)":    (60,     80,  100),
    "Stack replacement (%)":  (15,     25,   40),
    "Solar CAPEX (EUR/kW)":   (524,   750, 1200),
    "Wind CAPEX (EUR/kW)":   (1100,  1550, 2000),
    "Solar CF (%)":           (13,     15,   20),
    "Wind CF (%)":            (24,     33,   38),
    "WACC (%)":               (6,       8,   10),
    "Project lifetime (y)":   (20,     25,   30),
}


def sample_tri(low, mode, high, n=N, seed=SEED):
    """Sample from triangular distribution."""
    rng = np.random.default_rng(seed)
    c   = (mode - low) / (high - low)
    return triang.rvs(c, loc=low, scale=high-low,
                      size=n, random_state=rng)


def calc_lcoh(samples: dict) -> dict:
    """
    Calculate LCOH with endogenous electrolyser CF.

    LCOH (EUR/MWh_H2) = CAPEX_ann + OPEX_ann
                       + Stack_ann + Elec_ann

    Returns dict with LCOH and intermediate values.
    """
    wacc  = samples["WACC (%)"] / 100
    n_yr  = samples["Project lifetime (y)"]
    eff   = samples["PEM efficiency (%)"] / 100

    # Capital recovery factor
    crf_pem   = wacc / (1 - (1 + wacc)**-n_yr)
    crf_renov = wacc / (1 - (1 + wacc)**-25)

    # ── CORRECTION 1: Endogenous electrolyser CF ──────────────
    cf_solar = samples["Solar CF (%)"] / 100
    cf_wind  = samples["Wind CF (%)"]  / 100
    cf_renov = (cf_solar * RATIO_SOLAR
                + cf_wind  * RATIO_WIND)
    cf_elec  = np.minimum(cf_renov * OVERSIZING, 1.0)

    # H2 energy produced per MW_PEM per year (MWh_H2/MW/y)
    h2_mwh_per_mw = cf_elec * 8760 * eff

    # ── CAPEX annualised (EUR/MWh_H2) ─────────────────────────
    capex_ann = (samples["PEM CAPEX (EUR/kW)"] * 1000
                 * crf_pem / h2_mwh_per_mw)

    # ── OPEX annualised (EUR/MWh_H2) ──────────────────────────
    opex_ann = (samples["PEM CAPEX (EUR/kW)"] * 1000
                * samples["PEM OPEX (%)"] / 100
                / h2_mwh_per_mw)

    # ── CORRECTION 2: Stack replacement over lifetime hours ───
    # Cost per operating hour = CAPEX x rep_pct / lifetime_h
    # -> EUR/MWh_H2 = cost_per_hour / eff
    stack_cost_mw = (samples["PEM CAPEX (EUR/kW)"] * 1000
                     * samples["Stack replacement (%)"] / 100)
    stack_life_h  = samples["Stack lifetime (kh)"] * 1000
    stack_ann     = stack_cost_mw / stack_life_h / eff

    # ── Electricity cost (EUR/MWh_H2) ─────────────────────────
    c_solar = (samples["Solar CAPEX (EUR/kW)"] * 1000
               * crf_renov / (cf_solar * 8760))
    c_wind  = (samples["Wind CAPEX (EUR/kW)"] * 1000
               * crf_renov / (cf_wind  * 8760))
    c_elec  = (c_solar * cf_solar * RATIO_SOLAR
               + c_wind  * cf_wind  * RATIO_WIND) / cf_renov
    elec_ann = c_elec / eff

    # ── TOTAL LCOH ────────────────────────────────────────────
    lcoh_mwh = capex_ann + opex_ann + stack_ann + elec_ann
    lcoh_kg  = lcoh_mwh / LHV_H2_KWH_KG

    return {
        "lcoh_eur_kg":  lcoh_kg,
        "lcoh_eur_mwh": lcoh_mwh,
        "cf_elec":      cf_elec,
        "cf_solar":     cf_solar,
        "cf_wind":      cf_wind,
        "capex_ann":    capex_ann,
        "opex_ann":     opex_ann,
        "stack_ann":    stack_ann,
        "elec_ann":     elec_ann,
    }


def run_monte_carlo():
    """Run full Monte Carlo simulation."""
    print(f"Running Monte Carlo LCOH (N={N:,})...")

    # Sample all parameters
    samples = {}
    for i, (k, (lo, mo, hi)) in enumerate(PARAMS.items()):
        samples[k] = sample_tri(lo, mo, hi, n=N, seed=SEED+i)

    # Calculate LCOH
    results = calc_lcoh(samples)
    lcoh_kg = results["lcoh_eur_kg"]

    # ── STATISTICS ────────────────────────────────────────────
    pcts = np.percentile(lcoh_kg, [5, 25, 50, 75, 95])
    print(f"  P5  = {pcts[0]:.2f} EUR/kg")
    print(f"  P50 = {pcts[2]:.2f} EUR/kg")
    print(f"  P95 = {pcts[4]:.2f} EUR/kg")
    print(f"  Mean = {lcoh_kg.mean():.2f} EUR/kg")
    print(f"  CF_elec mean = {results['cf_elec'].mean():.3f}")
    print(f"  % < SMR (2.94): {(lcoh_kg < 2.94).mean()*100:.1f}%")

    # ── SPEARMAN CORRELATIONS ──────────────────────────────────
    spearman = {}
    for k, v in samples.items():
        r, _ = spearmanr(v, lcoh_kg)
        spearman[k] = round(r, 3)
    spearman_sorted = dict(
        sorted(spearman.items(),
               key=lambda x: abs(x[1]), reverse=True)
    )
    print("\nSpearman correlations (top 5):")
    for k, v in list(spearman_sorted.items())[:5]:
        print(f"  {k:<25} {v:+.3f}")

    # ── DECOMPOSITION AT P50 ───────────────────────────────────
    idx_p50 = np.argmin(np.abs(lcoh_kg - pcts[2]))
    total   = results["lcoh_eur_mwh"][idx_p50]
    print(f"\nDecomposition at P50 ({pcts[2]:.2f} EUR/kg):")
    for comp in ["elec_ann", "capex_ann", "opex_ann", "stack_ann"]:
        pct = results[comp][idx_p50] / total * 100
        print(f"  {comp:<12} {pct:.1f}%")

    # ── SAVE ──────────────────────────────────────────────────
    Path("results").mkdir(exist_ok=True)
    df = pd.DataFrame(results)
    df.to_csv("results/lcoh_mc_v3_final.csv", index=False)

    summary = pd.DataFrame([{
        "N": N,
        "p5_eur_kg":  pcts[0], "p25_eur_kg": pcts[1],
        "p50_eur_kg": pcts[2], "p75_eur_kg": pcts[3],
        "p95_eur_kg": pcts[4], "mean_eur_kg": lcoh_kg.mean(),
        "std_eur_kg": lcoh_kg.std(),
        "cf_elec_mean": results["cf_elec"].mean(),
        "pct_below_smr": (lcoh_kg < 2.94).mean() * 100,
        **{f"spearman_{k.replace(' ','_')}": v
           for k, v in spearman.items()},
    }])
    summary.to_csv("results/lcoh_mc_summary_v3.csv", index=False)
    print("\nSaved: results/lcoh_mc_v3_final.csv")
    print("Saved: results/lcoh_mc_summary_v3.csv")

    return results, spearman_sorted


if __name__ == "__main__":
    results, spearman = run_monte_carlo()
