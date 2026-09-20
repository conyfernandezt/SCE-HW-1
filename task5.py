import pandas as pd
import contextlib
import io
import matplotlib.pyplot as plt
import numpy as np

with contextlib.redirect_stdout(io.StringIO()):
    import task3bc as t3

tsukumo_demand = 2000000*0.036
otd_promises = ["1", "2", "3", "4", "5", "5+"]
otd_proportions_primary = [1, 0.9, 0.75, 0.6, 0.4, 0.3]
otd_proportions_secondary = [1, 1, 0.95, 0.75, 0.6, 0.4]
otd_proportions_tertiary = [1, 1, 1, 0.95, 0.8, 0.6]

# *** (a) Revenue (numbers from task 3) ***
demand_primary = 0.7108*tsukumo_demand
demand_secondary = 0.2769*tsukumo_demand
demand_tertiary = 0.0123*tsukumo_demand
demand_list = [demand_primary, demand_secondary, demand_tertiary]

revenue_primary = []
for prop in otd_proportions_primary:
    revenue_primary.append(3000*demand_primary*prop)

revenue_secondary = []
for prop in otd_proportions_secondary:
    revenue_secondary.append(3000*demand_secondary*prop)
revenue_tertiary = []
for prop in otd_proportions_tertiary:
    revenue_tertiary.append(3000*demand_tertiary*prop)

revenue_matrix = [revenue_primary, revenue_secondary, revenue_tertiary]


# *** (b) Total Shipping Cost ***
shipment_costs = [
    [607, 759, 1025, 1445, 2078, 2692, 2841, 2912],
    [353, 441, 585, 794, 924, 1427, 1795, 1854],
    [230, 287, 392, 533, 655, 895, 1202, 1330],
    [139, 173, 238, 316, 343, 491, 776, 894],
    [121, 151, 191, 242, 287, 340, 362, 388],
    [103, 128, 160, 198, 225, 259, 276, 301]
]
# get demand share by distance bucket
demand_share_by_bucket_1FC = (t3.df_1FC.groupby("Distance Bucket", observed=False)["PMF"]
                    .sum().round(4)
                    .reset_index())
demand_share_by_bucket_1FC.columns = ["Bucket", "Demand Share"]

demand_share_by_bucket_4FC = (t3.df_4FC.groupby("Distance Bucket", observed=False)["PMF"]
                    .sum().round(4)
                    .reset_index())
demand_share_by_bucket_4FC.columns = ["Bucket", "Demand Share"]

demand_share_by_bucket_15FC = (t3.df_15FC.groupby("Distance Bucket", observed=False)["PMF"]
                    .sum().round(4)
                    .reset_index())
demand_share_by_bucket_15FC.columns = ["Bucket", "Demand Share"]

# single-FC network
df_1FC_shipping_cost = pd.DataFrame()
df_1FC_shipping_cost["bucket"] = demand_share_by_bucket_1FC["Bucket"]
for i in range(len(otd_promises)):
    df_1FC_shipping_cost[otd_promises[i]] = tsukumo_demand * demand_share_by_bucket_1FC["Demand Share"] * shipment_costs[i]

shipping_cost_bucket_matrix_1FC = df_1FC_shipping_cost.iloc[:, 1:].to_numpy()
bucket_market_matrix_1FC = t3.result_bucket_market_1FC.iloc[:, :].to_numpy()
shipping_cost_matrix_1FC = bucket_market_matrix_1FC @ shipping_cost_bucket_matrix_1FC

# 4-FC network
df_4FC_shipping_cost = pd.DataFrame()
df_4FC_shipping_cost["bucket"] = demand_share_by_bucket_4FC["Bucket"]
for i in range(len(otd_promises)):
    df_4FC_shipping_cost[otd_promises[i]] = tsukumo_demand * demand_share_by_bucket_4FC["Demand Share"] * shipment_costs[i]

shipping_cost_bucket_matrix_4FC = df_4FC_shipping_cost.iloc[:, 1:].to_numpy()
bucket_market_matrix_4FC = t3.result_bucket_market_4FC.iloc[:, :].to_numpy()
shipping_cost_matrix_4FC = bucket_market_matrix_4FC @ shipping_cost_bucket_matrix_4FC

# 15-FC network
df_15FC_shipping_cost = pd.DataFrame()
df_15FC_shipping_cost["bucket"] = demand_share_by_bucket_15FC["Bucket"]
for i in range(len(otd_promises)):
    df_15FC_shipping_cost[otd_promises[i]] = tsukumo_demand * demand_share_by_bucket_15FC["Demand Share"] * shipment_costs[i]

shipping_cost_bucket_matrix_15FC = df_15FC_shipping_cost.iloc[:, 1:].to_numpy()
bucket_market_matrix_15FC = t3.result_bucket_market_15FC.iloc[:, :].to_numpy()
shipping_cost_matrix_15FC = bucket_market_matrix_15FC @ shipping_cost_bucket_matrix_15FC

# *** (c) Net Revenue ***
net_revenue_matrix_1FC = revenue_matrix - shipping_cost_matrix_1FC
net_revenue_matrix_4FC = revenue_matrix - shipping_cost_matrix_4FC
net_revenue_matrix_15FC = revenue_matrix - shipping_cost_matrix_15FC


# *** (d) gross operating profit ***
production_cost_list = [750*demand_primary, 750*demand_secondary, 750*demand_tertiary]
production_cost_matrix = np.tile(production_cost_list, (6, 1)).T

gross_operating_profit_matrix_1FC = net_revenue_matrix_1FC - production_cost_matrix
gross_operating_profit_matrix_4FC = net_revenue_matrix_4FC - production_cost_matrix
gross_operating_profit_matrix_15FC = net_revenue_matrix_15FC - production_cost_matrix


# *** Plot Results ***
market_list = ["Primary", "Secondary", "Tertiary"]

matrix_1FC_millions = gross_operating_profit_matrix_1FC / 1000000
for i, market in enumerate(market_list):
    plt.plot(otd_promises, matrix_1FC_millions[i], marker='o', label=market)
plt.xlabel("OTD Promise (days)")
plt.ylabel("Gross Operating Profit ($ millions)")
plt.title("Single-FC Network: Gross Operating Profit by OTD for each Market Type")
plt.legend()
plt.show()


matrix_4FC_millions = gross_operating_profit_matrix_4FC / 1000000
for i, market in enumerate(market_list):
    plt.plot(otd_promises, matrix_4FC_millions[i], marker='o', label=market)
plt.xlabel("OTD Promise (days)")
plt.ylabel("Gross Operating Profit ($ millions)")
plt.title("Four-FC Network: Gross Operating Profit by OTD for each Market Type")
plt.legend()
plt.show()


matrix_15FC_millions = gross_operating_profit_matrix_15FC / 1000000
for i, market in enumerate(market_list):
    plt.plot(otd_promises, matrix_15FC_millions[i], marker='o', label=market)
plt.xlabel("OTD Promise (days)")
plt.ylabel("Gross Operating Profit ($ millions)")
plt.title("15-FC Network: Gross Operating Profit by OTD for each Market Type")
plt.legend()
plt.show()