import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from tqdm import tqdm

# File paths
demographic_data_file = '/home/tomd/Documenti/demos/Data/Bilancio_demografico_mensile_2022.csv'
municipalities_geojson_file = '/home/tomd/Documenti/demos/Data/limits_IT_municipalities.geojson'

# Load demographic data
demographic_data = pd.read_csv(demographic_data_file, delimiter=';')

# Extract data for the start and end of the period
start_population_comune = demographic_data[
    (demographic_data['Mese'] == 1) & (demographic_data['Sesso'] == 'Totale')]
end_population_comune = demographic_data[
    (demographic_data['Mese'] == 15) & (demographic_data['Sesso'] == 'Totale')]

# Calculate yearly percentage change
yearly_population_change = (end_population_comune['Popolazione fine periodo'].values - 
                            start_population_comune['Popolazione inizio periodo'].values) / start_population_comune['Popolazione inizio periodo'].values * 100

# Add the percentage change to the end_population_comune DataFrame
end_population_comune = end_population_comune.assign(PercentageChange=yearly_population_change)

# Load GeoJSON data
italy_municipalities = gpd.read_file(municipalities_geojson_file)

# Merge the data
merged_data = italy_municipalities.merge(end_population_comune, left_on='name', right_on='Comune', how='left')


# Define the bounds for normalization
min_change, max_change = yearly_population_change.min(), yearly_population_change.max()

# Create a 3D plot
fig = plt.figure(figsize=(15, 15), dpi=300)
ax = fig.add_subplot(111, projection='3d')

# Scaling factors - these should be adjusted based on the range of your data
height_scaling_factor = 1e-4
area_scaling_factor = 1e-6

# Determine the bounds of your data to set the axes ranges
data_bounds = merged_data.total_bounds
pop_min, pop_max = merged_data['Popolazione fine periodo'].min(), merged_data['Popolazione fine periodo'].max()

# Plot each municipality
for idx, row in tqdm(merged_data.iterrows(), total=merged_data.shape[0]):
    geom = row['geometry']
    if geom.is_empty or not geom.is_valid:
        continue

    # Initialize variables to store the southernmost point
    southernmost_point = (None, float('inf'))  # Start with "infinity" as the y-coordinate
    
    # Check if the geometry is a MultiPolygon
    if geom.geom_type == 'MultiPolygon':
        # Iterate through all polygons to find the southernmost point
        for part in geom.geoms:  # Iterate over each polygon in the MultiPolygon
            for point in part.exterior.coords:
                if point[1] < southernmost_point[1]:  # Compare y-coordinates
                    southernmost_point = point
        x, y = southernmost_point
    elif geom.geom_type == 'Polygon':
        # It's a single Polygon
        x, y = min(geom.exterior.coords, key=lambda coord: coord[1])
    else:
        # Skip geometries that are not Polygon or MultiPolygon
        continue
# Manually set the axes ranges based on the data bounds and population range
ax.set_xlim([data_bounds[0], data_bounds[2]])
ax.set_ylim([data_bounds[1], data_bounds[3]])
ax.set_zlim([pop_min * height_scaling_factor, pop_max * height_scaling_factor])

# Set labels and title
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_zlabel('Population')

# Set the ticks to show the latitude and longitude range
ax.set_xticks(np.linspace(data_bounds[0], data_bounds[2], num=5))
ax.set_yticks(np.linspace(data_bounds[1], data_bounds[3], num=5))

# Set the color bar to show the percentage change
sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis, norm=plt.Normalize(vmin=min_change, vmax=max_change))
sm.set_array([])
cbar = plt.colorbar(sm, shrink=0.5)
cbar.set_label('Yearly Population Change (%)')

# Save the plot to a file with higher DPI for better resolution
plt.savefig('/home/tomd/Documenti/demos/Data/italy_municipality_2022_yearly_growth_3d_comuni.png', dpi=300)

plt.show()
