import os
from tkinter import filedialog

import gurobipy as gp
import pandas as pd


def main():
    # Select input folder using GUI
    input_folder = filedialog.askdirectory(title='Select input folder')
    results_folder = os.path.join(input_folder, 'results')

    def load_dataframe(filename: str):
        return pd.read_csv(os.path.join(input_folder, filename))

    # Import Data
    df_constants = load_dataframe('constants.csv')
    df_costs = load_dataframe('costs.csv').set_index(['site'])
    df_coverage = load_dataframe('coverage.csv').set_index(['site', 'region'])
    df_population = load_dataframe('population.csv').set_index(['region'])

    # Define constants
    budget = df_constants['budget'][0]

    # Create indexes
    sites = df_costs.index.to_list()
    regions = df_population.index.to_list()

    # Create params
    costs = df_costs['cost'].to_dict()
    coverage = df_coverage['is_covered'].to_dict()
    population = df_population['population'].to_dict()

    # Create model
    m = gp.Model('cell_coverage')

    # Create variables
    covered = m.addVars(regions, vtype=gp.GRB.BINARY, name='covered')
    build = m.addVars(sites, vtype=gp.GRB.BINARY, name='build')

    # Create constraints
    for r in regions:
        m.addLConstr(gp.LinExpr([(1, build[s]) for s in sites if coverage[s, r] == 1]), gp.GRB.GREATER_EQUAL,
                     covered[r], name=f'covered_{r}')

    m.addLConstr(gp.LinExpr([(costs[s], build[s]) for s in sites]), gp.GRB.LESS_EQUAL, budget, name='budget')

    # Create objective
    m.setObjective(gp.LinExpr([(population[r], covered[r]) for r in regions]), gp.GRB.MAXIMIZE)

    # Solve model
    m.optimize()

    # Save results
    if not os.path.exists(results_folder):
        os.mkdir(results_folder)
    else:
        # TODO warn user their data will be overwritten
        pass

    def save_data(df: pd.DataFrame, filename: str):
        df.to_csv(os.path.join(results_folder, filename))

    res_covered = pd.DataFrame.from_dict({r: covered[r].x for r in regions}, orient='index', columns=['covered'])
    res_covered.index = res_covered.index.rename('region')
    save_data(res_covered, 'covered.csv')

    res_build = pd.DataFrame.from_dict({s: build[s].x for s in sites}, orient='index', columns=['build'])
    res_build.index = res_build.index.rename('site')
    save_data(res_build, 'build.csv')


if __name__ == '__main__':
    main()
