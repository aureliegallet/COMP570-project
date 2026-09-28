"""
Class to load data from using URL API and save it to CSV.
"""

from urllib.request import Request, urlopen
import json
import csv


class Loader():
    def __init__(self):
        pass

    def load_to_csv(self, input_request, output_path):
        request = Request(input_request, headers={'User-Agent': 'COMP570-project'})
        response = urlopen(request).read().decode('utf-8')
        response = json.loads(response)

        data = response["result"]["records"]
        
        with open(output_path, "w") as file:
            headers = data[0].keys()
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)

