from generic_explorer import GenericExplorer


explorer = GenericExplorer()
explorer.explore_dataset("crime", date_column = "DATE", location_columns = ["X", "Y"], location_type = "NAD83")