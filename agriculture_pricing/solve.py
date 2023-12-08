import os
from collections import defaultdict
from tkinter import filedialog

import gurobipy as gp
import pandas as pd


def main():
    # Select input folder using GUI
    input_folder = filedialog.askdirectory(title="Select input folder")
    results_folder = os.path.join(input_folder, "results")

    def load_dataframe(filename: str):
        return pd.read_csv(os.path.join(input_folder, filename))

    # Import Data
    df_capacity = load_dataframe("capacity.csv").set_index("component")
    df_composition = load_dataframe("composition.csv").set_index(["dairy", "component"])
    df_constants = load_dataframe("constants.csv")
    df_elasticity = load_dataframe("elasticity.csv").set_index(["dairy_1", "dairy_2"])
    df_market = load_dataframe("market.csv").set_index("dairy")

    # Define constants
    price_index = df_constants["price_index"][0]

    # Create indexes
    COMPONENTS = df_capacity.index.to_list()
    DAIRIES = df_market.index.to_list()

    # Create params
    composition = df_composition["composition"].to_dict()
    capacity = df_capacity["capacity"].to_dict()
    cross_elasticity = df_elasticity["elasticity"].to_dict(into=defaultdict(int))
    last_year_demand = df_market["demand"].to_dict()
    last_year_price = df_market["price"].to_dict()

    # Create model
    m = gp.Model("agriculture_pricing")

    # Create variables
    Price = m.addVars(DAIRIES, name="Price")
    Demand = m.addVars(DAIRIES, name="Demand")

    # Create constraints

    # Capacity Limit
    for c in COMPONENTS:
        m.addLConstr(
            gp.LinExpr([(composition[d, c] / 100, Demand[d]) for d in DAIRIES]),
            gp.GRB.LESS_EQUAL,
            capacity[c],
            name=f"con_capacity_{c}",
        )

    # Prevent Last Year Price Increase
    m.addLConstr(
        gp.LinExpr([(last_year_demand[d], Price[d]) for d in DAIRIES]),
        gp.GRB.LESS_EQUAL,
        price_index,
        name="con_price_index",
    )

    # Constrain quantity via elasticities
    for d in DAIRIES:
        m.addLConstr(
            gp.LinExpr([(1 / last_year_demand[d], Demand[d])]),
            gp.GRB.EQUAL,
            gp.LinExpr(
                [(-cross_elasticity[d, d] / last_year_price[d], Price[d])]
                + [
                    (cross_elasticity[d, d2] / last_year_price[d2], Price[d2])
                    for d2 in DAIRIES
                    if d != d2
                ]
            )
            + (cross_elasticity[d, d] - sum(cross_elasticity[d, d2] for d2 in DAIRIES if d != d2) + 1),
            name=f"con_elasticity_{d}",
        )

    # Create objective
    m.setObjective(gp.quicksum(Demand[d] * Price[d] for d in DAIRIES), gp.GRB.MAXIMIZE)

    # Create results folder
    if not os.path.exists(results_folder):
        os.mkdir(results_folder)
    else:
        # TODO warn user their data will be overwritten
        pass

    # Debug
    m.write(os.path.join(results_folder, "model.lp"))

    # Set NonConvex to 2
    m.Params.NonConvex = 2

    # Solve model
    m.optimize()

    # Save results
    def save_data(df: pd.DataFrame, filename: str, **kwargs):
        df.to_csv(os.path.join(results_folder, filename), **kwargs)

    market = pd.DataFrame.from_dict(
        {d: (Demand[d].x, Price[d].x) for d in DAIRIES},
        orient="index",
        columns=["demand", "price"],
    )
    market.index = market.index.rename("dairy")
    save_data(market, "market.csv")
    save_data(pd.DataFrame({"objective": [m.objVal]}), "constants.csv", index=False)


if __name__ == "__main__":
    main()
