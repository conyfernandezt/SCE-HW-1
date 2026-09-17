import pandas as pd

df_distance_1FC = pd.read_csv("Assignment/fc_zip3_distance.csv")
df_distance_4FC = pd.read_csv("Assignment/fc_zip3_distance.csv")
df_distance_15FC = pd.read_csv("Assignment/fc_zip3_distance.csv")
df_pmf = pd.read_csv("Assignment/zip3_pmf.csv")
df_market = pd.read_csv("Assignment/zip3_market.csv")

# df_main = df_pmf
# df_main["Market"] = df_market["Market"]

distance_column_1FC = ["GA-303"]

distance_columns_4FC = [
    "GA-303",
    "NY-134",
    "TX-799",
    "UT-841"
]

distance_columns_15FC = [
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

df_distance_1FC["closest location"] = (
    df_distance_1FC[distance_column_1FC].idxmin(axis=1)
)

df_distance_4FC["closest location"] = (
    df_distance_4FC[distance_columns_4FC].idxmin(axis=1)
)

df_distance_15FC["closest location"] = (
    df_distance_15FC[distance_columns_15FC].idxmin(axis=1)
)

# create single fc data frame
df_1FC = df_market.merge(
    df_pmf, left_on="ZIP3", right_on="ZIP3", how="left"
).merge(
    df_distance_1FC[["ZIP3", "closest location"]], on="ZIP3", how="left"
)
df_1FC["PMF"] = df_1FC["PMF"].fillna(0.0)

# create 4 fc data frame
df_4FC = df_market.merge(
    df_pmf, left_on="ZIP3", right_on="ZIP3", how="left"
).merge(
    df_distance_4FC[["ZIP3", "closest location"]], on="ZIP3", how="left"
)
df_4FC["PMF"] = df_4FC["PMF"].fillna(0.0)

# create 15 fc data frame
df_15FC = df_market.merge(
    df_pmf, left_on="ZIP3", right_on="ZIP3", how="left"
).merge(
    df_distance_15FC[["ZIP3", "closest location"]], on="ZIP3", how="left"
)
df_15FC["PMF"] = df_15FC["PMF"].fillna(0.0)


# *** Single-FC Network ***
print("***** Single-FC Network Demand Share by Market Type: *****\n")
result_1C = (df_1FC.groupby("Market")["PMF"]
                    .sum().round(4)
                    .sort_values(ascending=False)
                    .reset_index())
result_1C.columns = ["Market", "Demand Share"]
print(result_1C)
print("\n\n")

# *** Four-FC Network ***
# estimate demand share for each FC
print("***** Four-FC Network Demand Share: *****\n")
result_4FC = (df_4FC.groupby("closest location")["PMF"]
                    .sum().round(4)
                    .sort_values(ascending=False)
                    .reset_index())
result_4FC.columns = ["FC", "Demand Share"]
print(result_4FC)
print("\n\n")

# estimate demand share for each FC and market type
print("***** Four-FC Network Demand Share by Market Type: *****\n")
result_4FC_market = df_4FC.pivot_table(
    index="closest location",
    columns="Market",
    values="PMF",
    aggfunc="sum",
    fill_value=0
).round(4)
result_4FC_market.index.name = "FC"
print(result_4FC_market)
print("\n\n")

# *** 15-FC Network ***
# estimate demand share for each FC
print("***** 15-FC Network Demand Share: *****\n")
result_15FC = (df_15FC.groupby("closest location")["PMF"]
                    .sum().round(4)
                    .sort_values(ascending=False)
                    .reset_index())
result_15FC.columns = ["FC", "Demand Share"]
print(result_15FC)
print("\n\n")

# estimate demand share for each FC and market type
print("***** 15-FC Network Demand Share by Market Type: *****\n")
result_15FC_market = df_15FC.pivot_table(
    index="closest location",
    columns="Market",
    values="PMF",
    aggfunc="sum",
    fill_value=0
).round(4)
result_15FC_market.index.name = "FC"
print(result_15FC_market)
print("\n\n")


# create distance buckets
distance_buckets = [0, 51, 151, 301, 601, 1001, 1401, 1801, float("inf")]
bucket_labels = ["0-50", "51-150", "151-300", "301-600", "601-1000", "1001-1400", "1401-1800", "over 1800"]

df_distance_1FC["smallest distance"] = df_distance_1FC[distance_column_1FC].min(axis=1)
df_1FC["Distance Bucket"] = pd.cut(
    df_distance_1FC["smallest distance"],
    bins=distance_buckets,
    labels=bucket_labels,
    right=False
)

df_distance_4FC["smallest distance"] = df_distance_4FC[distance_columns_4FC].min(axis=1)
df_4FC["Distance Bucket"] = pd.cut(
    df_distance_4FC["smallest distance"],
    bins=distance_buckets,
    labels=bucket_labels,
    right=False
)

df_distance_15FC["smallest distance"] = df_distance_15FC[distance_columns_15FC].min(axis=1)
df_15FC["Distance Bucket"] = pd.cut(
    df_distance_15FC["smallest distance"],
    bins=distance_buckets,
    labels=bucket_labels,
    right=False
)

print("***** Single-FC Network Demand Share by Market Type and Distance Bucket *****\n")
result_bucket_market_1FC = df_1FC.pivot_table(
    index="Market",
    columns="Distance Bucket",
    values="PMF",
    aggfunc="sum",
    fill_value=0
).round(4)
print(result_bucket_market_1FC)
print("\n\n")

print("***** Four-FC Network Demand Share by Market Type and Distance Bucket *****\n")
result_bucket_market_4FC = df_4FC.pivot_table(
    index="Market",
    columns="Distance Bucket",
    values="PMF",
    aggfunc="sum",
    fill_value=0
).round(4)
print(result_bucket_market_4FC)
print("\n\n")

print("***** 15-FC Network Demand Share by Market Type and Distance Bucket *****\n")
result_bucket_market_15FC = df_15FC.pivot_table(
    index="Market",
    columns="Distance Bucket",
    values="PMF",
    aggfunc="sum",
    fill_value=0
).round(4)
print(result_bucket_market_15FC)
print("\n\n")

