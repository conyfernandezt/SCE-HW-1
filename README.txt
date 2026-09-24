// From assignment specification: "describes the logic and data flow of your computation files and code. Please be specific, a reader should be able to reproduce your results from it alone." //

# General instructions

The purpose of this document is to explain the logic and data flow of the case work.

Throughout the whole project there were some basic libraries used:
1. Pandas
2. Numpy
3. Matplotlib
4. Pathlib


## Task 1

For task we had to compute the estimated overall market demand, considering a 1 year planning horizon. Given the hypothesis on the case work, there were a couple of assumptions that had to be considered to compute the overall market demand:
1. Current US market = 2_000_000
2. Market growth = 0.04
3. Current Tsukumo share = 0.036
4. Tsukumo share growth = 0.15
5. Average price = 3000
6. Average weight = 60
7. Average volume = 12

The code logic:
1. It begins by calculating the share and units for next year, and taking those values, then it goes to calculate the annual revenue and annual weight for the following year.
2. Then, taking into consideration the cvs files markets and geographies, the demand at ZIP3 level was calculated, considering the anual units, then monthly units -- therefore not considering seasonality --, and finally the daily units.
3. From the previous information, the yearly units by market type is calculated and plotted.
4. Similarly, the average monthly tsukumo demand is calculated and then the top 15 states are plotted.
5. The yearly revenue by state is calculated and the top 15 stated are plotted.
6. The daily weight by ZIP3 is calculated and the top 20 ZIP3 are plotted

## Task 2

The code logic:
1. Begins by calculating the two growth distributions, for market and share
2. Considering the 3 values of market growth (4%, 7.5%, 12%) and market share growth (15%, 20%, 25%), there are calculated using triangular distribution
3. The share growth and annual Tsukumo demand is calculated with the corresponding robustness levels and the corresponding coefficient of variation
4. Using those a values, the final annual demand is calculated
5. The variance and the mean for the annual demand is calculated
6. Using the seasonality information provided and previos calculated values (like variance, demand, etc), the weekly and daily national demand is calculated
7. Final report is built with all the required information:
    - Annual national demand
    - Annual demand by market type or state
    - Weekly national demand
    - Daily national demand
    - Optional daily ZIP3 demand
    - Market growth + Tsukumo share growth
    - Market growth + Tsukumo share growth + ZIP3 PMF
    - Market growth + Tsukumo share growth + week seasonality
    - Market growth + Tsukumo share growth + week seasonality + day seasonality
    - Market growth + Tsukumo share growth + week seasonality + day seasonality + ZIP3 PMF

## Task 3

The code logic:
1. Lists with the subgroups are created, for 4 FCs and 15 FCs
2. From the CSV file, the closest location (ZIP3) was determined for all FCs
3. A map is plotted considering 1 FC (GA-303)
4. A map is plotted considering 4 FCs (GA-303, NY-134, TX-799, UT-841) and its according closest ZIP3, coded by color
5. A map is plotted considering 15 FCs (GA-303, NY-134, TX-799, UT-841, AZ-852, CA-900, CA-945, CO-802, FL-331, IL-606, MA-021, MI-481, NC-275, NJ-070, TX-750, TX-770, WA-980) and its according closest ZIP3, coded by color
6. For all FC configurations (FC, 4FCs and 15FCs) the demand share and the demand share by market type was calculated
7. Distance buckets were created, and the  were assigned to each bucket depending on the FC configuration being evaluated
8. For each FC configuration (FC, 4FCs and 15FCs), the demand share by market type and distance bucket was calculated

## Task 4

The code logic:
1. The lists and dataframes used for task 3 were reused
2. For each FC configuration (FC, 4FCs and 15FCs) the ZIP3 were placed into their corresponding buckets
3. 3 different graphs are generated, where each FC has a different color and the intensity of the color of the ZIP3 represents the distance to the FC. So a darker colors would mean they are in the closest buckets and as the color gets lighter, the ZIP3 would be part of the furthest bucket
4. For the 4C configuration and the 15C configuration, a new column for the dataframes was added for the number of FCs that can serve the clusters
5. For both configurations maps were plotted, where the clusters colored red where the ones with less counts and the green ones where the ones with the highest counts
6. Using the same calculation for the eligible FCs, the proportion of demand that can only be served by a single FC was printed in a table
7. For both FC configuration, to evaluate the demand distribution, first the number of eligible FCs was counted. If there is only one eligible FC, then 100% of the demand is assigned to that FC. If there is more than 1 FC, then 80% would be assigned to the closest, and the remining 20% distributed equally among the rest

## Task 5

1. The outputs and dataframes from task 3 were reused
2. The demand for the different markets (primary, secondary and tertiary) were calculated from outputs from task 3 (manual input) multiplied times the Tsukumo demand
3. The revenue for the 3 markets was calculated using the OTD demand conversion rates
4. The demand share by bucket was calculared for all FC configurations
5. Using the shipment costs information, the final cost per FC configuration, bucket and OTD, was calculated
6. Subtracting the revenue matrix and the production cost matrix, the net revenue for each FC was obtained
7. Gross operating cost was calculated using the net revenue previously computed and substracting 750 for each item sold
8. Using all the previous data, a couple of plots were generated for:
    - Gross operating profit by OTD for each market type for all FC configurations

## Task 6
1. The outputs and dataframes from task 5 were reused


## Task 7


