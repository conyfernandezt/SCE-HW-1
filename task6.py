# TASK 6 - Optimize OTD Promise
import pandas as pd
import matplotlib.pyplot as plt
import contextlib
import io
import numpy as np
import task5 as t5

market_list = ["Primary", "Secondary", "Tertiary"]
otd_promises = ["1", "2", "3", "4", "5", "5+"]


def optimize_otd(gop_matrix,
                 revenue_matrix,
                 shipping_matrix,
                 net_revenue_matrix):

    # Find column with maximum GOP for each market
    best_indices = np.argmax(gop_matrix, axis=1)

    results = []

    for i, market in enumerate(market_list):
        j = best_indices[i]

        results.append({
            "Market": market,
            "Optimal OTD": otd_promises[j],
            "Revenue": revenue_matrix[i, j],
            "Shipping Cost": shipping_matrix[i, j],
            "Net Revenue": net_revenue_matrix[i, j],
            "Gross Operating Profit": gop_matrix[i, j]
        })

    return pd.DataFrame(results)

optimal_1FC = optimize_otd(
    t5.gross_operating_profit_matrix_1FC,
    np.array(t5.revenue_matrix),
    t5.shipping_cost_matrix_1FC,
    t5.net_revenue_matrix_1FC
)

optimal_4FC = optimize_otd(
    t5.gross_operating_profit_matrix_4FC,
    np.array(t5.revenue_matrix),
    t5.shipping_cost_matrix_4FC,
    t5.net_revenue_matrix_4FC
)

optimal_15FC = optimize_otd(
    t5.gross_operating_profit_matrix_15FC,
    np.array(t5.revenue_matrix),
    t5.shipping_cost_matrix_15FC,
    t5.net_revenue_matrix_15FC
)

#Optimal OTD Promise for each market type and network configuration
print("1 FC")
print(optimal_1FC)

print("\n4 FC")
print(optimal_4FC)

print("\n15 FC")
print(optimal_15FC)

#Optimal OTD for overall market
print("\nOverall Market results for 1 FC")
print(optimal_1FC[
    ["Revenue", "Shipping Cost", "Net Revenue", "Gross Operating Profit"]
].sum())

print("\nOverall Market results for 4 FC")
print(optimal_4FC[
    ["Revenue", "Shipping Cost", "Net Revenue", "Gross Operating Profit"]
].sum())

print("\nOverall Market results for 15 FC")
print(optimal_15FC[
    ["Revenue", "Shipping Cost", "Net Revenue", "Gross Operating Profit"]
].sum())

def scenario_totals(col,
                    revenue_matrix,
                    shipping_matrix,
                    net_revenue_matrix,
                    gop_matrix):

    return {
        "Revenue": float(np.sum(np.array(revenue_matrix)[:, col])),
        "Shipping Cost": float(np.sum(shipping_matrix[:, col])),
        "Net Revenue": float(np.sum(net_revenue_matrix[:, col])),
        "Gross Operating Profit": float(np.sum(gop_matrix[:, col]))
    }

all_1day_1FC = scenario_totals(
    0,
    t5.revenue_matrix,
    t5.shipping_cost_matrix_1FC,
    t5.net_revenue_matrix_1FC,
    t5.gross_operating_profit_matrix_1FC
)

all_5plus_1FC = scenario_totals(
    5,
    t5.revenue_matrix,
    t5.shipping_cost_matrix_1FC,
    t5.net_revenue_matrix_1FC,
    t5.gross_operating_profit_matrix_1FC
)

print("Everyone gets 1-day:")
print(all_1day_1FC)

print("\nEveryone gets 5+:")
print(all_5plus_1FC)

all_1day_4FC = scenario_totals(
    0,
    t5.revenue_matrix,
    t5.shipping_cost_matrix_4FC,
    t5.net_revenue_matrix_4FC,
    t5.gross_operating_profit_matrix_4FC
)

all_5plus_4FC = scenario_totals(
    5,
    t5.revenue_matrix,
    t5.shipping_cost_matrix_4FC,
    t5.net_revenue_matrix_4FC,
    t5.gross_operating_profit_matrix_4FC
)

print("Everyone gets 1-day:")
print(all_1day_4FC)

print("\nEveryone gets 5+:")
print(all_5plus_4FC)

all_1day_15FC = scenario_totals(
    0,
    t5.revenue_matrix,
    t5.shipping_cost_matrix_15FC,
    t5.net_revenue_matrix_15FC,
    t5.gross_operating_profit_matrix_15FC
)

all_5plus_15FC = scenario_totals(
    5,
    t5.revenue_matrix,
    t5.shipping_cost_matrix_15FC,
    t5.net_revenue_matrix_15FC,
    t5.gross_operating_profit_matrix_15FC
)

print("Everyone gets 1-day:")
print(all_1day_15FC)

print("\nEveryone gets 5+:")
print(all_5plus_15FC)