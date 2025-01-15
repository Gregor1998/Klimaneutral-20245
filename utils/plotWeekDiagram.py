from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator, DateFormatter
from utils.addTimeInformation import addTimeInformation
from utils.calcDifference_storage_flexpowerplant import differenceBetweenDataframes, StorageIntegration
from utils.cleanse_dataframes import cleanse_dataframes
#from szenarioDefinition.szenario import*
from utils import config

def plotWeekDiagramm(selectedWeek, selectedYear, consumption_extrapolation, production_df, storage_df, flexipowerplant_df, storage_ee_combined_df, all_combined_df, fileName=None):
    yearly_consumption = pd.DataFrame.from_dict(consumption_extrapolation.get(int(selectedYear)))


    # daten nur für angegebene woche und jahr finden
    week_filtered_data_consumption = yearly_consumption[
        (yearly_consumption['Year'] == selectedYear) & 
        (yearly_consumption['Week'] == selectedWeek)
    ]

    # dataframe erstellen nur mit datum und gesamtverbrauch
    week_consumption_df = week_filtered_data_consumption[['Datum', 'Gesamtverbrauch']]
    week_consumption_df['Datum'] = pd.to_datetime(week_consumption_df['Datum'])

    
    # Filter production data
    week_filtered_data_production = production_df[
        (production_df['Week'] == selectedWeek) &
        (production_df['Year'] == selectedYear)
    ]
    week_production_df = week_filtered_data_production[['Datum', 'Gesamterzeugung_EE']]
    week_production_df['Datum'] = pd.to_datetime(week_production_df['Datum'])

    # Filter storage data
    week_filtered_data_storage = storage_df[
        (storage_df['Year'] == selectedYear) & 
        (storage_df['Week'] == selectedWeek)
    ]
    data_storage_df = week_filtered_data_storage[['Datum', 'Laden/Einspeisen in MWh']]
    data_storage_df['Datum'] = pd.to_datetime(data_storage_df['Datum'])

    # Filter flex data
    week_filtered_data_flex = flexipowerplant_df[
        (flexipowerplant_df['Year'] == selectedYear) & 
        (flexipowerplant_df['Week'] == selectedWeek)
    ]
    data_flex_df = week_filtered_data_flex[['Datum', 'Einspeisung in MWh']]
    data_flex_df['Datum'] = pd.to_datetime(data_flex_df['Datum'])

    # Filter storage + ee data
    week_filtered_data_storage_ee_combined = storage_ee_combined_df[
        (storage_ee_combined_df['Year'] == selectedYear) & 
        (storage_ee_combined_df['Week'] == selectedWeek)
    ]
    data_storage_ee_combined = week_filtered_data_storage_ee_combined[['Datum', 'Speicher + Erneuerbare in MWh']]
    data_storage_ee_combined['Datum'] = pd.to_datetime(data_storage_ee_combined['Datum'])

    # Filter all combined data
    week_filtered_data_all_combined = all_combined_df[
        (all_combined_df['Year'] == selectedYear) & 
        (all_combined_df['Week'] == selectedWeek)
    ]
    data_all_combined = week_filtered_data_all_combined[['Datum', 'EE + Speicher + Flexible in MWh']]
    data_all_combined['Datum'] = pd.to_datetime(data_all_combined['Datum'])

    create_week_comparison(selectedYear, selectedWeek, week_consumption_df, week_production_df, fileName, data_storage_df, data_storage_ee_combined, data_flex_df, data_all_combined)


def create_week_comparison(year, week, consumption_data, production_data, fileName=None, storage_data=None, storage_ee_data=None, flex_data=None, all_combined_data=None):
    fig = go.Figure()

    # Plot consumption
    fig.add_trace(go.Scatter(x=consumption_data['Datum'], y=consumption_data.iloc[:, 1], mode='lines', name=consumption_data.columns[1]))

    # Plot production
    fig.add_trace(go.Scatter(x=production_data['Datum'], y=production_data.iloc[:, 1], mode='lines', name=production_data.columns[1]))

    # Plot storage 
    if storage_data is not None:
        fig.add_trace(go.Scatter(x=storage_data['Datum'], y=storage_data['Laden/Einspeisen in MWh'], mode='lines', name='Speicher - Laden/Einspeisen'))

    # Plot flex
    if flex_data is not None:
        fig.add_trace(go.Scatter(x=flex_data['Datum'], y=flex_data['Einspeisung in MWh'], mode='lines', name='Flexible'))

    # Plot storage plus ee
    if storage_ee_data is not None:
        fig.add_trace(go.Scatter(x=storage_ee_data['Datum'], y=storage_ee_data['Speicher + Erneuerbare in MWh'], mode='lines', name='Erzeugung + Speicher'))

    # Plot all combined
    if all_combined_data is not None:
        fig.add_trace(go.Scatter(x=all_combined_data['Datum'], y=all_combined_data['EE + Speicher + Flexible in MWh'], mode='lines', name='Erzeugung + Speicher + Flexible'))

    # Customize layout
    fig.update_layout(
        title=f'Vergleich für KW {week}, {year}',
        xaxis_title='Datum',
        yaxis_title='Mwh',
        legend_title='Legende',
        xaxis=dict(
            tickformat='%d.%m.%Y',
            tickmode='array',
            tickvals=pd.date_range(start=consumption_data['Datum'].min(), end=consumption_data['Datum'].max(), freq='D')
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # Save plot to file
    if fileName:
        fig.write_image(f'assets/plots/{fileName}.png')

    # Show plot
    fig.show()