import pandas as pd
import contextlib
import io
import numpy as np

with contextlib.redirect_stdout(io.StringIO()):
    import task3bc as t3
with contextlib.redirect_stdout(io.StringIO()):
    import task9 as t9


# get demand dfs with closest location
df_demand = pd.read_csv("task2_demand_results.csv")
df_demand_1FC = df_demand.merge(
    t3.df_1FC[["ZIP3", "closest location"]],
    on="ZIP3",
    how="left"
)
df_demand_4FC = df_demand.merge(
    t3.df_4FC[["ZIP3", "closest location"]],
    on="ZIP3",
    how="left"
)
df_demand_15FC = df_demand.merge(
    t3.df_15FC[["ZIP3", "closest location"]],
    on="ZIP3",
    how="left"
)

# get daily demand for each FC
daily_demand_1FC = (
    df_demand_1FC
    .groupby(["Week", "Day", "closest location"])["Mean_Demand"]
    .sum().reset_index()
)
daily_demand_4FC = (
    df_demand_4FC
    .groupby(["Week", "Day", "closest location"])["Mean_Demand"]
    .sum().reset_index()
)
daily_demand_15FC = (
    df_demand_15FC
    .groupby(["Week", "Day", "closest location"])["Mean_Demand"]
    .sum().reset_index()
)

# get mean and std for each FC
stats_1FC = (
    daily_demand_1FC
    .groupby("closest location")["Mean_Demand"]
    .agg(["mean", "std"])
    .reset_index()
)
stats_4FC = (
    daily_demand_4FC
    .groupby("closest location")["Mean_Demand"]
    .agg(["mean", "std"])
    .reset_index()
)
stats_15FC = (
    daily_demand_15FC
    .groupby("closest location")["Mean_Demand"]
    .agg(["mean", "std"])
    .reset_index()
)

# use mean to calculate replenishment interval for each FC
# using 34 to "comfortably exceed" 10% FTL
stats_1FC["replenishment_interval"] = np.ceil(
    27 / stats_1FC["mean"]
).astype(int)
stats_4FC["replenishment_interval"] = np.ceil(
    27 / stats_4FC["mean"]
).astype(int)
stats_15FC["replenishment_interval"] = np.ceil(
    27 / stats_15FC["mean"]
).astype(int)

# replenishment shipment times in terms of RAD
fc_list_1FC = ["GA-303"]
rad_1FC = [0]

fc_list_4FC = [
    "GA-303",
    "NY-134",
    "TX-799",
    "UT-841"
]
rad_4FC = [0, 2, 3, 4]

fc_list_15FC = [
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
rad_15FC = [0, 4, 4, 4, 5, 3, 2, 2, 2, 2, 1, 2, 2, 2, 5]
rad_dict_15FC = dict(zip(fc_list_15FC, rad_15FC))


# compute a forecasting error or "uncertainty" buffer
stats_1FC["rad"] = rad_1FC
stats_1FC["forecast_buffer_days"] = (
    2.33
    * stats_1FC["std"]
    * np.sqrt(stats_1FC["rad"])
    / stats_1FC["mean"]
)
stats_1FC["autonomy_threshold"] = np.ceil(stats_1FC["forecast_buffer_days"] + stats_1FC["rad"])

stats_4FC["rad"] = rad_4FC
stats_4FC["forecast_buffer_days"] = (
    2.33
    * stats_4FC["std"]
    * np.sqrt(stats_4FC["rad"])
    / stats_4FC["mean"]
)
stats_4FC["autonomy_threshold"] = np.ceil(stats_4FC["forecast_buffer_days"] + stats_4FC["rad"])

stats_15FC["rad"] = stats_15FC["closest location"].map(rad_dict_15FC)
stats_15FC["forecast_buffer_days"] = (
    2.33
    * stats_15FC["std"]
    * np.sqrt(stats_15FC["rad"])
    / stats_15FC["mean"]
)
# autonomy threshold = forecast buffer plus shipment time
stats_15FC["autonomy_threshold"] = np.ceil(stats_15FC["forecast_buffer_days"] + stats_15FC["rad"])

results_1FC = stats_1FC.drop(columns=["mean", "std", "rad", "forecast_buffer_days"])
results_1FC.rename(columns={"closest location": "FC"}, inplace=True)

results_4FC = stats_4FC.drop(columns=["mean", "std", "rad", "forecast_buffer_days"])
results_4FC.rename(columns={"closest location": "FC"}, inplace=True)

results_15FC = stats_15FC.drop(columns=["mean", "std", "rad", "forecast_buffer_days"])
results_15FC.rename(columns={"closest location": "FC"}, inplace=True)


stats_1FC["robust_inventory_target_units"] = (
    stats_1FC["mean"]
    * stats_1FC["autonomy_threshold"]
    + 2.33
    * stats_1FC["std"]
    * np.sqrt(stats_1FC["autonomy_threshold"])
)

stats_1FC["average_inventory"] = (
    stats_1FC["robust_inventory_target_units"] - (
        stats_1FC["mean"]
        * stats_1FC["replenishment_interval"] / 2
    )
).round(2)

stats_4FC["robust_inventory_target_units"] = (
    stats_4FC["mean"]
    * stats_4FC["autonomy_threshold"]
    + 2.33
    * stats_4FC["std"]
    * np.sqrt(stats_4FC["autonomy_threshold"])
)

stats_4FC["average_inventory"] = (
    stats_4FC["robust_inventory_target_units"] - (
        stats_4FC["mean"]
        * stats_4FC["replenishment_interval"] / 2
    )
).round(2)

stats_15FC["robust_inventory_target_units"] = (
    stats_15FC["mean"]
    * stats_15FC["autonomy_threshold"]
    + 2.33
    * stats_15FC["std"]
    * np.sqrt(stats_15FC["autonomy_threshold"])
)

stats_15FC["average_inventory"] = (
    stats_15FC["robust_inventory_target_units"] - (
        stats_15FC["mean"]
        * stats_15FC["replenishment_interval"] / 2
    )
).round(2)

results_1FC["demand_share"] = 1.0

demand_dict_4FC = dict(zip(t3.result_4FC["FC"], t3.result_4FC["Demand Share"]))
results_4FC["demand_share"] = results_4FC["FC"].map(demand_dict_4FC)

demand_dict_15FC = dict(zip(t3.result_15FC["FC"], t3.result_15FC["Demand Share"]))
results_15FC["demand_share"] = results_15FC["FC"].map(demand_dict_15FC)

results_1FC["RAD"] = stats_1FC["rad"]
results_1FC["avg_inv"] = stats_1FC["average_inventory"]
results_4FC["RAD"] = stats_4FC["rad"]
results_4FC["avg_inv"] = stats_4FC["average_inventory"]
results_15FC["RAD"] = stats_15FC["rad"]
results_15FC["avg_inv"] = stats_15FC["average_inventory"]

# print part b results
print("***** Part b: Parameters *****\n")
print("\n ----- Single-FC -----")
print(results_1FC)
print("\n ----- Four-FC -----")
print(results_4FC)
print("\n ----- 15-FC -----")
print(results_15FC)


# add 21 day target inventory
stats_1FC["target_inventory"] = (
    21 * stats_1FC["mean"]
    + 2.33 * stats_1FC["std"] * np.sqrt(21)
)
stats_4FC["target_inventory"] = (
    21 * stats_4FC["mean"]
    + 2.33 * stats_4FC["std"] * np.sqrt(21)
)
stats_15FC["target_inventory"] = (
    21 * stats_15FC["mean"]
    + 2.33 * stats_15FC["std"] * np.sqrt(21)
)

# simulate inventory to determine frequency of replenishment == 27
floor_results_1FC = []

for _, fc in stats_1FC.iterrows():

    fc_name = fc["closest location"]
    interval = int(fc["replenishment_interval"])
    target = fc["target_inventory"]

    demand = (
        daily_demand_1FC[
            daily_demand_1FC["closest location"] == fc_name
        ]
        .sort_values(["Week", "Day"])["Mean_Demand"]
        .to_numpy()
    )

    inventory = target
    num_replenishments = 0
    num_floored = 0

    daily_inventory = []

    for day in range(len(demand)):

        inventory -= demand[day]

        # replenish every R days
        if (day + 1) % interval == 0:

            inventory_position = inventory

            Q = max(target - inventory_position, 27)

            num_replenishments += 1

            if Q == 27:
                num_floored += 1

            inventory += Q

        daily_inventory.append(inventory)

    floor_frequency = (
        num_floored / num_replenishments
        if num_replenishments > 0
        else 0
    )

    average_inventory = np.mean(daily_inventory)

    floor_results_1FC.append({
        "FC": fc_name,
        "Total Replenishments": num_replenishments,
        "27-Unit Replenishments": num_floored,
        "27-Unit Frequency": floor_frequency,
        "Average Inventory": average_inventory
    })

df_floor_results_1FC = pd.DataFrame(floor_results_1FC)

# again for 4FC
floor_results_4FC = []

for _, fc in stats_4FC.iterrows():

    fc_name = fc["closest location"]
    interval = int(fc["replenishment_interval"])
    target = fc["target_inventory"]

    demand = (
        daily_demand_4FC[
            daily_demand_4FC["closest location"] == fc_name
        ]
        .sort_values(["Week", "Day"])["Mean_Demand"]
        .to_numpy()
    )

    inventory = target
    num_replenishments = 0
    num_floored = 0

    daily_inventory = []

    for day in range(len(demand)):

        inventory -= demand[day]

        # replenish every R days
        if (day + 1) % interval == 0:

            inventory_position = inventory

            Q = max(target - inventory_position, 27)

            num_replenishments += 1

            if Q == 27:
                num_floored += 1

            inventory += Q

        daily_inventory.append(inventory)

    floor_frequency = (
        num_floored / num_replenishments
        if num_replenishments > 0
        else 0
    )

    average_inventory = np.mean(daily_inventory)

    floor_results_4FC.append({
        "FC": fc_name,
        "Total Replenishments": num_replenishments,
        "27-Unit Replenishments": num_floored,
        "27-Unit Frequency": floor_frequency,
        "Average Inventory": average_inventory
    })
df_floor_results_4FC = pd.DataFrame(floor_results_4FC)

# again for 15FC
floor_results_15FC = []

for _, fc in stats_15FC.iterrows():

    fc_name = fc["closest location"]
    interval = int(fc["replenishment_interval"])
    target = fc["target_inventory"]

    demand = (
        daily_demand_15FC[
            daily_demand_15FC["closest location"] == fc_name
        ]
        .sort_values(["Week", "Day"])["Mean_Demand"]
        .to_numpy()
    )

    inventory = target
    num_replenishments = 0
    num_floored = 0

    daily_inventory = []

    for day in range(len(demand)):

        inventory -= demand[day]

        # replenish every R days
        if (day + 1) % interval == 0:

            inventory_position = inventory

            Q = max(target - inventory_position, 27)

            num_replenishments += 1

            if Q == 27:
                num_floored += 1

            inventory += Q

        daily_inventory.append(inventory)

    floor_frequency = (
        num_floored / num_replenishments
        if num_replenishments > 0
        else 0
    )

    average_inventory = np.mean(daily_inventory)

    floor_results_15FC.append({
        "FC": fc_name,
        "Total Replenishments": num_replenishments,
        "27-Unit Replenishments": num_floored,
        "27-Unit Frequency": floor_frequency,
        "Average Inventory": average_inventory
    })
df_floor_results_15FC = pd.DataFrame(floor_results_15FC)

# add floor frequency and resulting average inventory to our results
results_1FC["floor_freq"] = df_floor_results_1FC["27-Unit Frequency"].round(3)
results_1FC["resulting_avg_inv"] = df_floor_results_1FC["Average Inventory"].round(2)
results_4FC["floor_freq"] = df_floor_results_4FC["27-Unit Frequency"].round(3)
results_4FC["resulting_avg_inv"] = df_floor_results_4FC["Average Inventory"].round(2)
results_15FC["floor_freq"] = df_floor_results_15FC["27-Unit Frequency"].round(3)
results_15FC["resulting_avg_inv"] = df_floor_results_15FC["Average Inventory"].round(2)

partc_results_1FC = results_1FC[["FC", "floor_freq", "resulting_avg_inv"]]
partc_results_4FC = results_4FC[["FC", "floor_freq", "resulting_avg_inv"]]
partc_results_15FC = results_15FC[["FC", "floor_freq", "resulting_avg_inv"]]

# get results from task 9 to compare
task9_replenishment_df = pd.read_excel("outputs/task9/replenishment_summary_all_networks.xlsx")
task9_replenishment_df_1FC = task9_replenishment_df[task9_replenishment_df["network"] == "1-FC"]
task9_replenishment_df_4FC = task9_replenishment_df[task9_replenishment_df["network"] == "4-FC"]
task9_replenishment_df_15FC = task9_replenishment_df[task9_replenishment_df["network"] == "15-FC"]

task9_result_1FC = task9_replenishment_df_1FC[["FC", "floor_frequency_pct", "average_end_of_day_inventory_units"]]
task9_result_4FC = task9_replenishment_df_4FC[["FC", "floor_frequency_pct", "average_end_of_day_inventory_units"]]
task9_result_15FC = task9_replenishment_df_15FC[["FC", "floor_frequency_pct", "average_end_of_day_inventory_units"]]

# print part c results
print("\n\n***** Part c: Floor Frequency *****\n")
print("\n ----- Single-FC: Task 10 -----")
print(partc_results_1FC)
print("\n ----- Single-FC: Task 9 -----")
print(task9_result_1FC)
print("\n ----- Four-FC: Task 10 -----")
print(partc_results_4FC)
print("\n ----- Four-FC: Task 9 -----")
print(task9_result_4FC)
print("\n ----- 15-FC: Task 10 -----")
print(partc_results_15FC)
print("\n ----- 15-FC: Task 9 -----")
print(task9_result_15FC)

# part d
stats_1FC["typical_order_quantity"] = (
    stats_1FC["mean"] * stats_1FC["replenishment_interval"]
)
stats_1FC["below_27_units"] = (
    stats_1FC["typical_order_quantity"] < 27
)

stats_4FC["typical_order_quantity"] = (
    stats_4FC["mean"] * stats_4FC["replenishment_interval"]
)
stats_4FC["below_27_units"] = (
    stats_4FC["typical_order_quantity"] < 27
)

stats_15FC["typical_order_quantity"] = (
    stats_15FC["mean"] * stats_15FC["replenishment_interval"]
)
stats_15FC["below_27_units"] = (
    stats_15FC["typical_order_quantity"] < 27
)
