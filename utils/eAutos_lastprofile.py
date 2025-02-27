import pandas as pd
import numpy as np
import os
from concurrent.futures import ProcessPoolExecutor

def generate_eauto_profiles(year, base_number, increase_per_year, energy_per_car, charging_distribution):
    """
    Generate electric vehicle load profiles for a specific year.
    
    This function uses parallel processing for better performance when creating multiple profiles.
    
    Args:
        year (int): Year to generate profiles for
        base_number (float): Base number of electric vehicles
        increase_per_year (float): Yearly increase in electric vehicles
        energy_per_car (float): Energy consumption per car (kWh)
        charging_distribution (dict): Distribution of charging locations
    
    Returns:
        dict: Dictionary of load profiles by location
    """
    # Calculate number of electric vehicles for the year
    vehicles_count = base_number + increase_per_year * (year - 2023)
    
    # Define charging locations
    locations = ['Wohnen', 'Büro', 'Öffentliche_Ladepunkte']
    day_types = ['Wochentag', 'Samstag', 'Sonntag']
    
    # Make sure output directory exists
    os.makedirs(f'CSV/Lastprofile/eMobilitaet/{year}', exist_ok=True)
    for loc in locations:
        os.makedirs(f'CSV/Lastprofile/eMobilitaet/{year}/{loc}', exist_ok=True)
    
    # Process each location in parallel
    with ProcessPoolExecutor(max_workers=3) as executor:
        futures = []
        for location_idx, location in enumerate(locations):
            for day_type in day_types:
                futures.append(
                    executor.submit(
                        _generate_profile_for_location, 
                        year, 
                        location, 
                        day_type, 
                        vehicles_count, 
                        energy_per_car, 
                        charging_distribution[location_idx]
                    )
                )
        
        # Wait for all futures to complete
        for future in futures:
            future.result()
    
    return load_profiles(year)

def _generate_profile_for_location(year, location, day_type, vehicles_count, energy_per_car, distribution_factor):
    """Helper function to generate profile for a specific location and day type"""
    # Load base profile template
    base_profile = pd.read_csv(f'CSV/Lastprofile/eMobilitaet/Base/{location}/{day_type}.csv', 
                              delimiter=';', decimal='.')
    
    # Calculate scaling factor
    scaling_factor = vehicles_count * energy_per_car * distribution_factor / 4  # Divide by 4 for 15-minute intervals
    
    # Apply scaling - vectorized operation
    base_profile['Leistung_MW'] = base_profile['Leistung_MW'] * scaling_factor
    
    # Save the profile
    output_path = f'CSV/Lastprofile/eMobilitaet/{year}/{location}/{day_type}.csv'
    base_profile.to_csv(output_path, sep=';', decimal='.', index=False)
    
    return True

def load_profiles(year):
    """Load generated profiles for a specific year"""
    profiles = {}
    locations = ['Wohnen', 'Büro', 'Öffentliche_Ladepunkte']
    
    for location in locations:
        profiles[location] = {
            'workday': pd.read_csv(f'CSV/Lastprofile/eMobilitaet/{year}/{location}/Wochentag.csv', 
                                  delimiter=';', decimal='.'),
            'saturday': pd.read_csv(f'CSV/Lastprofile/eMobilitaet/{year}/{location}/Samstag.csv', 
                                   delimiter=';', decimal='.'),
            'sunday': pd.read_csv(f'CSV/Lastprofile/eMobilitaet/{year}/{location}/Sonntag.csv', 
                                 delimiter=';', decimal='.')
        }
    
    return profiles