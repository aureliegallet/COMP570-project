import pandas as pd
from loader import Loader
from borough_identifier import BoroughIdentifier

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
        categorical = []
        continuous = []

        for i, chunk in enumerate(self.loader.load_chunks(dataset)):

            df = pd.DataFrame(chunk)            
            df = df.drop(columns=["_full_text"])

            for column in df.columns:
                try:
                    df[column] = pd.to_numeric(df[column])
                    continuous.append(column)
                except ValueError: # If it fails, leave it as is
                    categorical.append(column)

            # FIRST CHUNK
            if i == 0:
                self.print_main_info(df)

                if date_column:
                    date_min = df[date_column].min()
                    date_max = df[date_column].max()

            # ALL CHUNKS
            df = self.clean_location(df, borough_column, location_columns, location_type)

            if date_column:
                if df[date_column].min() < date_min:
                    date_min = df[date_column].min()

                if df[date_column].min() > date_max:
                    date_max = df[date_column].max()

        print("\n ------------------ \n")
        print(f"Dates range from {date_min} to {date_max}")