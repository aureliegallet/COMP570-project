import pandas as pd
from borough_identifier import BoroughIdentifier

def str_to_num(df):
    "Changes str columns to numerical columns if possible"
    for column in df.columns:
        try:
            df[column] = pd.to_numeric(df[column])
        except ValueError: # If it fails, leave it as is
            pass
    return df

def clean_location(df, borough_column = None, location_columns = None, location_type = None):
    "Clean up the location to only BOROUGH column"

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
                lambda row: borough_identifier.match_WSG84_to_borough(row[location_columns[0]], row[location_columns[1]]), # Because custom function does not accept full Series
                axis = 1
            ) 
        else:
            print("\n ------------------ \n")
            print("\n Unsupported location type. \n")
        df = df.drop(columns=location_columns)
    
    return df