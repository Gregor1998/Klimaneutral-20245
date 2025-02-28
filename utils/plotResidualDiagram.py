# ==============================================================================
# plotResidualDiagram.py
# ==============================================================================
# This script calculates and visualizes the residual load of an energy system.
# Residual load represents the difference between renewable energy generation
# and total energy consumption - showing the energy demand that cannot be met
# by renewable sources.
# 
# The script takes yearly generation and consumption data, calculates the
# difference for each time point, and then visualizes the absolute sum of
# residual loads for each year to track progress toward climate neutrality.
# ==============================================================================

import pandas as pd
import matplotlib.pyplot as plt
from utils.cleanse_dataframes import cleanse_dataframes
from matplotlib.ticker import FuncFormatter

def plotResidualDiagram(startYear, endYear, directory_yearly_generation, directory_yearly_consumption):
    """
    Creates a residual load diagram showing the gap between renewable energy generation and consumption.
    
    Parameters:
    - startYear: First year to analyze
    - endYear: Last year to analyze (exclusive)
    - directory_yearly_generation: Dictionary mapping years to energy generation DataFrames
    - directory_yearly_consumption: Dictionary mapping years to energy consumption DataFrames
    """
    # Create an empty DataFrame to store the results of all years
    all_years_difference_df = pd.DataFrame()

    # Iterate through each year in the given range
    for year in range(startYear, endYear): 
        if year in directory_yearly_generation and year in directory_yearly_consumption:
            # Clean the DataFrames to ensure they have consistent timestamps (handling leap years, daylight saving time)
            consumption_df, production_df = cleanse_dataframes(directory_yearly_consumption[year], directory_yearly_generation[year])
            
            # Calculate total renewable energy generation by summing all renewable sources
            required_columns = ['Wind Offshore', 'Wind Onshore', 'Photovoltaik', 'Wasserkraft', 'Sonstige Erneuerbare', 'Biomasse']
            if all(column in production_df.columns for column in required_columns):
                production_df['Gesamterzeugung_EE'] = production_df[required_columns].sum(axis=1)
            else:
                print(f"Eine oder mehrere der erforderlichen Spalten fehlen im DataFrame für das Jahr {year}.")
                continue
            
            # Verify that both DataFrames have the same timeline before calculating differences
            if consumption_df['Datum'].equals(production_df['Datum']):
                # Calculate the difference between renewable generation and consumption (residual load)
                difference_df = pd.DataFrame()
                difference_df['Datum'] = consumption_df['Datum']
                difference_df['Differenz'] =  production_df['Gesamterzeugung_EE'] - consumption_df['Gesamtverbrauch']
                difference_df['Jahr'] = year
                
                # Add the results to the combined DataFrame
                all_years_difference_df = pd.concat([all_years_difference_df, difference_df], ignore_index=True)
            else:
                print(f"Die Zeitachsen der DataFrames stimmen für das Jahr {year} nicht überein.")
        else:
            print(f"DataFrames für das Jahr {year} fehlen in einem der Verzeichnisse.")

    # Calculate the absolute sum of residual load for each year
    yearly_sums = all_years_difference_df.groupby('Jahr')['Differenz'].sum().abs()

    print(yearly_sums)

    # Create the line chart visualization
    plt.figure(figsize=(10, 6))
    plt.plot(yearly_sums.index, yearly_sums.values, marker='o', linestyle='-', color='b')

    # Format y-axis to use whole numbers with thousands separator
    formatter = FuncFormatter(lambda x, _: f'{int(x):,}')
    plt.gca().yaxis.set_major_formatter(formatter)

    # Add axis labels and title
    plt.xlabel('Jahr')
    plt.ylabel('Höhe der Resiudallast, bzw. was EE nicht decken konnte, in MWh')
    plt.title('Verlauf der Residuallast')
    plt.grid(True)
    
    # Save the plot as a PNG file
    plt.savefig('assets/plots/residual_diagramm.png')
    
    # Display the chart
    plt.show()
