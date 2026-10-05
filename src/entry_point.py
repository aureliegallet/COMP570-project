from generic_explorer import GenericExplorer
import argparse

def run_exploration(dataset):
    explorer = GenericExplorer()

    match dataset:
        case "crime": 
            explorer.explore_dataset("crime", date_column = "DATE", location_columns = ["X", "Y"], location_type = "NAD83")
        case "parks": 
            explorer.explore_dataset("parks", borough_column = "GESTION")
        case "schools": 
            explorer.explore_dataset("schools", location_columns = ["COORD_X_LL84_IMM", "COORD_Y_LL84_IMM"], location_type = "WSG84")
        case "requests":
            explorer.explore_dataset("requests", date_column = "DDS_DATE_CREATION", location_columns = ["LOC_X", "LOC_Y"], location_type = "NAD83")
        case "housing":
            explorer.explore_dataset("housing", borough_column = "Géographie")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Runs generic exploration on a given dataset')

    parser.add_argument("dataset", help="Choose a dataset for generic exploration")
    args = parser.parse_args()
    
    run_exploration(args.dataset)