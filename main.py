import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

def load_data(file_path):
    # Step 1: Load Demographic Data
    demographic_data = pd.read_csv(file_path, delimiter=';')
    return demographic_data

file_path = r'/home/tomd/Documenti/demos/Data/Bilancio_demografico_mensile_2022.csv'
demographic_data = load_data(file_path)

# Step 2: Calculate Yearly Population Change
# Adjusting the code to calculate 'Popolazione fine periodo' for Mese=15 and Sesso='Totale'
# and 'Popolazione inizio periodo' for Mese=1 and Sesso='Totale'

# Filter the dataset for the conditions
start_population = demographic_data[(demographic_data['Mese'] == 1) & (demographic_data['Sesso'] == 'Totale')]
end_population = demographic_data[(demographic_data['Mese'] == 15) & (demographic_data['Sesso'] == 'Totale')]

# Group by 'Regione' and sum up 'Popolazione inizio periodo' and 'Popolazione fine periodo'
start_population_grouped = start_population.groupby('Regione')['Popolazione inizio periodo'].sum()
end_population_grouped = end_population.groupby('Regione')['Popolazione fine periodo'].sum()

# Create a new DataFrame to hold the calculated data
yearly_population_data = pd.DataFrame({
    'Popolazione inizio periodo': start_population_grouped,
    'Popolazione fine periodo': end_population_grouped
}).reset_index()

# Calculate the 'Percentage Change'
yearly_population_data['Percentage Change'] = (
    (yearly_population_data['Popolazione fine periodo'] - yearly_population_data['Popolazione inizio periodo']) /
    yearly_population_data['Popolazione inizio periodo'] * 100
)

# Step 3: Load Italy Map Data
# You need to provide the path to a GeoJSON or shapefile that contains the Italy regions.
# For example: italy_regions_geojson = '/path/to/italy_regions.geojson'
# Ensure the GeoJSON or shapefile path is correct
italy_regions_geojson = r'/home/tomd/Documenti/demos/Data/limits_IT_regions.geojson'  # Adjust the path as needed
# Load the detailed Italy municipalities map data
italy_municipalities_geojson = r'/home/tomd/Documenti/demos/Data/limits_IT_municipalities.geojson'
# Load the detailed Italy regions map data
italy_regions_map = gpd.read_file(italy_regions_geojson)
# Load the detailed Italy municipalities map data
italy_municipalities_map = gpd.read_file(italy_municipalities_geojson)

# Step 4: Merge Population Data with Map Data
# Make sure the 'Regione' column in your data matches the corresponding column in the geospatial data
# You might need to adjust 'name' to the correct column from your geospatial data that contains the region names
italy_population_map = italy_regions_map.set_index('reg_name').join(yearly_population_data.set_index('Regione'))

# Step 5: Create the Map Visualization
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.1)

# Use 'Percentage Change' for coloring if the merge was successful
# If the merge failed because of a mismatch in region names, this will not plot correctly
italy_population_map.plot(column='Percentage Change', cmap='RdYlGn', legend=True, ax=ax, cax=cax)

ax.set_title('Yearly Percentage Change of Population Growth by Region in Italy (2022)')
ax.set_axis_off()

# Specify the path where you want to save the image
plt.savefig(r'/home/tomd/Documenti/demos/Data/italy_region_2022_yearly_growth.png')

# Close the plot if you're running this in a script
plt.close()
# Group by 'Comune' (municipality) and sum up 'Popolazione inizio periodo' and 'Popolazione fine periodo'
# Assuming the demographic data contains a 'Comune' column
start_population_grouped_com = start_population.groupby('Comune')['Popolazione inizio periodo'].sum()
end_population_grouped_com = end_population.groupby('Comune')['Popolazione fine periodo'].sum()

# Create a new DataFrame to hold the calculated data for municipalities
yearly_population_data_com = pd.DataFrame({
    'Popolazione inizio periodo': start_population_grouped_com,
    'Popolazione fine periodo': end_population_grouped_com
}).reset_index()

# Calculate the 'Percentage Change' for municipalities
yearly_population_data_com['Percentage Change'] = (
    (yearly_population_data_com['Popolazione fine periodo'] - yearly_population_data_com['Popolazione inizio periodo']) /
    yearly_population_data_com['Popolazione inizio periodo'] * 100
)
print(yearly_population_data_com)
# Load the detailed Italy municipalities map data
italy_municipalities_map = gpd.read_file(italy_municipalities_geojson)

# Merge Population Data with Map Data for municipalities
italy_population_map_com = italy_municipalities_map.set_index('name').join(yearly_population_data_com.set_index('Comune'))

# Create the Map Visualization for municipalities
fig, ax = plt.subplots(1, 1, figsize=(15, 15))  # Adjust size as needed for detail
italy_population_map_com.plot(column='Percentage Change', cmap='RdYlGn', legend=True, ax=ax)
ax.set_title('Yearly Percentage Change of Population Growth by Municipality in Italy (2022)')
ax.axis('off')  # Turn off axis
plt.savefig('/home/tomd/Documenti/demos/Data/italy_municipality_2022_yearly_growth.png')
plt.close()