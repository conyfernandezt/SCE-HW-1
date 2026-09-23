"""
Tsukumo Casework - Discovery Set 5 - Task 9

"""

import numpy as np
import pandas as pd
import math
from pathlib import Path

DATA_DIR = Path(".")

Z99 = 2.326
FTL = 272
MIN_ORDER = 0.10 * FTL          # 27.2 -> 27 units per the task text
REVIEW_INTERVAL = 7
MIN_AUTONOMY_DAYS = 14
TARGET_AUTONOMY_DAYS = 21        # 3-week FC target
HORIZON = 364

RAD_LEAD_TIME = {                # Table 4
    "GA-303": 0, "NY-134": 2, "TX-799": 3, "UT-841": 4,
    "AZ-852": 4, "CA-900": 4, "CA-945": 5, "CO-802": 3, "FL-331": 2,
    "IL-606": 2, "MA-021": 2, "MI-481": 2, "NC-275": 1, "NJ-070": 2,
    "TX-750": 2, "TX-770": 2, "WA-980": 5,
}

DISTANCE_COLUMNS_15FC = [
    "GA-303", "UT-841", "AZ-852", "CA-900", "CA-945", "CO-802", "FL-331",
    "IL-606", "MA-021", "MI-481", "NC-275", "NJ-070", "TX-750", "TX-770", "WA-980",
]

# capacity conversion (Appendix 1 + task text)
UNIT_HANDLING_TIME_HR = 12 / 60
Q, A, R, E = 0.98, 0.90, 0.95, 0.90
SHIFT_HOURS = 8
F_THRESHOLD = 0.3
COST_THROUGHPUT_OM = 3.60        # $/unit(resource)/day
COST_THROUGHPUT_SETUP = 25.20    # $/unit increase, one-time
COST_THROUGHPUT_UTIL = 25.0      # $/unit of utilized capacity

# Load & prep (mirrors Task 7/8 construction exactly)

def load_fc_daily():
    demand = pd.read_csv("task2_demand_results.csv")
    df_distance = pd.read_csv("Assignment/fc_zip3_distance.csv")
    df_distance["closest_location"] = df_distance[DISTANCE_COLUMNS_15FC].idxmin(axis=1)

    demand = demand.merge(df_distance[["ZIP3", "closest_location"]], on="ZIP3", how="left")

    fc_daily = (
        demand.groupby(["Week", "Day", "closest_location"])
        .agg(Mean_Demand=("Mean_Demand", "sum"),
             Sigma=("Sigma", lambda x: np.sqrt((x ** 2).sum())))
        .reset_index()
    )
    fc_daily["Time"] = (fc_daily["Week"] - 1) * 7 + (fc_daily["Day"] - 1)
    fc_daily = fc_daily.sort_values(["closest_location", "Time"])

    network_daily = (
        demand.groupby(["Week", "Day"])
        .agg(Mean_Demand=("Mean_Demand", "sum"),
             Sigma=("Sigma", lambda x: np.sqrt((x ** 2).sum())))
        .reset_index()
    )
    network_daily["Time"] = (network_daily["Week"] - 1) * 7 + (network_daily["Day"] - 1)
    network_daily = network_daily.sort_values("Time")

    return fc_daily, network_daily


# ----------------------------------------------------------------------
# Part 1: replenishment simulation
# ----------------------------------------------------------------------
def robust_cum_demand(means, sigmas, start_day, n_days):
    """True rolling sum, wrapping the 364-day calendar if needed near year-end."""
    N = len(means)
    idx = [(start_day + i) % N for i in range(n_days)]
    d = means[idx].sum()
    s = np.sqrt((sigmas[idx] ** 2).sum())
    return d + Z99 * s


def robust_autonomy_days(means, sigmas, start_day, inventory_position, max_search=60):
    if inventory_position <= 0:
        return 0
    for l in range(1, max_search + 1):
        if robust_cum_demand(means, sigmas, start_day, l) > inventory_position:
            return l - 1
    return max_search


def target_21d(means, sigmas, day):
    return robust_cum_demand(means, sigmas, day, TARGET_AUTONOMY_DAYS)


def simulate_fc(fc_name, means, sigmas, horizon=HORIZON):
    lead_time = RAD_LEAD_TIME[fc_name]
    on_hand = target_21d(means, sigmas, 0)
    in_transit = {}
    last_review = 0
    replen_qty = np.zeros(horizon)
    on_hand_series = np.zeros(horizon)
    autonomy_series = np.zeros(horizon)

    for t in range(horizon):
        if t in in_transit:
            on_hand += in_transit.pop(t)
        on_hand -= means[t]
        on_hand = max(on_hand, 0.0)

        inv_position = on_hand + sum(in_transit.values())
        autonomy = robust_autonomy_days(means, sigmas, t + 1, inv_position)

        order_qty = 0.0
        if autonomy < MIN_AUTONOMY_DAYS:
            order_qty = max(target_21d(means, sigmas, t) - inv_position, MIN_ORDER)
            last_review = t
        elif (t - last_review) >= REVIEW_INTERVAL:
            if autonomy < TARGET_AUTONOMY_DAYS:
                order_qty = max(target_21d(means, sigmas, t) - inv_position, MIN_ORDER)
            last_review = t

        if order_qty > 0:
            arrival = t + lead_time
            if arrival < horizon:
                in_transit[arrival] = in_transit.get(arrival, 0.0) + order_qty
            replen_qty[t] = order_qty

        on_hand_series[t] = on_hand
        autonomy_series[t] = autonomy

    return pd.DataFrame({"Time": np.arange(horizon), "on_hand": on_hand_series,
                          "autonomy_days": autonomy_series, "replen_qty": replen_qty,
                          "demand": means[:horizon]})


# ----------------------------------------------------------------------
# Part 2c/2d: throughput -> resources -> cost
# ----------------------------------------------------------------------
def resources_needed(C_hours, shift_hours=SHIFT_HOURS, f=F_THRESHOLD):
    n_raw = C_hours / shift_hours
    frac = n_raw - int(n_raw)
    return (int(n_raw) if frac <= f else int(n_raw) + 1), n_raw


def capacity_hours(d_units, t=UNIT_HANDLING_TIME_HR, q=Q, a=A, r=R, e=E):
    return (d_units * t) / (q * a * r * e)



# Part 2a/2b: DC throughput under the three Task 8 production strategies

def dc_production_strategies(network_daily):
    means = network_daily["Mean_Demand"].to_numpy()
    N = len(means)
    avg_demand = means.mean()

    # Pursuit: reuse the team's own Task 8 DC_Inventory-delta approach if
    # present; else approximate via the 42-day rolling target's own delta.
    sigmas = network_daily["Sigma"].to_numpy()
    target42 = np.array([robust_cum_demand(means, sigmas, t, 42) for t in range(N)])
    dc_delta = np.diff(target42, prepend=target42[0])
    production_pursuit = means + dc_delta

    production_smooth = np.full(N, avg_demand)

    week = network_daily["Week"].to_numpy()
    segment = np.select(
        [(week >= 1) & (week <= 21), (week >= 22) & (week <= 27),
         (week >= 28) & (week <= 44), (week >= 45) & (week <= 48),
         (week >= 49) & (week <= 52)], [1, 2, 3, 4, 5])
    seg_rate = {s: means[segment == s].mean() for s in [1, 2, 3, 4, 5]}
    production_segmented = np.array([seg_rate[s] for s in segment])

    return {"Pursuit": production_pursuit, "Full Smoothing": production_smooth,
            "Segmented": production_segmented}, seg_rate


if __name__ == "__main__":
    fc_daily, network_daily = load_fc_daily()

    print("=" * 70)
    print("PART 1: Replenishment simulation per FC")
    print("=" * 70)
    all_fc_results = {}
    all_replen_total = np.zeros(HORIZON)
    for fc in fc_daily["closest_location"].unique():
        d = fc_daily[fc_daily["closest_location"] == fc].sort_values("Time")
        means = d["Mean_Demand"].to_numpy()
        sigmas = d["Sigma"].to_numpy()
        if len(means) < HORIZON:
            print(f"  [WARN] {fc}: only {len(means)} days of data, expected {HORIZON}")
            continue
        result = simulate_fc(fc, means, sigmas)
        all_fc_results[fc] = result
        all_replen_total[:len(result)] += result["replen_qty"].to_numpy()
        n_orders = (result["replen_qty"] > 0).sum()
        print(f"  {fc:8s}: {n_orders:3d} orders/yr, "
              f"avg {result.loc[result.replen_qty>0,'replen_qty'].mean():7.1f}, "
              f"max {result['replen_qty'].max():7.1f}")

    print("\n" + "=" * 70)
    print("PART 2a/2c/2d: FC throughput -> resources")
    print("=" * 70)
    fc_resource_rows = []
    for fc, result in all_fc_results.items():
        inbound_peak = result["replen_qty"].max()
        outbound_peak = result["demand"].max()
        peak = inbound_peak + outbound_peak
        C = capacity_hours(peak)
        N_res, n_raw = resources_needed(C)
        fc_resource_rows.append({"FC": fc, "inbound_peak": inbound_peak,
                                  "outbound_peak": outbound_peak, "peak_total": peak,
                                  "C_hours": C, "n_raw": n_raw, "N": N_res})
    fc_res_df = pd.DataFrame(fc_resource_rows).sort_values("peak_total", ascending=False)
    print(fc_res_df.round(2).to_string(index=False))
    print(f"\nTotal FC resources: {fc_res_df['N'].sum()}")

    print("\n" + "=" * 70)
    print("PART 2a/2b: DC throughput across the three Task 8 strategies")
    print("=" * 70)
    strategies, seg_rate = dc_production_strategies(network_daily)
    print("Segment production rates:", {k: round(v, 1) for k, v in seg_rate.items()})
    for name, production in strategies.items():
        dc_inbound = production
        dc_outbound = all_replen_total[:len(production)]
        total = dc_inbound + dc_outbound
        C = capacity_hours(total.max())
        N_res, n_raw = resources_needed(C)
        print(f"  {name:15s}: max production/day={production.max():8.1f}, "
              f"max DC throughput/day={total.max():8.1f}, N={N_res}")

    print("\n" + "=" * 70)
    print("PART 2d: Sensitivity on q, r, e (network-wide, FC total)")
    print("=" * 70)
    total_peak = fc_res_df["peak_total"].sum()
    for label, (q, r, e) in {
        "Baseline (.98/.95/.90)": (0.98, 0.95, 0.90),
        "Lower q (.90)": (0.90, 0.95, 0.90),
        "Lower r (.85)": (0.98, 0.85, 0.90),
        "Lower e (.80)": (0.98, 0.95, 0.80),
        "All lower": (0.90, 0.85, 0.80),
    }.items():
        C = capacity_hours(total_peak, q=q, r=r, e=e)
        N_res, n_raw = resources_needed(C)
        annual_om = N_res * COST_THROUGHPUT_OM * 365
        print(f"  {label:25s}: N={N_res:4d}  annual O&M=${annual_om:,.0f}")