"""
Find borough from location.
"""

import json
import shapely
from pathlib import Path
from pyproj import Transformer


class BoroughIdentifier():
    def __init__(self):
        self.boroughs = [
            "Ahuntsic-Cartierville", 
            "Anjou", 
            "Côte-des-Neiges-Notre-Dame-de-Grâce", 
            "Lachine",
            "LaSalle",
            "Le Plateau-Mont-Royal",
            "Le Sud-Ouest",
            "L'Île-Bizard-Sainte-Geneviève",
            "Mercier-Hochelaga-Maisonneuve",
            "Montréal-Nord",
            "Outremont",
            "Pierrefonds-Roxboro",
            "Rivière-des-Prairies-Pointe-aux-Trembles",
            "Rosemont-La Petite-Patrie",
            "Saint-Laurent",
            "Saint-Léonard",
            "Verdun",
            "Ville-Marie",
            "Villeray-Saint-Michel-Parc-Extension"
        ]

        self.borough_polygons = self._initialize_limits()


    def _initialize_limits(self):
        "Creates a dictionary of the borough shapes."
        path = Path.cwd().resolve().parent / "data" / "borough_limits.geojson"
        with open(path, "r", encoding = "utf-8") as file:
            data = json.load(file)

        polygons = {}
        for borough in data["features"]:
            borough_name = borough["properties"]["NOM"]
            if borough_name in self.boroughs:
                borough_string = json.dumps(borough["geometry"]) # Need json dumps because from_geojson expects a string, not the object
                polygons[borough_name] = shapely.from_geojson(borough_string) 

        if len(list(polygons.keys())) != len(self.boroughs):
            print("ERROR IN INITIALIZATION OF BOROUGH LIMITS.")

        return polygons

    def convert_WSG84_to_NAD83(self, x, y):
        "Converts WSG84 coordinates to the NAD83 system of the boroughs."
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:32188")
        (new_x, new_y) = transformer.transform(x, y)
        return new_x, new_y
        
    def match_WSG84_to_borough(self, x, y):
        "Finds the borough the WSG84 location belongs to."
        NAD83_x, NAD83_y  = self.convert_WSG84_to_NAD83(x, y)
        for borough in self.boroughs:
            if shapely.contains_xy(self.borough_polygons[borough], NAD83_x, NAD83_y):
                return borough
        return None

    def match_NAD83_to_borough(self, x, y):
        "Finds the borough the NAD83 location belongs to."
        for borough in self.boroughs:
            if shapely.contains_xy(self.borough_polygons[borough], x, y):
                return borough
        return None