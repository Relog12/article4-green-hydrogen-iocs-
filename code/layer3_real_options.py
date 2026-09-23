"""
layer3_real_options.py
======================
Longstaff-Schwartz Real Options Analysis — CORRECTED VERSION

Corrections applied vs prior version:
1. Terminal condition: max(payoff_2050, 0) — option never negative
2. Exercise rule: payoff > 0 AND payoff > continuation value
3. Never-exercise paths correctly identified and separated

Reference: Longstaff & Schwartz (2001), Rev. Financial Studies 14(1).
"""

import numpy as np
import pandas as pd
from pathlib import Path

# ── PARAMETERS ────────────────────────────────────────────────
N_PATHS  = 5_000
N_STEPS  = 6
DT       = 5
DISCOUNT = 0.07
SEED_LS  = 123

YEARS_LS = [2025, 2030, 2035, 2040, 2045, 2050]

ETS_TRAJ = {
    "STEPS": [80,  100, 115, 135, 140, 145],
    "APS":   [90,  140, 170, 200, 215, 230],
    "NZE":   [130, 175, 215, 250, 270, 290],
}
TTF_TRAJ = {
    "STEPS": [35, 30, 28, 25, 23, 22],
    "APS":   [38, 33, 30, 27, 24, 22],
    "NZE":   [40, 35, 30, 25, 20, 18],
}

VOL_ETS      = 0.35
VOL_TTF      = 0.45
CORR_ETS_TTF = 0.30

PEM_CAPEX_EUR_KW = 1200
PEM_CAPACITY_MW  = 100
H2_DEMAND_MWH_Y  = 100_000
SMR_GAS_CONSUMPTION = 1.33
SMR_CO2_INTENSITY   = 0.30

LCOH_PEM_TRAJ = {
    "STEPS": [160, 140, 125, 115, 108, 105],
    "APS":   [160, 130, 112,  98,  90,  85],
    "NZE":   [160, 115,  95,  82,  75,  70],
}


def simulate_paths(scen: str):
    """Simulate correlated GBM paths for ETS and TTF."""
    rng    = np.random.default_rng(SEED_LS)
    corr   = np.array([[1.0, CORR_ETS_TTF],
                        [CORR_ETS_TTF, 1.0]])
    L      = np.linalg.cholesky(corr)
    ets_mu = np.array(ETS_TRAJ[scen], dtype=float)
    ttf_mu = np.array(TTF_TRAJ[scen], dtype=float)

    ets = np.zeros((N_PATHS, N_STEPS))
    ttf = np.zeros((N_PATHS, N_STEPS))
    ets[:, 0] = ets_mu[0]
    ttf[:, 0] = ttf_mu[0]

    for t in range(1, N_STEPS):
        z      = rng.standard_normal((2, N_PATHS))
        z_corr = L @ z
        ets[:, t] = ets[:, t-1] * np.exp(
            np.log(ets_mu[t] / ets_mu[t-1])
            - 0.5 * VOL_ETS**2 * DT
            + VOL_ETS * np.sqrt(DT) * z_corr[0]
        )
        ttf[:, t] = ttf[:, t-1] * np.exp(
            np.log(ttf_mu[t] / ttf_mu[t-1])
            - 0.5 * VOL_TTF**2 * DT
            + VOL_TTF * np.sqrt(DT) * z_corr[1]
        )
    return ets, ttf


def compute_payoff(ets, ttf, t_idx, scen):
    """NPV of investing now in PEM. Can be negative."""
    smr_mc   = ttf * SMR_GAS_CONSUMPTION + ets * SMR_CO2_INTENSITY
    lcoh_pem = LCOH_PEM_TRAJ[scen][t_idx]
    annual_saving = (smr_mc - lcoh_pem) * H2_DEMAND_MWH_Y / 1e6
    capex = PEM_CAPEX_EUR_KW * PEM_CAPACITY_MW * 1000 / 1e6
    yrs   = max(1, YEARS_LS[-1] - YEARS_LS[t_idx])
    annuity = (1 - (1 + DISCOUNT)**-yrs) / DISCOUNT
    npv   = annual_saving * annuity - capex
    disc  = (1 + DISCOUNT)**(-(YEARS_LS[t_idx] - 2025))
    return npv * disc


def longstaff_schwartz_fixed(scen: str) -> dict:
    """
    LSM with corrected terminal condition and exercise rule.

    CORRECTIONS vs prior version:
    - Terminal: cash_flow = max(payoff_2050, 0)  [not exercised if negative]
    - Exercise: payoff > 0 AND payoff > continuation
    - Option value = max(0, mean(cash_flows)) [bounded below by zero]
    """
    ets_paths, ttf_paths = simulate_paths(scen)

    payoffs = np.zeros((N_PATHS, N_STEPS))
    for t in range(N_STEPS):
        payoffs[:, t] = compute_payoff(
            ets_paths[:, t], ttf_paths[:, t], t, scen
        )

    # ── CORRECTION 1: Terminal floor at zero ─────────────────
    cash_flow     = np.maximum(payoffs[:, -1], 0.0)
    exercise_time = np.where(
        payoffs[:, -1] > 0, N_STEPS - 1, N_STEPS
    )

    # ── BACKWARD INDUCTION ───────────────────────────────────
    for t in range(N_STEPS - 2, -1, -1):
        disc      = (1 + DISCOUNT)**(-DT)
        not_yet   = exercise_time > t

        # ── CORRECTION 2: Only ITM paths (payoff > 0) ────────
        itm = (payoffs[:, t] > 0) & not_yet

        if itm.sum() < 50:
            cash_flow[not_yet] *= disc
            continue

        X  = ets_paths[itm, t]
        Y  = ttf_paths[itm, t]
        basis = np.column_stack([
            np.ones(itm.sum()), X, Y, X**2, Y**2, X*Y
        ])
        try:
            coeffs, _, _, _ = np.linalg.lstsq(
                basis, cash_flow[itm] * disc, rcond=None
            )
            continuation = basis @ coeffs
        except Exception:
            cash_flow[not_yet] *= disc
            continue

        idx_itm = np.where(itm)[0]
        for i, path_idx in enumerate(idx_itm):
            if payoffs[path_idx, t] > continuation[i]:
                cash_flow[path_idx]     = payoffs[path_idx, t]
                exercise_time[path_idx] = t

        exercised = (exercise_time == t) & itm
        cash_flow[not_yet & ~exercised] *= disc

    # ── CORRECTION 3: Option value bounded at zero ───────────
    option_value = max(0.0, cash_flow.mean())
    option_std   = cash_flow.std() / np.sqrt(N_PATHS)
    npv_static   = payoffs[:, 0].mean()

    ex_yrs = np.where(
        exercise_time < N_STEPS,
        np.array(YEARS_LS)[np.minimum(exercise_time, N_STEPS-1)],
        9999
    )
    timing = {int(y): (ex_yrs == y).mean() for y in YEARS_LS}
    timing["never"] = (ex_yrs == 9999).mean()

    return {
        "scenario":       scen,
        "option_value_M": option_value,
        "option_std_M":   option_std,
        "npv_static_M":   npv_static,
        "pct_positive":   (cash_flow > 0).mean() * 100,
        "timing_dist":    timing,
        "cash_flows":     cash_flow,
        "payoffs_t0":     payoffs[:, 0],
    }


if __name__ == "__main__":
    print("LSM Real Options Analysis (corrected)")
    print("=" * 50)
    results = {}
    for scen in ["STEPS", "APS", "NZE"]:
        r = longstaff_schwartz_fixed(scen)
        results[scen] = r
        print(f"{scen}: option = {r['option_value_M']:+.2f} MEur "
              f"({r['pct_positive']:.1f}% positive)")

    # Save results
    records = [{
        "scenario":       s,
        "option_value_M": r["option_value_M"],
        "option_std_M":   r["option_std_M"],
        "npv_static_M":   r["npv_static_M"],
        "pct_positive":   r["pct_positive"],
        **{f"pct_{k}": v*100 for k, v in r["timing_dist"].items()},
    } for s, r in results.items()]
    pd.DataFrame(records).to_csv(
        Path("results") / "real_options_ls_fixed.csv", index=False
    )
    print("Saved: results/real_options_ls_fixed.csv")
