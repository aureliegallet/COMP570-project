"""
Class to load data from using URL API and save it to CSV.
"""

from urllib.request import Request, urlopen
import json
import csv
from pathlib import Path



class Loader():
    def __init__(self):
        self.data_url = "https://donnees.montreal.ca/api/3/action/datastore_search"
        self.sql_url = "https://www.donneesquebec.ca/recherche/api/3/action/datastore_search" # SQL commands not working with the montreal API
        self.datasets_url = {
            "crime" : "c6f482bf-bf0f-4960-8b2f-9982c211addd",
            "parks" : "f34c3555-c285-4ef3-a55c-f0f5c440ad2d",
            "schools" : "c6640a54-bc4b-43ec-864e-6c325dce61bc",
            "requests": "dbfc05f8-b939-4639-ae52-2e77f738e43f"
        }
        self.page_size = 32000 # 32000 is the max https://docs.ckan.org/en/latest/maintaining/datastore.html#the-data-api:~:text=limit%20(int)%20%E2%80%93%20maximum%20number%20of%20rows%20to%20return%20(optional%2C%20default%3A%20100%2C%20unless%20set%20in%20the%20site%E2%80%99s%20configuration%20ckan.datastore.search.rows_default%2C%20upper%20limit%3A%2032000%20unless%20set%20in%20site%E2%80%99s%20configuration
        self.data_dir = Path(__file__).resolve().parent.parent / "data"
        self.data_dir.mkdir(parents = True, exist_ok = True)
    
    # Builds the desired URL based on the requested dataset and the type of request
    def build_request(self, dataset, is_sql = False, sql_command = "", customized_command = ""):
        # customized_command for additional filtering like &limit=5
        request = ""
        if dataset in list(self.datasets_url.keys()):
            if is_sql:
                request = f"{self.sql_url}_sql?sql={sql_command}"
            else:
                request = f"{self.data_url}?resource_id={self.datasets_url[dataset]}{customized_command}"
        else:
            print("\n ------------------ \n")
            print("Invalid dataset.")
        return request


    def send_request(self, input):
        input = input.replace(" ", "%20")
        request = Request(input, headers={"User-Agent": "COMP570-project"}) # https://tariyekorogha.medium.com/solution-to-403-client-error-forbidden-for-url-with-python-3-180effbdb21
        response = urlopen(request).read().decode("utf-8")
        response = json.loads(response)

        data = response["result"]["records"]
        return data
    

    def load_chunks(self, dataset):
        if dataset not in list(self.datasets_url.keys()):
            print("\n ------------------ \n")
            print("Invalid dataset.")
            yield None

        page = 0
        load_more = True
        while load_more:
            sql = (
                'SELECT * '
                f'FROM "{self.datasets_url[dataset]}" '
                f'LIMIT {self.page_size} OFFSET {self.page_size * page}'
            )
            sql = sql.replace(" ", "%20")

            try: 
                input_request = self.build_request(dataset, is_sql = True, sql_command = sql)
                data = self.send_request(input_request)
            except Exception as e:
                print("\n ------------------ \n")
                print(f"Dataset stopped loading at {self.page_size * page} because of error {e}.")
                break

            if len(data) < self.page_size:
                load_more = False
            else: 
                page += 1
            yield data


    def load_to_csv(self, dataset, input_request):
        data = self.send_request(input_request)
        save_path = self.data_dir / f"raw_{dataset}.csv"

        with open(save_path, "w") as file: # https://www.geeksforgeeks.org/python/writing-csv-files-in-python/
            headers = data[0].keys()
            writer = csv.DictWriter(file, fieldnames = headers)
            writer.writeheader()
            writer.writerows(data)



