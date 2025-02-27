import pandas as pd
import numpy as np
from functools import lru_cache

from utils.read_CSV import getData  # For loading CSV data
from utils.extraploation_class import Extrapolation_Consumption  # For projecting future consumption
from utils.addTimeInformation import addTimeInformation  # For adding time-related columns
#from szenarioDefinition.szenario import*  # Currently unused
from utils import config  # For configuration parameters

@lru_cache(maxsize=8)
def getConsumptionYear(year):
    """
    Get consumption data for a specific year with caching.
    
    Args:
        year (int): Year to load consumption data for
        
    Returns:
        DataFrame: Consumption data for the year
    """
    try:
        # Optimized CSV reading
        consumption = pd.read_csv(f"CSV/Consumption/{year}.csv", 
                                delimiter=';', 
                                parse_dates=['Datum'],
                                dtype={'Gesamtverbrauch': 'float64'},
                                engine='c')
        
        # Add time information more efficiently
        consumption['Time'] = consumption['Datum'].dt.strftime('%H:%M:%S')
        consumption['Month'] = consumption['Datum'].dt.strftime('%b')
        consumption['Year'] = consumption['Datum'].dt.year
        consumption['Month'] = consumption['Datum'].dt.strftime('%m')
        consumption['Year Month Day'] = consumption['Datum'].dt.strftime('%Y %m %d')
        consumption['Day'] = consumption['Datum'].dt.strftime('%d')
        consumption['Year'] = consumption['Datum'].dt.strftime('%Y')
        consumption['Weekday'] = consumption['Datum'].dt.dayofweek + 1
        consumption['Week'] = consumption['Datum'].dt.strftime('%W')
        
        return consumption
    except Exception as e:
        print(f"Error loading consumption data for year {year}: {e}")
        return None

def calculateConsumption(consumption_development_per_year, lastprofile_dict, directory_heatpump_consumption):
    """
    Calculate consumption with performance optimizations.
    
    Args:
        consumption_development_per_year (dict): Development factors by year
        lastprofile_dict (dict): Load profiles dictionary
        directory_heatpump_consumption (dict): Heat pump consumption data
    
    Returns:
        dict: Dictionary of calculated consumption by year
    """
    consumption_all_years = {}
    base_year = 2023
    
    # Get base consumption once
    base_consumption_df = getConsumptionYear(base_year)
    if base_consumption_df is None:
        return consumption_all_years
        
    # Pre-calculate the day-type mapping for better performance
    base_consumption_df['profile'] = _get_day_profiles(base_consumption_df)
    
    # Process each year
    for year, factor in consumption_development_per_year.items():
        year = int(year)
        
        # Create a copy of base consumption
        yearly_consumption = base_consumption_df.copy()
        
        # Apply scaling factor vectorized
        yearly_consumption['Gesamtverbrauch'] = yearly_consumption['Gesamtverbrauch'] * factor
        
        # Update date information for the current year
        yearly_consumption['Datum'] = pd.to_datetime(yearly_consumption['Datum']).apply(
            lambda x: x.replace(year=year)
        )
        
        # Add heat pump consumption if available
        if year in directory_heatpump_consumption:
            heatpump_df = directory_heatpump_consumption[year]
            # Ensure both dataframes have the same length
            min_length = min(len(yearly_consumption), len(heatpump_df))
            yearly_consumption['Gesamtverbrauch'][:min_length] += heatpump_df['Verbrauch in MWh'][:min_length].values
        
        # Store the result
        consumption_all_years[year] = yearly_consumption
    
    return consumption_all_years

def _get_day_profiles(df):
    """Helper function to efficiently determine profile type for each row"""
    # Create a numpy array for profiles based on weekday
    profiles = np.empty(len(df), dtype=object)
    
    # Vectorized assignment by weekday condition
    weekdays = df['Weekday'].values
    profiles[:] = 'workday'  # Default
    profiles[weekdays == 6] = 'saturday'  # Saturday
    profiles[weekdays == 7] = 'sunday'    # Sunday
    
    return profiles

def calculateConsumption_lastprofile(consumption_development_per_year, lastprofile_dict, directory_heatpump_consumption):
    """
    Calculate consumption with load profiles and optimized performance.
    
    Args:
        consumption_development_per_year (dict): Development factors by year
        lastprofile_dict (dict): Load profiles dictionary
        directory_heatpump_consumption (dict): Heat pump consumption data
    
    Returns:
        dict: Dictionary of calculated consumption with load profiles by year
    """
    # Start with basic consumption
    consumption_all_years = calculateConsumption(
        consumption_development_per_year, 
        lastprofile_dict, 
        directory_heatpump_consumption
    )
    
    # Process electric vehicle consumption in batches for better performance
    for year in consumption_all_years:
        if year in lastprofile_dict:
            # Process in chunks for memory efficiency
            chunk_size = 1000
            consumption_df = consumption_all_years[year]
            
            for start_idx in range(0, len(consumption_df), chunk_size):
                end_idx = min(start_idx + chunk_size, len(consumption_df))
                chunk = consumption_df.iloc[start_idx:end_idx]
                
                # Vectorized operation for EV consumption
                for location, profiles in lastprofile_dict[year].items():
                    ev_consumption = np.zeros(len(chunk))
                    
                    # Apply profiles based on day type
                    workday_mask = chunk['profile'] == 'workday'
                    saturday_mask = chunk['profile'] == 'saturday'
                    sunday_mask = chunk['profile'] == 'sunday'
                    
                    # Get profile data efficiently
                    if sum(workday_mask) > 0:
                        indices = np.mod(np.where(workday_mask)[0], len(profiles['workday']))
                        ev_consumption[workday_mask] += profiles['workday']['Leistung_MW'].values[indices]
                    
                    if sum(saturday_mask) > 0:
                        indices = np.mod(np.where(saturday_mask)[0], len(profiles['saturday']))
                        ev_consumption[saturday_mask] += profiles['saturday']['Leistung_MW'].values[indices]
                    
                    if sum(sunday_mask) > 0:
                        indices = np.mod(np.where(sunday_mask)[0], len(profiles['sunday']))
                        ev_consumption[sunday_mask] += profiles['sunday']['Leistung_MW'].values[indices]
                
                # Add to total consumption
                consumption_df.loc[chunk.index, 'Gesamtverbrauch'] += ev_consumption
    
    return consumption_all_years