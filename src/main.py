"""
Main script for the project.
"""

from loader import Loader
from pathlib import Path

def main():
    url = "https://donnees.montreal.ca/api/3/action/datastore_search?resource_id=dbfc05f8-b939-4639-ae52-2e77f738e43f&limit=5"
    output_path = Path(__file__).resolve().parent.parent / "data" / "output.csv"
    loader = Loader()
    loader.load_to_csv(url, output_path)

if __name__ == "__main__":
    main()