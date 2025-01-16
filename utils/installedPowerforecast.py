import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import os 
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
# Faktoren, Variablen

# Füge den Pfad zu szenarioDefinition zum Python-Pfad hinzu
path =  "./simulation_szenario/simulation_szenario.py"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#from szenarioDefinition.szenario import *
from utils import config

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
installed_df[['PV', 'Onshore', 'Offshore']] = installed_df[['Photovoltaik', 'Wind Onshore', 'Wind Offshore']].apply(pd.to_numeric, errors='coerce')

# Define a function for trend projection
def project_trends(data, category, start_year, end_year, degree=2):
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

def project_growth_scenario(category, start_value, growth_rate, start_year, end_year):
    years = np.arange(start_year, end_year + 1)
    values = [start_value]
    for i in range(1, len(years)):
        if category == 'PV':
            new_value = values[-1] + growth_rate
            values.append(new_value)
        else:
            new_value = values[-1] * growth_rate
            values.append(new_value)
    return pd.DataFrame({'year': years, 'projected_capacity': values})

# Generate projections
regression_pv_start = 2013
regression_on_start =  2013
regression_off_start = 2016
start_year_growths_rates = 2023
end_year = config.params.end_year_extrapolation_installed_power

# Get 2023 start values
start_values = {
    'PV': installed_df.loc[installed_df['Jahr'].dt.year == 2023, 'PV'].values[0],
    'Onshore': installed_df.loc[installed_df['Jahr'].dt.year == 2023, 'Onshore'].values[0],
    'Offshore': installed_df.loc[installed_df['Jahr'].dt.year == 2023, 'Offshore'].values[0]}

regression_pv = project_trends(installed_df, 'PV', regression_pv_start, end_year, degree=2)
regression_on = project_trends(installed_df, 'Onshore', regression_on_start, end_year, degree=2)
regression_off = project_trends(installed_df, 'Offshore', regression_off_start, end_year, degree=2)

if not os.path.exists('./CSV/Installed/'):
    os.makedirs('./CSV/Installed/')

# Ensure the directory exists
output_dir = './CSV/Installed/'

# Save regression to CSV
regression_pv['PV'].to_csv(f'{output_dir}PV_regression.csv', index=False)
regression_on['Onshore'].to_csv(f'{output_dir}Onshore_regression.csv', index=False)
regression_off['Offshore'].to_csv(f'{output_dir}Wind_Offshore_regression.csv', index=False)


# Generate and save projections

all_projections = {}

for category in ['PV', 'Onshore', 'Offshore']:
    all_projections[category] = {}
    growth_rate = getattr(config.params, f"growth_rate_{category}")  # Use the growth rate from szenarien.py for each category
    projections = project_growth_scenario(category, start_values[category], growth_rate, start_year_growths_rates, end_year)
    
    filename = f'{output_dir}{category}_projections.csv'
    
    projections.to_csv(filename, index=False)
    all_projections[category] = projections


# Plot projections and save to file
plt.figure(figsize=(12, 8))

# Plot PV projections
plt.subplot(3, 1, 1)
plt.plot(regression_pv['PV']['year'], regression_pv['PV']['predicted_capacity'], label='Regression')
plt.plot(all_projections['PV']['year'], all_projections['PV']['projected_capacity'], label=f'PV {config.params.PV_scenario}')
plt.xlabel('Year')
plt.ylabel('Installed Capacity (MW)')
plt.title('PV Projections')
plt.legend()
plt.grid(True)

# Plot Wind Onshore projections
plt.subplot(3, 1, 2)
plt.plot(regression_on['Onshore']['year'], regression_on['Onshore']['predicted_capacity'], label='Regression')
plt.plot(all_projections['Onshore']['year'], all_projections['Onshore']['projected_capacity'], label=f'Wind Onshore {config.params.Onshore_scenario}')
plt.xlabel('Year')
plt.ylabel('Installed Capacity (MW)')
plt.title('Wind Onshore Projections')
plt.legend()
plt.grid(True)

# Plot Wind Offshore projections
plt.subplot(3, 1, 3)
plt.plot(regression_off['Offshore']['year'], regression_off['Offshore']['predicted_capacity'], label='Regression')
plt.plot(all_projections['Offshore']['year'], all_projections['Offshore']['projected_capacity'], label=f'Wind Offshore {config.params.Offshore_scenario}')
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
