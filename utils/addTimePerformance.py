"""
Time Performance Module
-----------------------
This module provides functionality to add a timestamp column to a DataFrame.
It creates a time series with 15-minute intervals for a specified year and adds it to the DataFrame.
Used for data processing and time-based analysis in climate data applications.
"""

import pandas as pd

def addTimePerformance(df, year):
    """
    Add a time series column to a DataFrame for a specific year with 15-minute intervals.
    
    Parameters:
    df (pandas.DataFrame): The DataFrame to which the time series will be added
    year (int or str): The year for which to create the time series
    
    Returns:
    pandas.DataFrame: DataFrame with added 'Datum' timestamp column
    """
    # Define start and end dates for the time range (full year)
    start_date  = f'{year}-01-01 00:00:00'
    end_date    = f'{year}-12-31 23:45:00'

    # Create a time range with 15-minute intervals
    time_range = pd.date_range(start=start_date, end=end_date, freq='15min')
    
    # Remove February 29th entries if present (handles leap years)
    time_range = time_range[~((time_range.month == 2) & (time_range.day == 29))]
    
    # Reset DataFrame index to ensure proper alignment
    df.reset_index(drop=True, inplace=True)

    # Verify that the DataFrame and time range have matching lengths
    if len(df) != len(time_range):
        raise ValueError('Length of DataFrame and Time Range do not match')
    else:
        # Insert the time series as the first column in the DataFrame
        df.insert(0,'Datum',time_range)

        # Format the date column to ensure consistent datetime format
        df['Datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y %H:%M')

    return df
