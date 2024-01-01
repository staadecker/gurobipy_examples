# Sudoku Example

This example is based on [Gurobi's Sudoku Example](https://www.gurobi.com/documentation/current/examples/sudoku_py.html).

## Data View

#### `constants.csv`

| `grid_size` |
| --------- |
| The grid size, typically 9  |

#### `existing_grid.csv`

| `row`* | `column`* | `value` |
| --- | ------ | ----- |
| Element belongs to $N$ | Element belongs to $N$ | The value in that cell. |

> Missing index values allowed? : Yes

## Model View

### Input Data

#### Grid Size (Param), $n$

> Source: `grid_size` in `constants.csv`

#### Subgrid size (Param), $s = \sqrt{n}$

> Validate: Must be integer

#### Indices (Set), $N$

> Computed Set: $0$ to $n$

#### Subgrid Indices (Set), $S$

> Computed Set: $0$ to $s$

#### Valid predefined values (Set), $P_{valid}$

> Computed Set: $(1 \text{ to } n+1) \times (1 \text{ to } n+1)$

#### Predefined Values (Set), $P$

> Validate: $P \in P_{valid} \times P_{valid}$

> Source: `row` and `column` in `existing_grid.csv`

#### Predefined Value (Param), $p_{r,c} \forall (r,c)\in P$

> Source: `value` in `existing_grid.csv`

### Core Model

#### Cell Enabled (Var), $\text{On}_{r,c,v} \forall (r,c,v)\in (N \times N \times N)$

> Binary variable

> Description: When the variable is 1, it means value $v+1$ is in the cell.

#### One value per cell (Constraint)

$$\sum_{v\in N} \text{On}_{r,c,v} = 1 \quad \forall(r,c) \in N \times N$$

#### No repeats in column (Constraint)

$$\sum_{r\in N} \text{On}_{r,c,v} = 1 \quad \forall (c,v) \in N\times N$$

#### No repeats in row (Constraint)

$$\sum_{c\in N} \text{On}_{r,c,v} = 1 \quad \forall (r,v) \in N\times N$$

#### No repeats in subgrid cell (Constraint)

$$\sum_{i\in S} \sum_{j\in S} \text{On}_{s \times r+i,s \times c+j,v} = 1 \quad \forall (r,c,v) \in S \times S \times N$$

#### Enforce predefined values (Constraint)

$$ \text{On}_ {r - 1,\, c - 1,\, \text{p}_{r,c} -1 } = 1 \quad \forall (r,c) \in P $$

