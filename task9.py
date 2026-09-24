"""Task 9: 1-FC, 4-FC, and 15-FC replenishment, handling resources, and storage contracting."""


import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent
Z99 = 2.326
FTL = 272
MIN_ORDER = 27  # Explicit rounded minimum used in Task 9's algorithm.
REVIEW_INTERVAL = 7
MIN_AUTONOMY_DAYS = 14
TARGET_AUTONOMY_DAYS = 21
HORIZON = 364  # Assignment's 52 seven-day weeks.
RAD_LEAD_TIME = {
    "GA-303": 0, "NY-134": 2, "TX-799": 3, "UT-841": 4,
    "AZ-852": 4, "CA-900": 4, "CA-945": 5, "CO-802": 3, "FL-331": 2,
    "IL-606": 2, "MA-021": 2, "MI-481": 2, "NC-275": 1, "NJ-070": 2,
    "TX-750": 2, "TX-770": 2, "WA-980": 5,
}
DISTANCE_COLUMNS_15FC = [
    "GA-303", "UT-841", "AZ-852", "CA-900", "CA-945", "CO-802", "FL-331",
    "IL-606", "MA-021", "MI-481", "NC-275", "NJ-070", "TX-750", "TX-770", "WA-980",
]
FC_CONFIGS = {
    "1-FC": ["GA-303"],
    "4-FC": ["GA-303", "NY-134", "TX-799", "UT-841"],
    "15-FC": DISTANCE_COLUMNS_15FC,
}

UNIT_HANDLING_TIME_HR = 12 / 60
Q, A, R, E = 0.98, 0.90, 0.95, 0.90
SHIFT_HOURS = 8
F_THRESHOLD = 0.3
COST_THROUGHPUT_OM = 3.60
COST_THROUGHPUT_SETUP = 25.20
COST_THROUGHPUT_UTIL = 25.0
BASE_STORAGE_RATE = 6.60
BASE_STORAGE_SETUP = 46.20


def load_fc_daily(network="15-FC"):
    """Reassign ZIP3 demand to the nearest FC in the selected network."""
    fc_list = FC_CONFIGS[network]
    demand = pd.read_csv(DATA_DIR / "task2_demand_results.csv")
    distances = pd.read_csv(DATA_DIR / "Assignment/fc_zip3_distance.csv")
    distances["closest_location"] = distances[fc_list].idxmin(axis=1)
    demand = demand.merge(distances[["ZIP3", "closest_location"]], on="ZIP3",
                          how="left", validate="many_to_one")
    if demand["closest_location"].isna().any():
        raise ValueError("Some demand ZIP3s have no FC assignment.")
    if demand.duplicated(["Week", "Day", "ZIP3"]).any():
        raise ValueError("Duplicate daily ZIP3 demand rows.")
    if (not np.isfinite(demand[["Mean_Demand", "Sigma"]]).all().all()
            or (demand[["Mean_Demand", "Sigma"]] < 0).any().any()):
        raise ValueError("Demand and sigma must be finite and nonnegative.")
    def aggregate(keys):
        result = demand.groupby(keys).agg(
            Mean_Demand=("Mean_Demand", "sum"),
            Sigma=("Sigma", lambda x: np.sqrt(np.square(x).sum())),
        ).reset_index()
        result["Time"] = (result["Week"] - 1) * 7 + result["Day"] - 1
        return result.sort_values("Time")
    fc_daily = aggregate(["Week", "Day", "closest_location"])
    network_daily = aggregate(["Week", "Day"])
    for fc in FC_CONFIGS[network]:
        times = fc_daily.loc[fc_daily.closest_location == fc, "Time"].to_numpy()
        if not np.array_equal(times, np.arange(HORIZON)):
            raise ValueError(f"{fc} must have exactly 364 consecutive daily observations.")
    return fc_daily, network_daily


def robust_cum_demand(means, sigmas, start_day, n_days):
    idx = (start_day + np.arange(n_days)) % len(means)
    return means[idx].sum() + Z99 * np.sqrt(np.square(sigmas[idx]).sum())


def robust_autonomy_days(means, sigmas, start_day, inventory_position, max_search=60):
    for days in range(1, max_search + 1):
        if robust_cum_demand(means, sigmas, start_day, days) > inventory_position:
            return days - 1
    return max_search


def target_21d(means, sigmas, day):
    return robust_cum_demand(means, sigmas, day, TARGET_AUTONOMY_DAYS)


def simulate_fc(fc_name, means, sigmas, horizon=HORIZON):
    """Receive, review/ship, receive zero-lead orders, then serve mean demand."""
    on_hand = target_21d(means, sigmas, 0)
    in_transit = {}
    last_shipment = 0  # Initial stock represents a replenishment at time zero.
    backlog = 0.0
    rows = []
    for day in range(horizon):
        inbound = in_transit.pop(day, 0.0)
        on_hand += inbound
        position = on_hand + sum(in_transit.values()) - backlog
        autonomy = robust_autonomy_days(means, sigmas, day, position)
        target = target_21d(means, sigmas, day)
        order = 0
        trigger = "none"
        if autonomy < MIN_AUTONOMY_DAYS:
            trigger = "threshold"
        elif day - last_shipment >= REVIEW_INTERVAL and autonomy < TARGET_AUTONOMY_DAYS:
            trigger = "interval"
        if trigger != "none":
            order = max(math.ceil(target - position), MIN_ORDER)
            arrival_day = day + RAD_LEAD_TIME[fc_name]
            if arrival_day == day:
                inbound += order
                on_hand += order
            else:
                # Retain year-end pipeline in the inventory position.
                in_transit[arrival_day] = in_transit.get(arrival_day, 0) + order
            last_shipment = day
        storage_peak = on_hand
        demand = means[day % len(means)]
        due = backlog + demand
        fulfilled = min(on_hand, due)
        on_hand -= fulfilled
        backlog = due - fulfilled
        robust_outbound = demand + Z99 * sigmas[day % len(means)]
        rows.append({
            "Time": day, "replen_qty": order, "inbound": inbound,
            "demand": demand, "fulfilled": fulfilled, "robust_outbound": robust_outbound,
            "throughput": inbound + robust_outbound,
            "utilized_throughput": inbound + fulfilled,
            "on_hand": on_hand, "storage_peak": storage_peak, "backlog": backlog,
            "in_transit": sum(in_transit.values()),
            "inventory_position_before_order": position,
            "inventory_position": on_hand + sum(in_transit.values()) - backlog,
            "autonomy_days": autonomy, "target_21d": target, "trigger": trigger,
        })
    return pd.DataFrame(rows)


def capacity_hours(d_units, t=UNIT_HANDLING_TIME_HR, q=Q, a=A, r=R, e=E):
    return d_units * t / (q * a * r * e)


def resources_needed(C_hours, shift_hours=SHIFT_HOURS, f=F_THRESHOLD):
    raw = C_hours / shift_hours
    whole = math.floor(raw)
    n = whole if raw - whole <= f + 1e-12 else whole + 1
    # A positive load still needs a worker to absorb the residual hours.
    return max(int(C_hours > 0), n), raw


def resource_profile(frame, q=Q, r=R, e=E):
    result = frame.copy()
    result["C_hours"] = capacity_hours(result["throughput"], q=q, r=r, e=e)
    result["N_daily"] = [resources_needed(c)[0] for c in result.C_hours]
    result["residual_hours"] = np.maximum(result.C_hours - result.N_daily * SHIFT_HOURS, 0)
    return result


def resource_summary(facility, strategy, frame, q=Q, r=R, e=E):
    peak = frame.throughput.max()
    hours = capacity_hours(peak, q=q, r=r, e=e)
    n, raw = resources_needed(hours)
    residual = max(hours - n * SHIFT_HOURS, 0)
    # Appendix rates are per product-unit/day capacity, not per worker.
    units_per_resource = SHIFT_HOURS / capacity_hours(1, q=q, r=r, e=e)
    contracted_units = n * units_per_resource
    om = contracted_units * COST_THROUGHPUT_OM * len(frame)
    setup = contracted_units * COST_THROUGHPUT_SETUP
    handling = frame.utilized_throughput.sum() * COST_THROUGHPUT_UTIL
    return {"facility": facility, "strategy": strategy, "q": q, "r": r, "e": e,
            "peak_throughput": peak, "C_hours": hours, "n_raw": raw, "N": n,
            "residual_hours": residual, "overtime_hours_per_resource": residual / n if n else 0,
            "contracted_units_per_day": contracted_units, "capacity_om": om,
            "capacity_setup": setup, "capacity_cost": om + setup,
            "handling_cost": handling, "total_cost_excluding_overtime": om + setup + handling}


def dc_production_strategies(network_daily, fc_target_total):
    """Task 7 DC target = network six-week target less FC three-week targets."""
    means = network_daily.Mean_Demand.to_numpy()
    sigmas = network_daily.Sigma.to_numpy()
    target42 = np.array([robust_cum_demand(means, sigmas, t, 42) for t in range(len(means))])
    dc_target = np.maximum(target42 - fc_target_total, 0)
    # Beginning-of-day target: serve today's demand, then move to tomorrow's target.
    pursuit = np.maximum(means + np.roll(dc_target, -1) - dc_target, 0)
    smooth = np.full(len(means), means.mean())
    week = network_daily.Week.to_numpy()
    segment = np.searchsorted([21, 27, 44, 48, 52], week, side="left")
    segmented = np.array([means[segment == s].mean() for s in segment])
    return {"Pursuit": pursuit, "Full Smoothing": smooth, "Segmented": segmented}, dc_target


def dc_inventory_profile(production, withdrawals, initial):
    """Receipts precede departures; negative end inventory is retained as backlog."""
    end = initial + np.cumsum(production - withdrawals)
    start = np.r_[initial, end[:-1]]
    return pd.DataFrame({"production": production, "withdrawals": withdrawals,
                         "ending_inventory": end, "storage_required": np.maximum(start + production, 0),
                         "backlog": np.maximum(-end, 0)})


def optimize_storage(inventory, seasonal_rate, spot_rate, min_weeks):
    """LP optimum for divisible capacity and additive whole-week lease blocks."""
    from scipy.optimize import linprog
    from scipy.sparse import csc_matrix, eye, hstack
    inventory = np.asarray(inventory, dtype=float)
    days = len(inventory)
    if days % 7 or not 1 <= min_weeks <= days // 7:
        raise ValueError("Storage horizon must contain whole weeks and valid lease duration.")
    if min(seasonal_rate, spot_rate) <= 0:
        raise ValueError("Seasonal and spot rates must be positive.")
    blocks = [(s * 7, e * 7) for s in range(days // 7)
              for e in range(s + min_weeks, days // 7 + 1)]
    coverage = np.zeros((days, len(blocks)))
    for j, (start, end) in enumerate(blocks):
        coverage[start:end, j] = 1
    costs = np.r_[BASE_STORAGE_RATE * days + BASE_STORAGE_SETUP,
                  [seasonal_rate * (end - start) for start, end in blocks],
                  np.full(days, spot_rate)]
    matrix = hstack([csc_matrix(np.ones((days, 1))), csc_matrix(coverage), eye(days)], format="csc")
    solution = linprog(costs, A_ub=-matrix, b_ub=-inventory, bounds=(0, None), method="highs")
    if not solution.success:
        raise RuntimeError(solution.message)
    base = solution.x[0]
    leases = solution.x[1:1 + len(blocks)]
    seasonal = coverage @ leases
    spot = solution.x[1 + len(blocks):]
    daily = pd.DataFrame({"Time": np.arange(days), "inventory": inventory,
                          "base_capacity": base, "seasonal_capacity": seasonal, "spot_capacity": spot})
    contracts = pd.DataFrame([
        {"start_week": start // 7 + 1, "end_week": end // 7, "capacity": qty,
         "unit_days": qty * (end - start), "cost": qty * (end - start) * seasonal_rate}
        for (start, end), qty in zip(blocks, leases) if qty > 1e-7
    ], columns=["start_week", "end_week", "capacity", "unit_days", "cost"])
    summary = {"base_capacity": base, "base_unit_days": base * days,
               "base_cost": base * costs[0], "seasonal_peak_capacity": seasonal.max(),
               "seasonal_unit_days": seasonal.sum(), "seasonal_cost": seasonal.sum() * seasonal_rate,
               "spot_peak_capacity": spot.max(), "spot_unit_days": spot.sum(),
               "spot_cost": spot.sum() * spot_rate, "total_storage_cost": solution.fun}
    return daily, contracts, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--network", choices=["all", *FC_CONFIGS], default="all",
                        help="Network to run (default: all three networks).")
    parser.add_argument("--seasonal-rate", type=float)
    parser.add_argument("--spot-rate", type=float)
    parser.add_argument("--min-seasonal-weeks", type=int)
    args = parser.parse_args()
    storage_inputs = [args.seasonal_rate, args.spot_rate, args.min_seasonal_weeks]
    if any(x is not None for x in storage_inputs) and not all(x is not None for x in storage_inputs):
        parser.error("Supply all three storage contract inputs together.")
    if all(x is not None for x in storage_inputs):
        if min(args.seasonal_rate, args.spot_rate) <= 0 or not 1 <= args.min_seasonal_weeks <= 52:
            parser.error("Rates must be positive and lease duration between 1 and 52 weeks.")
    networks = list(FC_CONFIGS) if args.network == "all" else [args.network]
    replenishment_summaries = []
    for network in networks:
        replenishment_summaries.append(run_network(network, storage_inputs))
    if args.network == "all":
        pd.concat(replenishment_summaries, ignore_index=True).to_excel(
            DATA_DIR / "outputs/task9/replenishment_summary_all_networks.xlsx", index=False)


def run_network(network, storage_inputs):
    """Write an independent set of workbooks for one FC network."""
    output = DATA_DIR / "outputs/task9" / network
    output.mkdir(parents=True, exist_ok=True)
    fc_daily, network_daily = load_fc_daily(network)
    frames, storage, summaries = {}, {}, []
    replenishment_rows = []
    outbound = np.zeros(HORIZON)
    fc_targets = np.zeros(HORIZON)
    for fc in FC_CONFIGS[network]:
        data = fc_daily[fc_daily.closest_location == fc]
        result = resource_profile(simulate_fc(fc, data.Mean_Demand.to_numpy(), data.Sigma.to_numpy()))
        result.to_excel(output / f"fc_{fc}_daily.xlsx", index=False)
        frames[(fc, "FC")] = result
        outbound += result.replen_qty.to_numpy()
        fc_targets += result.target_21d.to_numpy()
        # The assignment asks for Task 7 target storage, separate from simulated stock.
        storage[f"FC_{fc}_Task7"] = result.target_21d.to_numpy()
        summaries.append(resource_summary(fc, "FC", result))
        orders = result.replen_qty > 0
        # Count orders whose target shortfall is below the minimum, rather
        # than every 27-unit order (which might simply be rounded to 27).
        shortfall = result.target_21d - result.inventory_position_before_order
        floored = orders & (shortfall < MIN_ORDER)
        order_count = int(orders.sum())
        replenishment_rows.append({
            "network": network, "FC": fc,
            "review_interval_days": REVIEW_INTERVAL,
            "minimum_autonomy_days": MIN_AUTONOMY_DAYS,
            "total_orders": order_count, "floored_orders": int(floored.sum()),
            "floor_frequency_pct": 100 * floored.sum() / order_count if order_count else 0.0,
            "average_end_of_day_inventory_units": result.on_hand.mean(),
        })
    replenishment_summary = pd.DataFrame(replenishment_rows)
    replenishment_summary.to_excel(output / "replenishment_summary.xlsx", index=False)
    strategies, dc_target = dc_production_strategies(network_daily, fc_targets)
    means = network_daily.Mean_Demand.to_numpy()
    storage["DC_Task7"] = dc_target
    dc_comparison = []
    for name, production in strategies.items():
        # Preserve the Task 8 withdrawal convention for its storage profiles.
        reference = dc_inventory_profile(production, means, dc_target[0])
        deficit = max(0, -reference.ending_inventory.min())
        reference_feasible = dc_inventory_profile(production, means, dc_target[0] + deficit)
        storage[f"DC_Task8_{name.replace(' ', '_')}"] = reference_feasible.storage_required.to_numpy()
        # Check actual batch shipments as well; expose any extra initial stock needed.
        dc = dc_inventory_profile(production, outbound, dc_target[0])
        extra_initial = max(0, -dc.ending_inventory.min())
        feasible = dc_inventory_profile(production, outbound, dc_target[0] + extra_initial)
        dc["Time"] = np.arange(HORIZON)
        dc["throughput"] = production + outbound
        dc["utilized_throughput"] = dc.throughput
        dc["inventory_with_extra_initial_stock"] = feasible.ending_inventory
        dc["storage_with_extra_initial_stock"] = feasible.storage_required
        dc["Task7_DC_target"] = dc_target
        dc = resource_profile(dc)
        dc.to_excel(output / f"dc_{name.replace(' ', '_')}_daily.xlsx", index=False)
        frames[("DC-GA-303", name)] = dc
        summaries.append(resource_summary("DC-GA-303", name, dc))
        no_initial = dc_inventory_profile(production, means, 0)
        dc_comparison.append({"strategy": name, "peak_production": production.max(),
                              "Task7_initial_stock": dc_target[0],
                              "Task8_extra_initial_stock": deficit,
                              "Task8_peak_storage": reference_feasible.storage_required.max(),
                              "Task8_no_initial_max_backlog": no_initial.backlog.max(),
                              "Task8_no_initial_backlog_days": (no_initial.backlog > 1e-8).sum(),
                              "batch_shipments_max_backlog": dc.backlog.max(),
                              "batch_shipments_backlog_days": (dc.backlog > 1e-8).sum(),
                              "batch_shipments_extra_initial_stock": extra_initial})
    summary = pd.DataFrame(summaries)
    summary.insert(0, "network", network)
    summary.to_excel(output / "handling_summary.xlsx", index=False)
    pd.DataFrame(dc_comparison).to_excel(output / "production_comparison.xlsx", index=False)
    sensitivity = []
    for label, (q, r, e) in {
        "Baseline": (Q, R, E), "Lower quality": (.90, R, E),
        "Lower reliability": (Q, .85, E), "Lower efficiency": (Q, R, .80),
        "All lower": (.90, .85, .80),
    }.items():
        for (facility, strategy), frame in frames.items():
            row = resource_summary(facility, strategy, frame, q=q, r=r, e=e)
            row["network"] = network
            row["scenario"] = label
            baseline = summary[(summary.facility == facility) & (summary.strategy == strategy)].iloc[0]
            row["N_change"] = row["N"] - baseline.N
            row["capacity_cost_change"] = row["capacity_cost"] - baseline.capacity_cost
            sensitivity.append(row)
    pd.DataFrame(sensitivity).to_excel(output / "sensitivity.xlsx", index=False)
    pd.DataFrame(storage).rename_axis("Time").to_excel(output / "storage_inventory_profiles.xlsx")
    # A feasible, fully costed alternative using only rates supplied in Appendix 1.
    # This is an upper bound on optimal cost, not a claimed optimal tier split.
    pd.DataFrame([
        {"profile": label, "base_capacity": float(np.max(inventory)),
         "base_unit_days": float(np.max(inventory)) * HORIZON,
         "base_om_cost": float(np.max(inventory)) * HORIZON * BASE_STORAGE_RATE,
         "base_setup_cost": float(np.max(inventory)) * BASE_STORAGE_SETUP,
         "total_storage_cost": float(np.max(inventory)) *
             (HORIZON * BASE_STORAGE_RATE + BASE_STORAGE_SETUP)}
        for label, inventory in storage.items()
    ]).to_excel(output / "storage_all_base_alternative.xlsx", index=False)
    storage_status = "Storage tier optimum pending seasonal/spot rates and minimum lease duration."
    if all(x is not None for x in storage_inputs):
        storage_summaries = []
        for label, inventory in storage.items():
            daily, contracts, row = optimize_storage(inventory, *storage_inputs)
            daily.to_excel(output / f"storage_{label}_daily.xlsx", index=False)
            contracts.to_excel(output / f"storage_{label}_contracts.xlsx", index=False)
            row["profile"] = label
            storage_summaries.append(row)
        pd.DataFrame(storage_summaries).to_excel(output / "storage_tier_summary.xlsx", index=False)
        storage_status = "Storage tiers optimized for the supplied rates and lease duration."
    report = (f"Network: {network}\nFCs: {', '.join(FC_CONFIGS[network])}\n\n" + __doc__ + "\n\n" + storage_status + "\n\n"
            )
    (output / "assumptions.txt").write_text(report)
    print(f"\n{network} network")
    print(summary[["facility", "strategy", "peak_throughput", "N", "residual_hours", "capacity_cost"]].round(2).to_string(index=False))
    print("\n" + storage_status)
    print(f"Results saved to {output}")
    return replenishment_summary


if __name__ == "__main__":
    main()
