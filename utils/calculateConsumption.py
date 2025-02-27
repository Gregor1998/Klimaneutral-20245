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
        consumption = getData("Consumption", year)[year]
        
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
    base_year = config.params.consumption_year
    
    # Get base consumption once
    base_consumption_df = getConsumptionYear(base_year)

    if base_consumption_df is None:
        return consumption_all_years
    
    # Add time information to base consumption dataframe
    base_consumption_df = addTimeInformation(base_consumption_df[base_year])
    
    # Process each year
    for year, factor in consumption_development_per_year.items():
        year = int(year)
        
        # Create a copy of base consumption
        yearly_consumption = base_consumption_df.copy()
        
        # Apply scaling factor using vectorized operation
        yearly_consumption['Gesamtverbrauch'] = yearly_consumption['Gesamtverbrauch'] * factor
        
        # Update date information for the current year
        yearly_consumption['Datum'] = pd.to_datetime(yearly_consumption['Datum']).apply(
            lambda x: x.replace(year=year)
        )
        
        # Re-add time information for the updated dates
        yearly_consumption = addTimeInformation(yearly_consumption)
        
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
    # Start with basic consumption calculation
    consumption_all_years = calculateConsumption(
        consumption_development_per_year, 
        lastprofile_dict, 
        directory_heatpump_consumption
    )
    
    consumption_year = 2023
    directory_yearly_consumption = {}
    
    # Base heatpump load profile for 2023
    base_heatpump_lp = None
    if consumption_year in directory_heatpump_consumption:
        base_heatpump_lp = directory_heatpump_consumption[consumption_year]
    
    def apply_lastprofile(df, lastprofile, heatpump_profile, mode="add"):
        """Helper function to apply load profiles to a dataframe"""
        # Make a copy of the dataframe to avoid modifying the original
        df_result = df.copy()
        
        # Add profile column based on weekday
        df_result['profile'] = 'workday'  # Default
        df_result.loc[df_result['Weekday'] == 6, 'profile'] = 'saturday'  # Saturday
        df_result.loc[df_result['Weekday'] == 7, 'profile'] = 'sunday'    # Sunday
        
        # Filter out rows with missing profile
        df_result = df_result[df_result['profile'].notna()]
        
        # Apply load profiles efficiently
        for location, day_profiles in lastprofile.items():
            for day_type in ['workday', 'saturday', 'sunday']:
                # Get profile data for this day type
                profile_data = day_profiles[day_type]['Leistung_MW'].values
                profile_len = len(profile_data)
                
                # Create a mask for this day type
                mask = df_result['profile'] == day_type
                
                if sum(mask) > 0:
                    # Calculate indices into profile data for each row
                    indices = np.where(mask)[0] % profile_len
                    
                    # Apply the profile data
                    if mode == "add":
                        df_result.loc[mask, 'Gesamtverbrauch'] += profile_data[indices]
                    else:
                        df_result.loc[mask, 'Gesamtverbrauch'] -= profile_data[indices]
        
        return df_result
    
    try:
        import numpy as np
        
        # For each year, process the consumption with load profiles
        for year, factor in consumption_development_per_year.items():
            year = int(year)
            
            if year in consumption_all_years and year in lastprofile_dict:
                # Get the consumption dataframe for this year
                yearly_consumption = consumption_all_years[year]
                
                # Ensure time information is present
                yearly_consumption = addTimeInformation(yearly_consumption)
                
                # Apply load profiles
                yearly_consumption = apply_lastprofile(
                    yearly_consumption,
                    lastprofile_dict[year],
                    directory_heatpump_consumption.get(year),
                    mode="add"
                )
                
                # Store the result
                directory_yearly_consumption[year] = yearly_consumption
                
                print(f"UPDATE {yearly_consumption}")
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error in calculateConsumption_lastprofile: {e}")
    
    return directory_yearly_consumption or consumption_all_years