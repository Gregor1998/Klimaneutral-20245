import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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
def project_trends(data, start_year, end_year, degree=1):
    projections = {}
    for category in ['Photovoltaik', 'Wind Onshore', 'Wind Offshore']:
        category_data = data[['Jahr', category]].dropna()
        category_data = category_data[category_data['Jahr'].dt.year >= start_year]
        X = category_data['Jahr'].dt.year.values.reshape(-1, 1)
        y = category_data[category].values
        poly = PolynomialFeatures(degree=degree)
        X_poly = poly.fit_transform(X)
        model = LinearRegression()
        model.fit(X_poly, y)
        future_years = np.arange(start_year, end_year + 1).reshape(-1, 1)
        predictions = model.predict(poly.transform(future_years))
        projections[category] = pd.DataFrame({'year': future_years.flatten(), 'predicted_capacity': predictions})
    return projections

# Generate projections
scenarios = {'worst_case': 2010, 'mid_case': 2019, 'best_case': 2021}
end_year = 2030
scenario_projections = {scenario: project_trends(installed_df, start_year, end_year, degree=2) for scenario, start_year in scenarios.items()}

# Plot projections
plt.figure(figsize=(12, 8))
for scenario, projections in scenario_projections.items():
    for category, df in projections.items():
        plt.plot(df['year'], df['predicted_capacity'], label=f'{scenario} - {category}')
plt.xlabel('Year')
plt.ylabel('Installed Capacity (MW)')
plt.title('Projections of Installed Capacities for PV, Wind Onshore, and Offshore')
plt.legend()
plt.grid(True)
plt.show()

# Save projections to CSV
for scenario, projections in scenario_projections.items():
    for category, df in projections.items():
        df.to_csv(f'{scenario}_{category}_projections.csv', index=False)
