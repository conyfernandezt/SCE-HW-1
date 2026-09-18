import numpy as np
import pandas as pd

# Reproducibility: everyone on your team gets the same 25 scenarios
np.random.seed(42)

# Number of demand scenarios
n_scenarios = 25


# --------------------------------------------------
# 1. Inverse transform sampling for triangular distribution
# --------------------------------------------------

def triangular_inverse(u, minimum, mode, maximum):
    """
    Generate a value from a triangular distribution
    using inverse transform sampling.
    """

    # CDF value at the mode
    F_mode = (mode - minimum) / (maximum - minimum)

    # Left side of the triangular distribution
    if u <= F_mode:
        x = minimum + np.sqrt(
            u * (maximum - minimum) * (mode - minimum)
        )

    # Right side of the triangular distribution
    else:
        x = maximum - np.sqrt(
            (1 - u) * (maximum - minimum) * (maximum - mode)
        )

    return x


# --------------------------------------------------
# 2. Generate random probabilities
# --------------------------------------------------

u_market = np.random.uniform(0, 1, n_scenarios)
u_share = np.random.uniform(0, 1, n_scenarios)


# --------------------------------------------------
# 3. Generate growth scenarios
# --------------------------------------------------

market_growth = np.array([
    triangular_inverse(u, 0.04, 0.075, 0.12)
    for u in u_market
])

share_growth = np.array([
    triangular_inverse(u, 0.15, 0.20, 0.25)
    for u in u_share
])


# --------------------------------------------------
# 4. Put the scenarios into a table
# --------------------------------------------------

scenarios = pd.DataFrame({
    "Scenario": range(1, n_scenarios + 1),
    "Market_Growth": market_growth,
    "Tsukumo_Share_Growth": share_growth
})

# Display as percentages
scenarios["Market_Growth"] = scenarios["Market_Growth"] * 100
scenarios["Tsukumo_Share_Growth"] = scenarios["Tsukumo_Share_Growth"] * 100

print(scenarios)

# Current values from the case
current_market_demand = 2_000_000
current_tsukumo_share = 0.036

# Calculate future total market demand
scenarios["Future_Market_Demand"] = (
    current_market_demand * (1 + scenarios["Market_Growth"] / 100)
)

# Calculate future Tsukumo market share
scenarios["Future_Tsukumo_Share"] = (
    current_tsukumo_share * (1 + scenarios["Tsukumo_Share_Growth"] / 100)
)

# Calculate annual Tsukumo demand
scenarios["Annual_Tsukumo_Demand"] = (
    scenarios["Future_Market_Demand"]
    * scenarios["Future_Tsukumo_Share"]
)

# Display the results
print(scenarios)
