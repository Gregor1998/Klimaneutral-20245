import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from IPython.display import display
from datetime import datetime, timedelta
from utils.addTimeInformation import addTimeInformation
from utils.calcDifference_storage_flexpowerplant import differenceBetweenDataframes, StorageIntegration
from utils.cleanse_dataframes import cleanse_dataframes
from utils import config

def plotWeekDiagramm(selected_week, selected_year, consumption_dict, production_dict, storage_df, flexipowerplant_df, storage_ee_combined_df, all_combined_df, name):
    """
    Plot week diagram comparing consumption, production and storage.
    Optimized for performance and visual clarity.
    """
    # Get consumption data for the selected year
    yearly_consumption = consumption_dict.get(int(selected_year))
    
    # Filter data for the selected week
    week_filtered_data_consumption = yearly_consumption[yearly_consumption['Week'] == selected_week]
    
    # Get year/week data for production
    if isinstance(production_dict, dict):
        yearly_production = production_dict.get(int(selected_year))
    else:
        yearly_production = production_dict  # Already a DataFrame
        
    # Ensure datetime format
    week_filtered_data_consumption['Datum'] = pd.to_datetime(week_filtered_data_consumption['Datum'])
    yearly_production['Datum'] = pd.to_datetime(yearly_production['Datum'])
    
    # Filter production data by matching dates from consumption data
    dates = week_filtered_data_consumption['Datum'].unique()
    week_filtered_data_production = yearly_production[yearly_production['Datum'].isin(dates)]
    
    # Filter storage data by matching dates
    storage_filtered = storage_df[storage_df['Datum'].isin(dates)]
    flexpower_filtered = flexipowerplant_df[flexipowerplant_df['Datum'].isin(dates)]
    storage_ee_filtered = storage_ee_combined_df[storage_ee_combined_df['Datum'].isin(dates)]
    all_combined_filtered = all_combined_df[all_combined_df['Datum'].isin(dates)]
    
    # Create plot using plotly for better performance
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=('Energy Production and Consumption', 'Storage and Flexible Power Plant')
    )
    
    # Add traces for consumption and production
    fig.add_trace(
        go.Scatter(
            x=week_filtered_data_consumption['Datum'],
            y=week_filtered_data_consumption['Gesamtverbrauch'],
            mode='lines',
            name='Consumption',
            line=dict(color='red', width=2)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=week_filtered_data_production['Datum'],
            y=week_filtered_data_production['Gesamterzeugung_EE'],
            mode='lines',
            name='Renewable Production',
            line=dict(color='green', width=2)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=storage_ee_filtered['Datum'],
            y=storage_ee_filtered['Speicher + Erneuerbare in MWh'],
            mode='lines',
            name='Renewable + Storage',
            line=dict(color='blue', width=1.5)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=all_combined_filtered['Datum'],
            y=all_combined_filtered['EE + Speicher + Flexible in MWh'],
            mode='lines',
            name='Renewable + Storage + Flexible',
            line=dict(color='purple', width=1.5)
        ),
        row=1, col=1
    )
    
    # Add traces for storage and flexible power plant
    fig.add_trace(
        go.Scatter(
            x=storage_filtered['Datum'],
            y=storage_filtered['Speicher Ladeleistung'],
            mode='lines',
            name='Storage Charging',
            line=dict(color='cyan', width=1.5)
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=storage_filtered['Datum'],
            y=storage_filtered['Speicher Entladeleistung'],
            mode='lines',
            name='Storage Discharging',
            line=dict(color='orange', width=1.5)
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=flexpower_filtered['Datum'],
            y=flexpower_filtered['Leistung Flexkraftwerk'],
            mode='lines',
            name='Flexible Power Plant',
            line=dict(color='brown', width=1.5)
        ),
        row=2, col=1
    )
    
    # Update layout
    fig.update_layout(
        title=f'Week {selected_week} in {selected_year}',
        xaxis_title='Date',
        yaxis_title='Power (MWh)',
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        height=800,
        width=1200,
        hovermode='closest'
    )
    
    # Add better date formatting
    fig.update_xaxes(
        tickformat='%a %d-%b<br>%H:%M',
        tickangle=45,
        tickmode='auto',
        nticks=24
    )
    
    # Display the plot
    display(fig)
    
    # Save to HTML
    fig.write_html(f'assets/plots/{name}_week{selected_week}_{selected_year}.html')


def create_week_comparison(selected_week, selected_year, df1, df2, name):
    """
    Create comparison plot for two dataframes.
    Optimized for performance and visual clarity.
    """
    # Convert to datetime format
    df1['Datum'] = pd.to_datetime(df1['Datum'])
    df2['Datum'] = pd.to_datetime(df2['Datum'])
    
    # Create plotly figure
    fig = go.Figure()
    
    # Add traces
    fig.add_trace(
        go.Scatter(
            x=df1['Datum'],
            y=df1['Gesamtverbrauch'],
            mode='lines',
            name='Consumption Without Load Profiles',
            line=dict(color='blue', width=2)
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=df2['Datum'],
            y=df2['Gesamtverbrauch'],
            mode='lines',
            name='Consumption With Load Profiles',
            line=dict(color='red', width=2)
        )
    )
    
    # Update layout
    fig.update_layout(
        title=f'Week {selected_week} in {selected_year} - Load Profile Comparison',
        xaxis_title='Date',
        yaxis_title='Power (MWh)',
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        height=600,
        width=1000,
        hovermode='closest'
    )
    
    # Add better date formatting
    fig.update_xaxes(
        tickformat='%a %d-%b<br>%H:%M',
        tickangle=45,
        tickmode='auto',
        nticks=24
    )
    
    # Display the figure
    display(fig)
    
    # Save to HTML
    fig.write_html(f'assets/plots/{name}_week{selected_week}_{selected_year}.html')