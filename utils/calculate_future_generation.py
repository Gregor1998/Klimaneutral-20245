"""
Module: calculate_future_generation.py
--------------------------------------------------
This module calculates the forecasted renewable energy generation for future years based on
projected capacity installations and historical performance profiles.

The main function 'calculate_future_generation' takes historical performance data and 
generation data from a start year, then projects generation for each year up to the end year
based on capacity projections and daily expansion rates.

Parameters:
- dataFrame_performance: DataFrame with performance profiles for renewable sources
- dataFrame_generation_start_year: DataFrame with generation data for the start year
- gridlost: Grid loss factor to be applied to generation values
- start_year: First year for projections
- end_year: Last year for projections

Returns:
- Dictionary with yearly DataFrames containing projected generation for each renewable source
"""

import pandas as pd
from utils.addTimePerformance import addTimePerformance
#from szenarioDefinition.szenario import *
from utils import config


def calculate_future_generation(dataFrame_performance, dataFrame_generation_start_year, gridlost, start_year, end_year):
    # Erstellung eines leeren Dictionaries für die Generation
    # Creates an empty dictionary to store generation data for each year
    directoryGeneration = {}

    # Kopieren der DataFrames, um die Originaldaten nicht zu verändern
    # Create copies of input DataFrames to avoid modifying the original data
    df_performance = dataFrame_performance.copy()
    df_generation_start_year = dataFrame_generation_start_year.copy()

    # Pfade zu den CSV-Dateien, je nach Case
    # Select appropriate CSV files based on scenario configuration
    if config.params.scenario_name != 'SMARD':
        # Use projection files for non-SMARD scenarios
        filepath_PV = f'CSV/Installed/PV_projections.csv'
        filepath_Onshore = f'CSV/Installed/Onshore_projections.csv'
        filepath_Offshore = f'CSV/Installed/Offshore_projections.csv'
    else:
        # Use regression-based files for SMARD scenario
        filepath_PV = f'CSV/Installed/PV_regression.csv'
        filepath_Onshore = f'CSV/Installed/Onshore_regression.csv'
        filepath_Offshore = f'CSV/Installed/Offshore_regression.csv'

    # Einlesen der CSV-Dateien
    # Load capacity projection data from CSV files
    df_PV = pd.read_csv(filepath_PV)
    df_Onshore = pd.read_csv(filepath_Onshore)
    df_Offshore = pd.read_csv(filepath_Offshore)

    # Alle Daten ab start_year sind von Interesse
    # Filter data to include only years from start_year onwards
    df_filtered_PV = df_PV[df_PV['year'] >= start_year].reset_index(drop=True)
    df_filtered_Onshore = df_Onshore[df_Onshore['year'] >= start_year].reset_index(drop=True)
    df_filtered_Offshore = df_Offshore[df_Offshore['year'] >= start_year].reset_index(drop=True)

    # Determine which column to use based on scenario
    if config.params.scenario_name != 'SMARD':
        column_name = 'projected_capacity'
    else:
        column_name = 'predicted_capacity'
 
    # Zusammenführen der Daten
    # Combine capacity data from different sources into a single DataFrame
    df_combined = pd.concat([
        df_filtered_PV['year'],
        df_filtered_PV[column_name],
        df_filtered_Onshore[column_name],
        df_filtered_Offshore[column_name]
    ], axis=1)

    df_combined.columns = ['Jahr', 'Photovoltaik', 'Wind Onshore', 'Wind Offshore']

    # Umwandlung in ein Dictionary
    # Convert capacity data to a dictionary indexed by year for easier access
    directoryInstalled = df_combined.set_index('Jahr').to_dict(orient='index')

    # Process each year from start_year to end_year
    for year in range(start_year, end_year + 1):
        # Calculate daily expansion rates for each technology
        if year + 1 in directoryInstalled:  # Falls ein Folgejahr existiert (If next year exists in data)
            # Calculate daily capacity increase rate by dividing yearly increase by 365 days
            dayly_expansion_rate_PV = (directoryInstalled[year + 1]['Photovoltaik'] - directoryInstalled[year]['Photovoltaik']) / 365
            dayly_expansion_rate_Onshore = (directoryInstalled[year + 1]['Wind Onshore'] - directoryInstalled[year]['Wind Onshore']) / 365
            dayly_expansion_rate_Offshore = (directoryInstalled[year + 1]['Wind Offshore'] - directoryInstalled[year]['Wind Offshore']) / 365
        else:  # Keine Daten für das Folgejahr vorhanden (No data available for next year)
            # No expansion if data for next year is missing
            dayly_expansion_rate_PV = 0
            dayly_expansion_rate_Onshore = 0
            dayly_expansion_rate_Offshore = 0

        # Prepare lists to store generation values for each technology
        PV_generation = []
        Onshore_generation = []
        Offshore_generation = []

        # Calculate generation for each day of the year
        for day in range(365):
            # Calculate start and end indices in the performance data (96 values per day)
            start_index = day * 96
            end_index = (day + 1) * 96

            # Calculate daily capacity considering the expansion rate
            # Multiply by 0.25 to convert from MW to MWh/15min (quarter-hourly data)
            daily_PV = (directoryInstalled[year]['Photovoltaik'] + day * dayly_expansion_rate_PV) * 0.25
            daily_Onshore = (directoryInstalled[year]['Wind Onshore'] + day * dayly_expansion_rate_Onshore) * 0.25
            daily_Offshore = (directoryInstalled[year]['Wind Offshore'] + day * dayly_expansion_rate_Offshore) * 0.25

            # Apply performance profiles to calculate generation and add to lists
            PV_generation.extend(df_performance['Photovoltaik'].iloc[start_index:end_index] * daily_PV)
            Onshore_generation.extend(df_performance['Wind Onshore'].iloc[start_index:end_index] * daily_Onshore)
            Offshore_generation.extend(df_performance['Wind Offshore'].iloc[start_index:end_index] * daily_Offshore)

        # Create a DataFrame with calculated generation values
        # Keep hydropower, biomass and other renewables from the start year unchanged
        combined_generation = pd.DataFrame({
            'Photovoltaik': PV_generation,
            'Wind Onshore': Onshore_generation,
            'Wind Offshore': Offshore_generation,
            'Wasserkraft': df_generation_start_year['Wasserkraft'],
            'Biomasse': df_generation_start_year['Biomasse'],
            'Sonstige Erneuerbare': df_generation_start_year['Sonstige Erneuerbare']
        })

        # Apply grid loss factor to account for transmission losses
        combined_generation *= config.params.gridlost

        # Verify that all required columns are present
        required_columns = ['Photovoltaik', 'Wind Onshore', 'Wind Offshore', 'Wasserkraft', 'Biomasse', 'Sonstige Erneuerbare']
        if all(column in combined_generation.columns for column in required_columns):
            # Calculate total renewable generation as sum of all sources
            combined_generation['Gesamterzeugung_EE'] = combined_generation[required_columns].sum(axis=1)
        else:
            raise ValueError(f'Nicht alle Spalten vorhanden: {required_columns}')
        
        # Add time information (date, hour, etc.) to the DataFrame
        addTimePerformance(combined_generation, year)
        
        # Store the yearly DataFrame in the result dictionary
        directoryGeneration[year] = combined_generation

    return directoryGeneration