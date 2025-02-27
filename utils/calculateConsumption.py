import pandas as pd
import numpy as np
from functools import lru_cache
from utils.read_CSV import getData
from utils.extraploation_class import Extrapolation_Consumption
from utils.addTimeInformation import addTimeInformation
from utils import config

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
        consumption = getData("Consumption", year)[year]
        return consumption
    except Exception as e:
        print(f"Error loading consumption data for year {year}: {e}")
        return None

def apply_lastprofile(df, lastprofile, heatpump_profile, mode="add"):
    """
    Apply or subtract EV and heat pump profiles to/from consumption data.
    
    Args:
        df (DataFrame): Consumption data
        lastprofile (dict): EV load profiles by location and day type
        heatpump_profile (DataFrame): Heat pump consumption data
        mode (str): "add" or "subtract"
        
    Returns:
        DataFrame: Adjusted consumption data
    """
    df_result = df.copy()
    df_result['profile'] = 'workday'  # Default
    df_result.loc[df_result['Weekday'] == 6, 'profile'] = 'saturday'
    df_result.loc[df_result['Weekday'] == 7, 'profile'] = 'sunday'
    
    adjustments = np.zeros(len(df_result))
    
    # Sum EV profiles across locations
    for location in lastprofile:
        for day_type in ['workday', 'saturday', 'sunday']:
            profile_data = lastprofile[location][day_type]['Normierter Bedarf'].values
            profile_len = len(profile_data)
            mask = df_result['profile'] == day_type
            if sum(mask) > 0:
                indices = np.where(mask)[0] % profile_len
                adjustments[mask] += profile_data[indices]
    
    # Add heat pump consumption
    if heatpump_profile is not None:
        adjustments += heatpump_profile['Verbrauch in MWh'].values
    
    # Apply adjustments
    if mode == "add":
        df_result['Gesamtverbrauch'] += adjustments
    elif mode == "subtract":
        df_result['Gesamtverbrauch'] -= adjustments
    
    return df_result

def calculateConsumption(consumption_development_per_year, lastprofile_dict, directory_heatpump_consumption):
    """
    Calculate consumption without profiles, extrapolated for each year.
    
    Args:
        consumption_development_per_year (dict): Annual growth factors
        lastprofile_dict (dict): Load profiles dictionary
        directory_heatpump_consumption (dict): Heat pump consumption data
    
    Returns:
        dict: Consumption without profiles by year
    """
    consumption_all_years = {}
    base_year = config.params.consumption_year
    
    # Load base consumption
    base_consumption_df = getConsumptionYear(base_year)
    if base_consumption_df is None:
        return consumption_all_years
    
    base_consumption_df = addTimeInformation(base_consumption_df)
    
    # Subtract profiles from base year
    base_heatpump_lp = directory_heatpump_consumption.get(base_year)
    base_without_profiles = apply_lastprofile(
        base_consumption_df,
        lastprofile_dict[base_year],
        base_heatpump_lp,
        mode="subtract"
    )
    consumption_all_years[base_year] = base_without_profiles
    
    # Extrapolate sequentially
    current_consumption = base_without_profiles.copy()
    for year in range(base_year + 1, config.params.end_year_simulation + 1):
        growth_factor = consumption_development_per_year.get(year, 1.0)
        extrapolated_data = Extrapolation_Consumption(
            current_consumption, year, None, None, None, growth_factor
        )
        current_consumption = extrapolated_data.df
        consumption_all_years[year] = current_consumption.copy()
    
    return consumption_all_years

def calculateConsumption_lastprofile(consumption_development_per_year, lastprofile_dict, directory_heatpump_consumption):
    """
    Calculate total consumption with profiles added back.
    
    Args:
        consumption_development_per_year (dict): Annual growth factors
        lastprofile_dict (dict): Load profiles dictionary
        directory_heatpump_consumption (dict): Heat pump consumption data
    
    Returns:
        dict: Total consumption with profiles by year
    """
    # Get consumption without profiles
    consumption_without_profiles = calculateConsumption(
        consumption_development_per_year,
        lastprofile_dict,
        directory_heatpump_consumption
    )
    
    if not consumption_without_profiles:
        return {}
    
    # Add profiles for each year
    consumption_with_profiles = {}
    for year in consumption_without_profiles:
        yearly_consumption = consumption_without_profiles[year]
        heatpump_lp = directory_heatpump_consumption.get(year)
        yearly_consumption = apply_lastprofile(
            yearly_consumption,
            lastprofile_dict[year],
            heatpump_lp,
            mode="add"
        )
        consumption_with_profiles[year] = yearly_consumption
    
    return consumption_with_profiles
