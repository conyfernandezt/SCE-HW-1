import pandas as pd
#import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import math

print("----------------\n")
print('Task 7: 15 Fcs\n')
print("----------------\n")


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

print("----------------\n")
print('Task 7: 4 Fcs\n')
print("----------------\n")

distance_columns_4FC = [
    "GA-303",
    "NY-134",
    "TX-799",
    "UT-841"
]

df_distance["closest_location_4FC"] = (
    df_distance[distance_columns_4FC].idxmin(axis=1)
)

demand_4FC = pd.read_csv("task2_demand_results.csv")

demand_4FC = demand_4FC.merge(
    df_distance[["ZIP3", "closest_location_4FC"]],
    on="ZIP3",
    how="left"
)

fc_daily_4FC = (
    demand_4FC
    .groupby(
        ["Week", "Day", "closest_location_4FC"]
    )
    .agg(
        Mean_Demand=("Mean_Demand", "sum"),
        Sigma=("Sigma", lambda x: np.sqrt((x ** 2).sum()))
    )
    .reset_index()
)

fc_daily_4FC["Time"] = (
    (fc_daily_4FC["Week"] - 1) * 7
    + (fc_daily_4FC["Day"] - 1)
)

fc_daily_4FC = fc_daily_4FC.sort_values(
    ["closest_location_4FC", "Time"]
)

fc_daily_4FC["Demand_21d"] = np.nan
fc_daily_4FC["Sigma_21d"] = np.nan

for fc in fc_daily_4FC["closest_location_4FC"].unique():

    fc_data = fc_daily_4FC[
        fc_daily_4FC["closest_location_4FC"] == fc
    ].copy()

    fc_data = fc_data.sort_values("Time")

    for i in range(len(fc_data) - 20):

        demand_21d = fc_data.iloc[
            i:i+21
        ]["Mean_Demand"].sum()

        sigma_21d = np.sqrt(
            (
                fc_data.iloc[i:i+21]["Sigma"] ** 2
            ).sum()
        )

        fc_daily_4FC.loc[
            fc_data.index[i],
            "Demand_21d"
        ] = demand_21d

        fc_daily_4FC.loc[
            fc_data.index[i],
            "Sigma_21d"
        ] = sigma_21d

fc_daily_4FC["Stock_3w_99"] = (
    fc_daily_4FC["Demand_21d"]
    + z_99 * fc_daily_4FC["Sigma_21d"]
)

max_fc_4FC = (
    fc_daily_4FC
    .groupby("closest_location_4FC")["Stock_3w_99"]
    .max()
    .reset_index()
)

max_fc_4FC.columns = [
    "FC",
    "Maximum_3w_99_Inventory"
]

print("4-FC Maximum inventory by FC:")
print(max_fc_4FC)

daily_fc_total_4FC = (
    fc_daily_4FC
    .groupby("Time")["Stock_3w_99"]
    .sum()
    .reset_index(name="FC_Inventory_4FC")
)

print(
    "4-FC maximum total FC inventory:",
    daily_fc_total_4FC["FC_Inventory_4FC"].max()
)


print("----------------\n")
print('Task 7: 1 Fcs\n')
print("----------------\n")

distance_columns_1FC = [
    "GA-303"
]

df_distance["closest_location_1FC"] = (
    df_distance[distance_columns_1FC].idxmin(axis=1)
)

demand_1FC = pd.read_csv("task2_demand_results.csv")

demand_1FC = demand_1FC.merge(
    df_distance[["ZIP3", "closest_location_1FC"]],
    on="ZIP3",
    how="left"
)

fc_daily_1FC = (
    demand_1FC
    .groupby(
        ["Week", "Day", "closest_location_1FC"]
    )
    .agg(
        Mean_Demand=("Mean_Demand", "sum"),
        Sigma=("Sigma", lambda x: np.sqrt((x ** 2).sum()))
    )
    .reset_index()
)

fc_daily_1FC["Time"] = (
    (fc_daily_1FC["Week"] - 1) * 7
    + (fc_daily_1FC["Day"] - 1)
)

fc_daily_1FC = fc_daily_1FC.sort_values(
    ["closest_location_1FC", "Time"]
)

fc_daily_1FC["Demand_21d"] = np.nan
fc_daily_1FC["Sigma_21d"] = np.nan

for fc in fc_daily_1FC["closest_location_1FC"].unique():

    fc_data = fc_daily_1FC[
        fc_daily_1FC["closest_location_1FC"] == fc
    ].copy()

    fc_data = fc_data.sort_values("Time")

    for i in range(len(fc_data) - 20):

        demand_21d = fc_data.iloc[
            i:i+21
        ]["Mean_Demand"].sum()

        sigma_21d = np.sqrt(
            (
                fc_data.iloc[i:i+21]["Sigma"] ** 2
            ).sum()
        )

        fc_daily_1FC.loc[
            fc_data.index[i],
            "Demand_21d"
        ] = demand_21d

        fc_daily_1FC.loc[
            fc_data.index[i],
            "Sigma_21d"
        ] = sigma_21d

fc_daily_1FC["Stock_3w_99"] = (
    fc_daily_1FC["Demand_21d"]
    + z_99 * fc_daily_1FC["Sigma_21d"]
)

max_fc_1FC = (
    fc_daily_1FC
    .groupby("closest_location_1FC")["Stock_3w_99"]
    .max()
    .reset_index()
)

max_fc_1FC.columns = [
    "FC",
    "Maximum_3w_99_Inventory"
]

print("\n1-FC Maximum inventory:")
print(max_fc_1FC)

daily_fc_total_1FC = (
    fc_daily_1FC
    .groupby("Time")["Stock_3w_99"]
    .sum()
    .reset_index(name="FC_Inventory_1FC")
)

print(
    "1-FC maximum total FC inventory:",
    daily_fc_total_1FC["FC_Inventory_1FC"].max()
)

# 6 weeks 99%


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

network_daily = network_daily.merge(
    daily_fc_total_4FC,
    on="Time",
    how="left"
)

network_daily = network_daily.merge(
    daily_fc_total_1FC,
    on="Time",
    how="left"
)



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
).clip(lower=0)

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

        stock_col = (
            f"Network_Stock_"
            f"{autonomy}w_"
            f"{int(robustness*100)}"
        )

        # Overall network inventory target
        network_daily[stock_col] = (
            network_daily[demand_col]
            + z * network_daily[sigma_col]
        )

        # -----
        # 15-FC
        # -----

        dc_col_15FC = (
            f"DC_Inventory_15FC_"
            f"{autonomy}w_"
            f"{int(robustness*100)}"
        )

        network_daily[dc_col_15FC] = (
            network_daily[stock_col]
            - network_daily["FC_Inventory"]
        ).clip(lower=0)

        max_dc_15FC = network_daily[
            dc_col_15FC
        ].max()

        max_fc_15FC = network_daily[
            "FC_Inventory"
        ].max()

        max_network_15FC = (
            network_daily["FC_Inventory"]
            + network_daily[dc_col_15FC]
        ).max()

        scenario_results.append({
            "Network": "15-FC",
            "Autonomy": autonomy,
            "Robustness": robustness,
            "Maximum_FC_Inventory": max_fc_15FC,
            "Maximum_DC_Inventory": max_dc_15FC,
            "Maximum_Network_Inventory": max_network_15FC
        })


        # ----
        # 4-FC
        # ----

        dc_col_4FC = (
            f"DC_Inventory_4FC_"
            f"{autonomy}w_"
            f"{int(robustness*100)}"
        )

        network_daily[dc_col_4FC] = (
            network_daily[stock_col]
            - network_daily["FC_Inventory_4FC"]
        ).clip(lower=0)

        max_dc_4FC = network_daily[
            dc_col_4FC
        ].max()

        max_fc_4FC = network_daily[
            "FC_Inventory_4FC"
        ].max()

        max_network_4FC = (
            network_daily["FC_Inventory_4FC"]
            + network_daily[dc_col_4FC]
        ).max()

        scenario_results.append({
            "Network": "4-FC",
            "Autonomy": autonomy,
            "Robustness": robustness,
            "Maximum_FC_Inventory": max_fc_4FC,
            "Maximum_DC_Inventory": max_dc_4FC,
            "Maximum_Network_Inventory": max_network_4FC
        })


        # ----
        # 1-FC
        # ----

        dc_col_1FC = (
            f"DC_Inventory_1FC_"
            f"{autonomy}w_"
            f"{int(robustness*100)}"
        )

        network_daily[dc_col_1FC] = (
            network_daily[stock_col]
            - network_daily["FC_Inventory_1FC"]
        ).clip(lower=0)

        max_dc_1FC = network_daily[
            dc_col_1FC
        ].max()

        max_fc_1FC = network_daily[
            "FC_Inventory_1FC"
        ].max()

        max_network_1FC = (
            network_daily["FC_Inventory_1FC"]
            + network_daily[dc_col_1FC]
        ).max()

        scenario_results.append({
            "Network": "1-FC",
            "Autonomy": autonomy,
            "Robustness": robustness,
            "Maximum_FC_Inventory": max_fc_1FC,
            "Maximum_DC_Inventory": max_dc_1FC,
            "Maximum_Network_Inventory": max_network_1FC
        })


scenario_results = pd.DataFrame(scenario_results)

print(scenario_results)

print("\n----")
print("\nTask 7: 6 weeks 99%")
print("\n----")

print(
    network_daily[
        [
            "Time",
            "Network_Stock_6w_99",

            "FC_Inventory_1FC",
            "DC_Inventory_1FC_6w_99",

            "FC_Inventory_4FC",
            "DC_Inventory_4FC_6w_99",

            "FC_Inventory",
            "DC_Inventory_15FC_6w_99"
        ]
    ].head(20)
)

for network in ["1-FC", "4-FC", "15-FC"]:

    temp = scenario_results[
        scenario_results["Network"] == network
    ]

    print("\n----")
    print(network)
    print("----")

    fc_table = temp.pivot(
        index="Autonomy",
        columns="Robustness",
        values="Maximum_FC_Inventory"
    )

    print("\nMaximum FC Inventory")
    print(fc_table)

    dc_table = temp.pivot(
        index="Autonomy",
        columns="Robustness",
        values="Maximum_DC_Inventory"
    )

    print("\nMaximum DC Inventory")
    print(dc_table)

    network_table = temp.pivot(
        index="Autonomy",
        columns="Robustness",
        values="Maximum_Network_Inventory"
    )

    print("\nMaximum Network Inventory")
    print(network_table)
   # ============================================================
# FIGURE 1: Maximum 3-Week, 99% Inventory by FC
# ============================================================

figure1_data = pd.DataFrame({
    "FC": [
        "AZ-852", "CA-900", "CA-945", "CO-802", "FL-331",
        "GA-303", "IL-606", "MA-021", "MI-481", "NC-275",
        "NJ-070", "TX-750", "TX-770", "UT-841", "WA-980"
    ],
    "Maximum Inventory": [
        698.178004, 1527.882928, 713.122168, 963.844996,
        1003.594678, 1381.037540, 1905.176574, 811.066374,
        1379.636229, 956.865530, 2907.501465, 849.953381,
        775.921198, 325.544732, 557.012698
    ]
})

plt.figure(figsize=(12, 6))

plt.bar(
    figure1_data["FC"],
    figure1_data["Maximum Inventory"]
)

plt.title("Maximum 3-Week, 99% Inventory Requirement by FC")
plt.xlabel("Fulfillment Center")
plt.ylabel("Maximum Inventory (Units)")

plt.xticks(rotation=45, ha="right")
plt.tight_layout()

plt.savefig("Task7_Figure1_Max_FC_Inventory.png", dpi=300)

plt.show()
# ============================================================
# FIGURE 2: Daily Inventory - 6-Week, 99% Network Policy
# 15-FC Network
# ============================================================

plt.figure(figsize=(12, 6))

plt.plot(
    network_daily["Time"],
    network_daily["FC_Inventory"],
    label="FC Inventory"
)

plt.plot(
    network_daily["Time"],
    network_daily["DC_Inventory_15FC_6w_99"],
    label="DC Inventory"
)

plt.plot(
    network_daily["Time"],
    network_daily["Network_Stock_6w_99"],
    label="Total Network Inventory"
)

plt.title("Daily Inventory under 6-Week, 99% Network Autonomy Policy")
plt.xlabel("Day")
plt.ylabel("Inventory (Units)")
plt.legend()

plt.tight_layout()
plt.savefig("Task7_Figure2_Daily_Inventory.png", dpi=300, bbox_inches="tight")
plt.show()
# ============================================================
# FIGURE 3: Sensitivity of Maximum Network Inventory
# 15-FC Network
# ============================================================

figure3_data = scenario_results[
    scenario_results["Network"] == "15-FC"
].copy()

plt.figure(figsize=(10, 6))

for robustness in [0.50, 0.68, 0.95, 0.99]:

    temp = figure3_data[
        figure3_data["Robustness"] == robustness
    ].sort_values("Autonomy")

    plt.plot(
        temp["Autonomy"],
        temp["Maximum_Network_Inventory"],
        marker="o",
        label=f"{int(robustness * 100)}% Robustness"
    )

plt.title("Maximum Network Inventory by Autonomy and Robustness")
plt.xlabel("Network Autonomy (Weeks)")
plt.ylabel("Maximum Network Inventory (Units)")

plt.xticks([4, 6, 8])
plt.legend()
plt.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(
    "Task7_Figure3_Inventory_Sensitivity.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
# ============================================================
# TASK 7: REPORT TABLES - 15-FC NETWORK
# ============================================================

table_data = scenario_results[
    scenario_results["Network"] == "15-FC"
].copy()

# ----- Maximum FC Inventory -----

fc_report_table = table_data.pivot(
    index="Autonomy",
    columns="Robustness",
    values="Maximum_FC_Inventory"
).round(0).astype(int)

fc_report_table.columns = ["50%", "68%", "95%", "99%"]
fc_report_table.index = [
    f"{int(x)} weeks" for x in fc_report_table.index
]

print("\nTABLE 1: Maximum FC Inventory")
print(fc_report_table)


# ----- Maximum DC Inventory -----

dc_report_table = table_data.pivot(
    index="Autonomy",
    columns="Robustness",
    values="Maximum_DC_Inventory"
).round(0).astype(int)

dc_report_table.columns = ["50%", "68%", "95%", "99%"]
dc_report_table.index = [
    f"{int(x)} weeks" for x in dc_report_table.index
]

print("\nTABLE 2: Maximum DC Inventory")
print(dc_report_table)


# ----- Maximum Total Network Inventory -----

network_report_table = table_data.pivot(
    index="Autonomy",
    columns="Robustness",
    values="Maximum_Network_Inventory"
).round(0).astype(int)

network_report_table.columns = ["50%", "68%", "95%", "99%"]
network_report_table.index = [
    f"{int(x)} weeks" for x in network_report_table.index
]

print("\nTABLE 3: Maximum Total Network Inventory")
print(network_report_table)
