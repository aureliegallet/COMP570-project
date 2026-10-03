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
            "schools" : "c6640a54-bc4b-43ec-864e-6c325dce61bc"
        }
        self.page_size = 10000
        self.data_dir = Path(__file__).resolve().parent.parent / "data"
        self.data_dir.parent.mkdir(parents = True, exist_ok = True)
    
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
            input_request = self.build_request(dataset, is_sql = True, sql_command = sql)
            data = self.send_request(input_request)

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



