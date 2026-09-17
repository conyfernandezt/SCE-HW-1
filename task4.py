import pandas as pd

df_distance_4FC = pd.read_csv("Assignment/fc_zip3_distance.csv")
df_distance_15FC = pd.read_csv("Assignment/fc_zip3_distance.csv")
df_pmf = pd.read_csv("Assignment/zip3_pmf.csv")
df_market = pd.read_csv("Assignment/zip3_market.csv")


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


df_distance_4FC["closest location"] = (
    df_distance_4FC[distance_columns_4FC].idxmin(axis=1)
)

df_distance_15FC["closest location"] = (
    df_distance_15FC[distance_columns_15FC].idxmin(axis=1)
)


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


# create distance buckets
distance_buckets = [0, 51, 151, 301, 601, 1001, 1401, 1801, float("inf")]
bucket_labels = ["0-50", "51-150", "151-300", "301-600", "601-1000", "1001-1400", "1401-1800", "over 1800"]

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


# helper function to be used for checking eligible fcs
def get_bucket(distance):
    if distance <= 50:
        return "0-50"
    elif distance <= 150:
        return "51-150"
    elif distance <= 300:
        return "151-300"
    elif distance <= 600:
        return "301-600"
    elif distance <= 1000:
        return "601-1000"
    elif distance <= 1400:
        return "1001-1400"
    elif distance <= 1800:
        return "1401-1800"
    else:
        return "over 1800"

# identifies eligible fcs for each 3 digit zip
def get_fcs(row, distance_columns):
    bucket = row["Distance Bucket"]
    bucket_index = bucket_labels.index(bucket)

    eligible_buckets = bucket_labels[bucket_index:bucket_index+2]
    eligible_fcs = []

    for fc in distance_columns:
        if get_bucket(row[fc]) in eligible_buckets:
            eligible_fcs.append(fc)
    
    return eligible_fcs

# apply functions to add eligible fcs to each data frame
# 4-FC
df_distance_4FC["Distance Bucket"] = df_4FC["Distance Bucket"]
df_distance_4FC["Eligible FCs"] = df_distance_4FC.apply(get_fcs, axis=1, distance_columns=distance_columns_4FC)
df_4FC["Eligible FCs"] = df_distance_4FC["Eligible FCs"]

# 15-FC
df_distance_15FC["Distance Bucket"] = df_15FC["Distance Bucket"]
df_distance_15FC["Eligible FCs"] = df_distance_15FC.apply(get_fcs, axis=1, distance_columns=distance_columns_15FC)
df_15FC["Eligible FCs"] = df_distance_15FC["Eligible FCs"]