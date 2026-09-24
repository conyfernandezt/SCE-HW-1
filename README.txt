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
2. It imports task 5 using: import task5 as task5
3.For each market and Order to Date (OTD) option, units sold equal potential demand x demand conversion rate
4.revenue = units sold x 3000
5.shipping cost, cost of goods sold and gross operating cost is derived from task 5 and depends on FC network, distance bucket,OTD promise and converted demand
6. Net revenue calculated by revenue - shipping cost
7. The analysis was performed for 1-FC, 4-FC and 15-FC. For each network, np.argmax(gross_operating_profit_matrix, axis=1) identifies the most profitable OTD promise for each market.
8. Selected primary, secondary and tertiary results are summed to calculate metrics such as total revenue, shipping cost, net revenue and GOP.
9.The optimized solution is compared with 1-day delivery and 5+ day delivery benchmark cases.
10. Final discussion compares higher converstion from faster delivery against lower shipping cost.
11. preferred OTD policy is combination of market specific promises that produces highest gross operating profit.



## Task 7
1. test


## Task 8

## Task 9
1. The FC networks are defined
2. ZIP3-level demand from Task 2 is assigned to every ZIP3 to the closest FC in the selected network
3. Demand is aggregated by FC and day, while also creating a network-wide daily demand
4. Demand required to cover a 21 days at 99% robustness, and then the autonomy is tested considering that given the current inventory, how many robust days can be covered
5. FCs operations are simulated day by day:
    - FC starts with enough inventory for the 21-day robust target
    - It receives shipments, so if something was ordered previously and its lead time has elapsed, it arrives
    - It calculated inventory (inventory physically at the FC + inventory currently in transit - backlog)
    - Calculates autonomy, how many robust days of demand the FC can cover
    - Decides whether to order: if autonomy falls below 14 days, order immediately or every 7 days, check whether autonomy is below the 21-day target
6. If order/replenishment is needed, quantity has to be determined so it orders enough to restore the FC to the 21-day target, but never less than 27 units
7. Demand is served
8. Given the amount flowing through the facility, the code determines how many resources/workers are required
9. Calculate the DC's 6-week target
10. Calculates the three production strategies: smoothing without pre-production, smoothing with pre-production and segmented smoothing
11. Calculates inventory/backlog resulting from each strategy
12. Calculates resources requirements for the DC
13. With all these results, a report is printed for sensitivity analysis
