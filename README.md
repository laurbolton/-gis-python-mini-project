# -gis-python-mini-project
This project analyzes Boston 311 pothole repair requests (January–March 2026) by neighborhood.

## Technologies Used
- Python 3.x
- ArcPy

## Setup Instructions
1. Install required dependencies
2. Update file paths in variables section
3. Run the script

## Input Data
1. input_file = file path for CSV with 311 request records.

   Data can be downloaded from https://data.boston.gov/dataset/311-service-requests.

   Data for this analysis was filtered by type = "Request for Pothole Repair".
   
3. neighborhood_shp = file path for neighborhood shapefile.

    Data can be downloaded from https://data.boston.gov/dataset/census-2020-block-group-neighborhoods.

## Expected Outputs
1. gdb_path = File Geodatabase
2. output_file = Revised CSV File
3. output_fc = Shapefile from XY Table to Point
4. HTML Report File from Average Nearest Neighbor
5. neighborhood_prj = Projected Neighborhood Shapefile
6. potholes_prj = Projected Potholes Shapefile
7. summary_shp = Summarize Within Shapefile
