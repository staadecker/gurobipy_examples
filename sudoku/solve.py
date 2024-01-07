import os
from tkinter import filedialog
import gurobipy as gp
import pandas as pd
import math

def main():
    # Select input folder using GUI
    input_folder = filedialog.askdirectory(title="Select input folder")
    results_folder = os.path.join(input_folder, "results")

    def load_dataframe(filename: str):
        return pd.read_csv(os.path.join(input_folder, filename))

    # Import Data
    df_constants = load_dataframe("constants.csv")
    df_existing_grid = load_dataframe("existing_grid.csv").set_index(["row", "column"])

    # Define constants
    grid_size = df_constants["grid_size"][0]
    subgrid_size = math.sqrt(grid_size)

    if subgrid_size.is_integer():
        subgrid_size = int(subgrid_size)
    else:
        raise ValueError("subgrid_size is not an integer")
    
    # Create indexes
    VALID_PREDEFINED_VALUES = [(i,j) for i in range(1, grid_size + 1) for j in range(1, grid_size + 1)]
    PREDEFINED_VALUES = df_existing_grid.index.to_list()
    INDICES = range(0, grid_size)
    SUBGRID_INDICES = range(0, subgrid_size)

    # Validate Set
    if any(x not in VALID_PREDEFINED_VALUES for x in PREDEFINED_VALUES):
        raise ValueError("Predefined values contain invalid values")
    
    # Create params
    predefined_values = df_existing_grid["value"].to_dict()

    # Create variables
    m = gp.Model("sudoku")
    On = m.addVars(INDICES, INDICES, INDICES, vtype=gp.GRB.BINARY, name="On")

    # Create constraints

    # One value per cell
    for r in INDICES:
        for c in INDICES:
            m.addLConstr(
                gp.LinExpr([(1,On[r, c, v]) for v in INDICES]),
                gp.GRB.EQUAL,
                1,
                name=f"con_one_value_{r}_{c}",
            )

    # No repeats in column
    for c in INDICES:
        for v in INDICES:
            m.addLConstr(
                gp.LinExpr([(1,On[r, c, v]) for r in INDICES]),
                gp.GRB.EQUAL,
                1,
                name=f"con_no_repeats_column_{c}_{v}",
            )

    # No repeats in row
    for r in INDICES:
        for v in INDICES:
            m.addLConstr(
                gp.LinExpr([(1,On[r, c, v]) for c in INDICES]),
                gp.GRB.EQUAL,
                1,
                name=f"con_no_repeats_row_{r}_{v}",
            )
    
    # No repeats in subgrid cell
    for r in SUBGRID_INDICES:
        for c in SUBGRID_INDICES:
            for v in INDICES:
                m.addLConstr(
                    gp.LinExpr([(1,On[subgrid_size * r + ro, subgrid_size * c + co, v]) for ro in SUBGRID_INDICES for co in SUBGRID_INDICES]),
                    gp.GRB.EQUAL,
                    1,
                    name=f"con_no_repeats_subgrid_{r}_{c}_{v}",
                )
    
    # Enforce predefined values
    for (r, c), v in predefined_values.items():
        m.addLConstr(
            gp.LinExpr([(1,On[r - 1, c - 1, v - 1])]),
            gp.GRB.EQUAL,
            1,
            name=f"con_predefined_{r}_{c}",
        )

    # Debug
    m.write(os.path.join(results_folder, "model.lp"))

    
    m.optimize()

    # Save results
    def save_data(df: pd.DataFrame, filename: str, **kwargs):
        df.to_csv(os.path.join(results_folder, filename), **kwargs)

    res_on = pd.DataFrame.from_records(
        ((r,c,v, int(On[r,c,v].X)) for r in INDICES for c in INDICES for v in INDICES),
        columns=["row", "column", "value", "On"],
    ).set_index(["row", "column", "value"])
    save_data(res_on, "result_on.csv")



if __name__ == "__main__":
    main()