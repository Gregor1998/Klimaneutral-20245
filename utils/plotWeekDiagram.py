"""
Energy System Analysis Visualization Module
------------------------------------------
This module provides functions to visualize energy consumption, production, and storage data
for specified weeks and years. It helps in analyzing renewable energy integration,
storage utilization, and flexible power plant operations.

Functions:
- plotWeekDiagramm: Creates a two-panel visualization showing energy flows and storage operations
- create_week_comparison: Compares two datasets (typically for consumption patterns)

Dependencies:
- pandas: For data manipulation
- plotly: For interactive visualizations
- IPython: For displaying plots in notebook environments
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from IPython.display import display

def plotWeekDiagramm(selected_week, selected_year, consumption_dict, production_dict, storage_df, flexipowerplant_df, storage_ee_combined_df, all_combined_df, name):
    """
    Plot week diagram comparing consumption, production and storage.
    Optimized for performance and visual clarity.
    
    Parameters:
    -----------
    selected_week: int - Week number to visualize
    selected_year: int - Year to visualize
    consumption_dict: dict - Dictionary with yearly consumption data
    production_dict: dict or DataFrame - Production data by year or as a single DataFrame
    storage_df: DataFrame - Storage operations data
    flexipowerplant_df: DataFrame - Flexible power plant data
    storage_ee_combined_df: DataFrame - Combined storage and renewable energy data
    all_combined_df: DataFrame - All energy sources combined data
    name: str - Base filename for saved plots
    """
    # Get consumption data for the selected year
    yearly_consumption = consumption_dict.get(int(selected_year))
    
    # Filter data for the selected week
    week_filtered_data_consumption = yearly_consumption[yearly_consumption['Week'] == selected_week]
    
    # Get year/week data for production - handle both dict and DataFrame formats
    if isinstance(production_dict, dict):
        yearly_production = production_dict.get(int(selected_year))
    else:
        yearly_production = production_dict  # Already a DataFrame
        
    # Ensure datetime format for proper time series plotting
    week_filtered_data_consumption['Datum'] = pd.to_datetime(week_filtered_data_consumption['Datum'])
    yearly_production['Datum'] = pd.to_datetime(yearly_production['Datum'])
    
    # Filter production data by matching dates from consumption data
    dates = week_filtered_data_consumption['Datum'].unique()
    week_filtered_data_production = yearly_production[yearly_production['Datum'].isin(dates)]
    
    # Filter all other datasets using the same date range
    storage_filtered = storage_df[storage_df['Datum'].isin(dates)]
    flexpower_filtered = flexipowerplant_df[flexipowerplant_df['Datum'].isin(dates)]
    storage_ee_filtered = storage_ee_combined_df[storage_ee_combined_df['Datum'].isin(dates)]
    all_combined_filtered = all_combined_df[all_combined_df['Datum'].isin(dates)]
    
    # Create a two-panel plot: top for energy flows, bottom for storage operations
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=('Energy Production and Consumption', 'Storage and Flexible Power Plant')
    )
    
    # Top panel: Add traces for consumption and production data
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
    
    # Add combined traces to show stacked energy contributions
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
    
    # Bottom panel: Add traces for storage operations and flexible power plant
    fig.add_trace(
        go.Scatter(
            x=storage_filtered['Datum'],
            y=storage_filtered['Laden/Einspeisen in MWh'],
            mode='lines',
            name='Storage Charging/Discharging',
            line=dict(color='orange', width=1.5)
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=flexpower_filtered['Datum'],
            y=flexpower_filtered['Einspeisung in MWh'],
            mode='lines',
            name='Flexible Power Plant',
            line=dict(color='brown', width=1.5)
        ),
        row=2, col=1
    )
    
    # Configure overall plot layout and styling
    fig.update_layout(
        title=f'Week {selected_week} in {selected_year}',
        xaxis_title='Date',
        yaxis_title='Arbeit/Energie (MWh)',
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        height=800,
        width=1200,
        hovermode='closest'
    )
    
    # Format x-axis to show day and time clearly
    fig.update_xaxes(
        tickformat='%a %d-%b<br>%H:%M',
        tickangle=45,
        tickmode='auto',
        nticks=24
    )
    
    # Display the plot in notebook environment
    display(fig)
    
    # Save to HTML for interactive viewing in browser
    fig.write_html(f'assets/plots/{name}_week{selected_week}_{selected_year}.html')
    fig.write_image(f'assets/plots/{name}_week{selected_week}_{selected_year}.png', format='png')


def create_week_comparison(selected_week, selected_year, df1, df2, name):
    """
    Create comparison plot for two dataframes.
    Optimized for performance and visual clarity.
    
    Parameters:
    -----------
    selected_week: int - Week number to visualize
    selected_year: int - Year to visualize
    df1: DataFrame - First dataset for comparison
    df2: DataFrame - Second dataset for comparison (typically with load profiles)
    name: str - Base filename for saved plots
    """
    # Convert to datetime format for proper time-series plotting
    df1['Datum'] = pd.to_datetime(df1['Datum'])
    df2['Datum'] = pd.to_datetime(df2['Datum'])
    
    # Create plotly figure for the comparison
    fig = go.Figure()
    
    # Add trace for consumption with load profiles
    fig.add_trace(
        go.Scatter(
            x=df2['Datum'],
            y=df2['Gesamtverbrauch'],
            mode='lines',
            name='Consumption With Load Profiles',
            line=dict(color='red', width=2)
        )
    )
    
    # Configure plot layout and styling
    fig.update_layout(
        title=f'Week {selected_week} in {selected_year} - Load Profile Comparison',
        xaxis_title='Date',
        yaxis_title='Arbeit/Energie (MWh)',
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        height=600,
        width=1000,
        hovermode='closest'
    )
    
    # Format x-axis to show day and time clearly
    fig.update_xaxes(
        tickformat='%a %d-%b<br>%H:%M',
        tickangle=45,
        tickmode='auto',
        nticks=24
    )
    
    # Display the figure in notebook environment
    display(fig)
    # Save static image for reports and presentations
    #fig.write_image(f'assets/plots/{name}_week{selected_week}_{selected_year}.png', format='png')
    fig.write_image(f'assets/plots/{name}_week{selected_week}_{selected_year}.png', format='png')
    # Save outputs in different formats
    #fig.write_html(f'assets/plots/{name}_week{selected_week}_{selected_year}.html')
    
