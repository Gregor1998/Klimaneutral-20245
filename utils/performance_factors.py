# Performance Factors Calculation Module
# ---------------------------------------
# This module calculates performance factors for renewable energy sources (Photovoltaik/Solar PV, 
# Wind Onshore, and Wind Offshore) based on installed capacity and generation data.
# Performance factors represent the ratio of actual energy generation to installed capacity,
# normalized to a quarter-hourly basis. These factors are essential for modeling future energy
# production based on historical generation patterns and planned capacity expansions.

import pandas as pd

def performance_factors(directoryGeneration, directoryInstalled):
    """
    Calculate performance factors for renewable energy sources.
    
    Args:
        directoryGeneration: Dictionary with yearly generation data (quarter-hourly)
        directoryInstalled: Dictionary with yearly installed capacity data
        
    Returns:
        dictionary: Performance factors per quarter-hour for each year
    """
    directory_performance_factors = {}

    for year in range(2015, 2024):
        if directoryInstalled.get(year + 1) is not None:
            # Calculate daily expansion rate based on the difference between current and next year's capacity
            dayly_expansion_rate_PV = (directoryInstalled[year + 1]["Photovoltaik"].iloc[0] - directoryInstalled[year]["Photovoltaik"].iloc[0]) / 365
            dayly_expansion_rate_Wind_Onshore = (directoryInstalled[year + 1]["Wind Onshore"].iloc[0] - directoryInstalled[year]["Wind Onshore"].iloc[0]) / 365
            dayly_expansion_rate_Wind_Offshore = (directoryInstalled[year + 1]["Wind Offshore"].iloc[0] - directoryInstalled[year]["Wind Offshore"].iloc[0]) / 365
        else:
            # For the last year (or if next year data is missing), calculate base performance factors
            # The factor 0.25 normalizes the quarterly values (4 quarter-hours per hour)
            PV_factor = directoryInstalled[year]["Photovoltaik"].iloc[0] * 0.25
            OnShore_factor = directoryInstalled[year]["Wind Onshore"].iloc[0] * 0.25
            OffShore_factor = directoryInstalled[year]["Wind Offshore"].iloc[0] * 0.25

        # Create empty DataFrame to store performance factors per quarter-hour
        performance_factors = pd.DataFrame(columns=["Datum", "Photovoltaik", "Wind Onshore", "Wind Offshore"])
        performance_factors["Datum"] = directoryGeneration[year]["Datum"]

        # Calculate performance factors with daily capacity increase (for years with next year data)
        if directoryInstalled.get(year + 1) is not None:
            for day in range(365):
                # Calculate indices for each day (96 quarter-hours per day)
                start_index = day * 96
                end_index = start_index + 96

                # Calculate capacity factors for the specific day, considering daily expansion
                PV_factor = (directoryInstalled[year]["Photovoltaik"].iloc[0] + dayly_expansion_rate_PV * day) * 0.25
                OnShore_factor = (directoryInstalled[year]["Wind Onshore"].iloc[0] + dayly_expansion_rate_Wind_Onshore * day) * 0.25
                OffShore_factor = (directoryInstalled[year]["Wind Offshore"].iloc[0] + dayly_expansion_rate_Wind_Offshore * day) * 0.25

                # Calculate performance factors as generation divided by capacity
                performance_factors.loc[start_index:end_index, "Photovoltaik"] = directoryGeneration[year]["Photovoltaik"][start_index:end_index] / PV_factor
                performance_factors.loc[start_index:end_index, "Wind Onshore"] = directoryGeneration[year]["Wind Onshore"][start_index:end_index] / OnShore_factor
                performance_factors.loc[start_index:end_index, "Wind Offshore"] = directoryGeneration[year]["Wind Offshore"][start_index:end_index] / OffShore_factor
        else:
            # For the last year, use constant factors throughout the year
            performance_factors["Photovoltaik"] = directoryGeneration[year]["Photovoltaik"] / PV_factor
            performance_factors["Wind Onshore"] = directoryGeneration[year]["Wind Onshore"] / OnShore_factor
            performance_factors["Wind Offshore"] = directoryGeneration[year]["Wind Offshore"] / OffShore_factor

        # Store the calculated performance factors in the result dictionary
        directory_performance_factors[year] = performance_factors

    return directory_performance_factors
