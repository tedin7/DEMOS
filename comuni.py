import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.express as px

# File paths
demographic_data_file = '/home/tomd/Documenti/demos/Data/Bilancio_demografico_mensile_2022.csv'
municipalities_geojson_file = '/home/tomd/Documenti/demos/Data/limits_IT_municipalities.geojson'
output_path = '/home/tomd/Documenti/demos/Data/italy_municipality_2022_yearly_growth.png'
output_path_plotly = '/home/tomd/Documenti/demos/Data/italy_municipality_2022_yearly_growth_plotly.png'
quantile_list = [0.05, 0.95]
# Load Demographic Data
demographic_data = pd.read_csv(demographic_data_file, delimiter=';')

# Apply the specified filters for 'Popolazione inizio periodo' and 'Popolazione fine periodo'
start_population_comune = demographic_data[
    (demographic_data['Mese'] == 1) & (demographic_data['Sesso'] == 'Totale')]
end_population_comune = demographic_data[
    (demographic_data['Mese'] == 15) & (demographic_data['Sesso'] == 'Totale')]

# Group by 'Comune' and sum up 'Popolazione inizio periodo' and 'Popolazione fine periodo' with the filtered data
start_population_grouped_com = start_population_comune.groupby('Comune')['Popolazione inizio periodo'].sum()
end_population_grouped_com = end_population_comune.groupby('Comune')['Popolazione fine periodo'].sum()

# Create a new DataFrame to hold the calculated data for municipalities with the correct conditions
yearly_population_data_com = pd.DataFrame({
    'Popolazione inizio periodo': start_population_grouped_com,
    'Popolazione fine periodo': end_population_grouped_com
}).reset_index()

# Calculate the 'Percentage Change' for municipalities
yearly_population_data_com['Percentage Change'] = (
    (yearly_population_data_com['Popolazione fine periodo'] - yearly_population_data_com['Popolazione inizio periodo']) /
    yearly_population_data_com['Popolazione inizio periodo'] * 100
)


# Ensure 'Comune' in demographic data is in the correct format for merging
demographic_data['Comune'] = demographic_data['Comune'].str.title()

# Load the detailed Italy municipalities map data
italy_municipalities_map = gpd.read_file(municipalities_geojson_file)

# Merge the updated population data with the GeoJSON map data
italy_population_map_com = italy_municipalities_map.set_index('name').join(yearly_population_data_com.set_index('Comune'))
# Check for NaN values in the merged DataFrame
print("Number of NaN values in 'Percentage Change':", italy_population_map_com['Percentage Change'].isna().sum())

# You can choose to fill NaN values with a default value, such as 0
italy_population_map_com['Percentage Change'].fillna(0, inplace=True)

# Define the quantiles for color scaling
quantile_list = [0.05, 0.95]
quantiles = yearly_population_data_com['Percentage Change'].quantile(quantile_list)

# Create the map visualization
fig, ax = plt.subplots(1, 1, figsize=(20, 20))
geojson = italy_municipalities_map.geometry.__geo_interface__

# Plot the population data
italy_population_map_com.plot(
    column='Percentage Change', 
    cmap='RdYlGn', 
    legend=True, 
    legend_kwds={
        'label': "Yearly Change (%)", 
        'orientation': "horizontal",
        'shrink': 0.5
    },
    vmin=quantiles.iloc[0], 
    vmax=quantiles.iloc[1], 
    ax=ax, 
    alpha=0.8
)

# Set the title and remove axis
ax.set_title('Yearly Percentage Change of Population Growth by Municipality in Italy (2022)')
ax.axis('off')

# Save and close the plot
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"Map has been saved to {output_path}")

# Assuming all previous steps are the same and you have your 'italy_population_map_com' ready

# Convert the GeoDataFrame to JSON format
geojson = italy_municipalities_map.__geo_interface__

# If 'name' was the index, after reset_index it will be in the column 'index'
# Before creating the choropleth, reset the index of your DataFrame to make 'Comune' a column
italy_population_map_com.reset_index(inplace=True)

# Then create the choropleth map
fig = px.choropleth(italy_population_map_com, 
                    geojson=geojson,
                    locations='name',  # Now 'Comune' is a column in the DataFrame
                    color='Percentage Change',
                    color_continuous_scale="Viridis",
                    range_color=(quantiles.iloc[0], quantiles.iloc[1]),
                    featureidkey="properties.name",
                    labels={'Percentage Change':'Yearly Population Change (%)'}
                   )
# The rest of your code for updating the layout and saving the figure...


# Update the layout of the map
fig.update_traces(marker_line_width=0, selector=dict(type='choropleth'))  # Remove borders around regions

fig.update_layout(
    coloraxis_colorbar=dict(
        title="Yearly Change",
        tickvals=[-2, -1, 0, 1],
        ticktext=['-2%', '-1%', '0%', '+1%']
    )
)

# Customize map appearance
fig.update_geos(
    showcountries=False,  # Hide country borders
    showsubunits=True,  # Show subunit borders (regions within countries)
    subunitcolor="grey"  # Color for the subunit borders
)

# Remove the background map for a cleaner look
fig.update_geos(
    showland=False, 
    showocean=False,
    showlakes=False,
    showrivers=False
)
fig.update_geos(
    visible=False, 
    projection_type="mercator",
    scope="europe",
    center={"lat": 41.8719, "lon": 12.5674},  # Center on Italy
    lataxis_range=[36, 48],  # Latitude range for Italy
    lonaxis_range=[6, 19]    # Longitude range for Italy
)
fig.update_layout(
    margin={"r":0,"t":0,"l":0,"b":0},
    coloraxis_colorbar=dict(
        title="Yearly Change",
        thicknessmode="pixels", thickness=15,
        lenmode="pixels", len=300,
        yanchor="top", y=1,
        ticks="outside", ticksuffix="%"
    )
)

# Adjust the hover information
fig.update_traces(
    hoverinfo='location+name+z',
    hovertemplate="<b>%{location}</b><br>Change: %{z}%<extra></extra>"
)

#fig.show()


# Display the figure in a Jupyter notebook or an interactive Python environment:
# fig.show()

# Save the figure to a file:
fig.write_image(output_path_plotly)

print(f"Interactive map has been saved to {output_path_plotly}")
