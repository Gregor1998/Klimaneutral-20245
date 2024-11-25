from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator, DateFormatter
from utils.addTimeInformation import addTimeInformation
from utils.calcDifference import StorageIntegration, differenceBetweenDataframes

def plotWeekDiagramm(selectedWeek, selectedYear, consumption_extrapolation, directory_yearly_generation):
    #yearly_consumption = pd.DataFrame.from_dict(consumption_extrapolation.get(int(selectedYear)))
    print("consumption", consumption_extrapolation)

    # daten nur für angegebene woche und jahr finden
    week_filtered_data_consumption = consumption_extrapolation[
        (consumption_extrapolation['Year'] == selectedYear) & 
        (consumption_extrapolation['Week'] == selectedWeek)
    ]

    print("c", week_filtered_data_consumption['Year'])

    # dataframe erstellen nur mit datum und gesamtverbrauch
    week_consumption_df = week_filtered_data_consumption[['Datum', 'Gesamtverbrauch']]
    week_consumption_df['Datum'] = pd.to_datetime(week_consumption_df['Datum'])



    yearly_generation = pd.DataFrame.from_dict(directory_yearly_generation.get(int(selectedYear)))
    required_columns = ['Wind Offshore', 'Wind Onshore', 'Photovoltaik']

    #yearly_generation['Gesamterzeugung_EE'] = yearly_generation[required_columns].sum(axis=1)

    week_filtered_data_production = directory_yearly_generation[
        (directory_yearly_generation['Year'] == selectedYear) & 
        (directory_yearly_generation['Week'] == selectedWeek)
    ]
   

    week_production_df = week_filtered_data_production[['Datum', 'Gesamterzeugung_EE']]
    week_consumption_df['Datum'] = pd.to_datetime(week_consumption_df['Datum'])



    # Speicherintegration

    resdidual_df = differenceBetweenDataframes(yearly_consumption, yearly_generation)
    storage_df = StorageIntegration(resdidual_df, 2000)
    addTimeInformation(storage_df)

    week_filtered_data_storage = storage_df[
        (storage_df['Year'] == selectedYear) & 
        (storage_df['Week'] == selectedWeek)
    ]

    print("storage", week_filtered_data_storage)

    # dataframe erstellen nur mit datum und gesamtverbrauch
    week_storage_df = week_filtered_data_storage[['Datum', 'Speicher']]
    week_storage_df['Datum'] = pd.to_datetime(week_storage_df['Datum'])

    # Merge the dataframes on 'Datum' column
    Storage_EE = pd.merge(yearly_generation[['Datum', 'Gesamterzeugung_EE']], storage_df[['Datum', 'Speicher']], on='Datum')

    # Add the relevant columns
    Storage_EE['Total_EE'] = Storage_EE['Gesamterzeugung_EE'] + Storage_EE['Speicher']
    # Add the 'Speicher' column from storage_df and 'Gesamterzeugung_EE' column from production_2030
    combined_df = pd.merge(yearly_generation[['Datum', 'Gesamterzeugung_EE']], storage_df[['Datum', 'Speicher', 'Week', 'Year']], on='Datum')
    combined_df['Erzeugung&Speicher'] = combined_df['Gesamterzeugung_EE'] + combined_df['Speicher']

    # Create the new dataframe with the required columns
    storage_ee_df = combined_df[['Datum', 'Erzeugung&Speicher', 'Week', 'Year']]

    week_filtered_data_storage_ee = storage_ee_df[
        (storage_ee_df['Year'] == selectedYear) & 
        (storage_ee_df['Week'] == selectedWeek)
    ]

    # dataframe erstellen nur mit datum und gesamtverbrauch
    week_storage_ee_df = week_filtered_data_storage_ee[['Datum', 'Erzeugung&Speicher']]
    week_storage_ee_df['Datum'] = pd.to_datetime(week_storage_ee_df['Datum'])

    print(week_storage_df)
    print(week_storage_ee_df)
    create_week_comparison(selectedYear, selectedWeek, week_consumption_df, week_production_df, week_storage_df, week_storage_ee_df)


def create_week_comparison(year, week, consumption_data, production_data, storage_data, storage_ee_data):
    
    # Assuming your dataframes have columns 'Date' and 'Energy'
    plt.figure(figsize=(10, 6))

    # Plot consumption
    plt.plot(consumption_data['Datum'], consumption_data['Gesamtverbrauch'], label='Verbrauch', marker='o')

    # Plot production
    plt.plot(production_data['Datum'], production_data['Gesamterzeugung_EE'], label='EE-Erzeugung', marker='o')

    # Plot storage
    plt.plot(storage_data['Datum'], storage_data['Speicher'], label='Speicher', marker='o')

    # Plot storage plus ee
    plt.plot(storage_ee_data['Datum'], storage_ee_data['Erzeugung&Speicher'], label='Speicher + EE', marker='o')
    
     # Customize x-axis to show one tick per day
    unique_dates = consumption_data['Datum'].dt.normalize().unique()  # Get unique dates (one per day)
    plt.gca().set_xticks(unique_dates)  # Set ticks to these dates
    formatted_labels = [date.strftime('%d.%m.%Y') for date in unique_dates]  # Format labels
    plt.gca().set_xticklabels(formatted_labels, rotation=45, ha='right')  # Set labels and rotate


    # Adding labels and title
    plt.xlabel('Datum', fontsize=12)
    plt.ylabel('Mwh', fontsize=12)
    plt.title(f'Wochenverbrauch und -erzeugung KW + Speicher {week}, {year}', fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True)

    # Display the plot
    plt.tight_layout()
    plt.show()