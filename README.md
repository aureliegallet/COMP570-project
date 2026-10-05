# COMP57-project

TO RUN: 
For generic explorer, change which line is uncommented and use one of the following commands: 
- python3 src/entry_point.py crime > data/exploration/crime_output.txt
- python3 src/entry_point.py parks > data/exploration/parks_output.txt
- python3 src/entry_point.py schools > data/exploration/schools_output.txt
- python3 src/entry_point.py requests > data/exploration/requests_output.txt
- python3 src/entry_point.py housing > data/exploration/housing_output.txt

For individual processing:
- python3 src/crime_data.py 
- python3 src/parks_data.py 
- python3 src/schools_data.py 
- python3 src/requests_data.py 

Notes:
Use &limit=32000 to get full dataset when not using SQL 