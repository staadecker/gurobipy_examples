import os
from tkinter import filedialog
import pandas as pd

def main():
    results_folder = "sudoku/results"
    results = pd.read_csv(os.path.join(results_folder, "result_on.csv"))
    results = results.pivot_table(index=["row", "column"], columns="value", values="On")
    # Multiply value by column name
    results = results.multiply(results.columns, axis=1)
    # Sum all columns
    results = results.sum(axis=1).to_frame("On").reset_index()
    # Pivot table
    results = results.pivot_table(index="row", columns="column", values="On")
    # Cast to int
    results = results.astype(int)
    # Save results
    results.to_csv(os.path.join(results_folder, "result_processed.csv"))


if __name__ == "__main__":
    main()
