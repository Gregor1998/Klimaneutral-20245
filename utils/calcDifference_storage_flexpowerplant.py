import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from functools import lru_cache
import os
from multiprocessing import Pool, cpu_count
from typing import Tuple, List, Dict, Optional, Union, Any

# Cache for frequently accessed intermediate results
_cache = {}

def differenceBetweenDataframes(consumption_df: pd.DataFrame, production_df: pd.DataFrame) -> List[pd.DataFrame]:
    """
    Calculate the difference between consumption and production dataframes.
    Optimized using vectorized operations.
    """
    # Create a copy to avoid modifying the original dataframe
    consumption = consumption_df.copy()
    production = production_df.copy()
    
    # Convert Datum columns to datetime if they're not already
    consumption['Datum'] = pd.to_datetime(consumption['Datum'])
    production['Datum'] = pd.to_datetime(production['Datum'])
    
    # Merge dataframes on Datum for efficient comparison
    merged_df = pd.merge(consumption, production, on='Datum', how='inner')
    
    # Vectorized calculation of difference
    merged_df['Differenz in MWh'] = merged_df['Gesamterzeugung_EE'] - merged_df['Gesamtverbrauch']
    
    # Create the result dataframe with required columns
    result_df = merged_df[['Datum', 'Differenz in MWh']].copy()
    
    # Calculate positive and negative values vectorized
    result_df['positive Werte'] = result_df['Differenz in MWh'].clip(lower=0)
    result_df['negative Werte'] = result_df['Differenz in MWh'].clip(upper=0)
    
    # Save difference results to CSV
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output')
    os.makedirs(output_dir, exist_ok=True)
    result_df.to_csv(os.path.join(output_dir, 'energy_difference.csv'), index=False)
    
    return [result_df]

@lru_cache(maxsize=32)  # Cache results of this function
def _find_continuous_periods(series: Tuple[float], threshold: float = 0) -> List[List[int]]:
    """
    Find continuous periods where values are above or below a threshold.
    Takes a tuple (hashable) for caching and returns indices of periods.
    """
    values = np.array(series)
    indices = np.where(values < threshold)[0]
    
    if len(indices) == 0:
        return []
    
    # Find breaks in consecutive indices
    breaks = np.where(np.diff(indices) > 1)[0] + 1
    # Split indices at breaks
    periods = np.split(indices, breaks)
    
    # Convert to list for return
    return [period.tolist() for period in periods]

def calculateLongestPeriods(difference_df: List[pd.DataFrame], threshold: Optional[float] = None) -> Tuple[float, float, float, float]:
    """
    Calculate storage demand based on the longest deficit periods.
    Optimized using vectorized operations and caching.
    """
    df = difference_df[0]
    
    # Create cache key based on dataframe and threshold
    cache_key = f"longest_periods_{hash(tuple(df['Differenz in MWh']))}"
    if cache_key in _cache:
        return _cache[cache_key]
    
    # Find deficit periods (negative difference values)
    periods = _find_continuous_periods(tuple(df['Differenz in MWh'].values), 0)
    
    if not periods:
        return 0, 0, 0, 0
    
    # Calculate total energy deficit for each period
    period_deficits = []
    period_max_powers = []
    
    for period in periods:
        if period:
            # Get the slice of values for this period
            deficit_values = df.iloc[period]['Differenz in MWh'].values
            
            # Calculate total deficit (absolute sum of negative values)
            total_deficit = np.abs(np.sum(deficit_values))
            
            # Calculate maximum power deficit (maximum absolute negative value)
            max_deficit = np.abs(np.min(deficit_values))
            
            period_deficits.append(total_deficit)
            period_max_powers.append(max_deficit)
    
    if not period_deficits:
        return 0, 0, 0, 0
    
    # Find period with maximum deficit
    max_deficit_idx = np.argmax(period_deficits)
    
    # Calculate values for battery storage (short-term) and hydrogen (long-term)
    max_storage_demand = period_deficits[max_deficit_idx]
    max_storage_power = period_max_powers[max_deficit_idx]
    
    # For hydrogen calculation, use the second largest period if available
    if len(period_deficits) > 1:
        sorted_indices = np.argsort(period_deficits)[::-1]  # Sort in descending order
        max_tank_demand = period_deficits[sorted_indices[1]]
        max_tank_power = period_max_powers[sorted_indices[1]]
    else:
        max_tank_demand = 0
        max_tank_power = 0
    
    result = (max_storage_demand, max_storage_power, max_tank_demand, max_tank_power)
    _cache[cache_key] = result
    
    return result

def _simulate_storage_step(state: Dict, idx: int, row: pd.Series, max_power: float, max_capacity: float) -> Dict:
    """
    Simulate a single step of storage operation.
    """
    storage_level = state['storage_level']
    storage_charge = state['storage_charge']
    storage_discharge = state['storage_discharge']
    
    diff = row['Differenz in MWh']
    
    if diff > 0:  # Excess production, charge storage
        charge_capacity = min(diff, max_power, max_capacity - storage_level)
        storage_level += charge_capacity
        storage_charge[idx] = charge_capacity
        storage_discharge[idx] = 0
        
    else:  # Production deficit, discharge storage
        discharge_needed = min(abs(diff), max_power, storage_level)
        storage_level -= discharge_needed
        storage_charge[idx] = 0
        storage_discharge[idx] = discharge_needed
    
    return {
        'storage_level': storage_level,
        'storage_charge': storage_charge,
        'storage_discharge': storage_discharge
    }

def StorageIntegration(
    name: str, 
    consumption_df: pd.DataFrame, 
    production_df: pd.DataFrame, 
    difference_df: List[pd.DataFrame],
    max_power_storage: float,
    max_storage_capacity: float, 
    max_power_flexpowerplant: float
) -> Union[Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, float], 
          Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame], 
          Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, float, float]]:
    """
    Simulate storage integration with renewable energy.
    Optimized using vectorized operations where possible and more efficient algorithms.
    
    Returns different values based on the 'name' parameter:
    - "calculation just storage": Returns storage_df, storage_ee_combined_df, new_difference_df, calculated_flexpower
    - "calculation Storage + flexipowerplant": Returns flexpowerplant_df, all_combined_df, new_difference_df
    - Any other name: Returns all values
    """
    # Cache key for this combination of parameters
    cache_key = f"storage_integration_{name}_{max_power_storage}_{max_storage_capacity}_{max_power_flexpowerplant}"
    if cache_key in _cache:
        return _cache[cache_key]
    
    df = difference_df[0].copy()
    num_rows = len(df)
    
    # Initialize arrays for better performance
    storage_level = 0
    storage_charge = np.zeros(num_rows)
    storage_discharge = np.zeros(num_rows)
    flexpowerplant_generation = np.zeros(num_rows)
    
    # First pass: simulate storage operation
    for i, (_, row) in enumerate(df.iterrows()):
        state = {
            'storage_level': storage_level,
            'storage_charge': storage_charge,
            'storage_discharge': storage_discharge
        }
        
        updated_state = _simulate_storage_step(
            state, i, row, max_power_storage, max_storage_capacity
        )
        
        storage_level = updated_state['storage_level']
        storage_charge = updated_state['storage_charge']
        storage_discharge = updated_state['storage_discharge']
    
    # Second pass: calculate new difference after storage
    new_difference = df['Differenz in MWh'].values + storage_discharge - storage_charge
    
    # Third pass: simulate flexible power plant
    if max_power_flexpowerplant > 0:
        for i in range(num_rows):
            if new_difference[i] < 0:
                flexpowerplant_needed = min(abs(new_difference[i]), max_power_flexpowerplant)
                flexpowerplant_generation[i] = flexpowerplant_needed
                new_difference[i] += flexpowerplant_needed
    
    # Create dataframes from the results
    storage_df = pd.DataFrame({
        'Datum': df['Datum'],
        'Speicher Ladekapazität': storage_charge,
        'Speicher Entladekapazität': storage_discharge
    })
    
    flexpowerplant_df = pd.DataFrame({
        'Datum': df['Datum'],
        'Leistung Flexkraftwerk': flexpowerplant_generation
    })
    
    # Create combined dataframes
    production_ee = production_df.copy()
    consumption = consumption_df.copy()
    
    # Ensure datetime format
    production_ee['Datum'] = pd.to_datetime(production_ee['Datum'])
    consumption['Datum'] = pd.to_datetime(consumption['Datum'])
    storage_df['Datum'] = pd.to_datetime(storage_df['Datum'])
    flexpowerplant_df['Datum'] = pd.to_datetime(flexpowerplant_df['Datum'])
    
 
    # Merge all dataframes on Datum
    storage_ee_combined_df = pd.merge(
        production_ee[['Datum', 'Gesamterzeugung_EE']], 
        storage_df, 
        on='Datum'
    )
    storage_ee_combined_df['Restenergiebedarf in MWh'] = df['Differenz in MWh'] - storage_df['Speicher Entladekapazität'] + storage_df['Speicher Ladekapazität']
    
    
    # Add storage discharge to renewable generation
    storage_ee_combined_df['Speicher + Erneuerbare in MWh'] = (
        storage_ee_combined_df['Gesamterzeugung_EE'] + 
        storage_ee_combined_df['Speicher Entladekapazität'] -
        storage_ee_combined_df['Speicher Ladekapazität'])
    storage_ee_combined_df['Restenergiebedarf in MWh'] = difference_df['Differenz in MWh'] - storage_df['Speicher Entladekapazität'] + storage_df['Speicher Ladekapazität'] 
    
    # Merge with flexible power plant data
    all_combined_df = pd.merge(storage_ee_combined_df, flexpowerplant_df, on='Datum')
    all_combined_df['EE + Speicher + Flexible in MWh'] = (
        all_combined_df['Speicher + Erneuerbare in MWh'] + 
        all_combined_df['Leistung Flexkraftwerk']
    )
    
    # Create new difference dataframe - FIX: Use np.clip instead of .clip with upper parameter
    new_difference_df = pd.DataFrame({
        'Datum': df['Datum'],
        'Restenergiebedarf in MWh': -np.clip(new_difference, None, 0)  # Only negative values
    })
    
    # Calculate residual values
    residual_power = abs(new_difference_df['Restenergiebedarf in MWh']).max()
    residual_energy = abs(new_difference_df['Restenergiebedarf in MWh']).sum()
    
    # Calculate maximum power needed for flex power plant
    calculated_flexpower = abs(new_difference_df['Restenergiebedarf in MWh']).max()
    
    # Save results to CSV files
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    storage_df.to_csv(os.path.join(output_dir, 'storage_operation.csv'), index=False)
    flexpowerplant_df.to_csv(os.path.join(output_dir, 'flexpowerplant_operation.csv'), index=False)
    storage_ee_combined_df.to_csv(os.path.join(output_dir, 'storage_renewables_combined.csv'), index=False)
    all_combined_df.to_csv(os.path.join(output_dir, 'all_sources_combined.csv'), index=False)
    new_difference_df.to_csv(os.path.join(output_dir, 'residual_energy_demand.csv'), index=False)
    
    # Return different values based on the name parameter
    if name == "calculation just storage":
        result = (storage_df, storage_ee_combined_df, new_difference_df, calculated_flexpower)
    elif name == "calculation Storage + flexipowerplant":
        result = (flexpowerplant_df, all_combined_df, new_difference_df)
    else:
        result = (
            storage_df,
            flexpowerplant_df,
            storage_ee_combined_df,
            all_combined_df,
            new_difference_df,
            residual_power,
            residual_energy
        )
    
    # Cache the results
    _cache[cache_key] = result
    
    return result

# Helper function to clear cache when needed
def clear_cache():
    """Clear all cached results"""
    global _cache
    _cache = {}
    from functools import lru_cache
    _find_continuous_periods.cache_clear()
