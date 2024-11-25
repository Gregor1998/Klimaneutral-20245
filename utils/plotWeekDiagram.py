from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator, DateFormatter

def plotWeekDiagramm(selectedWeek, selectedYear, consumption_extrapolation, directory_yearly_generation):
    yearly_consumption = pd.DataFrame.from_dict(consumption_extrapolation.get(int(selectedYear)))

    # daten nur für angegebene woche und jahr finden
    week_filtered_data_consumption = yearly_consumption[
        (yearly_consumption['Week'] == selectedWeek)
    ]

    # dataframe erstellen nur mit datum und gesamtverbrauch
    week_consumption_df = week_filtered_data_consumption[['Datum', 'Gesamtverbrauch']]
    week_consumption_df['Datum'] = pd.to_datetime(week_consumption_df['Datum'])



    yearly_generation = pd.DataFrame.from_dict(directory_yearly_generation.get(int(selectedYear)))
    required_columns = ['Wind Offshore', 'Wind Onshore', 'Photovoltaik']

    yearly_generation['EE_Gesamt'] = yearly_generation[required_columns].sum(axis=1)

    week_filtered_data_production = yearly_generation[
        (yearly_generation['Week'] == selectedWeek)
    ]

    week_production_df = week_filtered_data_production[['Datum', 'EE_Gesamt']]
    week_consumption_df['Datum'] = pd.to_datetime(week_consumption_df['Datum'])

    create_week_comparison(selectedYear, selectedWeek, week_consumption_df, week_production_df)


def create_week_comparison(year, week, consumption_data, production_data):
    
    # Assuming your dataframes have columns 'Date' and 'Energy'
    plt.figure(figsize=(10, 6))

    # Plot consumption
    plt.plot(consumption_data['Datum'], consumption_data['Gesamtverbrauch'], label='Verbrauch', marker='o')

    # Plot production
    plt.plot(production_data['Datum'], production_data['EE_Gesamt'], label='EE-Erzeugung', marker='o')

    
     # Customize x-axis to show one tick per day
    unique_dates = consumption_data['Datum'].dt.normalize().unique()  # Get unique dates (one per day)
    plt.gca().set_xticks(unique_dates)  # Set ticks to these dates
    formatted_labels = [date.strftime('%d.%m.%Y') for date in unique_dates]  # Format labels
    plt.gca().set_xticklabels(formatted_labels, rotation=45, ha='right')  # Set labels and rotate


    # Adding labels and title
    plt.xlabel('Datum', fontsize=12)
    plt.ylabel('Mwh', fontsize=12)
    plt.title(f'Wochenverbrauch und -erzeugung KW {week}, {year}', fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True)

    # Display the plot
    plt.tight_layout()
    plt.show()