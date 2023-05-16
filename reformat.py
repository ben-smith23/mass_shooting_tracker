import csv

input_filename = "combined_data.csv"
output_filename = "new_combined_data.csv"

# Read the input CSV file
with open(input_filename, "r") as csvfile:
    reader = csv.DictReader(csvfile)
    data = list(reader)

# Remove the "injured" column
for row in data:
    del row["wounded"]

# Filter out rows where deaths are 0
data = [row for row in data if int(row["killed"]) >= 3]

# Filter out rows where lat or lon is empty
data = [row for row in data if row["lat"] != "" and row["lon"] != ""]

# Write the filtered data to the output CSV file
fieldnames = ["date", "killed", "city", "state", "lat", "lon"]

with open(output_filename, "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)

print("Data processing complete. Saved as", output_filename)
