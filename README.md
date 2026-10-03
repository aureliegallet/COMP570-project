# COMP57-project


notes:
Use &limit=32000 to get full dataset when not using SQL 
32000 is the max 
https://docs.ckan.org/en/latest/maintaining/datastore.html#the-data-api:~:text=limit%20(int)%20%E2%80%93%20maximum%20number%20of%20rows%20to%20return%20(optional%2C%20default%3A%20100%2C%20unless%20set%20in%20the%20site%E2%80%99s%20configuration%20ckan.datastore.search.rows_default%2C%20upper%20limit%3A%2032000%20unless%20set%20in%20site%E2%80%99s%20configuration

For generic explorer: python3 src/test.py > data/exploration/schools_output.txt