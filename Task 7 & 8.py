import pandas as pd
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
#task 8

print("----------------\n")
print('Task 8: \n')
print("----------------\n")

# dc_t+1 = dc_t + production_t - demand_t
# production_t = demand_t - dc_t+1 - dc_t

# i'll use the constucted network_daily

dc_15FC = network_daily["DC_Inventory_15FC_6w_99"].copy()
dc_4FC = network_daily["DC_Inventory_4FC_6w_99"].copy()
dc_1FC = network_daily["DC_Inventory_1FC_6w_99"].copy()

grouped_demand = demand.groupby(["Week", "Day"])["Mean_Demand"].sum().reset_index()

grouped_demand["Time"] = (grouped_demand["Week"] - 1) * 7 + (grouped_demand["Day"] - 1)

#print(grouped_demand.head(10))

network_task8 = network_daily.copy()

network_task8 = network_task8.merge(
    grouped_demand,
    on=["Time", "Week", "Day"],
    how="left"
)

network_task8["DC_Inventory"] = dc_15FC

network_task8 = network_task8.drop(
    columns=['Demand_42d','Sigma_42d','Demand_4w','Sigma_4w','Network_Stock_4w_50','Network_Stock_4w_68',
        'Network_Stock_4w_95','Network_Stock_4w_99','Demand_6w','Sigma_6w','Network_Stock_6w_50',
        'Network_Stock_6w_68','Network_Stock_6w_95','Network_Stock_6w_99','Demand_8w',
        'Sigma_8w','Network_Stock_8w_50','Network_Stock_8w_68','Network_Stock_8w_95',
        'Network_Stock_8w_99','Mean_Demand_y'
    ],
    errors='ignore'
)

# print(network_task8.columns.tolist())


network_task8 = network_task8.sort_values("Time")

network_task8['DC_delta'] = network_task8['DC_Inventory'] - network_task8['DC_Inventory'].shift(1)

inventory_t0 = network_task8.loc[network_task8["Time"] == network_task8["Time"].min(), "DC_Inventory"].iloc[0]

network_task8.loc[
    network_task8["Time"] == network_task8["Time"].min(),
    "DC_delta"
] = (
    network_task8.loc[
        network_task8["Time"] == network_task8["Time"].min(),
        "DC_Inventory"
    ].iloc[0]
    - inventory_t0
)

network_task8['Production'] = network_task8['Mean_Demand_x'] + network_task8['DC_delta']

network_task8['DC_calculated_inventory'] = np.nan

dc_day1 = (inventory_t0 + network_task8.loc[
        network_task8["Time"] == network_task8["Time"].min(), "Production"].iloc[0] - network_task8.loc[
        network_task8["Time"] == network_task8["Time"].min(), "Mean_Demand_x"].iloc[0])

network_task8.loc[network_task8['Time'] == network_task8['Time'].min(), 'DC_calculated_inventory'] = dc_day1

for i in range (1, len(network_task8)):

    current_index = network_task8.index[i]
    previous_index = network_task8.index[i-1]

    inventory = (
        network_task8.loc[previous_index, "DC_calculated_inventory"]
    + network_task8.loc[current_index, "Production"]
    - network_task8.loc[current_index, "Mean_Demand_x"])

    network_task8.loc[current_index, 'DC_calculated_inventory'] = inventory
print("\n--- Pursuit Production Strategy: 15 FCs ---")
print("Maximum daily AF production:", network_task8["Production"].max())
print("Average daily AF production:", network_task8["Production"].mean())

# smoothing where we will assume that the initial inventory at the DC is the inventory target

avg_demand = network_task8['Mean_Demand_x'].mean()

network_task8['smooth_production'] = avg_demand

network_task8['smooth_inv'] = np.nan

sm_inv = (inventory_t0 + network_task8.loc[network_task8["Time"] == network_task8["Time"].min(), "smooth_production"].iloc[0]
    - network_task8.loc[network_task8["Time"] == network_task8["Time"].min(), "Mean_Demand_x"].iloc[0])

network_task8.loc[network_task8["Time"] == network_task8["Time"].min(), 'smooth_inv'] = sm_inv

for i in range(1, len(network_task8)):

    current_index = network_task8.index[i]
    previous_index = network_task8.index[i-1]

    sm_inv = (network_task8.loc[previous_index, "smooth_inv"]
    + network_task8.loc[current_index, "smooth_production"]
    - network_task8.loc[current_index, "Mean_Demand_x"]
)

    network_task8.loc[current_index, 'smooth_inv'] = sm_inv

backlog = network_task8['smooth_inv'].min()

print("----")
print("15 FCs considering inventory in t0 to be enough for demand of the first period ")
print("Smoothing without pre-production")
print("----")

print(
    "Minimum inventory:",
    network_task8["smooth_inv"].min()
)

if backlog < 0:
    print(f"There's backlog of {backlog}")
else:
    print("There's no backlog")

print("Initial inventory:", inventory_t0)
print("Average production:", avg_demand)
print("Minimum inventory:", network_task8["smooth_inv"].min())
print("Maximum inventory:", network_task8["smooth_inv"].max())


print(
    network_task8[
        [
            "Time",
            "Mean_Demand_x",
            "smooth_production",
            "smooth_inv"
        ]
    ].head(20)
)
# Constant production
avg_demand = network_task8["Mean_Demand_x"].mean()

network_task8["smooth_production"] = avg_demand

# Initialize inventory
network_task8["smooth_inv"] = np.nan

# Initial inventory
inventory = inventory_t0

# Calculate inventory day by day
for i in range(len(network_task8)):

    current_index = network_task8.index[i]

    inventory = (
        inventory
        + network_task8.loc[current_index, "smooth_production"]
        - network_task8.loc[current_index, "Mean_Demand_x"]
    )

    network_task8.loc[
        current_index,
        "smooth_inv"
    ] = inventory

# there is no backlog, too much inventory

# now we will try with smoothing no initial invetory

print("----")
print("15 FCs considering no initial inventory")
print("Smoothing without pre-production")
print("----")

avg_demand = network_task8['Mean_Demand_x'].mean()

network_task8['smooth_production'] = avg_demand

network_task8['smooth_inv'] = np.nan

network_task8.loc[network_task8["Time"] == network_task8["Time"].min(), 'smooth_inv'] = 0

for i in range(1, len(network_task8)):

    current_index = network_task8.index[i]
    previous_index = network_task8.index[i-1]

    sm_inv = (network_task8.loc[previous_index, "smooth_inv"]
    + network_task8.loc[current_index, "smooth_production"]
    - network_task8.loc[current_index, "Mean_Demand_x"]
)

    network_task8.loc[current_index, 'smooth_inv'] = sm_inv

backlog = network_task8['smooth_inv'].min()

print(
    "Minimum inventory:",
    network_task8["smooth_inv"].min()
)

if backlog < 0:
    print(f"There's backlog of {backlog}")
else:
    print("There's no backlog")

print("Initial inventory:", inventory_t0)
print("Average production:", avg_demand)
print("Minimum inventory:", network_task8["smooth_inv"].min())
print("Maximum inventory:", network_task8["smooth_inv"].max())


print(
    network_task8[
        [
            "Time",
            "Mean_Demand_x",
            "smooth_production",
            "smooth_inv"
        ]
    ].head(20)
)
# Constant production
avg_demand = network_task8["Mean_Demand_x"].mean()

network_task8["smooth_production"] = avg_demand

# Initialize inventory
network_task8["smooth_inv"] = np.nan

# Initial inventory
inventory = inventory_t0

# Calculate inventory day by day
for i in range(len(network_task8)):

    current_index = network_task8.index[i]

    inventory = (
        inventory
        + network_task8.loc[current_index, "smooth_production"]
        - network_task8.loc[current_index, "Mean_Demand_x"]
    )

    network_task8.loc[
        current_index,
        "smooth_inv"
    ] = inventory


# there's backlog

# smoothing with pre-production

print("----")
print("15 FCs considering no initial inventory")
print("Smoothing with pre-production")
print("----")


required_inventory = 0

required_inventory_values = []

for i in range(len(network_task8)-1, -1, -1):

    current_index = network_task8.index[i]

    required_inventory = (
        required_inventory
        + network_task8.loc[current_index, "Mean_Demand_x"]
        - avg_demand
    )

    required_inventory = max(required_inventory, 0)

    required_inventory_values.append(required_inventory)

required_inventory_values = required_inventory_values[::-1]

network_task8["Required_Starting_Inventory"] = required_inventory_values

required_preproduction_inventory = (
    network_task8["Required_Starting_Inventory"].iloc[0]
)

print(
    "Required inventory at start of horizon:",
    required_preproduction_inventory
)

preproduction_days = (
    required_preproduction_inventory / avg_demand
)

print("Pre-production days:", preproduction_days)

preproduction_days = math.ceil(preproduction_days)

network_task8['preprod_smooth_inv'] = np.nan

inv = required_preproduction_inventory

for i in range(len(network_task8)):

    current_index = network_task8.index[i]

    inv = inv + avg_demand - network_task8.loc[current_index, 'Mean_Demand_x']

    network_task8.loc[current_index, 'preprod_smooth_inv'] = inv

print(
    "Minimum inventory:",
    network_task8["preprod_smooth_inv"].min()
)

print(
    "Maximum inventory:",
    network_task8["preprod_smooth_inv"].max()
)

# network_task8["excess_over_target"] = (
#     network_task8["preprod_smooth_inv"]
#     - network_task8["DC_Inventory"]
# )

# print(
#     "Maximum excess inventory:",
#     network_task8["excess_over_target"].max()
# )


# segment smoothing per period - group by week

week_demand = network_task8.groupby("Week")['Mean_Demand_x'].mean().reset_index()


# plt.figure(figsize=(12, 5))

# plt.plot(
#     week_demand["Week"],
#     week_demand["Mean_Demand_x"]
# )

# plt.xlabel("Week")
# plt.ylabel("Average Daily Demand")
# plt.title("Weekly Seasonality Profile")

# plt.show()

# we will divide the period into 5 segments gotten from the view of the graph

network_task8["segment"] = np.nan

network_task8.loc[
    network_task8["Week"].between(1, 21),
    "segment"
] = 1

network_task8.loc[
    network_task8["Week"].between(22, 27),
    "segment"
] = 2

network_task8.loc[
    network_task8["Week"].between(28, 44),
    "segment"
] = 3

network_task8.loc[
    network_task8["Week"].between(45, 48),
    "segment"
] = 4

network_task8.loc[
    network_task8["Week"].between(49, 52),
    "segment"
] = 5

prod_seg = (
    network_task8
    .groupby("segment")["Mean_Demand_x"]
    .mean()
)

print("----")
print("15 FCs considering no initial inventory")
print("Segmented smoothing")
print("----")

#if initial inventory is 0

inv_segmented = 0

network_task8['prod_seg'] = network_task8['segment'].map(prod_seg)

network_task8['inv_seg'] = np.nan

for i in range(len(network_task8)):

    current_index = network_task8.index[i]

    inv_segmented = (
        inv_segmented
        + network_task8.loc[
            current_index,
            'prod_seg'
        ]
        - network_task8.loc[
            current_index,
            "Mean_Demand_x"
        ]
    )

    network_task8.loc[
        current_index,
        'inv_seg'
    ] = inv_segmented

print(
    network_task8[
        [
            "Time",
            "Week",
            "Mean_Demand_x",
            "segment",
            "prod_seg",
            "inv_seg"
        ]
    ].head(20)
)

print(
    "Maximum AF production:",
    network_task8["prod_seg"].max()
)

print(
    "Minimum DC inventory:",
    network_task8["inv_seg"].min()
)

print(
    "Maximum DC inventory:",
    network_task8["inv_seg"].max()
)


if network_task8["inv_seg"].min() < 0:
    print("There is backlog.")
else:
    print("There is no backlog.")

# if initial invetory is different from cero

print("----")
print("15 FCs considering initial inventory")
print("Segmented smoothing")
print("----")

inventory_t0 = network_task8.loc[network_task8["Time"] == network_task8["Time"].min(), "DC_Inventory"].iloc[0]

inv_segmented = inventory_t0

network_task8['prod_seg'] = network_task8['segment'].map(prod_seg)

network_task8['inv_seg'] = np.nan

for i in range(len(network_task8)):

    current_index = network_task8.index[i]

    inv_segmented = (
        inv_segmented
        + network_task8.loc[
            current_index,
            'prod_seg'
        ]
        - network_task8.loc[
            current_index,
            "Mean_Demand_x"
        ]
    )

    network_task8.loc[
        current_index,
        'inv_seg'
    ] = inv_segmented

print(
    network_task8[
        [
            "Time",
            "Week",
            "Mean_Demand_x",
            "segment",
            "prod_seg",
            "inv_seg"
        ]
    ].head(20)
)

print(
    "Maximum AF production:",
    network_task8["prod_seg"].max()
)

print(
    "Minimum DC inventory:",
    network_task8["inv_seg"].min()
)

print(
    "Maximum DC inventory:",
    network_task8["inv_seg"].max()
)

backlog_days = network_task8[
    network_task8["inv_seg"] < 0
]

print(
    backlog_days[
        [
            "Time",
            "Week",
            "Mean_Demand_x",
            "segment",
            "prod_seg",
            "inv_seg"
        ]
    ]
)


if network_task8["inv_seg"].min() < 0:
    print("There is backlog.")
else:
    print("There is no backlog.")

# FIGURE 1 - Production Strategy Comparison

plt.figure(figsize=(12, 6))

plt.plot(
    network_task8["Time"],
    network_task8["Production"],
    label="Pursuit Production"
)

plt.plot(
    network_task8["Time"],
    network_task8["smooth_production"],
    label="Full Smoothing"
)

plt.plot(
    network_task8["Time"],
    network_task8["prod_seg"],
    label="Segmented Smoothing"
)

plt.xlabel("Day of Planning Horizon")
plt.ylabel("AF Production (units/day)")
plt.title("AF Production Requirements under Alternative Production Strategies")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig("Task8_Figure1_Production_Strategies.png", dpi=300)
plt.show()

# ============================================================
# FIGURE 2 - DC Inventory Comparison
# 15-FC Network
# ============================================================

plt.figure(figsize=(12, 6))

# Pursuit strategy
plt.plot(
    network_task8["Time"],
    network_task8["DC_Inventory"],
    label="Pursuit"
)

# Full smoothing with pre-production
plt.plot(
    network_task8["Time"],
    network_task8["preprod_smooth_inv"],
    label="Full Smoothing with Pre-production"
)

# Segmented smoothing
plt.plot(
    network_task8["Time"],
    network_task8["inv_seg"],
    label="Segmented Smoothing"
)

plt.xlabel("Day of Planning Horizon")
plt.ylabel("DC Inventory (units)")
plt.title("DC Inventory under Alternative Production Strategies")

plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(
    "Task8_Figure2_DC_Inventory_Strategies.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("\n----")
print("\nTask 8 for 4 FCs")
print("\n----")
print("\nTask 8 for 4 FCs")
print("\n----")

grouped_demand = demand.groupby(["Week", "Day"])["Mean_Demand"].sum().reset_index()

grouped_demand["Time"] = (grouped_demand["Week"] - 1) * 7 + (grouped_demand["Day"] - 1)

#print(grouped_demand.head(10))

network_task8 = network_daily.copy()

network_task8 = network_task8.merge(
    grouped_demand,
    on=["Time", "Week", "Day"],
    how="left"
)

network_task8["DC_Inventory"] = dc_4FC

network_task8 = network_task8.drop(
    columns=['Demand_42d','Sigma_42d','Demand_4w','Sigma_4w','Network_Stock_4w_50','Network_Stock_4w_68',
        'Network_Stock_4w_95','Network_Stock_4w_99','Demand_6w','Sigma_6w','Network_Stock_6w_50',
        'Network_Stock_6w_68','Network_Stock_6w_95','Network_Stock_6w_99','Demand_8w',
        'Sigma_8w','Network_Stock_8w_50','Network_Stock_8w_68','Network_Stock_8w_95',
        'Network_Stock_8w_99','Mean_Demand_y'
    ],
    errors='ignore'
)

print(network_task8.columns.tolist())

network_task8 = network_task8.sort_values("Time")

network_task8['DC_delta'] = network_task8['DC_Inventory'] - network_task8['DC_Inventory'].shift(1)

inventory_t0 = network_task8.loc[network_task8["Time"] == network_task8["Time"].min(), "DC_Inventory"].iloc[0]

network_task8.loc[
    network_task8["Time"] == network_task8["Time"].min(),
    "DC_delta"
] = (
    network_task8.loc[
        network_task8["Time"] == network_task8["Time"].min(),
        "DC_Inventory"
    ].iloc[0]
    - inventory_t0
)

network_task8['Production'] = network_task8['Mean_Demand_x'] + network_task8['DC_delta']

network_task8['DC_calculated_inventory'] = np.nan

dc_day1 = (inventory_t0 + network_task8.loc[
        network_task8["Time"] == network_task8["Time"].min(), "Production"].iloc[0] - network_task8.loc[
        network_task8["Time"] == network_task8["Time"].min(), "Mean_Demand_x"].iloc[0])

network_task8.loc[network_task8['Time'] == network_task8['Time'].min(), 'DC_calculated_inventory'] = dc_day1

for i in range (1, len(network_task8)):

    current_index = network_task8.index[i]
    previous_index = network_task8.index[i-1]

    inventory = (
        network_task8.loc[previous_index, "DC_calculated_inventory"]
    + network_task8.loc[current_index, "Production"]
    - network_task8.loc[current_index, "Mean_Demand_x"])

    network_task8.loc[current_index, 'DC_calculated_inventory'] = inventory


# smoothing where we will assume that the initial inventory at the DC is the inventory target

avg_demand = network_task8['Mean_Demand_x'].mean()

network_task8['smooth_production'] = avg_demand

network_task8['smooth_inv'] = np.nan

sm_inv = (inventory_t0 + network_task8.loc[network_task8["Time"] == network_task8["Time"].min(), "smooth_production"].iloc[0]
    - network_task8.loc[network_task8["Time"] == network_task8["Time"].min(), "Mean_Demand_x"].iloc[0])

network_task8.loc[network_task8["Time"] == network_task8["Time"].min(), 'smooth_inv'] = sm_inv

for i in range(1, len(network_task8)):

    current_index = network_task8.index[i]
    previous_index = network_task8.index[i-1]

    sm_inv = (network_task8.loc[previous_index, "smooth_inv"]
    + network_task8.loc[current_index, "smooth_production"]
    - network_task8.loc[current_index, "Mean_Demand_x"]
)

    network_task8.loc[current_index, 'smooth_inv'] = sm_inv

backlog = network_task8['smooth_inv'].min()

print("----")
print("4 FCs considering inventory in t0 to be enough for demand of the first period")
print("Smoothing without pre-production")
print("----")

print(
    "Minimum inventory:",
    network_task8["smooth_inv"].min()
)

if backlog < 0:
    print(f"There's backlog of {backlog}")
else:
    print("There's no backlog")

print("Initial inventory:", inventory_t0)
print("Average production:", avg_demand)
print("Minimum inventory:", network_task8["smooth_inv"].min())
print("Maximum inventory:", network_task8["smooth_inv"].max())


print(
    network_task8[
        [
            "Time",
            "Mean_Demand_x",
            "smooth_production",
            "smooth_inv"
        ]
    ].head(20)
)
# Constant production
avg_demand = network_task8["Mean_Demand_x"].mean()

network_task8["smooth_production"] = avg_demand

# Initialize inventory
network_task8["smooth_inv"] = np.nan

# Initial inventory
inventory = inventory_t0

# Calculate inventory day by day
for i in range(len(network_task8)):

    current_index = network_task8.index[i]

    inventory = (
        inventory
        + network_task8.loc[current_index, "smooth_production"]
        - network_task8.loc[current_index, "Mean_Demand_x"]
    )

    network_task8.loc[
        current_index,
        "smooth_inv"
    ] = inventory

    

# there is no backlog, too much inventory

# now we will try with smoothing no initial invetory

print("----")
print("4 FCs considering no initial inventory")
print("Smoothing without pre-production")
print("----")

avg_demand = network_task8['Mean_Demand_x'].mean()

network_task8['smooth_production'] = avg_demand

network_task8['smooth_inv'] = np.nan

network_task8.loc[network_task8["Time"] == network_task8["Time"].min(), 'smooth_inv'] = 0

for i in range(1, len(network_task8)):

    current_index = network_task8.index[i]
    previous_index = network_task8.index[i-1]

    sm_inv = (network_task8.loc[previous_index, "smooth_inv"]
    + network_task8.loc[current_index, "smooth_production"]
    - network_task8.loc[current_index, "Mean_Demand_x"]
)

    network_task8.loc[current_index, 'smooth_inv'] = sm_inv

backlog = network_task8['smooth_inv'].min()

print(
    "Minimum inventory:",
    network_task8["smooth_inv"].min()
)

if backlog < 0:
    print(f"There's backlog of {backlog}")
else:
    print("There's no backlog")

print("Initial inventory:", inventory_t0)
print("Average production:", avg_demand)
print("Minimum inventory:", network_task8["smooth_inv"].min())
print("Maximum inventory:", network_task8["smooth_inv"].max())


print(
    network_task8[
        [
            "Time",
            "Mean_Demand_x",
            "smooth_production",
            "smooth_inv"
        ]
    ].head(20)
)
# Constant production
avg_demand = network_task8["Mean_Demand_x"].mean()

network_task8["smooth_production"] = avg_demand

# Initialize inventory
network_task8["smooth_inv"] = np.nan

# Initial inventory
inventory = inventory_t0

# Calculate inventory day by day
for i in range(len(network_task8)):

    current_index = network_task8.index[i]

    inventory = (
        inventory
        + network_task8.loc[current_index, "smooth_production"]
        - network_task8.loc[current_index, "Mean_Demand_x"]
    )

    network_task8.loc[
        current_index,
        "smooth_inv"
    ] = inventory


# there's backlog

# smoothing with pre-production

print("----")
print("4 FCs considering no initial inventory")
print("Smoothing with pre-production")
print("----")

required_inventory = 0

required_inventory_values = []

for i in range(len(network_task8)-1, -1, -1):

    current_index = network_task8.index[i]

    required_inventory = (
        required_inventory
        + network_task8.loc[current_index, "Mean_Demand_x"]
        - avg_demand
    )

    required_inventory = max(required_inventory, 0)

    required_inventory_values.append(required_inventory)

required_inventory_values = required_inventory_values[::-1]

network_task8["Required_Starting_Inventory"] = required_inventory_values

required_preproduction_inventory = (
    network_task8["Required_Starting_Inventory"].iloc[0]
)

print(
    "Required inventory at start of horizon:",
    required_preproduction_inventory
)

preproduction_days = (
    required_preproduction_inventory / avg_demand
)

print("Pre-production days:", preproduction_days)

preproduction_days = math.ceil(preproduction_days)

network_task8['preprod_smooth_inv'] = np.nan

inv = required_preproduction_inventory

for i in range(len(network_task8)):

    current_index = network_task8.index[i]

    inv = inv + avg_demand - network_task8.loc[current_index, 'Mean_Demand_x']

    network_task8.loc[current_index, 'preprod_smooth_inv'] = inv

print(
    "Minimum inventory:",
    network_task8["preprod_smooth_inv"].min()
)

print(
    "Maximum inventory:",
    network_task8["preprod_smooth_inv"].max()
)



# segment smoothing per period - group by week

week_demand = network_task8.groupby("Week")['Mean_Demand_x'].mean().reset_index()



# we will divide the period into 5 segments gotten from the view of the graph

network_task8["segment"] = np.nan

network_task8.loc[
    network_task8["Week"].between(1, 21),
    "segment"
] = 1

network_task8.loc[
    network_task8["Week"].between(22, 27),
    "segment"
] = 2

network_task8.loc[
    network_task8["Week"].between(28, 44),
    "segment"
] = 3

network_task8.loc[
    network_task8["Week"].between(45, 48),
    "segment"
] = 4

network_task8.loc[
    network_task8["Week"].between(49, 52),
    "segment"
] = 5

prod_seg = (
    network_task8
    .groupby("segment")["Mean_Demand_x"]
    .mean()
)

#if initial inventory is 0

print("----")
print("4 FCs considering no initial inventory")
print("Segmented smoothing")
print("----")

inv_segmented = 0

network_task8['prod_seg'] = network_task8['segment'].map(prod_seg)

network_task8['inv_seg'] = np.nan

for i in range(len(network_task8)):

    current_index = network_task8.index[i]

    inv_segmented = (
        inv_segmented
        + network_task8.loc[
            current_index,
            'prod_seg'
        ]
        - network_task8.loc[
            current_index,
            "Mean_Demand_x"
        ]
    )

    network_task8.loc[
        current_index,
        'inv_seg'
    ] = inv_segmented

print(
    network_task8[
        [
            "Time",
            "Week",
            "Mean_Demand_x",
            "segment",
            "prod_seg",
            "inv_seg"
        ]
    ].head(20)
)

print(
    "Maximum AF production:",
    network_task8["prod_seg"].max()
)

print(
    "Minimum DC inventory:",
    network_task8["inv_seg"].min()
)

print(
    "Maximum DC inventory:",
    network_task8["inv_seg"].max()
)


if network_task8["inv_seg"].min() < 0:
    print("There is backlog.")
else:
    print("There is no backlog.")

# if initial invetory is different from cero

print("----")
print("4 FCs considering inventory in t0 is enough to cover initial demand")
print("Segmented smoothing")
print("----")

inventory_t0 = network_task8.loc[network_task8["Time"] == network_task8["Time"].min(), "DC_Inventory"].iloc[0]

inv_segmented = inventory_t0

network_task8['prod_seg'] = network_task8['segment'].map(prod_seg)

network_task8['inv_seg'] = np.nan

for i in range(len(network_task8)):

    current_index = network_task8.index[i]

    inv_segmented = (
        inv_segmented
        + network_task8.loc[
            current_index,
            'prod_seg'
        ]
        - network_task8.loc[
            current_index,
            "Mean_Demand_x"
        ]
    )

    network_task8.loc[
        current_index,
        'inv_seg'
    ] = inv_segmented

print(
    network_task8[
        [
            "Time",
            "Week",
            "Mean_Demand_x",
            "segment",
            "prod_seg",
            "inv_seg"
        ]
    ].head(20)
)

print(
    "Maximum AF production:",
    network_task8["prod_seg"].max()
)

print(
    "Minimum DC inventory:",
    network_task8["inv_seg"].min()
)

print(
    "Maximum DC inventory:",
    network_task8["inv_seg"].max()
)

backlog_days = network_task8[
    network_task8["inv_seg"] < 0
]

print(
    backlog_days[
        [
            "Time",
            "Week",
            "Mean_Demand_x",
            "segment",
            "prod_seg",
            "inv_seg"
        ]
    ]
)


if network_task8["inv_seg"].min() < 0:
    print("There is backlog.")
else:
    print("There is no backlog.")



print("\n----")
print("\nTask 8 for 1 FCs")
print("\n----")

grouped_demand = demand.groupby(["Week", "Day"])["Mean_Demand"].sum().reset_index()

grouped_demand["Time"] = (grouped_demand["Week"] - 1) * 7 + (grouped_demand["Day"] - 1)

#print(grouped_demand.head(10))

network_task8 = network_daily.copy()

network_task8 = network_task8.merge(
    grouped_demand,
    on=["Time", "Week", "Day"],
    how="left"
)

network_task8["DC_Inventory"] = dc_1FC

network_task8 = network_task8.drop(
    columns=['Demand_42d','Sigma_42d','Demand_4w','Sigma_4w','Network_Stock_4w_50','Network_Stock_4w_68',
        'Network_Stock_4w_95','Network_Stock_4w_99','Demand_6w','Sigma_6w','Network_Stock_6w_50',
        'Network_Stock_6w_68','Network_Stock_6w_95','Network_Stock_6w_99','Demand_8w',
        'Sigma_8w','Network_Stock_8w_50','Network_Stock_8w_68','Network_Stock_8w_95',
        'Network_Stock_8w_99','Mean_Demand_y'
    ],
    errors='ignore'
)

print(network_task8.columns.tolist())

network_task8 = network_task8.sort_values("Time")

network_task8['DC_delta'] = network_task8['DC_Inventory'] - network_task8['DC_Inventory'].shift(1)

inventory_t0 = network_task8.loc[network_task8["Time"] == network_task8["Time"].min(), "DC_Inventory"].iloc[0]

network_task8.loc[
    network_task8["Time"] == network_task8["Time"].min(),
    "DC_delta"
] = (
    network_task8.loc[
        network_task8["Time"] == network_task8["Time"].min(),
        "DC_Inventory"
    ].iloc[0]
    - inventory_t0
)

network_task8['Production'] = network_task8['Mean_Demand_x'] + network_task8['DC_delta']

network_task8['DC_calculated_inventory'] = np.nan

dc_day1 = (inventory_t0 + network_task8.loc[
        network_task8["Time"] == network_task8["Time"].min(), "Production"].iloc[0] - network_task8.loc[
        network_task8["Time"] == network_task8["Time"].min(), "Mean_Demand_x"].iloc[0])

network_task8.loc[network_task8['Time'] == network_task8['Time'].min(), 'DC_calculated_inventory'] = dc_day1

for i in range (1, len(network_task8)):

    current_index = network_task8.index[i]
    previous_index = network_task8.index[i-1]

    inventory = (
        network_task8.loc[previous_index, "DC_calculated_inventory"]
    + network_task8.loc[current_index, "Production"]
    - network_task8.loc[current_index, "Mean_Demand_x"])

    network_task8.loc[current_index, 'DC_calculated_inventory'] = inventory


# smoothing where we will assume that the initial inventory at the DC is the inventory target

avg_demand = network_task8['Mean_Demand_x'].mean()

network_task8['smooth_production'] = avg_demand

network_task8['smooth_inv'] = np.nan

sm_inv = (inventory_t0 + network_task8.loc[network_task8["Time"] == network_task8["Time"].min(), "smooth_production"].iloc[0]
    - network_task8.loc[network_task8["Time"] == network_task8["Time"].min(), "Mean_Demand_x"].iloc[0])

network_task8.loc[network_task8["Time"] == network_task8["Time"].min(), 'smooth_inv'] = sm_inv

for i in range(1, len(network_task8)):

    current_index = network_task8.index[i]
    previous_index = network_task8.index[i-1]

    sm_inv = (network_task8.loc[previous_index, "smooth_inv"]
    + network_task8.loc[current_index, "smooth_production"]
    - network_task8.loc[current_index, "Mean_Demand_x"]
)

    network_task8.loc[current_index, 'smooth_inv'] = sm_inv

backlog = network_task8['smooth_inv'].min()

print("----")
print("1 FC considering inventory in t0 to be enough for demand of the first period")
print("Smoothing without pre-production")
print("----")

print(
    "Minimum inventory:",
    network_task8["smooth_inv"].min()
)

if backlog < 0:
    print(f"There's backlog of {backlog}")
else:
    print("There's no backlog")

print("Initial inventory:", inventory_t0)
print("Average production:", avg_demand)
print("Minimum inventory:", network_task8["smooth_inv"].min())
print("Maximum inventory:", network_task8["smooth_inv"].max())


print(
    network_task8[
        [
            "Time",
            "Mean_Demand_x",
            "smooth_production",
            "smooth_inv"
        ]
    ].head(20)
)
# Constant production
avg_demand = network_task8["Mean_Demand_x"].mean()

network_task8["smooth_production"] = avg_demand

# Initialize inventory
network_task8["smooth_inv"] = np.nan

# Initial inventory
inventory = inventory_t0

# Calculate inventory day by day
for i in range(len(network_task8)):

    current_index = network_task8.index[i]

    inventory = (
        inventory
        + network_task8.loc[current_index, "smooth_production"]
        - network_task8.loc[current_index, "Mean_Demand_x"]
    )

    network_task8.loc[
        current_index,
        "smooth_inv"
    ] = inventory

# there is no backlog, too much inventory

# now we will try with smoothing no initial invetory

print("----")
print("1 FC considering no initial inventory")
print("Smoothing without pre-production")
print("----")

avg_demand = network_task8['Mean_Demand_x'].mean()

network_task8['smooth_production'] = avg_demand

network_task8['smooth_inv'] = np.nan

network_task8.loc[network_task8["Time"] == network_task8["Time"].min(), 'smooth_inv'] = 0

for i in range(1, len(network_task8)):

    current_index = network_task8.index[i]
    previous_index = network_task8.index[i-1]

    sm_inv = (network_task8.loc[previous_index, "smooth_inv"]
    + network_task8.loc[current_index, "smooth_production"]
    - network_task8.loc[current_index, "Mean_Demand_x"]
)

    network_task8.loc[current_index, 'smooth_inv'] = sm_inv

backlog = network_task8['smooth_inv'].min()

print(
    "Minimum inventory:",
    network_task8["smooth_inv"].min()
)

if backlog < 0:
    print(f"There's backlog of {backlog}")
else:
    print("There's no backlog")

print("Initial inventory:", inventory_t0)
print("Average production:", avg_demand)
print("Minimum inventory:", network_task8["smooth_inv"].min())
print("Maximum inventory:", network_task8["smooth_inv"].max())


print(
    network_task8[
        [
            "Time",
            "Mean_Demand_x",
            "smooth_production",
            "smooth_inv"
        ]
    ].head(20)
)
# Constant production
avg_demand = network_task8["Mean_Demand_x"].mean()

network_task8["smooth_production"] = avg_demand

# Initialize inventory
network_task8["smooth_inv"] = np.nan

# Initial inventory
inventory = inventory_t0

# Calculate inventory day by day
for i in range(len(network_task8)):

    current_index = network_task8.index[i]

    inventory = (
        inventory
        + network_task8.loc[current_index, "smooth_production"]
        - network_task8.loc[current_index, "Mean_Demand_x"]
    )

    network_task8.loc[
        current_index,
        "smooth_inv"
    ] = inventory


# there's backlog

# smoothing with pre-production

print("----")
print("1 FC considering no initial inventory")
print("Smoothing with pre-production")
print("----")

required_inventory = 0

required_inventory_values = []

for i in range(len(network_task8)-1, -1, -1):

    current_index = network_task8.index[i]

    required_inventory = (
        required_inventory
        + network_task8.loc[current_index, "Mean_Demand_x"]
        - avg_demand
    )

    required_inventory = max(required_inventory, 0)

    required_inventory_values.append(required_inventory)

required_inventory_values = required_inventory_values[::-1]

network_task8["Required_Starting_Inventory"] = required_inventory_values

required_preproduction_inventory = (
    network_task8["Required_Starting_Inventory"].iloc[0]
)

print(
    "Required inventory at start of horizon:",
    required_preproduction_inventory
)

preproduction_days = (
    required_preproduction_inventory / avg_demand
)

print("Pre-production days:", preproduction_days)

preproduction_days = math.ceil(preproduction_days)

network_task8['preprod_smooth_inv'] = np.nan

inv = required_preproduction_inventory

for i in range(len(network_task8)):

    current_index = network_task8.index[i]

    inv = inv + avg_demand - network_task8.loc[current_index, 'Mean_Demand_x']

    network_task8.loc[current_index, 'preprod_smooth_inv'] = inv

print(
    "Minimum inventory:",
    network_task8["preprod_smooth_inv"].min()
)

print(
    "Maximum inventory:",
    network_task8["preprod_smooth_inv"].max()
)



# segment smoothing per period - group by week

week_demand = network_task8.groupby("Week")['Mean_Demand_x'].mean().reset_index()



# we will divide the period into 5 segments gotten from the view of the graph

network_task8["segment"] = np.nan

network_task8.loc[
    network_task8["Week"].between(1, 21),
    "segment"
] = 1

network_task8.loc[
    network_task8["Week"].between(22, 27),
    "segment"
] = 2

network_task8.loc[
    network_task8["Week"].between(28, 44),
    "segment"
] = 3

network_task8.loc[
    network_task8["Week"].between(45, 48),
    "segment"
] = 4

network_task8.loc[
    network_task8["Week"].between(49, 52),
    "segment"
] = 5

prod_seg = (
    network_task8
    .groupby("segment")["Mean_Demand_x"]
    .mean()
)

#if initial inventory is 0

print("----")
print("1 FC considering no initial inventory")
print("Segmented Smoothing")
print("----")

inv_segmented = 0

network_task8['prod_seg'] = network_task8['segment'].map(prod_seg)

network_task8['inv_seg'] = np.nan

for i in range(len(network_task8)):

    current_index = network_task8.index[i]

    inv_segmented = (
        - network_task8.loc[
            current_index,
            "Mean_Demand_x"
        ]
    )

    network_task8.loc[
        current_index,
        'inv_seg'
    ] = inv_segmented

print(
    network_task8[
        [
            "Time",
            "Week",
            "Mean_Demand_x",
            "segment",
            "prod_seg",
            "inv_seg"
        ]
    ].head(20)
)

print(
    "Maximum AF production:",
    network_task8["prod_seg"].max()
)

print(
    "Minimum DC inventory:",
    network_task8["inv_seg"].min()
)

print(
    "Maximum DC inventory:",
    network_task8["inv_seg"].max()
)


if network_task8["inv_seg"].min() < 0:
    print("There is backlog.")
else:
    print("There is no backlog.")

# if initial invetory is different from cero


print("----")
print("1 FC considering initial inventory is enough to cober initial demand")
print("Segmented Smoothing")
print("----")

inventory_t0 = network_task8.loc[network_task8["Time"] == network_task8["Time"].min(), "DC_Inventory"].iloc[0]

inv_segmented = inventory_t0

network_task8['prod_seg'] = network_task8['segment'].map(prod_seg)

network_task8['inv_seg'] = np.nan

for i in range(len(network_task8)):

    current_index = network_task8.index[i]

    inv_segmented = (
        inv_segmented
        + network_task8.loc[
            current_index,
            'prod_seg'
        ]
        - network_task8.loc[
            current_index,
            "Mean_Demand_x"
        ]
    )

    network_task8.loc[
        current_index,
        'inv_seg'
    ] = inv_segmented

print(
    network_task8[
        [
            "Time",
            "Week",
            "Mean_Demand_x",
            "segment",
            "prod_seg",
            "inv_seg"
        ]
    ].head(20)
)

print(
    "Maximum AF production:",
    network_task8["prod_seg"].max()
)

print(
    "Minimum DC inventory:",
    network_task8["inv_seg"].min()
)

print(
    "Maximum DC inventory:",
    network_task8["inv_seg"].max()
)

backlog_days = network_task8[
    network_task8["inv_seg"] < 0
]

print(
    backlog_days[
        [
            "Time",
            "Week",
            "Mean_Demand_x",
            "segment",
            "prod_seg",
            "inv_seg"
        ]
    ]
)

if network_task8["inv_seg"].min() < 0:
    print("There is backlog.")
else:
    print("There is no backlog.")
