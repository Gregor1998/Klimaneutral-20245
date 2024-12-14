from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator, DateFormatter
from utils.addTimeInformation import addTimeInformation
from utils.calcDifference_storage_flexpowerplant import differenceBetweenDataframes, StorageIntegration

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



    yearly_generation = directory_yearly_generation.get(2030)

    # Überprüfe, ob die Spalten vorhanden sind
    required_columns = ['Wind Offshore', 'Wind Onshore', 'Photovoltaik']
    # Berechne die Summe der gewünschten Spalten für jede 15-Minuten-Periode
    yearly_generation['Gesamterzeugung_EE'] = yearly_generation[required_columns].sum(axis=1)
        
    # Speichere die Ergebnisse in production_2030
    production_2030 = yearly_generation[['Datum', 'Gesamterzeugung_EE']]
    addTimeInformation(production_2030)


    week_filtered_data_production = production_2030[
        (production_2030['Week'] == selectedWeek) &
        (production_2030['Year'] == selectedYear)
    ]
    print(week_filtered_data_production)
    week_production_df = week_filtered_data_production[['Datum', 'Gesamterzeugung_EE']]
    week_consumption_df['Datum'] = pd.to_datetime(week_consumption_df['Datum'])

    # Speicherintegration

    resdidual_df = differenceBetweenDataframes(yearly_consumption, yearly_generation)
    storage_df, flexipowerplant_df = StorageIntegration(resdidual_df, 83, 47)
    addTimeInformation(storage_df)
    addTimeInformation(flexipowerplant_df)

    week_filtered_data_storage = storage_df[
        (storage_df['Year'] == selectedYear) & 
        (storage_df['Week'] == selectedWeek)
    ]

    week_filtered_data_flex = flexipowerplant_df[
        (flexipowerplant_df['Year'] == selectedYear) & 
        (flexipowerplant_df['Week'] == selectedWeek)
    ]
    #print("storage", week_filtered_data_storage)

    # dataframe erstellen nur mit datum und gesamtverbrauch
    week_storage_df = week_filtered_data_storage[['Datum', 'Laden/Einspeisen in kWh']]
    week_storage_df['Datum'] = pd.to_datetime(week_storage_df['Datum'])

    # Merge the dataframes on 'Datum' column
    Storage_EE = pd.merge(yearly_generation[['Datum', 'Gesamterzeugung_EE']], storage_df[['Datum', 'Laden/Einspeisen in kWh']], on='Datum')
     # Merge the dataframes on 'Datum' column
    #Storage_flex_EE = pd.merge(Storage_EE[['Datum','Gesamterzeugung_EE', 'Laden/Einspeisen in kWh']], flexipowerplant_df[['Datum', 'Einspeisung in kWh']], on='Datum')
    # Add the relevant columns
    Storage_EE['Total_Energy'] = Storage_EE['Gesamterzeugung_EE'] - Storage_EE['Laden/Einspeisen in kWh']
    # Add the relevant columns
    #Storage_flex_EE['Total_Energy'] = Storage_flex_EE['Gesamterzeugung_EE'] + Storage_flex_EE['Laden/Einspeisen in kWh'] + Storage_flex_EE['Einspeisung in kWh']
    # Add the 'Laden/Einspeisen in kWh' column from storage_df and 'Gesamterzeugung_EE' column from production_2030
    combined_ee_storage_df = pd.merge(yearly_generation[['Datum', 'Gesamterzeugung_EE']], storage_df[['Datum', 'Laden/Einspeisen in kWh', 'Week', 'Year']], on='Datum')
    combined_ee_storage_df['Erzeugung + Speicher in kWh'] = combined_ee_storage_df['Gesamterzeugung_EE'] - combined_ee_storage_df['Laden/Einspeisen in kWh']

    #combined_ee_storage_flex_df = pd.merge(flexipowerplant_df[['Datum', 'Einspeisung in kWh']], combined_ee_storage_df['Datum', 'Erzeugung&Laden/Einspeisen in kWh','Week', 'Year'], on='Datum')
    #combined_ee_storage_flex_df['Erzeugung&Laden/Einspeisen&Flex in kWh'] = combined_ee_storage_flex_df['Gesamterzeugung_EE'] + combined_ee_storage_flex_df['Laden/Einspeisen in kWh'] + combined_ee_storage_flex_df['Einspeisung in kWh']

    # Create the new dataframe with the required columns
    storage_ee_df = combined_ee_storage_df[['Datum', 'Erzeugung + Speicher in kWh', 'Week', 'Year']]

    week_filtered_data_storage_ee = storage_ee_df[
        (storage_ee_df['Year'] == selectedYear) & 
        (storage_ee_df['Week'] == selectedWeek)
    ]

    # dataframe erstellen nur mit datum und gesamtverbrauch
    week_storage_ee_df = week_filtered_data_storage_ee[['Datum', 'Erzeugung + Speicher in kWh']]
    week_storage_ee_df['Datum'] = pd.to_datetime(week_storage_ee_df['Datum'])

    # Create the new dataframe with the required columns
    #storage_ee_flex_df = combined_ee_storage_df[['Datum', 'Erzeugung + Speicher + Flexible in kWh', 'Week', 'Year']]

    #week_filtered_data_storage_flex_ee = storage_ee_flex_df[
    #    (storage_ee_df['Year'] == selectedYear) & 
    #    (storage_ee_df['Week'] == selectedWeek)
   # ]

    # dataframe erstellen nur mit datum und gesamtverbrauch
    #week_storage_ee_flex_df = week_filtered_data_storage_flex_ee[['Datum', 'Erzeugung + Speicher in kWh']]
    #week_storage_ee_flex_df['Datum'] = pd.to_datetime(week_storage_ee_flex_df['Datum'])

    #print(week_storage_df)
    #print(week_storage_ee_df)
    create_week_comparison(selectedYear, selectedWeek, week_consumption_df, week_production_df, week_storage_df, week_storage_ee_df)


def create_week_comparison(year, week, consumption_data, production_data, storage_data=None, storage_ee_data=None):
    # TODO:spaltenname der verglichen werden soll mitübergeben
    
    # Assuming your dataframes have columns 'Date' and 'Energy'
    plt.figure(figsize=(10, 6))

    # Plot consumption
    plt.plot(consumption_data['Datum'], consumption_data.iloc[:, 1], label=production_data.columns[1], marker=',')

    # Plot production
    plt.plot(production_data['Datum'], production_data.iloc[:, 1], label=production_data.columns[1], marker=',')

    # Plot storage
    if(storage_ee_data is not None):
        plt.plot(storage_ee_data['Datum'], storage_ee_data['Erzeugung + Speicher in kWh'], label='Erzeugung + Speicher', marker='o')

    # Plot storage plus ee
    if(storage_data is not None):
        plt.plot(storage_data['Datum'], storage_data['Laden/Einspeisen in kWh'], label='Laden/Einspeisen', marker='o')

    
     # Customize x-axis to show one tick per day
    unique_dates = consumption_data['Datum'].dt.normalize().unique()  # Get unique dates (one per day)
    plt.gca().set_xticks(unique_dates)  # Set ticks to these dates
    formatted_labels = [date.strftime('%d.%m.%Y') for date in unique_dates]  # Format labels
    plt.gca().set_xticklabels(formatted_labels, rotation=45, ha='right')  # Set labels and rotate

    plt.gcf().autofmt_xdate()

    # Setzen der Ticks auf stündliche Intervalle
    hourly_ticks = pd.date_range(start=consumption_data['Datum'].min(), end=consumption_data['Datum'].max(), freq='h')
    plt.gca().set_xticks(hourly_ticks)

    plt.xlim(consumption_data['Datum'].min(), consumption_data['Datum'].max())



    # Adding labels and title
    plt.xlabel('Datum', fontsize=12)
    plt.ylabel('Mwh', fontsize=12)
    plt.title(f'Vergleich für KW {week}, {year}', fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True)

    # Display the plot
    plt.tight_layout()
    plt.show()