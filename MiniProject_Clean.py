# March 2026

print("\nINTRODUCTION ###########################################################################################################\n")
print("Boston 311 is a telephone line that provides non-emergency city services and information.")
print("All service requests are public access and can be downloaded from https://data.boston.gov/dataset/311-service-requests")
#   Data was filtered by type (Request for Pothole Repair) and downloaded as a CSV.
print("\nBoston roads develop many potholes due to the freeze-thaw cycle throughout the winter.")
print("This project examines all 311 requests related to pothole repairs for the year 2026 to present (January - March).\n")

# import modules
import arcpy
from arcpy import da
import csv
import os

# METHODS & EXPECTED OUTPUTS ###############################################################################################
#   1. CREATE GDB FOR PROJECT OUTPUTS
#       1.1. File Geodatabase (gdb_path)
#   2. REMOVE DUPLICATE RECORDS FROM THE CSV
#       2.1. Revised CSV File (output_file)
#   3. CREATE SHAPEFILE FROM UPDATED CSV
#       3.1. Shapefile (output_fc)
#   4. AVERAGE NEAREST NEIGHBOR
#       4.1. HTML Report File
#   5. RUN SUMMARIZE WITHIN TOOL
#       5.1. Projected Neighborhoods Shapefile (neighborhood_prj)
#       5.2. Projected Potholes Shapefile (potholes_prj)
#       5.3. Summarize Within Shapefile (summary_shp)
#   6. CALCULATE NEIGHBORHOOD DENSITY



print(f"\nINPUT DATA #############################################################################################################")

# TODO: Set arcpy workspace
arcpy.env.workspace = r"C:\..."
print(f"\nArcPy Workspace Property: {arcpy.env.workspace}")

# TODO: Create variable for input 311 request CSV file
input_file = r"C:\..."
print(f"\nPothole Request CSV File: {input_file}")

# TODO: Create variable for the neighborhood polygon shapefile
neighborhood_shp = r"C:\..."
print(f"\nNeighborhood Polygon Shapefile: {neighborhood_shp}")



print(f"\n\n1. CREATE GDB FOR PROJECT OUTPUTS ######################################################################################\n")

# Create variable for the file geodatabase
gdb_path = fr"{arcpy.env.workspace}\MiniProject.gdb"

# If gdb_path does not exist, create the file geodatabase
if not arcpy.Exists(gdb_path):
    arcpy.management.CreateFileGDB(out_folder_path = arcpy.env.workspace,
                                   out_name = "MiniProject.gdb")
print(f"Geodatabase File Path: {gdb_path}\n")



print(f"\n2. REMOVE DUPLICATE RECORDS FROM THE CSV ###############################################################################\n")
print(f"Because the city receives service requests from the general public, many of the records are duplicate.")
print(f"The following code removes records that contain '%Duplicate%' in the field closure_reason.\n")

print(f"Input file: {input_file}")
output_file = fr"{arcpy.env.workspace}\311_Requests_revised.csv"

# Create variables to store the count and a blank dictionary for neighborhoods to be updated later in the code
duplicate_count = 0
total_count = 0
neighborhood_count = {}

# Create a DictReader object using the input file
with open(input_file, mode="r", newline="") as infile:
    reader = csv.DictReader(infile)
    column_names = reader.fieldnames

    # Create a DictWriter object using the column names from the input file
    with open(output_file, mode="w", newline="") as outfile:
        writer = csv.DictWriter(outfile, column_names)
        writer.writeheader()

        # Count each iteration in the input file to find total number of records
        for row in reader:
            total_count += 1

            # Count each iteration in the input file that contains "duplicate" in the column "closure_reason"
            if "duplicate" in (row["closure_reason"] or "").lower():
                duplicate_count += 1

            # If the record is not a duplicate, write each row to the output file
            else:
                writer.writerow(row)

print(f"Updated file path: {output_file}"
      f"\n\tTotal records in input file: {total_count}"
      f"\n\tNumber of duplicate records removed: {duplicate_count}"
      f"\n\tTotal records written to output file: {total_count - duplicate_count}")



print(f"\n\n3. CREATE SHAPEFILE FROM UPDATED CSV ###################################################################################\n")

# Set spatial reference to WGS 1984 (4326) to convert latitude and longitude values to points
spatial_ref = arcpy.SpatialReference(4326)
print(f"Spatial Reference for XY Table to Points: {spatial_ref.name}\n")

# Set output feature class to a new file in the geodatabase called "pothole_requests"
output_fc = os.path.join(gdb_path, "pothole_requests")

# If the output feature class does not exist, create the shapefile using XY Table to Point:
if not arcpy.Exists(output_fc):
    arcpy.management.XYTableToPoint(in_table=output_file,
                                    out_feature_class=output_fc,
                                    x_field="longitude",
                                    y_field="latitude",
                                    coordinate_system=spatial_ref)
    print(f"{output_fc} successfully created.")

# If the file already exists, print the following statement:
else:
    print(f"{output_fc} already exists.")



print(f"\n\n4. AVERAGE NEAREST NEIGHBOR ############################################################################################\n")

arcpy.env.workspace = r"C:\GIS\513\Assignments\MiniProject"
arcpy.env.overwriteOutput = True

potholes_file = output_fc
print(f"Input features: {potholes_file}")

# Run the Average Nearest Neighbor tool using the input shapefile of 311 requests.
#    The Manhattan method measures distance at right angles instead of the straight-line distance.
#    This is more representative of the distance between two points in a city grid.

ann_result = arcpy.stats.AverageNearestNeighbor(Input_Feature_Class = potholes_file,
                                                    Distance_Method = "MANHATTAN_DISTANCE",
                                                    Generate_Report = "GENERATE_REPORT",
                                                    Area = "")
# Print the location of the HTML report file
print(f"\nHTML Report File = {ann_result[5]}\n")

# Print the results of the average nearest neighbor tool
print("Nearest Neighbor Results for pothole_requests:")

# Convert nearest neighbor index value to a float object and print result
nn_index = float(ann_result[0])

# Examine the results of the nearest neighbor index
if nn_index < 1:
    print(f"\tNearest Neighbor Index = {nn_index} \n\t\tPoint pattern exhibits clustering.")
elif nn_index > 1:
    print(f"\tNearest Neighbor Index = {nn_index} \n\t\tPoint pattern exhibits dispersion.")
else:
    print(f"\tNearest Neighbor Index = {nn_index} \n\t\tPoint pattern exhibits randomness.")

# Check results of Z-Score (standard deviations) and P-Value (probability)
zscore = float(ann_result[1])
pvalue = float(ann_result[2])
print(f"\tZ-Score = {zscore}")
print(f"\tP-Value = {pvalue}")

# Check confidence levels of analysis based on Z-Score and P-Value
if (zscore < -2.58 or zscore > 2.58) and pvalue < 0.01:
    print(f"\t\tConfidence level: 99%")
elif (zscore < -1.96 or zscore > 1.96) and pvalue < 0.05:
    print(f"\t\tConfidence level: 95%")
elif (zscore < -1.65 or zscore > 1.65) and pvalue < 0.10:
    print(f"\t\tConfidence value: 90%")
else:
    print(f"\t\tConfidence value: <90%")



print(f"\n\n5. RUN SUMMARIZE WITHIN TOOL ###########################################################################################\n")

arcpy.env.workspace = gdb_path
potholes_file = output_fc

# Print input file paths
print(f"Neighborhood shapefile path: {neighborhood_shp}")
print(f"Potholes shapefile path: {potholes_file}")

# Project both shapefiles to Mass State Plane (meters) to more accurately calculate neighborhood area
spatial_ref_ma = arcpy.SpatialReference(26986)
print(f"\nProject shapefiles to {spatial_ref_ma.name}")

neighborhood_prj = os.path.join(arcpy.env.workspace,"neighborhood_prj")
arcpy.management.Project(
    in_dataset = neighborhood_shp,
    out_dataset = neighborhood_prj,
    out_coor_system = spatial_ref_ma
)
print(f"\tProjected neighborhood shapefile path: {neighborhood_prj}")

potholes_prj = os.path.join(arcpy.env.workspace,"potholes_prj")
arcpy.management.Project(
    in_dataset = potholes_file,
    out_dataset = potholes_prj,
    out_coor_system = spatial_ref_ma
)
print(f"\tProjected potholes shapefile path: {potholes_prj}")

# Create an output feature class for the summarize within tool
summary_shp = os.path.join(arcpy.env.workspace,"summary")

# Run the summarize within tool with neighborhood boundaries as the input polygons and potholes as the sum features
arcpy.analysis.SummarizeWithin(
    in_polygons = neighborhood_prj,
    in_sum_features = potholes_prj,
    out_feature_class = summary_shp,
    keep_all_polygons = "KEEP_ALL"
)

print("\nSummarize within completed.")
print(f"\tSummarize within shapefile path: {summary_shp}\n")



print("\n6. CALCULATE NEIGHBORHOOD DENSITY ######################################################################################\n")

# Create an empty dictionary to store values from the summarize within shapefile
density_dict = {}

# New variable for list of field names in search cursor
field_names = ["BlockGr202", "Point_Count", "Shape_Area"]

with arcpy.da.SearchCursor(summary_shp, field_names) as s_cursor:
    for row in s_cursor:
        neighborhood = row[0]
        count = row[1]
        # Convert area (square meters) to square kilometers by dividing by 1,000,000
        area = round(row[2] / 1000000, 4)
        # New variable calculates density as count (311 complaints) / area (square kilometers)
        density = round(count / area, 4)

        # Add another key to the dictionary to store values associated with each neighborhood
        density_dict[neighborhood] = {"count":count, "area":area, "density":density}

print(f" {'NEIGHBORHOOD':^25} | {'POINT COUNT':^12} | {'AREA (SQ KM)':^12} | {'DENSITY':^12}")
print(f" {'':->25} | {'':-^12} | {'':-^12} | {'':-^20}")

# Sort neighborhoods by density in descending order
for neighborhood, values in sorted(density_dict.items(), key=lambda x: x[1]["density"], reverse=True):
    # Print neighborhood values from nested dictionary
    print(f" {neighborhood:^25} | {values['count']:^12} | {values['area']:^12} | {values['density']:^12}")

# Create variables for the neighborhood with the max density and min density
max_neighborhood = max(density_dict, key=lambda x: density_dict[x]["density"])
min_neighborhood = min(density_dict, key=lambda x: density_dict[x]["density"])

# Print statements for the max and min density neighborhoods
print(f"\n{max_neighborhood} has the highest density of {density_dict[max_neighborhood]['density']} potholes per square km.")
print(f"{min_neighborhood} has the lowest density of {density_dict[min_neighborhood]['density']} potholes per square km.")
