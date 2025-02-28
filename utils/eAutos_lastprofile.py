"""
eAutos_lastprofile.py - E-Mobility Load Profile Generator

This script calculates and generates load profiles for electric vehicles in Germany based on:
- Different location types (residential, office, public charging stations)
- Day types (weekday, Saturday, Sunday)
- Annual projections with increasing e-vehicle adoption rates

The script:
1. Reads base load profiles from CSV files
2. Scales them according to projected e-vehicle numbers
3. Calculates energy demand based on vehicle count and average consumption
4. Generates yearly load profiles from start to end simulation year
5. Distributes vehicles across different charging location types

Outputs are saved as CSV files organized by year, location type, and day type.
"""

import pandas as pd
import os
from utils import config

# Configuration parameters
eAutoskWh = config.params.eAutoskWh  # Average energy consumption per e-vehicle in kWh
eAutosNow = config.params.eAutosNow  # 1.4 Mio eAutos in Deutschland Stand 2023
eAutosIncrease = config.params.eAutosIncrease  # Annual increase in e-vehicle numbers 
wochentage = ['Wochentag', 'Samstag', 'Sonntag']  # Day types for load profiles
lastprofilTypes = ['Wohnen', 'Büro', 'Öffentliche_Ladepunkte']  # Types of charging locations

# Distribution of e-vehicles across different charging location types
chargin_distribution = {
    'Wohnen': config.params.chargin_distribution_home,  # Percentage charging at home
    'Büro': config.params.chargin_distribution_office,  # Percentage charging at office
    'Öffentliche_Ladepunkte': config.params.chargin_distribution_public  # Percentage charging at public stations
}

def calcLastprofil(year, eAutosAmount, lastprofilType):
    """
    Calculate and generate load profiles for a specific year, e-vehicle amount, and charging location type
    
    Args:
        year: The year for which to calculate the load profile
        eAutosAmount: Number of e-vehicles for this location type
        lastprofilType: Type of charging location (residential, office, public)
    """
    # Process each day type (weekday, Saturday, Sunday)
    for tag in wochentage:
        # Define input and output file paths
        filepath_lp = f'CSV/Lastprofile/eMobilitaet/base/{lastprofilType}/{tag}.csv'
        output_dir = f'CSV/Lastprofile/eMobilitaet/{year}/{lastprofilType}'
        output_filepath = f'{output_dir}/{tag}.csv'

        # Read base load profile from CSV file
        lp = pd.read_csv(filepath_lp, delimiter=';')

        # Convert relative consumption values from German to standard format (comma to dot)
        lp['Relativer Bedarf'] = lp['Relativer Bedarf'].str.replace(',', '.').astype(float)

        # Calculate normalized values and energy demand
        sum_relative_bedarf = lp['Relativer Bedarf'].sum()

        # Normalize relative demand to ensure sum equals 1
        lp['Normierter Bedarf'] = lp['Relativer Bedarf'] / sum_relative_bedarf

        # Calculate number of vehicles charging at each time step
        lp['Anzahl Autos'] = lp['Normierter Bedarf'] * eAutosAmount

        # Calculate energy demand in kWh based on vehicle count
        lp['Strombedarf (kWh)'] = lp['Anzahl Autos'] * eAutoskWh

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Save the calculated load profile to CSV
        lp.to_csv(output_filepath, index=False, sep=';')

# Main execution loop: Process each simulation year
for year in range(config.params.start_year_simulation-1, config.params.end_year_simulation+1):
    # For each charging location type, calculate yearly load profiles
    for lastprofilType in lastprofilTypes:
        # Calculate number of e-vehicles for this location type based on distribution
        eAutos_per_chargin_area = eAutosNow * chargin_distribution[lastprofilType]
        
        # Generate the load profile for this year and location type
        calcLastprofil(year, eAutos_per_chargin_area, lastprofilType)

    # Increase the total number of e-vehicles for the next year
    eAutosNow += eAutosIncrease