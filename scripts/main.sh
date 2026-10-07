#!/bin/bash

echo "$(date)"

echo "EXPLORATION" 

echo "Running crime exploration..." 
python3 src/entry_point.py crime > data/exploration/crime_output.txt

echo "Running parks exploration..." 
python3 src/entry_point.py parks > data/exploration/parks_output.txt

echo "Running schools exploration..." 
python3 src/entry_point.py schools > data/exploration/schools_output.txt

echo "Running requests exploration..." 
python3 src/entry_point.py requests > data/exploration/requests_output.txt

echo "Running housing exploration..." 
python3 src/entry_point.py housing > data/exploration/housing_output.txt

echo "CLEANING" 

echo "Running crime cleaning..." 
python3 src/crime_data.py 

echo "Running parks cleaning..." 
python3 src/parks_data.py 

echo "Running schools cleaning..." 
python3 src/schools_data.py 

echo "Running requests cleaning..." 
python3 src/requests_data.py 

echo "Running housing cleaning..." 
python3 src/housing_data.py 

echo "MERGING"
python3 src/merge_datasets.py 

echo "$(date)"