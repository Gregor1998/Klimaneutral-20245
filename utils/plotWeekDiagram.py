from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator, DateFormatter
from utils.addTimeInformation import addTimeInformation
from utils.calcDifference_storage_flexpowerplant import StorageIntegration, differenceBetweenDataframes

def plotWeekDiagramm(selectedWeek, selectedYear, consumption_extrapolation, directory_yearly_generation):
    yearly_consumption = pd.DataFrame.from_dict(consumption_extrapolation.get(int(selectedYear)))
    #print("consumption", consumption_extrapolation)

    # daten nur für angegebene woche und jahr finden
    week_filtered_data_consumption = yearly_consumption[
        (yearly_consumption['Year'] == selectedYear) & 
        (yearly_consumption['Week'] == selectedWeek)
    ]

    #print("c", week_filtered_data_consumption['Year'])

    # dataframe erstellen nur mit datum und gesamtverbrauch
    week_consumption_df = week_filtered_data_consumption[['Datum', 'Gesamtverbrauch']]
    week_consumption_df['Datum'] = pd.to_datetime(week_consumption_df['Datum'])



    yearly_generation = pd.DataFrame.from_dict(directory_yearly_generation.get(int(selectedYear)))

    # Überprüfe, ob die Spalten vorhanden sind
    required_columns = ['Wind Offshore', 'Wind Onshore', 'Photovoltaik']
    # Berechne die Summe der gewünschten Spalten für jede 15-Minuten-Periode
    yearly_generation['Gesamterzeugung_EE'] = yearly_generation[required_columns].sum(axis=1)
        
    # Speichere die Ergebnisse in production_2030
    production_df = yearly_generation[['Datum', 'Gesamterzeugung_EE']]
    addTimeInformation(production_df)


    week_filtered_data_production = production_df[
        (production_df['Week'] == selectedWeek) &
        (production_df['Year'] == selectedYear)
    ]
    #print(week_filtered_data_production)
    week_production_df = week_filtered_data_production[['Datum', 'Gesamterzeugung_EE']]
    week_production_df['Datum'] = pd.to_datetime(week_production_df['Datum'])

    # Speicherintegration

    resdidual_df = differenceBetweenDataframes(yearly_consumption, yearly_generation)
    storage_df, flexipowerplant_df,storage_ee_combined_df, all_combined_df = StorageIntegration(production_df, resdidual_df, 83, 47)
    addTimeInformation(storage_df)
    addTimeInformation(flexipowerplant_df)
    addTimeInformation(storage_ee_combined_df)
    addTimeInformation(all_combined_df)

    week_filtered_data_storage = storage_df[
        (storage_df['Year'] == selectedYear) & 
        (storage_df['Week'] == selectedWeek)
    ]

    data_storage_df = week_filtered_data_storage[['Datum', 'Laden/Einspeisen in MWh']]
    data_storage_df['Datum'] = pd.to_datetime(data_storage_df['Datum'])

    week_filtered_data_flex = flexipowerplant_df[
        (flexipowerplant_df['Year'] == selectedYear) & 
        (flexipowerplant_df['Week'] == selectedWeek)
    ]

    data_flex_df = week_filtered_data_flex[['Datum', 'Einspeisung in MWh']]
    data_flex_df['Datum'] = pd.to_datetime(data_flex_df['Datum'])

    week_filtered_data_storage_ee_combined = storage_ee_combined_df[
        (storage_ee_combined_df['Year'] == selectedYear) & 
        (storage_ee_combined_df['Week'] == selectedWeek)
    ]

    data_storage_ee_combined = week_filtered_data_storage_ee_combined[['Datum', 'Speicher + Erneuerbare in MWh']]
    data_storage_ee_combined['Datum'] = pd.to_datetime(data_storage_ee_combined['Datum'])

    week_filtered_data_all_combined = all_combined_df[
        (all_combined_df['Year'] == selectedYear) & 
        (all_combined_df['Week'] == selectedWeek)
    ]

    data_all_combined = week_filtered_data_all_combined[['Datum', 'EE + Speicher + Flexible in MWh']]
    data_all_combined['Datum'] = pd.to_datetime(data_all_combined['Datum'])
    
   

    create_week_comparison(selectedYear, selectedWeek, week_consumption_df, week_production_df, data_storage_df, data_storage_ee_combined, data_flex_df, data_all_combined)


def create_week_comparison(year, week, consumption_data, production_data, storage_data, storage_ee_data, flex_data, all_combined_data):
    
    # Assuming your dataframes have columns 'Date' and 'Energy'
    plt.figure(figsize=(12, 8))  # Increase the figure size

    # Plot consumption
    plt.plot(consumption_data['Datum'], consumption_data['Gesamtverbrauch'], label='Verbrauch', linewidth=1)

    # Plot production
    plt.plot(production_data['Datum'], production_data['Gesamterzeugung_EE'], label='EE-Erzeugung', linewidth=1)

    # Plot storage 
    plt.plot(storage_data['Datum'], storage_data['Laden/Einspeisen in MWh'], label='Speicher - Laden/Einspeisen', linewidth=1)

    # Plot flex
    plt.plot(flex_data['Datum'], flex_data['Einspeisung in MWh'], label='Flexible', linewidth=1)

    # Plot storage plus ee
    plt.plot(storage_ee_data['Datum'], storage_ee_data['Speicher + Erneuerbare in MWh'], label='Erzeugung + Speicher', linewidth=1)

    # Plot all combined
    plt.plot(all_combined_data['Datum'], all_combined_data['EE + Speicher + Flexible in MWh'], label='Erzeugung + Speicher + Flexible', linewidth=1)

    # Customize x-axis to show one tick per day
    unique_dates = consumption_data['Datum'].dt.normalize().unique()  # Get unique dates (one per day)
    plt.gca().set_xticks(unique_dates)  # Set ticks to these dates
    formatted_labels = [date.strftime('%d.%m.%Y') for date in unique_dates]  # Format labels
    plt.gca().set_xticklabels(formatted_labels, rotation=45, ha='right')  # Set labels and rotate

    # Adding labels and title
    plt.xlabel('Datum', fontsize=12)
    plt.ylabel('Mwh', fontsize=12)
    plt.title(f'Wochenverbrauch und -erzeugung + Speicher + Flexible in KW {week}, {year}', fontsize=14)
    plt.legend(fontsize=12, loc='upper left', bbox_to_anchor=(1, 1))  # Move legend outside the plot

    # Customize grid
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)  # Make the grid finer

    # Display the plot
    plt.tight_layout()
    plt.show()
