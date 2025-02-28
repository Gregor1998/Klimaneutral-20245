# Heat Pump Load Profile Generation Module
# ----------------------------------------
# This module generates electricity load profiles for heat pumps based on installation projections.
# It scales a standard heat pump load profile according to the projected number of heat pumps
# for each year between a start and end year.
#
# The module requires a base heat pump load profile to be available through the getData function.
# The output is a dictionary of yearly load profiles with adjusted consumption values.

from utils.read_CSV import getData
from functools import lru_cache

@lru_cache(maxsize=8)
def load_profile_heatpump(current_installed, target_installed, start_year, end_year):
    """
    Generate heat pump load profiles scaled by projected installations.
    
    Parameters:
    - current_installed: Number of heat pumps currently installed
    - target_installed: Target number of heat pumps to be installed by end_year
    - start_year: First year of the simulation period
    - end_year: Last year of the simulation period
    
    Returns:
    - Dictionary mapping years to their respective heat pump load profiles
    """
    # Get the base heat pump load profile (standard normalized profile)
    # This is the foundation load curve that will be scaled for each year
    base_profile_dict = getData("Heatpump")
    
    # Extract the actual DataFrame from the dictionary
    # Handle different possible data structures for backward compatibility
    if "Lastprofil" in base_profile_dict:
        base_profile = base_profile_dict["Lastprofil"]
    else:
        # Fall back to first key if the expected key isn't found
        first_key = next(iter(base_profile_dict))
        base_profile = base_profile_dict[first_key]
    
    # Calculate annual heat pump installations
    # Assumes linear growth from current to target installation numbers
    installations = {}
    annual_growth = (target_installed - current_installed) / (end_year - start_year)
    
    for year in range(start_year, end_year + 1):
        installations[year] = current_installed + (year - start_year) * annual_growth
    
    # Create year-specific load profiles
    directory_heatpump = {}
    
    for year in range(start_year, end_year + 1):
        # Create a copy of the base profile to avoid modifying the original
        yearly_profile = base_profile.copy()
                
        # Calculate scaling factor based on projected installations for this year
        # compared to current installation numbers
        scaling_factor = installations[year] / current_installed
        
        # Scale the load profile values by the calculated factor
        # to represent increased electricity consumption from more heat pumps
        if "Lastprofil" in yearly_profile.columns:
            yearly_profile['Verbrauch in MWh'] = yearly_profile['Lastprofil'] * scaling_factor
        else:
            # Handle different column naming conventions if needed
            numeric_cols = yearly_profile.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                yearly_profile['Verbrauch in MWh'] = yearly_profile[numeric_cols[0]] * scaling_factor
            else:
                raise ValueError(f"No numeric column found in heat pump profile: {yearly_profile.columns}")
        
        # Update dates in the profile to match the target year
        # This ensures time series consistency when combining with other data
        if "Datum" in yearly_profile.columns:
            yearly_profile['Datum'] = yearly_profile['Datum'].apply(lambda x: x.replace(year=year))
        
        # Store the yearly profile in the results dictionary
        directory_heatpump[year] = yearly_profile
    
    return directory_heatpump
