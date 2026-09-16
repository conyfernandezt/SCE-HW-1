import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


df = pd.read_csv("Assignment/zip3_coordinates.csv")

df_distance = pd.read_csv("Assignment/fc_zip3_distance.csv")


# All fulfillment centers
distance_columns = [
    "GA-303",
    "NY-134",
    "TX-799",
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

# Fulfillment centers for the subgroup network
distance_columns_subgroup = [
    "GA-303",
    "NY-134",
    "TX-799",
    "UT-841"
]


df_distance["closest_location"] = (
    df_distance[distance_columns].idxmin(axis=1)
)

df_distance_subgroup = df_distance[
    ["ZIP3"] + distance_columns_subgroup
].copy()


df_distance_subgroup["closest_location_subgroup"] = (
    df_distance_subgroup[distance_columns_subgroup].idxmin(axis=1)
)


df_map = df.merge(
    df_distance[["ZIP3", "closest_location"]],
    on="ZIP3"
)

df_map = df_map.merge(
    df_distance_subgroup[
        ["ZIP3", "closest_location_subgroup"]
    ],
    on="ZIP3"
)

gdf = gpd.GeoDataFrame(
    df_map,
    geometry=gpd.points_from_xy(
        df_map["Lon"],
        df_map["Lat"]
    ),
    crs="EPSG:4326"
)


usa = gpd.read_file(
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/"
    "geojson/ne_110m_admin_1_states_provinces.geojson"
)

usa = usa[usa["adm0_a3"] == "USA"]



# Map 1 — All ZIP3 locations


fig, ax = plt.subplots(figsize=(14, 9))

usa.plot(
    ax=ax,
    edgecolor="black",
    facecolor="white",
    linewidth=0.5
)

gdf.plot(
    ax=ax,
    markersize=12,
    alpha=0.6
)

ax.set_title(
    "ZIP3 Locations Across the United States",
    fontsize=16
)

ax.set_axis_off()

plt.tight_layout()
plt.savefig(
    "Assignment/network.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()


# Map 2 — 4 FC network


fig, ax = plt.subplots(figsize=(14, 9))


usa.plot(
    ax=ax,
    edgecolor="black",
    facecolor="white",
    linewidth=0.5
)


for location in distance_columns_subgroup:

    subset = gdf[
        gdf["closest_location_subgroup"] == location
    ]

    subset.plot(
        ax=ax,
        markersize=15,
        alpha=0.7,
        label=location
    )


ax.set_title(
    "ZIP3 Areas by Closest FC — 4 FC Network",
    fontsize=16
)

ax.legend(title="Closest Fulfillment Center")

ax.set_axis_off()

plt.tight_layout()
plt.savefig(
    "Assignment/4_FC_network.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()


# Map 3 — all FC network


fig, ax = plt.subplots(figsize=(14, 9))

usa.plot(
    ax=ax,
    edgecolor="black",
    facecolor="white",
    linewidth=0.5
)


for location in distance_columns:

    subset = gdf[
        gdf["closest_location"] == location
    ]

    subset.plot(
        ax=ax,
        markersize=15,
        alpha=0.7,
        label=location
    )


ax.set_title(
    "ZIP3 Areas by Closest FC — All FC Network",
    fontsize=16
)

ax.legend(
    title="Closest Fulfillment Center",
    bbox_to_anchor=(1.05, 1),
    loc="upper left"
)

ax.set_axis_off()

plt.tight_layout()
plt.savefig(
    "Assignment/all_FC_network.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()