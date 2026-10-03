from generic_explorer import GenericExplorer


explorer = GenericExplorer()
explorer.explore_dataset("crime", date_column = "DATE", location_columns = ["X", "Y"], location_type = "NAD83")
# explorer.explore_dataset("parks", borough_column = "GESTION")
# explorer.explore_dataset("schools", location_columns = ["COORD_X_LL84_IMM", "COORD_Y_LL84_IMM"], location_type = "WSG84")