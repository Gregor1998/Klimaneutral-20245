# Heat Pump Load Profile Generation Module

import pandas as pd #type: ignore
import os
import numpy as np
import multiprocessing as mp
from utils.read_CSV import getData
from utils.addTimePerformance import addTimePerformance
from functools import lru_cache

@lru_cache(maxsize=8)
def load_profile_heatpump(current_installed, target_installed, start_year, end_year):
    """
    Generate heat pump load profiles scaled by projected installations.
    """
    # Get the base heat pump load profile (standard normalized profile)
    base_profile_dict = getData("Heatpump")
    
    # Extract the actual DataFrame from the dictionary
    if "Lastprofil" in base_profile_dict:
        base_profile = base_profile_dict["Lastprofil"]
    else:
        # If the first key contains the DataFrame (for backward compatibility)
        first_key = next(iter(base_profile_dict))
        base_profile = base_profile_dict[first_key]
    
    # Calculate annual heat pump installations
    installations = {}
    annual_growth = (target_installed - current_installed) / (end_year - start_year)
    
    for year in range(start_year, end_year + 1):
        installations[year] = current_installed + (year - start_year) * annual_growth
    
    # Create year-specific load profiles
    directory_heatpump = {}
    
    for year in range(start_year, end_year + 1):
        # Create a copy of the base profile to avoid modifying the original
        yearly_profile = base_profile.copy()
                
        # Scale the consumption based on heat pump numbers - vectorized operation
        scaling_factor = installations[year] / current_installed
        
        # Make sure we're accessing the right column
        if "Lastprofil" in yearly_profile.columns:
            yearly_profile['Verbrauch in MWh'] = yearly_profile['Lastprofil'] * scaling_factor
        else:
            # If there's no Lastprofil column, it might be the first numeric column
            numeric_cols = yearly_profile.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                yearly_profile['Verbrauch in MWh'] = yearly_profile[numeric_cols[0]] * scaling_factor
            else:
                raise ValueError(f"No numeric column found in heat pump profile: {yearly_profile.columns}")
        
        # Ensure the dates correspond to the target year
        if "Datum" in yearly_profile.columns:
            yearly_profile['Datum'] = yearly_profile['Datum'].apply(lambda x: x.replace(year=year))
        
        directory_heatpump[year] = yearly_profile
    
    return directory_heatpump




















