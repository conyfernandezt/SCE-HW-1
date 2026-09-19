import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import os

data_dir = Path(__file__).resolve().parent / "Assignment"


# ============================================================
# TASK 2 — DEMAND SCENARIOS, SEASONALITY & UNCERTAINTY
# ============================================================
OUTPUT_FOLDER = "task2_outputs"

# ------------------------------------------------------------
# 1. GENERATE 25 GROWTH SCENARIOS
# ------------------------------------------------------------

np.random.seed(42)

n_scenarios = 25

# HELPER FUNCTIONS
def triangular_inverse(u, minimum, mode, maximum):
    """
    Inverse CDF sampling for a triangular distribution.
    """
    
    F_mode = (mode - minimum) / (maximum - minimum)

    if u <= F_mode:
        x = minimum + np.sqrt(
            u * (maximum - minimum) * (mode - minimum)
        )
    else:
        x = maximum - np.sqrt(
            (1 - u) * (maximum - minimum) * (maximum - mode)
        )

    return x

def add_robust_bounds(mean, sigma, mode):
    """Return the mean, mode, standard deviation, and robust bounds."""
    answer = {
        "Mode": mode,
        "Mean": mean,
        "Sigma": sigma
    }

    for level, z in z_values.items():
        answer[f"Robust_{level}_Min"] = max(0, mean - z * sigma)
        answer[f"Robust_{level}_Max"] = mean + z * sigma

    return answer


def demand_mean_and_sigma(annual_mean, annual_second_moment, factors):
    """
    Find the mean and standard deviation after multiplying annual demand
    by uncertain week, day, or ZIP3 factors.

    Each item in factors is written as (mean factor, coefficient of variation).
    """
    factor_mean = 1
    factor_second_moment = 1

    for factor, cv in factors:
        factor_mean *= factor
        factor_second_moment *= factor ** 2 * (1 + cv ** 2)

    mean = annual_mean * factor_mean
    variance = annual_second_moment * factor_second_moment - mean ** 2
    sigma = np.sqrt(max(variance, 0))

    return mean, sigma

# Random numbers for the two growth distributions
u_market = np.random.uniform(0, 1, n_scenarios)
u_share = np.random.uniform(0, 1, n_scenarios)


# Market growth: 4%, 7.5%, 12%
market_growth = np.array([
    triangular_inverse(u, 0.04, 0.075, 0.12)
    for u in u_market
])


# Tsukumo market-share growth: 15%, 20%, 25%
share_growth = np.array([
    triangular_inverse(u, 0.15, 0.20, 0.25)
    for u in u_share
])


# Create scenario table
scenarios = pd.DataFrame({
    "Scenario": range(1, n_scenarios + 1),
    "Market_Growth": market_growth,
    "Tsukumo_Share_Growth": share_growth
})


# ------------------------------------------------------------
# 2. CALCULATE ANNUAL TSUKUMO DEMAND
# ------------------------------------------------------------

current_market_demand = 2_000_000
current_tsukumo_share = 0.036
product_price = 3000
product_weight = 60

# Robustness levels from the assignment
z_values = {
    "68": 1.00,
    "95": 1.65,
    "99": 2.33
}
# Coefficients of variation
week_cv = 0.20
day_cv = 0.15
zip3_cv = 0.15

# Future total market demand
scenarios["Future_Market_Demand"] = (
    current_market_demand
    * (1 + scenarios["Market_Growth"])
)


# Future Tsukumo market share
scenarios["Future_Tsukumo_Share"] = (
    current_tsukumo_share
    * (1 + scenarios["Tsukumo_Share_Growth"])
)


# Annual Tsukumo demand
scenarios["Annual_Tsukumo_Demand"] = (
    scenarios["Future_Market_Demand"]
    * scenarios["Future_Tsukumo_Share"]
)


print("\n25 Growth Scenarios")
print(scenarios)


# ------------------------------------------------------------
# 3. LOAD ACTUAL SEASONALITY DATA
# ------------------------------------------------------------

seasonality = pd.read_csv(
    data_dir / "demand_seasonalities.csv"
)


# IMPORTANT:
# Check the column names in your Excel file
print("\nSeasonality columns:")
print(seasonality.columns)


# Week-of-year proportions
week_factors = (
    seasonality["Proportion"].dropna().str.rstrip("%").astype(float).to_numpy()
    / 100
)


# Day-of-week proportions
day_factors = (
    seasonality["Proportion.1"].dropna().str.rstrip("%").astype(float).to_numpy()
    / 100
)


print("\nNumber of weeks:", len(week_factors))
print("Number of days:", len(day_factors))

print("\nSum of week proportions:",
      week_factors.sum())

print("Sum of day proportions:",
      day_factors.sum())


# ------------------------------------------------------------
# 4. LOAD ZIP3 DEMAND-SHARE PMF
# ------------------------------------------------------------

zip3_pmf = pd.read_csv(
    data_dir / "zip3_pmf.csv"
)

zip3_market = pd.read_csv(
    data_dir / "zip3_market.csv"
)

# Clean ZIP3 so leading zeros are not lost.
zip3_pmf["ZIP3"] = (
    zip3_pmf["ZIP3"].astype(str).str.replace(".0", "", regex=False).str.zfill(3)
)

zip3_market["ZIP3"] = (
    zip3_market["ZIP3"].astype(str).str.replace(".0", "", regex=False).str.zfill(3)
)

# Normalize the PMF so it adds to one.
zip3_pmf["PMF"] = zip3_pmf["PMF"] / zip3_pmf["PMF"].sum()

# Join the PMF to state and market type.
# ZIP3s without a PMF receive zero demand, as stated in the case.
zip3_data = zip3_market.merge(zip3_pmf, on="ZIP3", how="left")
zip3_data["PMF"] = zip3_data["PMF"].fillna(0)

# Accept either "Market Type" or "Market_Type" as the column name.
if "Market Type" in zip3_data.columns:
    zip3_data = zip3_data.rename(columns={"Market Type": "Market_Type"})


print("\nZIP3 PMF")
print(zip3_pmf.head())

print("Number of ZIP3s:",
      len(zip3_pmf))

print("PMF sum:",
      zip3_pmf["PMF"].sum())


# ------------------------------------------------------------
# 6. MEAN AND VARIANCE OF ANNUAL DEMAND
# ------------------------------------------------------------

annual_demand_mean = (
    scenarios["Annual_Tsukumo_Demand"].mean()
)


annual_demand_second_moment = (
    scenarios["Annual_Tsukumo_Demand"] ** 2
).mean()


annual_demand_variance = (
    annual_demand_second_moment
    - annual_demand_mean ** 2
)

# The mode uses the mode of both triangular growth distributions.
annual_mode = (
    current_market_demand
    * (1 + 0.075)
    * current_tsukumo_share
    * (1 + 0.20)
)

annual_demand_std = np.sqrt(
    annual_demand_variance
)

annual_summary = pd.DataFrame([{
    "Metric": "Annual Tsukumo Demand",
    **add_robust_bounds(annual_demand_mean, annual_demand_std, annual_mode),
    "Variability_Included": "Market growth + Tsukumo share growth"
}])

print("\nAnnual Demand Statistics")

print("Mean:",
      annual_demand_mean)

print("Standard deviation:",
      annual_demand_std)

# ------------------------------------------------------------
# 5. WEEKLY AND DAILY NATIONAL DEMAND
# ------------------------------------------------------------

weekly_rows = []

for week_number, week_factor in enumerate(week_factors, start=1):
    mean, sigma = demand_mean_and_sigma(
        annual_demand_mean,
        annual_demand_second_moment,
        [(week_factor, week_cv)]
    )

    weekly_rows.append({
        "Week": week_number,
        "Week_Factor": week_factor,
        **add_robust_bounds(
            mean,
            sigma,
            annual_mode * week_factor
        ),
        "Variability_Included": (
            "Market growth + Tsukumo share growth + week seasonality"
        )
    })

weekly_summary = pd.DataFrame(weekly_rows)


daily_rows = []
day_of_year = 0

for week_number, week_factor in enumerate(week_factors, start=1):
    for day_number, day_factor in enumerate(day_factors, start=1):
        day_of_year += 1

        mean, sigma = demand_mean_and_sigma(
            annual_demand_mean,
            annual_demand_second_moment,
            [
                (week_factor, week_cv),
                (day_factor, day_cv)
            ]
        )

        daily_rows.append({
            "Day_of_Year": day_of_year,
            "Week": week_number,
            "Day": day_number,
            "Week_Factor": week_factor,
            "Day_Factor": day_factor,
            **add_robust_bounds(
                mean,
                sigma,
                annual_mode
                * week_factor
                * day_factor
            ),
            "Variability_Included": (
                "Market growth + Tsukumo share growth + "
                "week seasonality + day seasonality"
            )
        })

daily_summary = pd.DataFrame(daily_rows)

# ------------------------------------------------------------
# 6. ANNUAL DEMAND BY MARKET TYPE AND STATE
# ------------------------------------------------------------

def make_geographic_summary(group_column):
    rows = []

    for group_name, group in zip3_data.groupby(group_column):
        demand_share = group["PMF"].sum()

        # ZIP3 errors are treated as independent, so their variances add.
        share_variance = ((zip3_cv * group["PMF"]) ** 2).sum()
        share_second_moment = demand_share ** 2 + share_variance

        mean = annual_demand_mean * demand_share
        variance = (
            annual_demand_second_moment * share_second_moment
            - mean ** 2
        )
        sigma = np.sqrt(max(variance, 0))

        row = {
            group_column: group_name,
            "Expected_Demand_Share": demand_share,
            **add_robust_bounds(
                mean,
                sigma,
                annual_mode * demand_share
            ),
            "Variability_Included": (
                "Market growth + Tsukumo share growth + ZIP3 PMF"
            )
        }

        rows.append(row)

    result = pd.DataFrame(rows)
    return result.sort_values("Mean", ascending=False)


market_type_summary = make_geographic_summary("Market")
state_summary = make_geographic_summary("State")


# Add revenue and weight columns to the geographic results.
measure_columns = [
    "Mode",
    "Mean",
    "Sigma",
    "Robust_68_Min",
    "Robust_68_Max",
    "Robust_95_Min",
    "Robust_95_Max",
    "Robust_99_Min",
    "Robust_99_Max"
]

for column in measure_columns:
    market_type_summary[column + "_Revenue"] = (
        market_type_summary[column] * product_price
    )
    market_type_summary[column + "_Weight_lb"] = (
        market_type_summary[column] * product_weight
    )

    state_summary[column + "_Revenue"] = (
        state_summary[column] * product_price
    )
    state_summary[column + "_Weight_lb"] = (
        state_summary[column] * product_weight
    )


# ------------------------------------------------------------
# 7. SMALL ROBUSTNESS SUMMARY FOR THE REPORT
# ------------------------------------------------------------

robustness_rows = []

robustness_rows.append(annual_summary.iloc[0].to_dict())


def add_peak_row(data, metric_name, multiplier, variability):
    row = {
        "Metric": metric_name,
        "Variability_Included": variability
    }

    for column in measure_columns:
        row[column] = data[column].max() * multiplier

    robustness_rows.append(row)


add_peak_row(
    weekly_summary,
    "Peak Weekly Demand (units)",
    1,
    "Market growth + Tsukumo share growth + week seasonality"
)

daily_variability = (
    "Market growth + Tsukumo share growth + "
    "week seasonality + day seasonality"
)

add_peak_row(
    daily_summary,
    "Peak Daily Demand (units)",
    1,
    daily_variability
)

add_peak_row(
    daily_summary,
    "Peak Daily Weight (lb)",
    product_weight,
    daily_variability
)

robustness_summary = pd.DataFrame(robustness_rows)


# ------------------------------------------------------------
# 8. SAVE THE COMPACT TABLES
# ------------------------------------------------------------

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

scenarios_for_output = scenarios.copy()
scenarios_for_output["Market_Growth"] *= 100
scenarios_for_output["Tsukumo_Share_Growth"] *= 100
scenarios_for_output["Future_Tsukumo_Share"] *= 100

scenarios_for_output = scenarios_for_output.rename(columns={
    "Market_Growth": "Market_Growth_Percent",
    "Tsukumo_Share_Growth": "Tsukumo_Share_Growth_Percent",
    "Future_Tsukumo_Share": "Future_Tsukumo_Share_Percent"
})

variability_sources = pd.DataFrame({
    "Result": [
        "Annual national demand",
        "Annual demand by market type or state",
        "Weekly national demand",
        "Daily national demand",
        "Optional daily ZIP3 demand"
    ],
    "Variability_Included": [
        "Market growth + Tsukumo share growth",
        "Market growth + Tsukumo share growth + ZIP3 PMF",
        "Market growth + Tsukumo share growth + week seasonality",
        "Market growth + Tsukumo share growth + week seasonality + day seasonality",
        "Market growth + Tsukumo share growth + week seasonality + day seasonality + ZIP3 PMF"
    ]
})

output_tables = {
    "01_scenario_summary.csv": scenarios_for_output,
    "02_annual_national_demand.csv": annual_summary,
    "03_annual_demand_by_market_type.csv": market_type_summary,
    "04_annual_demand_revenue_by_state.csv": state_summary,
    "05_weekly_national_demand.csv": weekly_summary,
    "06_daily_national_demand.csv": daily_summary,
    "07_robustness_summary.csv": robustness_summary,
    "08_variability_sources.csv": variability_sources
}

for file_name, table in output_tables.items():
    table.to_csv(
        os.path.join(OUTPUT_FOLDER, file_name),
        index=False
    )


# Put all of the small tables into one Excel workbook too.
with pd.ExcelWriter(
    os.path.join(OUTPUT_FOLDER, "Task2_report_tables.xlsx")
) as writer:
    scenarios_for_output.to_excel(writer, sheet_name="Scenarios", index=False)
    annual_summary.to_excel(writer, sheet_name="Annual National", index=False)
    market_type_summary.to_excel(writer, sheet_name="Market Type", index=False)
    state_summary.to_excel(writer, sheet_name="State", index=False)
    weekly_summary.to_excel(writer, sheet_name="Weekly", index=False)
    daily_summary.to_excel(writer, sheet_name="Daily", index=False)
    robustness_summary.to_excel(writer, sheet_name="Robustness", index=False)
    variability_sources.to_excel(writer, sheet_name="Variability", index=False)



# ------------------------------------------------------------
# 7. COMBINE SEASONALITY + ZIP3 UNCERTAINTY
# ------------------------------------------------------------

uncertainty_multiplier = (
    (1 + week_cv ** 2)
    * (1 + day_cv ** 2)
    * (1 + zip3_cv ** 2)
)


# ------------------------------------------------------------
# 8. CALCULATE DEMAND FOR EACH
#    WEEK × DAY × ZIP3
# ------------------------------------------------------------

results = []


for week in range(52):

    for day in range(7):

        for _, zip_row in zip3_pmf.iterrows():

            week_factor = week_factors[week]
            day_factor = day_factors[day]
            zip_factor = zip_row["PMF"]


            # Expected demand
            mean_demand = (
                annual_demand_mean
                * week_factor
                * day_factor
                * zip_factor
            )


            # Combined variance
            variance = (
                (week_factor
                 * day_factor
                 * zip_factor) ** 2
                *
                (
                    annual_demand_second_moment
                    * uncertainty_multiplier
                    - annual_demand_mean ** 2
                )
            )


            sigma = np.sqrt(
                max(variance, 0)
            )


            results.append({
                "Week": week + 1,
                "Day": day + 1,
                "ZIP3": zip_row["ZIP3"],
                "Mean_Demand": mean_demand,
                "Sigma": sigma
            })


results = pd.DataFrame(results)


# ------------------------------------------------------------
# 10. VIEW RESULTS
# ------------------------------------------------------------

print("\nFinal Demand Results")
print(results.head(20))


# ------------------------------------------------------------
# 11. SAVE RESULTS
# ------------------------------------------------------------

results.to_csv(
    "task2_demand_results.csv",
    index=False
)

scenarios.to_csv(
    "task2_growth_scenarios.csv",
    index=False
)


print("\nDone!")
print("Results saved as:")
print("- task2_demand_results.csv")
print("- task2_growth_scenarios.csv")
