"""
Main script for the project.
"""

from loader import Loader
from pathlib import Path

URL_311 = "https://donnees.montreal.ca/api/3/action/datastore_search?resource_id=dbfc05f8-b939-4639-ae52-2e77f738e43f"
URL_CRIME = "https://donnees.montreal.ca/api/3/action/datastore_search?resource_id=c6f482bf-bf0f-4960-8b2f-9982c211addd"

def main():
    output_path = Path(__file__).resolve().parent.parent / "data" / "output_crime.csv"
    loader = Loader()
    path = loader.build_request(URL_CRIME, limit = 100)
    loader.load_to_csv(path, output_path)

if __name__ == "__main__":
    main()