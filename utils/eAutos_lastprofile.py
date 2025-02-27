import pandas as pd
import os
import traceback
from concurrent.futures import ProcessPoolExecutor
from utils import config

def generate_eauto_profiles(year, base_number, increase_per_year, energy_per_car, charging_distribution):
    """
    Generate electric vehicle load profiles for a specific year.
    
    Uses parallel processing to create profiles for different locations and day types.
    
    Args:
        year (int): Year to generate profiles for
        base_number (float): Base number of electric vehicles in the starting year
        increase_per_year (float): Yearly increase in electric vehicles
        energy_per_car (float): Energy consumption per car (kWh)
        charging_distribution (dict): Distribution of charging locations (e.g., {'Wohnen': 0.5, 'Büro': 0.3, 'Öffentliche_Ladepunkte': 0.2})
    
    Returns:
        dict: Dictionary of load profiles by location
    """
    # Calculate total number of electric vehicles for the year
    vehicles_count = base_number + increase_per_year * (year - config.params.start_year_simulation)
    
    # Define charging locations and day types
    locations = ['Wohnen', 'Büro', 'Öffentliche_Ladepunkte']
    day_types = ['Wochentag', 'Samstag', 'Sonntag']
    
    # Ensure output directories exist
    os.makedirs(f'CSV/Lastprofile/eMobilitaet/{year}', exist_ok=True)
    for loc in locations:
        os.makedirs(f'CSV/Lastprofile/eMobilitaet/{year}/{loc}', exist_ok=True)
    
    # Verify that all base files exist before processing
    missing_files = []
    for location in locations:
        for day_type in day_types:
            filepath = f'CSV/Lastprofile/eMobilitaet/Base/{location}/{day_type}.csv'
            if not os.path.exists(filepath):
                missing_files.append(filepath)
    
    if missing_files:
        print(f"Warning: Missing base profile files: {missing_files}")
        print("Attempting to create base directory structure...")
        os.makedirs('CSV/Lastprofile/eMobilitaet/Base', exist_ok=True)
        for loc in locations:
            os.makedirs(f'CSV/Lastprofile/eMobilitaet/Base/{loc}', exist_ok=True)
        
        print("Creating default base profiles...")
        # Create a simple default profile with 96 15-minute intervals (24 hours)
        for location in locations:
            for day_type in day_types:
                filepath = f'CSV/Lastprofile/eMobilitaet/Base/{location}/{day_type}.csv'
                if not os.path.exists(filepath):
                    # Create a simple default profile if missing
                    default_profile = pd.DataFrame({
                        'Uhrzeit': [f"{h:02d}:{m:02d}" for h in range(24) for m in [0, 15, 30, 45]],
                        'Relativer Bedarf': [1.0] * 96  # Equal distribution as default
                    })
                    default_profile.to_csv(filepath, sep=';', decimal=',', index=False)
                    print(f"Created default profile: {filepath}")
    
    # Try sequential processing first, which is more robust
    try:
        profiles = {}
        for location in locations:
            profiles[location] = {}
            # Calculate vehicles for this charging area
            vehicles_per_area = vehicles_count * charging_distribution[location]
            
            for day_type in day_types:
                # Map German day type names to English for dictionary keys
                day_key = {
                    'Wochentag': 'workday',
                    'Samstag': 'saturday',
                    'Sonntag': 'sunday'
                }[day_type]
                
                try:
                    result = _generate_profile_for_location(
                        year, location, day_type, vehicles_per_area, energy_per_car
                    )
                    
                    # If generation successful, load the profile
                    if result:
                        profile_path = f'CSV/Lastprofile/eMobilitaet/{year}/{location}/{day_type}.csv'
                        profiles[location][day_key] = pd.read_csv(
                            profile_path, delimiter=';', decimal='.'
                        )
                except Exception as e:
                    print(f"Error generating profile for {location}/{day_type}: {str(e)}")
                    traceback.print_exc()
                    # Create a simple default profile as fallback
                    default_profile = pd.DataFrame({
                        'Uhrzeit': [f"{h:02d}:{m:02d}" for h in range(24) for m in [0, 15, 30, 45]],
                        'Relativer Bedarf': [1.0] * 96,  # Equal distribution
                        'Normierter Bedarf': [1.0/96] * 96,  # Normalized
                        'Strombedarf (kWh)': [(vehicles_per_area * energy_per_car) / 96] * 96  # Total energy divided equally
                    })
                    profile_path = f'CSV/Lastprofile/eMobilitaet/{year}/{location}/{day_type}.csv'
                    default_profile.to_csv(profile_path, sep=';', decimal='.', index=False)
                    profiles[location][day_key] = default_profile
        
        return profiles
        
    except Exception as e:
        print(f"Error in sequential processing: {str(e)}")
        traceback.print_exc()
        # Return empty profiles as last resort
        return {loc: {'workday': pd.DataFrame(), 'saturday': pd.DataFrame(), 'sunday': pd.DataFrame()} 
                for loc in locations}

def _generate_profile_for_location(year, location, day_type, vehicles_per_area, energy_per_car):
    """Generate profile for a specific location and day type."""
    try:
        # Load base profile template
        base_filepath = f'CSV/Lastprofile/eMobilitaet/Base/{location}/{day_type}.csv'
        if not os.path.exists(base_filepath):
            print(f"Base profile not found: {base_filepath}")
            return False
            
        base_profile = pd.read_csv(base_filepath, delimiter=';', decimal=',')
        
        # Ensure 'Relativer Bedarf' is numeric
        if 'Relativer Bedarf' not in base_profile.columns:
            print(f"Column 'Relativer Bedarf' not found in {base_filepath}")
            print(f"Available columns: {base_profile.columns.tolist()}")
            return False
            
        if base_profile['Relativer Bedarf'].dtype == object:
            base_profile['Relativer Bedarf'] = base_profile['Relativer Bedarf'].str.replace(',', '.').astype(float)
        
        # Normalize the demand values
        sum_relative_bedarf = base_profile['Relativer Bedarf'].sum()
        if sum_relative_bedarf == 0:
            print(f"Warning: Sum of 'Relativer Bedarf' is zero in {base_filepath}")
            base_profile['Normierter Bedarf'] = 1.0 / len(base_profile)
        else:
            base_profile['Normierter Bedarf'] = base_profile['Relativer Bedarf'] / sum_relative_bedarf
        
        # Calculate actual energy demand in kWh
        base_profile['Strombedarf (kWh)'] = base_profile['Normierter Bedarf'] * vehicles_per_area * energy_per_car
        
        # Save the profile
        output_path = f'CSV/Lastprofile/eMobilitaet/{year}/{location}/{day_type}.csv'
        base_profile.to_csv(output_path, sep=';', decimal='.', index=False)
        
        return True
        
    except Exception as e:
        print(f"Error in _generate_profile_for_location for {location}/{day_type}: {str(e)}")
        traceback.print_exc()
        return False

def load_profiles(year):
    """Load generated profiles for a specific year."""
    profiles = {}
    locations = ['Wohnen', 'Büro', 'Öffentliche_Ladepunkte']
    
    for location in locations:
        profiles[location] = {}
        for day_type, file_name in [
            ('workday', 'Wochentag'), 
            ('saturday', 'Samstag'), 
            ('sunday', 'Sonntag')
        ]:
            file_path = f'CSV/Lastprofile/eMobilitaet/{year}/{location}/{file_name}.csv'
            try:
                if os.path.exists(file_path):
                    profiles[location][day_type] = pd.read_csv(file_path, delimiter=';', decimal='.')
                else:
                    print(f"Warning: File not found: {file_path}")
                    # Create a simple default profile as fallback
                    profiles[location][day_type] = pd.DataFrame({
                        'Uhrzeit': [f"{h:02d}:{m:02d}" for h in range(24) for m in [0, 15, 30, 45]],
                        'Strombedarf (kWh)': [0.0] * 96  # Zero values as fallback
                    })
            except Exception as e:
                print(f"Error loading profile {file_path}: {str(e)}")
                profiles[location][day_type] = pd.DataFrame({'Strombedarf (kWh)': [0.0] * 96})
                
    return profiles