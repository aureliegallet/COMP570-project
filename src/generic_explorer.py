"""
Runs basic exploration
"""
import utils
import pandas as pd
from loader import Loader
import matplotlib.pyplot as plt
from pathlib import Path

class GenericExplorer():
    def __init__(self):
        self.loader = Loader()
        self.save_dir = Path(__file__).resolve().parent.parent / "data/figures"
        self.save_dir.mkdir(parents = True, exist_ok = True)
    
    def print_main_info(self, df):
        "Print statements as function to clean up the main explore function"
        print("Dataframe Head\n")
        print(df.head(5)) # Print only once
        print("\n ------------------ \n")
        print("Dataframe Columns\n")
        print(df.columns)
        print("\n ------------------ \n")
        print("Dataframe Information\n")
        print(df.info())
        print("\n ------------------ \n")
        print("Dataframe Description\n")
        print(df.describe())


    # Final printing
    def print_empty(self, length, empty_values, rows_with_missing):
        "Print statements as function to clean up the main explore function"
        print("\n ------------------ \n")
        print(f"Total length of reported dataset: {length}")
        print(f"Empty values per column")
        print(empty_values.sort_values(ascending = False))
        print(f"Total rows with missing values: {rows_with_missing}")

    def print_date_range(self, min, max):
        "Print statements as function to clean up the main explore function"
        print("\n ------------------ \n")
        print(f"Dates range from {min} to {max}")

    def print_boroughs(self, dataset, borough_counts):
        "Print statements as function to clean up the main explore function"
        print("\n ------------------ \n")
        print(borough_counts.sort_values(ascending = False))

        # https://matplotlib.org/stable/gallery/ticks/ticklabels_rotation.html
        fig, ax = plt.subplots(layout = "constrained")
        plt.bar(
            borough_counts.index, 
            borough_counts.values, 
        )
        ax.tick_params("x", rotation = 45, rotation_mode = "xtick")
        ax.set_title("Value counts for: boroughs")
        plt.savefig(self.save_dir / f"{dataset}_boroughs_values.png")

    def print_other_counts(self, dataset, categorical, other_counts):
        "Print statements as function to clean up the main explore function"
        for column in categorical:
            print("\n ------------------ \n")
            print(other_counts[column].sort_values(ascending = False))

            # Avoid completely unreadable plots
            if len(other_counts[column].index) < 20:
                # https://matplotlib.org/stable/gallery/ticks/ticklabels_rotation.html
                fig, ax = plt.subplots(layout = "constrained")
                ax.bar(
                    other_counts[column].index, 
                    other_counts[column].values, 
                )
                ax.tick_params("x", rotation = 45, rotation_mode = "xtick")
                ax.set_title(f"Value counts for: {column}")
                plt.savefig(self.save_dir / f"{dataset}_{column}_values.png")


    def explore_dataset(self, dataset, date_column = None, borough_column = None, location_columns = None, location_type = None):
        "Runs full generic exploration of dataset"
        
        borough_counts = pd.Series() # return type of value counts
        other_counts = {}
        categorical = []
        continuous = []
        length = 0
        empty_values = pd.Series()
        rows_with_missing = 0

        for i, chunk in enumerate(self.loader.load_chunks(dataset)):

            df = pd.DataFrame(chunk)  
            if "_full_text" in df.columns:  
                df = df.drop(columns=["_full_text"])

            # Convert some columns from str to numbers
            df = utils.str_to_num(df)

            # FIRST CHUNK
            if i == 0:
                self.print_main_info(df)

                for col in df.columns:
                    if df[col].dtype == "str" and (col != date_column) and (col != borough_column) and (location_columns is None or (col not in location_columns)):
                        categorical.append(col)
                    else: 
                        continuous.append(col)

                # Value counts prep
                for column in categorical:
                    other_counts[column] = pd.Series()

                # Date range prep
                if date_column:
                    date_min = df[date_column].min()
                    date_max = df[date_column].max()

            # ALL CHUNKS
            df = utils.clean_location(df, borough_column = borough_column, location_columns = location_columns, location_type = location_type)

            # Length and missing values
            length += len(df)
            empty_values = empty_values.add(df.isna().sum(), fill_value = 0)

            normal_length = len(df)
            temp = df.dropna()
            removed_length = len(temp)
            rows_with_missing += normal_length - removed_length
            
            # Value counts
            if borough_column or location_columns:
                borough_counts = borough_counts.add(df["BOROUGH"].value_counts(), fill_value = 0) # https://stackoverflow.com/questions/28353577/merging-and-sum-up-several-value-counts-series-in-pandas
            
            for column in categorical:
                other_counts[column] = other_counts[column].add(df[column].value_counts(), fill_value = 0)

            # Date range
            if date_column:
                if df[date_column].min() < date_min:
                    date_min = df[date_column].min()

                if df[date_column].min() > date_max:
                    date_max = df[date_column].max()

        # Final printing
        self.print_empty(length, empty_values, rows_with_missing)

        if date_column:
            self.print_date_range(date_min, date_max)

        if borough_column or location_columns:
            self.print_boroughs(dataset, borough_counts)

        self.print_other_counts(dataset, categorical, other_counts)