import numpy as np
import pandas as pd


# ============================================================
# TASK 2 — DEMAND SCENARIOS, SEASONALITY & UNCERTAINTY
# ============================================================


# ------------------------------------------------------------
# 1. GENERATE 25 GROWTH SCENARIOS
# ------------------------------------------------------------

np.random.seed(42)

n_scenarios = 25


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

seasonality = pd.read_excel(
    "demand_seasonalities(1).xlsx"
)


# IMPORTANT:
# Check the column names in your Excel file
print("\nSeasonality columns:")
print(seasonality.columns)


# Week-of-year proportions
week_factors = seasonality["Proportion"].dropna().to_numpy()


# Day-of-week proportions
day_factors = seasonality["Proportion.1"].dropna().to_numpy()


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
    "zip3_pmf(1).csv"
)


print("\nZIP3 PMF")
print(zip3_pmf.head())

print("Number of ZIP3s:",
      len(zip3_pmf))

print("PMF sum:",
      zip3_pmf["PMF"].sum())


# ------------------------------------------------------------
# 5. UNCERTAINTY PARAMETERS
# ------------------------------------------------------------

week_cv = 0.20
day_cv = 0.15
zip3_cv = 0.15


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


annual_demand_std = np.sqrt(
    annual_demand_variance
)


print("\nAnnual Demand Statistics")

print("Mean:",
      annual_demand_mean)

print("Standard deviation:",
      annual_demand_std)


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
# 9. CALCULATE ROBUST DEMAND BOUNDS
# ------------------------------------------------------------

# 68% robustness
results["Robust_68"] = (
    results["Mean_Demand"]
    + 1.00 * results["Sigma"]
)


# 95% robustness
results["Robust_95"] = (
    results["Mean_Demand"]
    + 1.65 * results["Sigma"]
)


# 99% robustness
results["Robust_99"] = (
    results["Mean_Demand"]
    + 2.33 * results["Sigma"]
)


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

