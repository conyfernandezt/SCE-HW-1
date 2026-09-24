import pandas as pd
import contextlib
import io
import numpy as np

with contextlib.redirect_stdout(io.StringIO()):
    import task3bc as t3


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
    34 / stats_1FC["mean"]
).astype(int)
stats_4FC["replenishment_interval"] = np.ceil(
    34 / stats_4FC["mean"]
).astype(int)
stats_15FC["replenishment_interval"] = np.ceil(
    34 / stats_15FC["mean"]
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
print(results_1FC)

results_4FC = stats_4FC.drop(columns=["mean", "std", "rad", "forecast_buffer_days"])
results_4FC.rename(columns={"closest location": "FC"}, inplace=True)
print(results_4FC)

results_15FC = stats_15FC.drop(columns=["mean", "std", "rad", "forecast_buffer_days"])
results_15FC.rename(columns={"closest location": "FC"}, inplace=True)
print(results_15FC)