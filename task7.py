import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

# we'll take the demand from task 2

demand = pd.read_csv("task2_demand_results.csv")


df = pd.read_csv("Assignment/zip3_coordinates.csv")

df_distance = pd.read_csv("Assignment/fc_zip3_distance.csv")


# All fulfillment centers
distance_columns = [
    "GA-303",
    "UT-841",
    "AZ-852",
    "CA-900",
    "CA-945",
    "CO-802",
    "FL-331",
    "IL-606",
    "MA-021",
    "MI-481",
    "NC-275",
    "NJ-070",
    "TX-750",
    "TX-770",
    "WA-980"
]


df_distance["closest_location"] = (
    df_distance[distance_columns].idxmin(axis=1)
)


demand = demand.merge(
    df_distance[["ZIP3", "closest_location"]],
    on="ZIP3",
    how="left"
)

fc_daily = (
    demand.groupby(["Week", "Day", "closest_location"])
    .agg(
        Mean_Demand=("Mean_Demand", "sum"),
        Sigma=("Sigma", lambda x: np.sqrt((x ** 2).sum()))
    )
    .reset_index()
)

fc_daily["Time"] = (
    (fc_daily["Week"] - 1) * 7
    + (fc_daily["Day"] - 1)
)

fc_daily = fc_daily.sort_values(
    ["closest_location", "Time"]
)


fc_daily["Demand_21d"] = np.nan
fc_daily["Sigma_21d"] = np.nan


for fc in fc_daily["closest_location"].unique():

    fc_data = fc_daily[
        fc_daily["closest_location"] == fc
    ].copy()

    fc_data = fc_data.sort_values("Time")

    for i in range(len(fc_data) - 20):

        demand_21d = fc_data.iloc[
            i:i+21
        ]["Mean_Demand"].sum()

        sigma_values = fc_data.iloc[
            i:i+21
        ]["Sigma"]

        sigma_21d = np.sqrt(
            (sigma_values ** 2).sum()
        )

        # Store results
        fc_daily.loc[
            fc_data.index[i],
            "Demand_21d"
        ] = demand_21d

        fc_daily.loc[
            fc_data.index[i],
            "Sigma_21d"
        ] = sigma_21d

z_99 = 2.326

fc_daily["Stock_3w_99"] = (
    fc_daily["Demand_21d"]
    + z_99 * fc_daily["Sigma_21d"]
)

max_fc = (
    fc_daily
    .groupby("closest_location")["Stock_3w_99"]
    .max()
    .reset_index()
)

max_fc.columns = [
    "FC",
    "Maximum_3w_99_Inventory"
]

print(max_fc)

daily_fc_total = (
    fc_daily
    .groupby("Time")["Stock_3w_99"]
    .sum()
    .reset_index(name="FC_Inventory")
)

max_fc_network = daily_fc_total["FC_Inventory"].max()

print(
    "Maximum inventory across all FCs:",
    max_fc_network
)

network_daily = (
    demand
    .groupby(["Week", "Day"])
    .agg(
        Mean_Demand=("Mean_Demand", "sum"),
        Sigma=("Sigma", lambda x: np.sqrt((x ** 2).sum()))
    )
    .reset_index()
)

network_daily["Time"] = (
    (network_daily["Week"] - 1) * 7
    + (network_daily["Day"] - 1)
)

network_daily = network_daily.sort_values("Time")

network_daily["Demand_42d"] = np.nan
network_daily["Sigma_42d"] = np.nan

for i in range(len(network_daily) - 41):

    demand_42d = network_daily.iloc[
        i:i+42
    ]["Mean_Demand"].sum()

    sigma_values = network_daily.iloc[
        i:i+42
    ]["Sigma"]

    sigma_42d = np.sqrt(
        (sigma_values ** 2).sum()
    )

    network_daily.loc[
        network_daily.index[i],
        "Demand_42d"
    ] = demand_42d

    network_daily.loc[
        network_daily.index[i],
        "Sigma_42d"
    ] = sigma_42d


network_daily["Network_Stock_6w_99"] = (
    network_daily["Demand_42d"]
    + z_99 * network_daily["Sigma_42d"]
)

network_daily = network_daily.merge(
    daily_fc_total,
    on="Time",
    how="left"
)

network_daily["DC_Inventory"] = (
    network_daily["Network_Stock_6w_99"]
    - network_daily["FC_Inventory"]
)

print(
    "Maximum FC inventory:",
    network_daily["FC_Inventory"].max()
)

print(
    "Maximum DC inventory:",
    network_daily["DC_Inventory"].max()
)

print(
    "Maximum network inventory:",
    network_daily["Network_Stock_6w_99"].max()
)

robustness_levels = {
    0.50: 0.000,
    0.68: 0.468,
    0.95: 1.645,
    0.99: 2.326
}

autonomy_weeks = [4, 6, 8]

# Calculate all alternative network scenarios

scenario_results = []

for autonomy in autonomy_weeks:

    horizon_days = autonomy * 7

    demand_col = f"Demand_{autonomy}w"
    sigma_col = f"Sigma_{autonomy}w"

    network_daily[demand_col] = np.nan
    network_daily[sigma_col] = np.nan

    for i in range(len(network_daily) - horizon_days + 1):

        demand_horizon = network_daily.iloc[
            i:i+horizon_days
        ]["Mean_Demand"].sum()

        sigma_values = network_daily.iloc[
            i:i+horizon_days
        ]["Sigma"]

        sigma_horizon = np.sqrt(
            (sigma_values ** 2).sum()
        )

        network_daily.loc[
            network_daily.index[i],
            demand_col
        ] = demand_horizon

        network_daily.loc[
            network_daily.index[i],
            sigma_col
        ] = sigma_horizon


    for robustness, z in robustness_levels.items():

        stock_col = f"Network_Stock_{autonomy}w_{int(robustness*100)}"

        network_daily[stock_col] = (
            network_daily[demand_col]
            + z * network_daily[sigma_col]
        )

        dc_col = f"DC_Inventory_{autonomy}w_{int(robustness*100)}"

        network_daily[dc_col] = (
            network_daily[stock_col]
            - network_daily["FC_Inventory"]
        )

        max_network = network_daily[stock_col].max()

        max_dc = network_daily[dc_col].max()

        max_fc = network_daily["FC_Inventory"].max()

        scenario_results.append({
            "Autonomy": autonomy,
            "Robustness": robustness,
            "Maximum_FC_Inventory": max_fc,
            "Maximum_DC_Inventory": max_dc,
            "Maximum_Network_Inventory": max_network
        })

scenario_results = pd.DataFrame(scenario_results)

print(scenario_results)

fc_table = scenario_results.pivot(
    index="Autonomy",
    columns="Robustness",
    values="Maximum_FC_Inventory"
)

print("Maximum FC Inventory")
print(fc_table)

dc_table = scenario_results.pivot(
    index="Autonomy",
    columns="Robustness",
    values="Maximum_DC_Inventory"
)

print("Maximum DC Inventory")
print(dc_table)

network_table = scenario_results.pivot(
    index="Autonomy",
    columns="Robustness",
    values="Maximum_Network_Inventory"
)

print("Maximum Network Inventory")
print(network_table)