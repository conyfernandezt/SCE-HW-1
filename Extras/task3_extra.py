import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# Load your data
df = pd.read_csv("zip3_coordinates.csv")

# Convert to geographic points
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["Lon"], df["Lat"]),
    crs="EPSG:4326"
)

# Load US states
usa = gpd.read_file(
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/"
    "geojson/ne_110m_admin_1_states_provinces.geojson"
)

# Keep US states
usa = usa[usa["adm0_a3"] == "USA"]

# Plot
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

ax.set_title("ZIP3 Locations Across the United States", fontsize=16)
ax.set_axis_off()

plt.tight_layout()
plt.show()