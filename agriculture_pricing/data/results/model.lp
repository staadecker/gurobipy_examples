\ Model agriculture_pricing
\ LP format - for model browsing. Use MPS format to capture full model detail.
Maximize
 [ 2 Price[milk] * Demand[milk] + 2 Price[butter] * Demand[butter]
   + 2 Price[cheese_1] * Demand[cheese_1]
   + 2 Price[cheese_2] * Demand[cheese_2] ] / 2 
Subject To
 con_capacity_fat: 0.04 Demand[milk] + 0.8 Demand[butter]
   + 0.35 Demand[cheese_1] + 0.25 Demand[cheese_2] <= 600
 con_capacity_dry_matter: 0.09 Demand[milk] + 0.02 Demand[butter]
   + 0.3 Demand[cheese_1] + 0.4 Demand[cheese_2] <= 750
 con_price_index: 4.82 Price[milk] + 0.32 Price[butter]
   + 0.21 Price[cheese_1] + 0.07 Price[cheese_2] <= 1.939
 con_elasticity_milk: 1.346801346801347 Price[milk]
   + 0.2074688796680498 Demand[milk] = 1.4
 con_elasticity_butter: 3.75 Price[butter] + 3.125 Demand[butter] = 3.7
 con_elasticity_cheese_1: 1.047619047619048 Price[cheese_1]
   - 0.1226993865030675 Price[cheese_2]
   + 4.761904761904762 Demand[cheese_1] = 2
 con_elasticity_cheese_2: - 0.3809523809523809 Price[cheese_1]
   + 0.49079754601227 Price[cheese_2] + 14.28571428571428 Demand[cheese_2]
   = 1
Bounds
End
