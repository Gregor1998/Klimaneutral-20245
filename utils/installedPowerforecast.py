import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os 
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

# Load the data
data = pd.read_csv('./CSV/Installed/smard_installierte_leistungen.csv', delimiter=';')

# Clean column names
data.columns = [col.strip().replace('"', '') for col in data.columns]

# Ensure correct column names are used
expected_columns = ['Jahr', 'Photovoltaik', 'Wind Onshore', 'Wind Offshore']
if not all(col in data.columns for col in expected_columns):
    raise KeyError(f"Missing columns in dataset: {set(expected_columns) - set(data.columns)}")

# Select and preprocess relevant columns
installed_df = data[['Jahr', 'Photovoltaik', 'Wind Onshore', 'Wind Offshore']]
installed_df['Jahr'] = pd.to_datetime(installed_df['Jahr'], format='%Y')
installed_df[['Photovoltaik', 'Wind Onshore', 'Wind Offshore']] = installed_df[['Photovoltaik', 'Wind Onshore', 'Wind Offshore']].apply(pd.to_numeric, errors='coerce')

# Define a function for trend projection
def project_trends(data, category, start_year, end_year, degree=1):
    projections = {}
    category_data = data[['Jahr', category]].dropna()
    category_data = category_data[category_data['Jahr'].dt.year >= start_year]
    X = category_data['Jahr'].dt.year.values.reshape(-1, 1)
    y = category_data[category].values
    
    # Fit polynomial regression model
    poly = PolynomialFeatures(degree=degree)
    X_poly = poly.fit_transform(X)
    model = LinearRegression()
    model.fit(X_poly, y)
    
    # Generate projections
    future_years = np.arange(start_year, end_year + 1).reshape(-1, 1)
    predictions = model.predict(poly.transform(future_years))
    
    # Enforce non-decreasing trend
    predictions = np.maximum.accumulate(predictions)
    
    projections[category] = pd.DataFrame({'year': future_years.flatten(), 'predicted_capacity': predictions})
    return projections

def project_growth_scenario(start_value, growth_rate, start_year, end_year):
    years = np.arange(start_year, end_year + 1)
    values = [start_value]
    for i in range(1, len(years)):
        new_value = values[-1] * (1 + growth_rate / 100)
        values.append(new_value)
    return pd.DataFrame({'year': years, 'projected_capacity': values})

# Generate projections
regression_pv_start = 2013
regression_on_start =  2013
regression_off_start = 2016
start_year_growths_rates = 2023
end_year = 2030

projections_pv = project_trends(installed_df, 'Photovoltaik', regression_pv_start, end_year, degree=2)
projections_on = project_trends(installed_df, 'Wind Onshore', regression_on_start, end_year, degree=2)
projections_off = project_trends(installed_df, 'Wind Offshore', regression_off_start, end_year, degree=2)

growth_rates = {
    'Photovoltaik': {'worst': 8.8, 'average': 12.9, 'best': 16.9},
    'Wind Onshore': {'worst': 3.3, 'average': 6.6, 'best': 10.4},
    'Wind Offshore': {'worst': 3.0, 'average': 13.1, 'best': 23.2}
}

if not os.path.exists('./CSV/Installed/'):
    os.makedirs('./CSV/Installed/')

# Ensure the directory exists
output_dir = './CSV/Installed/'

# Save projections to CSV
projections_pv['Photovoltaik'].to_csv(f'{output_dir}Photovoltaik_projections.csv', index=False)
projections_on['Wind Onshore'].to_csv(f'{output_dir}Wind_Onshore_projections.csv', index=False)
projections_off['Wind Offshore'].to_csv(f'{output_dir}Wind_Offshore_projections.csv', index=False)

# Get 2023 start values
start_values = {
    'Photovoltaik': installed_df.loc[installed_df['Jahr'].dt.year == 2023, 'Photovoltaik'].values[0],
    'Wind Onshore': installed_df.loc[installed_df['Jahr'].dt.year == 2023, 'Wind Onshore'].values[0],
    'Wind Offshore': installed_df.loc[installed_df['Jahr'].dt.year == 2023, 'Wind Offshore'].values[0]}

# Generate and save projections
scenarios = ['worst', 'average', 'best']
all_projections = {}

for category, rates in growth_rates.items():
    all_projections[category] = {}
    for scenario in scenarios:
        projections = project_growth_scenario(start_values[category], rates[scenario], start_year_growths_rates, end_year)
        filename = f'{output_dir}{category}_{scenario}_projection.csv'
        projections.to_csv(filename, index=False)
        all_projections[category][scenario] = projections

# Plot projections and save to file
plt.figure(figsize=(12, 8))

# Plot Photovoltaik projections
plt.subplot(3, 1, 1)
plt.plot(projections_pv['Photovoltaik']['year'], projections_pv['Photovoltaik']['predicted_capacity'], label='Regression')
for scenario in scenarios:
    plt.plot(all_projections['Photovoltaik'][scenario]['year'], all_projections['Photovoltaik'][scenario]['projected_capacity'], label=f'Photovoltaik {scenario}')
plt.xlabel('Year')
plt.ylabel('Installed Capacity (MW)')
plt.title('Photovoltaik Projections')
plt.legend()
plt.grid(True)

# Plot Wind Onshore projections
plt.subplot(3, 1, 2)
plt.plot(projections_on['Wind Onshore']['year'], projections_on['Wind Onshore']['predicted_capacity'], label='Regression')
for scenario in scenarios:
    plt.plot(all_projections['Wind Onshore'][scenario]['year'], all_projections['Wind Onshore'][scenario]['projected_capacity'], label=f'Wind Onshore {scenario}')
plt.xlabel('Year')
plt.ylabel('Installed Capacity (MW)')
plt.title('Wind Onshore Projections')
plt.legend()
plt.grid(True)

# Plot Wind Offshore projections
plt.subplot(3, 1, 3)
plt.plot(projections_off['Wind Offshore']['year'], projections_off['Wind Offshore']['predicted_capacity'], label='Regression')
for scenario in scenarios:
    plt.plot(all_projections['Wind Offshore'][scenario]['year'], all_projections['Wind Offshore'][scenario]['projected_capacity'], label=f'Wind Offshore {scenario}')
plt.xlabel('Year')
plt.ylabel('Installed Capacity (MW)')
plt.title('Wind Offshore Projections')
plt.legend()
plt.grid(True)

# Save the plot to a file
plot_filename = f'{output_dir}installed_capacities_projections.png'
plt.tight_layout()
plt.savefig(plot_filename)
plt.close()

