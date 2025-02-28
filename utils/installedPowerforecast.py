"""
Installed Power Forecast Module
-------------------------------
This module analyzes historical data of installed power capacities for renewable energy
sources (Photovoltaic, Wind Onshore, Wind Offshore) and projects future capacities.

The module provides:
- Data loading and preprocessing of installed capacities
- Polynomial regression-based trend projections
- Growth rate-based scenario projections
- Visualization of projections
- CSV exports of calculated forecasts

The projections are used for simulation scenarios to estimate future renewable energy production.
"""

# Import necessary libraries for data handling, modeling, and visualization
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import os 
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

# Setup path for importing configuration
path =  "./simulation_szenario/simulation_szenario.py"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import config

# Load the installed capacity data from CSV file
data = pd.read_csv('./CSV/Installed/smard_installierte_leistungen.csv', delimiter=';')

# Clean column names by removing quotes and extra spaces
data.columns = [col.strip().replace('"', '') for col in data.columns]

# Validate that all required columns are present in the dataset
expected_columns = ['Jahr', 'Photovoltaik', 'Wind Onshore', 'Wind Offshore']
if not all(col in data.columns for col in expected_columns):
    raise KeyError(f"Missing columns in dataset: {set(expected_columns) - set(data.columns)}")

# Select and preprocess columns: convert year to datetime and numeric values for power capacities
installed_df = data[['Jahr', 'Photovoltaik', 'Wind Onshore', 'Wind Offshore']]
installed_df['Jahr'] = pd.to_datetime(installed_df['Jahr'], format='%Y')
installed_df[['PV', 'Onshore', 'Offshore']] = installed_df[['Photovoltaik', 'Wind Onshore', 'Wind Offshore']].apply(pd.to_numeric, errors='coerce')

# Define function for trend projection using polynomial regression
def project_trends(data, category, start_year, end_year, degree=2):
    """
    Project future capacity trends using polynomial regression.
    
    Args:
        data: DataFrame with historical data
        category: Column name of capacity to project (PV, Onshore, Offshore)
        start_year: Starting year for regression analysis
        end_year: End year for projection
        degree: Polynomial degree for the regression model
        
    Returns:
        Dictionary with projection results as DataFrame
    """
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
    
    # Generate projections for future years
    future_years = np.arange(start_year, end_year + 1).reshape(-1, 1)
    predictions = model.predict(poly.transform(future_years))
    
    # Enforce non-decreasing trend (capacity should not decrease over time)
    predictions = np.maximum.accumulate(predictions)
    
    projections[category] = pd.DataFrame({'year': future_years.flatten(), 'predicted_capacity': predictions})
    return projections

# Define function for projecting based on annual growth rates
def project_growth_scenario(category, start_value, growth_rate, start_year, end_year):
    """
    Project capacity based on specified growth rates.
    
    Args:
        category: Type of energy (PV, Onshore, Offshore)
        start_value: Initial capacity value
        growth_rate: Annual growth rate (absolute for PV, percentage for wind)
        start_year: Starting year for projection
        end_year: End year for projection
        
    Returns:
        DataFrame with projected capacities by year
    """
    years = np.arange(start_year, end_year + 1)
    values = [start_value]
    
    # Calculate growth based on different models for PV vs Wind
    for i in range(1, len(years)):
        if category == 'PV':
            # PV uses absolute growth in MW per year
            new_value = values[-1] + growth_rate
            values.append(new_value)
        else:
            # Wind uses multiplicative growth (percentage)
            new_value = values[-1] * growth_rate
            values.append(new_value)
    return pd.DataFrame({'year': years, 'projected_capacity': values})

# Configure projection parameters
regression_pv_start = 2013
regression_on_start = 2013
regression_off_start = 2016
start_year_growths_rates = 2023
end_year = config.params.end_year_extrapolation_installed_power

# Get 2023 capacity values as starting points for projections
start_values = {
    'PV': installed_df.loc[installed_df['Jahr'].dt.year == 2023, 'PV'].values[0],
    'Onshore': installed_df.loc[installed_df['Jahr'].dt.year == 2023, 'Onshore'].values[0],
    'Offshore': installed_df.loc[installed_df['Jahr'].dt.year == 2023, 'Offshore'].values[0]}

# Generate trend-based projections using polynomial regression
regression_pv = project_trends(installed_df, 'PV', regression_pv_start, end_year, degree=2)
regression_on = project_trends(installed_df, 'Onshore', regression_on_start, end_year, degree=2)
regression_off = project_trends(installed_df, 'Offshore', regression_off_start, end_year, degree=2)

# Ensure output directory exists
if not os.path.exists('./CSV/Installed/'):
    os.makedirs('./CSV/Installed/')

output_dir = './CSV/Installed/'

# Save regression results to CSV files
regression_pv['PV'].to_csv(f'{output_dir}PV_regression.csv', index=False)
regression_on['Onshore'].to_csv(f'{output_dir}Onshore_regression.csv', index=False)
regression_off['Offshore'].to_csv(f'{output_dir}Offshore_regression.csv', index=False)

# Generate and save growth-based scenario projections
all_projections = {}

for category in ['PV', 'Onshore', 'Offshore']:
    all_projections[category] = {}
    # Get growth rate from configuration for each energy type
    growth_rate = getattr(config.params, f"growth_rate_{category}")
    projections = project_growth_scenario(category, start_values[category], growth_rate, start_year_growths_rates, end_year)
    
    filename = f'{output_dir}{category}_projections.csv'
    projections.to_csv(filename, index=False)
    all_projections[category] = projections

# Create visualization of projections
plt.figure(figsize=(12, 8))

# Plot PV projections: compare regression-based and growth-based scenarios
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

# Save the visualization to a PNG file
plot_filename = f'{output_dir}installed_capacities_projections.png'
plt.tight_layout()
plt.savefig(plot_filename)
plt.close()
