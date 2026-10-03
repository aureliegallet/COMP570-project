import pandas as pd
from loader import Loader
from borough_identifier import BoroughIdentifier

# TO DO check NAs

class GenericExplorer():
    def __init__(self):
        self.loader = Loader()

    def print_main_info(self, df):
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

    def clean_location(self, df, borough_column, location_columns, location_type):
        if borough_column:
            df = df.rename(columns = {borough_column : "BOROUGH"})

        if location_columns:
            borough_identifier = BoroughIdentifier()
            if location_type == "NAD83":
                df["BOROUGH"] = df.apply(
                    lambda row: borough_identifier.match_NAD83_to_borough(row[location_columns[0]], row[location_columns[1]]), # Because custom function does not accept full Series
                    axis = 1
                ) 
            elif location_type == "WSG84":
                df["BOROUGH"] = df.apply(
                    lambda row: borough_identifier.match_NAD83_to_borough(row[location_columns[0]], row[location_columns[1]]), # Because custom function does not accept full Series
                    axis = 1
                ) 
            else:
                print("\n ------------------ \n")
                print("\n Unsupported location type. \n")
            df = df.drop(columns=location_columns)
            return df
        

    def explore_dataset(self, dataset, date_column = None, borough_column = None, location_columns = None, location_type = None):
        borough_counts = pd.Series() # return type of value counts
        other_counts = {}
        categorical = []
        continuous = []

        for i, chunk in enumerate(self.loader.load_chunks(dataset)):

            df = pd.DataFrame(chunk)            
            df = df.drop(columns=["_full_text"])

            # Convert some columns from str to numbers
            for column in df.columns:
                try:
                    df[column] = pd.to_numeric(df[column])
                    if i == 0:
                        continuous.append(column)
                except ValueError: # If it fails, leave it as is
                    if i == 0:
                        categorical.append(column)

            # Remove this from the value counts
            if date_column and (i == 0):
                categorical.remove(date_column)

            # FIRST CHUNK
            if i == 0:
                self.print_main_info(df)

                for column in categorical:
                    other_counts[column] = pd.Series()

                if date_column:
                    date_min = df[date_column].min()
                    date_max = df[date_column].max()

            # ALL CHUNKS
            df = self.clean_location(df, borough_column, location_columns, location_type)

            if borough_column or location_columns:
                borough_counts = borough_counts.add(df["BOROUGH"].value_counts(), fill_value = 0) # https://stackoverflow.com/questions/28353577/merging-and-sum-up-several-value-counts-series-in-pandas
            
            for column in categorical:
                other_counts[column] = other_counts[column].add(df[column].value_counts(), fill_value = 0)
            
            if date_column:
                if df[date_column].min() < date_min:
                    date_min = df[date_column].min()

                if df[date_column].min() > date_max:
                    date_max = df[date_column].max()

        print("\n ------------------ \n")
        print(f"Dates range from {date_min} to {date_max}")

        print("\n ------------------ \n")
        print(borough_counts)

        for column in categorical:
            print("\n ------------------ \n")
            print(other_counts[column])