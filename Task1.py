# ============================================================
# TSUKUMO CONSERVATIVE MARKET DEMAND ANALYSIS
#
# Requested aggregations:
# Y-B-# : Yearly  x Market Type x Units
# M-C-# : Monthly x State       x Units
# Y-C-$ : Yearly  x State       x Dollars
# D-D-W : Daily   x ZIP3        x Weight
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# 1. INPUTS / ASSUMPTIONS
# ============================================================

CURRENT_US_MARKET = 2_000_000

# Conservative overall market growth scenario
MARKET_GROWTH = 0.04

# Conservative Tsukumo share-growth scenario
CURRENT_TSUKUMO_SHARE = 0.036
TSUKUMO_SHARE_GROWTH = 0.15

AVG_PRICE = 3_000       # $ / unit
AVG_WEIGHT = 60         # lb / unit
AVG_VOLUME = 3 * 2 * 2  # 12 ft^3 / unit

MONTHS_PER_YEAR = 12
DAYS_PER_YEAR = 365


# ============================================================
# 2. NATIONAL TSUKUMO FORECAST
# ============================================================

next_year_market = CURRENT_US_MARKET * (1 + MARKET_GROWTH)

next_year_tsukumo_share = (
    CURRENT_TSUKUMO_SHARE * (1 + TSUKUMO_SHARE_GROWTH)
)

tsukumo_annual_units = (
    next_year_market * next_year_tsukumo_share
)

tsukumo_annual_revenue = (
    tsukumo_annual_units * AVG_PRICE
)

tsukumo_annual_weight = (
    tsukumo_annual_units * AVG_WEIGHT
)

print("=" * 55)
print("TSUKUMO CONSERVATIVE FORECAST")
print("=" * 55)

print(f"Next-year U.S. market:      {next_year_market:,.0f} units")
print(f"Next-year Tsukumo share:    {next_year_tsukumo_share:.2%}")
print(f"Tsukumo annual demand:      {tsukumo_annual_units:,.0f} units")
print(f"Tsukumo annual revenue:     ${tsukumo_annual_revenue:,.0f}")
print(f"Tsukumo annual weight:      {tsukumo_annual_weight:,.0f} lb")

# ============================================================
# 3. LOAD THE PROVIDED CSV FILES
# ============================================================

from pathlib import Path

market = pd.read_csv("Assignment/zip3_market.csv")
market["ZIP3"] = market["ZIP3"].astype(str)
pmf = pd.read_csv("Assignment/zip3_pmf.csv")
pmf["ZIP3"] = pmf["ZIP3"].astype(str)
msa = pd.read_csv("Assignment/msa.csv")
msa["3-digit ZIP code"] = msa["3-digit ZIP code"].astype(str)

# Preserve three-digit ZIP formatting
market["ZIP3"] = market["ZIP3"].str.zfill(3)
pmf["ZIP3"] = pmf["ZIP3"].str.zfill(3)
msa["3-digit ZIP code"] = msa["3-digit ZIP code"].str.zfill(3)


print("zip3_market.csv:")
print(market.head())

print("\nzip3_pmf.csv:")
print(pmf.head())

print("\nmsa.csv:")
print(msa.head())

# ============================================================
# 4. BUILD THE GEOGRAPHIC DEMAND TABLE
# ============================================================

geo = market.merge(
    pmf,
    on="ZIP3",
    how="left"
)

# Case instruction:
# ZIP3s missing from zip3_pmf.csv receive zero demand share
geo["PMF"] = geo["PMF"].fillna(0)


# The provided PMFs total 0.999999119 because of rounding.
# Normalize by the tiny rounding difference so that geographic
# demand sums exactly to the national Tsukumo forecast.
geo["PMF_Normalized"] = (
    geo["PMF"] / geo["PMF"].sum()
)

print(f"Original merged PMF sum:   {geo['PMF'].sum():.9f}")
print(f"Normalized PMF sum:        {geo['PMF_Normalized'].sum():.9f}")

# ============================================================
# 6. CALCULATE DEMAND AT ZIP3 LEVEL
# ============================================================

geo["Annual_Units"] = (
    tsukumo_annual_units * geo["PMF_Normalized"]
)

# No seasonality
geo["Monthly_Units"] = (
    geo["Annual_Units"] / MONTHS_PER_YEAR
)

geo["Daily_Units"] = (
    geo["Annual_Units"] / DAYS_PER_YEAR
)


# Monetary measure
geo["Annual_Dollars"] = (
    geo["Annual_Units"] * AVG_PRICE
)


# Weight measure
geo["Annual_Weight_lb"] = (
    geo["Annual_Units"] * AVG_WEIGHT
)

geo["Daily_Weight_lb"] = (
    geo["Daily_Units"] * AVG_WEIGHT
)


# Optional volume measures
geo["Annual_Volume_ft3"] = (
    geo["Annual_Units"] * AVG_VOLUME
)

geo["Daily_Volume_ft3"] = (
    geo["Annual_Volume_ft3"] / DAYS_PER_YEAR
)


# Validation
print(
    f"Allocated annual units: "
    f"{geo['Annual_Units'].sum():,.2f}"
)

print(
    f"National forecast units: "
    f"{tsukumo_annual_units:,.2f}"
)

# ============================================================
# 5. Y-B-# : YEARLY x MARKET TYPE x UNITS
# ============================================================

Y_B_units = (
    geo.groupby("Market", as_index=False)
    .agg(
        Annual_Units=("Annual_Units", "sum"),
        Demand_Share=("PMF_Normalized", "sum")
    )
    .sort_values(
        "Annual_Units",
        ascending=False
    )
)

print("\nY-B-# : YEARLY UNITS BY MARKET TYPE")
print(
    Y_B_units.to_string(
        index=False,
        formatters={
            "Annual_Units": "{:,.0f}".format,
            "Demand_Share": "{:.2%}".format
        }
    )
)

fig, ax = plt.subplots(figsize=(8, 5))

plot_data = Y_B_units.sort_values(
    "Annual_Units"
)

bars = ax.barh(
    plot_data["Market"],
    plot_data["Annual_Units"]
)

ax.set_title(
    "Tsukumo Conservative Annual Demand by Market Type"
)
ax.set_xlabel("Annual Units")
ax.set_ylabel("Market Type")

for bar in bars:
    value = bar.get_width()

    ax.text(
        value,
        bar.get_y() + bar.get_height() / 2,
        f" {value:,.0f}",
        va="center"
    )

plt.tight_layout()
plt.show()

# ============================================================
# 6. M-C-# : MONTHLY x STATE x UNITS
# ============================================================

state_units = (
    geo.groupby("State", as_index=False)
    .agg(
        Annual_Units=("Annual_Units", "sum")
    )
)

state_units["Monthly_Units"] = (
    state_units["Annual_Units"] / 12
)

state_units = state_units.sort_values(
    "Monthly_Units",
    ascending=False
)

print("\nAVERAGE MONTHLY UNITS BY STATE")
print(
    state_units.head(20).to_string(
        index=False,
        formatters={
            "Annual_Units": "{:,.1f}".format,
            "Monthly_Units": "{:,.1f}".format
        }
    )
)

top15_states = (
    state_units
    .head(15)
    .sort_values("Monthly_Units")
)

fig, ax = plt.subplots(figsize=(9, 7))

bars = ax.barh(
    top15_states["State"],
    top15_states["Monthly_Units"]
)

ax.set_title(
    "Average Monthly Tsukumo Demand — Top 15 States"
)
ax.set_xlabel("Units per Month")
ax.set_ylabel("State")

for bar in bars:
    value = bar.get_width()

    ax.text(
        value,
        bar.get_y() + bar.get_height() / 2,
        f" {value:,.0f}",
        va="center"
    )

plt.tight_layout()
plt.show()

# ============================================================
# 7. Y-C-$ : YEARLY x STATE x DOLLARS
# ============================================================

Y_C_dollars = (
    geo.groupby("State", as_index=False)
    .agg(
        Annual_Units=("Annual_Units", "sum"),
        Annual_Dollars=("Annual_Dollars", "sum"),
        Demand_Share=("PMF_Normalized", "sum")
    )
    .sort_values(
        "Annual_Dollars",
        ascending=False
    )
)

print("\nY-C-$ : YEARLY REVENUE BY STATE")

print(
    Y_C_dollars.head(20).to_string(
        index=False,
        formatters={
            "Annual_Units": "{:,.0f}".format,
            "Annual_Dollars": "${:,.0f}".format,
            "Demand_Share": "{:.2%}".format
        }
    )
)

top15_revenue = (
    Y_C_dollars
    .head(15)
    .sort_values("Annual_Dollars")
)

fig, ax = plt.subplots(figsize=(9, 7))

bars = ax.barh(
    top15_revenue["State"],
    top15_revenue["Annual_Dollars"] / 1_000_000
)

ax.set_title(
    "Tsukumo Annual Revenue — Top 15 States"
)
ax.set_xlabel("Annual Revenue ($ Millions)")
ax.set_ylabel("State")

for bar in bars:
    value = bar.get_width()

    ax.text(
        value,
        bar.get_y() + bar.get_height() / 2,
        f" ${value:,.1f}M",
        va="center"
    )

plt.tight_layout()
plt.show()

# ============================================================
# 8. D-D-W : DAILY x ZIP3 x WEIGHT
# ============================================================

D_D_weight = (
    geo[
        [
            "ZIP3",
            "State",
            "Market",
            "PMF_Normalized",
            "Daily_Units",
            "Daily_Weight_lb"
        ]
    ]
    .sort_values(
        "Daily_Weight_lb",
        ascending=False
    )
    .reset_index(drop=True)
)

print("\nD-D-W : DAILY WEIGHT BY ZIP3")

print(
    D_D_weight.head(20).to_string(
        index=False,
        formatters={
            "PMF_Normalized": "{:.3%}".format,
            "Daily_Units": "{:,.2f}".format,
            "Daily_Weight_lb": "{:,.1f}".format
        }
    )
)

top20_zip = (
    D_D_weight
    .head(20)
    .sort_values("Daily_Weight_lb")
)

fig, ax = plt.subplots(figsize=(9, 8))

bars = ax.barh(
    top20_zip["ZIP3"],
    top20_zip["Daily_Weight_lb"]
)

ax.set_title(
    "Average Daily Shipment Weight — Top 20 ZIP3 Markets"
)
ax.set_xlabel("Weight per Day (lb)")
ax.set_ylabel("3-Digit ZIP")

for bar in bars:
    value = bar.get_width()

    ax.text(
        value,
        bar.get_y() + bar.get_height() / 2,
        f" {value:,.0f} lb",
        va="center"
    )

plt.tight_layout()
plt.show()
