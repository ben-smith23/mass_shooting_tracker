import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import ssl
from matplotlib.animation import FuncAnimation
from datetime import datetime
import numpy as np

ssl._create_default_https_context = ssl._create_unverified_context

# Read the CSV file into a pandas DataFrame
df = pd.read_csv('new_combined_data.csv', parse_dates=['date'])

# Filter the DataFrame to include shootings from 2013 onwards
df = df[df['date'].dt.year >= 2013]

# Group the data by year
grouped = df.groupby(df['date'].dt.year)

# Create a Cartopy map with the desired projection
fig = plt.figure(figsize=(12, 6))
ax_map = plt.subplot2grid((1, 10), (0, 0), colspan=7, projection=ccrs.LambertConformal())
ax_chart = plt.subplot2grid((1, 10), (0, 8), colspan=3)  # Adjusted colspan for spacing

# Set the extent of the map to focus on the contiguous United States
ax_map.set_extent([-130, -75, 24, 50], crs=ccrs.PlateCarree())

# Add state borders
ax_map.add_feature(cfeature.STATES, edgecolor='black')

# Add map features
ax_map.coastlines()
ax_map.add_feature(cfeature.LAND, facecolor='lightgray')
ax_map.add_feature(cfeature.OCEAN, facecolor='lightblue')

# Initialize an empty scatter plot for the shootings
scatter = ax_map.scatter([], [], s=5, color='red', transform=ccrs.PlateCarree())

# Initialize the bar chart
bar_chart = ax_chart.bar([], [], align='center', color='black')  # Changed bar color

# Set the x-axis and y-axis labels for the bar chart
ax_chart.set_xlabel('Year')
ax_chart.set_ylabel('Number of Deaths')

# Store the initial data
initial_shootings = df[df['date'] == df['date'].min()]

# Initialize the map date label
text_date = ax_map.text(-130, 50, '', fontsize=12, transform=ccrs.PlateCarree(), verticalalignment='top', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

# Update function for each frame of the animation
def update(frame):
    # Filter the data up to the current day
    shootings = pd.concat([initial_shootings, df[df['date'] <= df['date'].min() + pd.DateOffset(days=frame)]])

    # Update the scatter plot data and dot sizes
    scatter.set_offsets(list(zip(shootings['lon'], shootings['lat'])))
    scatter.set_sizes(shootings['killed'] * 10)  # Increase size based on the number of deaths

    # Format the date for display in the annotation
    date_str = (df['date'].min() + pd.DateOffset(days=frame)).strftime('%Y-%m-%d')

    # Update the date annotation
    text_date.set_text(date_str)

    # Group the shootings by year
    grouped_shootings = shootings.groupby(shootings['date'].dt.year)

    # Clear the previous bar chart
    ax_chart.clear()

    # Iterate over each year and update the bar chart
    for year, group in grouped_shootings:
        deaths = group['killed'].sum()
        bar = ax_chart.bar(year, deaths, align='center', color='black')  # Changed bar color

        # Add labels under each bar
        ax_chart.text(year, deaths, str(int(deaths)), ha='center', va='bottom', rotation=90, color='white')
    
    # Set the x-axis and y-axis labels for the bar chart
    ax_chart.set_xlabel('Year')
    ax_chart.set_ylabel('Number of Deaths')

    # Store the years
    years = sorted(df['date'].dt.year.unique())

    # Set the x-tick positions and labels
    ax_chart.set_xticks(years)
    ax_chart.set_xticklabels(years)

    # Rotate the x-axis tick labels by 90 degrees
    plt.setp(ax_chart.get_xticklabels(), rotation=90)

    # Set the title of the bar chart as the total number of deaths for each year
    ax_chart.set_title('Mass Shooting Deaths by Year')

    # Adjust the size of the bar chart to fit the data
    ax_chart.set_xlim(years[0] - 1, years[-1] + 1)

    # Adjust the size of the bars based on the number of deaths
    for bar, year in zip(bar_chart, years):
        deaths = grouped.get_group(year)['killed'].sum()
        bar.set_height(deaths)
        ax_chart.text(bar.get_x() + bar.get_width() / 2, deaths, str(int(deaths)), ha='center', va='bottom', rotation=90, color='white')

    plt.subplots_adjust(top=0.85)
    ax_chart.set_ylim(0, 500)

    # Define the desired circle sizes for the legend
    circle_sizes = [5, 20, 35]  # Example sizes, adjust as needed

    # Calculate the scaling factor for the marker sizes
    scaling_factor = 4

    # Calculate the corresponding marker sizes for the legend based on the scaling factor
    legend_marker_sizes = [size / scaling_factor for size in circle_sizes]

    # Create a legend for the scatter plot
    legend_elements = []
    for size, legend_size in zip(circle_sizes, legend_marker_sizes):
        marker_size = np.sqrt(size) * scaling_factor  # Adjust size based on sqrt() for better visibility
        legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=marker_size, label=f'{size} Deaths'))

    # Add the legend to the map
    ax_map.legend(handles=legend_elements, loc='lower left', title='Number of Deaths', numpoints=1, labelspacing = 1.5, handlelength=0, handletextpad=2, borderaxespad=1.0, bbox_to_anchor=(0.0, 0))

    # Add text indicating the data source
    text_source = ax_map.text(-127, 17, 'Source: https://massshootingtracker.site', fontsize=8, transform=ccrs.PlateCarree())

    # Return the updated scatter plot and annotation
    return scatter, text_date, bar_chart

# Animation and display
animation = FuncAnimation(fig, update, frames=(df['date'].max() - df['date'].min()).days, interval=2)  # Decreased interval

plt.show()

# Save the animation as a GIF using Pillow
animation.save('mass_shooting_animation.gif', writer='pillow')