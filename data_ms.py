import csv
import json
import ssl
from geopy.geocoders import Nominatim

# Disable SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

combined_data = []

for year in range(2013, 2024):
    filename = f"./data/{year}-data.json"
    with open(filename, "r") as file:
        data = json.load(file)
        for row in data:
            state = row['state'].upper()  # Convert state to uppercase
            if state in ['DC', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']:
                combined_data.append(row)

# Removing the last two columns
for row in combined_data:
    del row['names']
    del row['sources']

# Adding latitude and longitude for each city within the US
geolocator = Nominatim(user_agent="my-app")

for row in combined_data:
    city_name = row['city']

    try:
        location = geolocator.geocode(city_name, country_codes='us', timeout=10)
        if location and location.raw.get('display_name', '').endswith(', United States'):
            row['lat'] = location.latitude
            print(location)
            row['lon'] = location.longitude
        else:
            row['lat'] = None
            row['lon'] = None
    except:
        row['lat'] = None
        row['lon'] = None

# Saving combined data to a CSV file
csv_filename = "combined_data.csv"

with open(csv_filename, "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=combined_data[0].keys())
    writer.writeheader()
    writer.writerows(combined_data)

print("Conversion to CSV complete. Saved as", csv_filename)