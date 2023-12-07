# Agriculture Pricing Example

Example of implementation of agriculture pricing adapted from [here](https://github.com/Gurobi/modeling-examples/tree/master/agricultural_pricing).

## Data View

Columns marked with __*__ are index columns.

#### `capacity.csv`

| `component`* | `capacity` |
| --- | --- |
| __Defines__ set <u>Components</u> ($C$) | __Defines__ param <U>Last Year's Demand |

> Missing index values allowed? : N/A

#### `composition.csv`

| `dairy`* | `component`* | `composition` |
| --- | --- | -- |
| Elements __belong__ to <u>Dairy ($D$)</u> | Elements __belong__ to set <u>Components ($C$)</u> | __Defines__ param <u>Composition</u> |

> Missing index values allowed? : No

#### `constants.csv`

| `price_index` |
| --- |
| __Defines__ param <u>Price Index</u> |

> Missing index values allowed? : N/A

#### elasticity.csv

| `dairy_1`* | `dairy_2`* | `elasticity` |
| --- | --- | -- |
| Elements __belong__ to <u>Dairy ($D$)</u> | Elements __belong__ to <u>Dairy ($D$)</u> | __Defines__ param <u>Elasticity</u> |

> Missing index values allowed? : Yes

#### `market.csv`

| `dairy`* | `demand` | `price` |
| --- | --- | -- |
| __Defines__ set <u>Dairy</u> ($D$) | __Defines__ param <u>Last Year's Demand | __Defines__ param <u>Last year's price |

> Missing index values allowed? : N/A

## Model View


#### Dairy (Set), $\text{D}$

> Source: From `index columns` of `market.csv`.

#### Components (Set), $\text{C}$

> Source: From `index columns` in `capacity.csv`.

#### Capacity (Param), $\text{capacity}_c$

$$0 \le \text{capacity}_{c} \quad \forall c \in C$$

> Description: Yearly availability of component $c$ (1000 tons).

> Source: From column `capacity` in `capacity.csv`.

#### Composition (Param), $\text{qtyper}_{c,d}$

$$0 \le \text{qtyper}_{c,d}\le 1 \quad \forall c\in C, d\in D$$

> Source: From column `composition` in `composition.csv`

> Description: Percentage of component $c$ in dairy product $d$.

#### Last Year's Demand (Param), $\text{consumption}_d$

$$0 \le \text{consumption}_d \quad \forall d \in D$$

> Source: From column `demand` in `market.csv`.

> Description: Last year domestic consumption of dairy product  $d$ (1000 tons).

#### Last Year's Price (Param), $\text{price}_d$

$$0 \le \text{price}_d \quad \forall d \in D$$

> Source : From column `price` in `market.csv`.

> Description: Last year price of dairy product $d$ (dollars/1000 tons).

#### Cross-Elasticities (Param), $\text{elasticity}_{d1,d2}$

$$\text{elasticity}_{d1, d2} \quad \forall d1 \in D, d2 \in D$$

> Default: `0`

> Source: From column `elasticity` in `elasticity.csv`

> Description: Last year price cross-elasticity of domestic consumption of $d1$ and $d2$. When $d1=d2$, it is simply the (self-)elasticity.

#### Price Index (Param), $\text{prcIndex}$

> Validation: $\text{prcIndex} > 0$

> Description: Price index reflecting last year total consumption cost.

> Source: From column `price_index` in `constants.csv`

#### Product Price (var), $\text{p}_d$

$$0 < \text{p}_d \quad \forall d \in D$$

> Description: Price of dairy product $d$ (dollars/1000 tons).

#### Product Quantity (Var)

$$ 0 < \text{q}_d \quad \forall d \in D$$

> Description: Demand of dairy product $d$ (1000 tons).

#### Capacity Limit (Const)

$$
\sum_{d \in \text{D}}{\text{qtyper}_{c,d}*\text{q}_{d} } \leq \text{capacity}_{c} \quad \forall c \in \text{C}
$$

> Description: The limited availabilities of fat and dry matter are enforced by the constraint.

#### Prevent Last Year Price Increase (Const)

$$
\sum_{d \in \text{Dairy}}{\text{consumption}_{d}*\text{p}_{d} } \leq \text{prcIndex}
$$

> Description: This constraint establishes that the new prices must be such that the total cost of last year’s consumption would not be increased.

#### Define Elasticities (Const)

$$
\frac{\text{q}_{d} - \text{consumption}_{d}}{\text{consumption}_{d}}
 =
-\text{elasticity}_{d,d}\frac{\text{p}_{d} - \text{price}_{d}}{\text{price}_{d}} + \sum_{d2 \in D;d2 \ne d}{} \text{elasticity}_{d2, d}\frac{\text{p}_{d2} - \text{price}_{d2}}{\text{price}_{d2}}

\quad \forall d \in D
$$

> Description: The demand variables $q_{d}$ are related to the price variables $p_{d}$  through the price elasticities relationships. We approximate the elasticities with linear relationships.