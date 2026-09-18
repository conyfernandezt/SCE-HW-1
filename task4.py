import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import colors as mcolors

df_coordinates = pd.read_csv("Assignment/zip3_coordinates.csv")
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


# task 4a

df_4c = df_4FC.merge(df_coordinates, left_on="ZIP3", right_on="ZIP3", how="left")

df_15FC = df_15FC.merge(df_coordinates, left_on="ZIP3", right_on="ZIP3", how="left")

gdf_4c = gpd.GeoDataFrame(
    df_4c, geometry=gpd.points_from_xy(df_4c['Lon'], df_4c['Lat']), crs="EPSG:4326")

gdf_15FC = gpd.GeoDataFrame(
    df_15FC, geometry=gpd.points_from_xy(df_15FC['Lon'], df_15FC['Lat']), crs="EPSG:4326")

usa = gpd.read_file(
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/"
    "geojson/ne_110m_admin_1_states_provinces.geojson"
)

usa = usa[usa["adm0_a3"] == "USA"]


fc_base_colors = {
    "GA-303": "#1f77b4", 
    "NY-134": "#ff7f0e",   
    "TX-799": "#2ca02c",  
    "UT-841": "#9467bd",
    "AZ-852": "#d62728",
    "CA-900": "#8c564b",
    "CA-945": "#17becf",
    "CO-802": "#bcbd22",
    "FL-331": "#e377c2",
    "IL-606": "#7f7f7f",
    "MA-021": "#1f9e89",
    "MI-481": "#e6550d",
    "NC-275": "#756bb1",
    "NJ-070": "#31a354",
    "TX-750": "#636363",
    "TX-770": "#9c9ede",
    "WA-980": "#6baed6"
}

def plot_map(gdf, title, fc_list):
    fig, ax = plt.subplots(figsize=(14, 9))

    usa.plot(
        ax=ax,
        edgecolor="black",
        facecolor="white",
        linewidth=0.5
    )

    gdf = gdf[
        gdf.geometry.notna() &
        ~gdf.geometry.is_empty
    ].copy()

    for fc in fc_list:

        fc_subset = gdf[gdf["closest location"] == fc]

        for i, bucket in enumerate(bucket_labels):

            subset = fc_subset[
                fc_subset["Distance Bucket"] == bucket
            ]

            if subset.empty:
                continue

            # Create a color from the FC's base color
            base_color = fc_base_colors[fc]

            # Make different shades
            # i = 0 → darkest
            # i = 7 → lightest

            import matplotlib.colors as mcolors

            rgb = mcolors.to_rgb(base_color)

            intensity = 0.2 + (i / len(bucket_labels)) * 0.7

            if i <= 2:
                intensity = 1       # super dark
            elif i <= 4:
                intensity = 0.65       # normal
            else:
                intensity = 0.2      # super light


            color = tuple(
                1 - intensity * (1 - c)
                for c in rgb
            )

            subset.plot(
                ax=ax,
                markersize=15,
                alpha=0.8,
                color=color
            )

    ax.set_title(
    title,
    fontsize=16
    )

    ax.set_axis_off()

    plt.tight_layout()
    plt.savefig(
        f"Assignment/{title}.png",
        dpi=300,
        bbox_inches="tight"
    )
    plt.show()

plot_map(gdf_4c, "4-FC ZIP3 Buckets Across the United States", distance_columns_4FC)
plot_map(gdf_15FC, "15-FC ZIP3 Buckets Across the United States", distance_columns_15FC)

# task 4b

df_4c["Number of FCs"] = df_4c["Eligible FCs"].apply(len)
df_15FC["Number of FCs"] = df_15FC["Eligible FCs"].apply(len)



gdf_4b = gpd.GeoDataFrame(
    df_4c,
    geometry=gpd.points_from_xy(
        df_4c["Lon"],
        df_4c["Lat"]
    ),
    crs="EPSG:4326"
)

gdf_15b = gpd.GeoDataFrame(
    df_15FC,
    geometry=gpd.points_from_xy(
        df_15FC["Lon"],
        df_15FC["Lat"]
    ),
    crs="EPSG:4326"
)


def plot_number_fcs(gdf, title):

    fig, ax = plt.subplots(figsize=(14, 9))

    # Plot US map
    usa.plot(
        ax=ax,
        edgecolor="black",
        facecolor="white",
        linewidth=0.5
    )

    # Remove ZIP3s without coordinates
    gdf = gdf[
        gdf.geometry.notna() &
        ~gdf.geometry.is_empty
    ].copy()

    # Red -> Yellow -> Green
    cmap = LinearSegmentedColormap.from_list(
        "red_yellow_green",
        ["red", "yellow", "green"]
    )

    # Determine range of number of eligible FCs
    min_fcs = gdf["Number of FCs"].min()
    max_fcs = gdf["Number of FCs"].max()

    norm = mcolors.Normalize(
        vmin=min_fcs,
        vmax=max_fcs
    )

    # Plot ZIP3s
    gdf.plot(
        ax=ax,
        column="Number of FCs",
        cmap=cmap,
        norm=norm,
        markersize=15,
        alpha=0.8
    )

    # Add colorbar
    sm = plt.cm.ScalarMappable(
        cmap=cmap,
        norm=norm
    )
    sm.set_array([])

    cbar = fig.colorbar(
        sm,
        ax=ax,
        shrink=0.7
    )

    cbar.set_label(
        "Number of FCs that can serve the ZIP3",
        fontsize=12
    )

    ax.set_title(
        title,
        fontsize=16
    )

    ax.set_axis_off()

    plt.tight_layout()

    plt.savefig(
        f"Assignment/{title}.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()


plot_number_fcs(gdf_4b, "Number of Eligible FCs for 4-FC Network")
plot_number_fcs(gdf_15b, "Number of Eligible FCs for 15-FC Network")


# task 4c
print("\n *** Task 4c ***\n\n")
# calculate total demand share of zips that are only served by a single FC
# we'll call these "exclusive zips"
exclusive_demand_4FC = df_4FC.loc[df_4FC["Eligible FCs"].str.len()==1, "PMF"].sum().round(4)
print("Single-FC Exclusive Demand for 4-FC Network: " + str(exclusive_demand_4FC) + "\n")

exclusive_demand_15FC = df_15FC.loc[df_15FC["Eligible FCs"].str.len()==1, "PMF"].sum().round(4)
print("Single-FC Exclusive Demand for 15-FC Network: " + str(exclusive_demand_15FC) + "\n")


# task 4d
print("\n *** Task 4d ***\n\n")
# dictionary to hold demand share of each bucket
bucket_demand_dict_4FC = {
    "0-50": 0,
    "51-150": 0,
    "151-300": 0,
    "301-600": 0,
    "601-1000": 0,
    "1001-1400": 0,
    "1401-1800": 0,
    "over 1800": 0
}

df_distance_4FC["PMF"] = df_4FC["PMF"]
clean_df_distance_4FC = df_distance_4FC.rename(columns=lambda x: x.replace("-", "_"))
clean_df_distance_4FC.columns = clean_df_distance_4FC.columns.str.lower().str.replace(" ", "_")
clean_df_distance_4FC["eligible_fcs"] = clean_df_distance_4FC["eligible_fcs"].apply(
    lambda fcs: [fc.replace("-", "_") for fc in fcs]
)

# loop thru each row
for row in clean_df_distance_4FC.itertuples():
    num_eligible_fcs = len(row.eligible_fcs)
    # if only one eligible FC, add 100% of demand
    if num_eligible_fcs == 1:
        bucket_demand_dict_4FC[row.distance_bucket] += row.pmf
    # otherwise, 80% to closest FC, 20% split among the rest
    else:
        bucket_demand_dict_4FC[row.distance_bucket] += (0.8*row.pmf)
        for fc in row.eligible_fcs[1:]:
            current_bucket = get_bucket(getattr(row, fc.lower()))
            bucket_demand_dict_4FC[current_bucket] += ((0.2/(num_eligible_fcs-1)) * row.pmf)

print("Demand Distribution across Distance Buckets under Fulfillment Rule (4-FC Network):\n")
print("Bucket  :  Demand\n")
for bucket, demand in bucket_demand_dict_4FC.items():
    print(f"{bucket}: {round(demand, 4)}")
print("\n\n")
# repeat for 15-FC
# dictionary to hold demand share of each bucket
bucket_demand_dict_15FC = {
    "0-50": 0,
    "51-150": 0,
    "151-300": 0,
    "301-600": 0,
    "601-1000": 0,
    "1001-1400": 0,
    "1401-1800": 0,
    "over 1800": 0
}

df_distance_15FC["PMF"] = df_15FC["PMF"]
clean_df_distance_15FC = df_distance_15FC.rename(columns=lambda x: x.replace("-", "_"))
clean_df_distance_15FC.columns = clean_df_distance_15FC.columns.str.lower().str.replace(" ", "_")
clean_df_distance_15FC["eligible_fcs"] = clean_df_distance_15FC["eligible_fcs"].apply(
    lambda fcs: [fc.replace("-", "_") for fc in fcs]
)

# loop thru each row
for row in clean_df_distance_15FC.itertuples():
    num_eligible_fcs = len(row.eligible_fcs)
    # if only one eligible FC, add 100% of demand
    if num_eligible_fcs == 1:
        bucket_demand_dict_15FC[row.distance_bucket] += row.pmf
    # otherwise, 80% to closest FC, 20% split among the rest
    else:
        bucket_demand_dict_15FC[row.distance_bucket] += (0.8*row.pmf)
        for fc in row.eligible_fcs[1:]:
            current_bucket = get_bucket(getattr(row, fc.lower()))
            bucket_demand_dict_15FC[current_bucket] += ((0.2/(num_eligible_fcs-1)) * row.pmf)

print("Demand Distribution across Distance Buckets under Fulfillment Rule (15-FC Network):\n")
print("Bucket  :  Demand\n")
for bucket, demand in bucket_demand_dict_15FC.items():
    print(f"{bucket}: {round(demand, 4)}")
print("\n\n")