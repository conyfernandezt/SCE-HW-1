import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


df = pd.read_csv("Assignment/zip3_coordinates.csv")

df_distance = pd.read_csv("Assignment/fc_zip3_distance.csv")

distance_columns = ["GA-303", "NY-134", "TX-799", "UT-841", "AZ-852", "CA-900", "CA-945", "CO-802", "FL-331", "IL-606", "MA-021", "MI-481", "NC-275", "NJ-070", "TX-750", "TX-770", "WA-980"]

df_distance["closest_location"] = df_distance[distance_columns].idxmin(axis=1)


df_map = df.merge(
    df_distance[["ZIP3", "closest_location"]],
    on="ZIP3"
)

gdf = gpd.GeoDataFrame(
    df_map,
    geometry=gpd.points_from_xy(df_map["Lon"], df_map["Lat"]),
    crs="EPSG:4326"
)

usa = gpd.read_file(
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/"
    "geojson/ne_110m_admin_1_states_provinces.geojson"
)

usa = usa[usa["adm0_a3"] == "USA"]

fig, ax = plt.subplots(figsize=(14, 9))

usa.plot(
    ax=ax,
    edgecolor="black",
    facecolor="white",
    linewidth=0.5
)


for location in distance_columns:
    
    subset = gdf[gdf["closest_location"] == location]
    
    subset.plot(
        ax=ax,
        markersize=15,
        alpha=0.7,
        label=location
    )


ax.set_title(
    "ZIP3 Areas by Closest Location",
    fontsize=16
)

ax.legend(title="Closest Location")

ax.set_axis_off()

plt.tight_layout()
plt.show()
