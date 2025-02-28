"""
Energy System Balance and Storage Calculation Module
---------------------------------------------------

This module calculates and analyzes the balance between energy consumption and renewable 
energy production, then simulates energy storage and flexible power plant operations.

Key functionality:
- Calculate the difference between energy consumption and renewable production
- Find the longest periods of energy surplus and deficit
- Simulate energy storage charging/discharging behavior
- Model flexible power plant operations to meet remaining demand
- Calculate key metrics for energy system planning

The module is designed for energy system analysis and planning, particularly
for scenarios with high renewable energy penetration.
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Ensure output directory exists
Path('./CSV/Storage_co').mkdir(parents=True, exist_ok=True)

def differenceBetweenDataframes(df1, df2):
    """
    Calculates the difference between energy consumption and production dataframes.
    
    Parameters:
    df1: DataFrame containing consumption data with 'Datum' and 'Gesamtverbrauch' columns
    df2: DataFrame containing production data with 'Datum' and 'Gesamterzeugung_EE' columns
    
    Returns:
    DataFrame with date and energy difference columns, or None if dates don't match
    """
    if df1['Datum'].equals(df2['Datum']):
        # Vectorized operations instead of DataFrame creation + assignment
        difference_df = pd.DataFrame({
            'Datum': df1['Datum'],
            'Differenz in MWh': df1['Gesamtverbrauch'] - df2['Gesamterzeugung_EE']
        })
        
        # Add time period columns for easier aggregation and analysis
        difference_df['Year Month'] = difference_df['Datum'].dt.to_period('M').astype(str)
        difference_df['Day'] = difference_df['Datum'].dt.day.astype(str).str.zfill(2)
        
        return difference_df
    else:
        return None

def calculateLongestPeriods(difference_df, Case=None):
    """
    Identifies the longest continuous periods of energy surplus and deficit.
    
    Parameters:
    difference_df: DataFrame with energy difference values
    Case: String indicating the analysis case (e.g., "residual")
    
    Returns:
    Tuple of energy metrics: energy_demand, energy_power, further_demand, further_demand_power
    
    Note: Also writes CSV files with period data to the Storage_co directory
    """
    # Determine which energy column to use for calculations
    if 'Differenz in MWh' in difference_df.columns:
        energy_column = 'Differenz in MWh'
    elif 'Restenergiebedarf in MWh' in difference_df.columns:
        energy_column = 'Restenergiebedarf in MWh'
    else:
        raise ValueError("Neither 'Differenz in MWh' nor 'Restenergiebedarf in MWh' column found in the DataFrame")

    # Mark each row as positive or negative energy difference
    difference_df['Sign'] = np.where(difference_df[energy_column] > 0, 'Positive', 'Negative')
    
    # Group consecutive periods with the same sign (positive/negative)
    difference_df['Group'] = (difference_df['Sign'] != difference_df['Sign'].shift()).cumsum()
    
    # Find the longest continuous periods efficiently
    sign_groups = difference_df.groupby(['Sign', 'Group']).size()
    
    # Get longest periods more efficiently
    longest_negative_period = None
    longest_positive_period = None
    
    # Find the longest continuous negative period (energy surplus)
    if 'Negative' in sign_groups.index.get_level_values(0):
        negative_counts = sign_groups['Negative']
        if not negative_counts.empty:
            longest_negative_period = negative_counts.idxmax()
    
    # Find the longest continuous positive period (energy deficit)
    if 'Positive' in sign_groups.index.get_level_values(0):
        positive_counts = sign_groups['Positive']
        if not positive_counts.empty:
            longest_positive_period = positive_counts.idxmax()
    
    # Extract the data for the longest periods using efficient boolean masks
    longest_negative_mask = (difference_df['Sign'] == 'Negative') & (difference_df['Group'] == longest_negative_period) if longest_negative_period is not None else pd.Series(False, index=difference_df.index)
    longest_positive_mask = (difference_df['Sign'] == 'Positive') & (difference_df['Group'] == longest_positive_period) if longest_positive_period is not None else pd.Series(False, index=difference_df.index)
    
    longest_negative_df = difference_df[longest_negative_mask]
    longest_positive_df = difference_df[longest_positive_mask]

    # Calculate total energy for each period
    sum_longest_negative = longest_negative_df[energy_column].sum() if not longest_negative_df.empty else 0
    sum_longest_positive = longest_positive_df[energy_column].sum() if not longest_positive_df.empty else 0

    # Write results to CSV files for later analysis
    csv_outputs = {
        './CSV/Storage_co/longest_negative_period.csv': longest_negative_df if not longest_negative_df.empty else None,
        './CSV/Storage_co/longest_positive_period.csv': longest_positive_df if not longest_positive_df.empty else None,
        './CSV/Storage_co/sums_longest_periods.csv': pd.DataFrame({
            'Summe der längsten negativen Periode in MWh': [sum_longest_negative],
            'Summe der längsten positiven Periode in MWh': [sum_longest_positive]
        })
    }
    
    # Write files in one batch
    for path, df in csv_outputs.items():
        if df is not None:
            df.to_csv(path, index=False)

    # Calculate energy system metrics based on the case
    if Case == "residual":
        # For residual analysis, only consider positive energy needs
        energy_demand = sum_longest_positive
        energy_power = 0  # Not used in this case but keeping for consistency
    else:
        # For standard analysis, consider absolute negative period (storage need)
        energy_demand = abs(sum_longest_negative)
        energy_power = abs(difference_df[energy_column].max() / 0.25)  # Convert to power (MW)

    # Calculate additional flexibility demand based on energy balance
    if sum_longest_negative + sum_longest_positive <= 0:
        # If periods balance each other, no additional flexibility needed
        further_demand = 0
        further_demand_power = 0
    else:
        # Calculate additional flexibility requirements
        further_demand = sum_longest_negative + sum_longest_positive 
        
        # Convert to power values (MW) considering time duration
        t_negativ = len(longest_negative_df) if not longest_negative_df.empty else 1
        t_positiv = len(longest_positive_df) if not longest_positive_df.empty else 1
        negativ_power = sum_longest_negative / (t_negativ / 60)
        positiv_power = sum_longest_positive / (t_positiv / 60)
        further_demand_power = negativ_power + positiv_power if not longest_positive_df.empty else 0

    return energy_demand, energy_power, further_demand, further_demand_power

def StorageIntegration(Case, consumption_df, generation_df, difference_df, storage_max_power, storage_capacity, flexipowerplant_power):
    """
    Simulates the operation of energy storage and flexible power plants in the energy system.
    
    Parameters:
    Case: String indicating the analysis scenario
    consumption_df: DataFrame with energy consumption data
    generation_df: DataFrame with renewable energy generation data
    difference_df: DataFrame with the difference between consumption and generation
    storage_max_power: Maximum power capacity of storage in GW
    storage_capacity: Energy capacity of storage in GWh
    flexipowerplant_power: Power capacity of flexible power plant in GW
    
    Returns:
    Various DataFrames depending on the Case, including storage operation, 
    flexible power plant operation, and residual energy needs
    
    Note: Also writes CSV files with simulation results to the Storage_co directory
    """
    # Convert input parameters from GW/GWh to MW/MWh
    battery_capacity = storage_capacity * 10**3  # in MWh
    storage_max_power = storage_max_power * 10**3  # in MW
    flexipowerplant_power = flexipowerplant_power * 10**3  # in MW
    
    # Calculate flexipowerplant energy capacity (15-minute intervals)
    flexipowerplant_capacity = flexipowerplant_power * (15/60)  # in MWh
    
    # Get dataset dimensions and prepare arrays
    n_rows = len(difference_df)
    dates = difference_df['Datum']
    differences = difference_df['Differenz in MWh']
    
    # Pre-allocate arrays for better performance
    storage_values = np.zeros(n_rows)  # Current storage level
    charging_values = np.zeros(n_rows)  # Charging/discharging energy
    
    # Arrays for flexible power plant simulation
    flexipowerplant_capacities = np.full(n_rows, flexipowerplant_capacity)
    flexipowerplant_remaining = np.full(n_rows, flexipowerplant_capacity)
    flexipowerplant_input = np.zeros(n_rows)
    
    # Starting with empty storage
    storage = 0
    
    # Simulate storage and flexible power plant operation for each time step
    for i in range(n_rows):
        diff = differences.iloc[i]
        power_diff = diff / 0.25  # Convert MWh to MW for 15 minutes

        if diff < 0:  # Excess energy (production > consumption)
            if storage < battery_capacity:
                # Charge the storage with excess energy, limited by power capacity
                charge_power = min(abs(power_diff), storage_max_power)
                charge_energy = charge_power * 0.25  # Convert MW back to MWh

                # Ensure we don't exceed battery capacity
                if storage + charge_energy > battery_capacity:
                    charge_energy = battery_capacity - storage
                    storage = battery_capacity
                else:
                    storage += charge_energy

                storage_values[i] = storage
                charging_values[i] = -charge_energy  # Negative indicates charging
            else:
                # Storage is full, can't absorb more energy
                storage_values[i] = storage
        else:  # Energy deficit (consumption > production)
            # Limit discharge by power capacity
            discharge_power = min(power_diff, storage_max_power)
            discharge_energy = discharge_power * 0.25  # Convert MW back to MWh

            if storage > 0:
                # Discharge from storage to meet demand
                if storage - discharge_energy < 0:
                    discharge_energy = storage
                    storage = 0
                else:
                    storage -= discharge_energy

                storage_values[i] = storage
                charging_values[i] = discharge_energy  # Positive indicates discharging
            else:
                # Storage is empty, use flexible power plant if needed
                storage_values[i] = 0
                if flexipowerplant_capacity - abs(diff) > 0:
                    flexipowerplant_input[i] = -discharge_energy
                    flexipowerplant_remaining[i] = flexipowerplant_capacity - abs(discharge_energy)
                else:
                    flexipowerplant_input[i] = -flexipowerplant_capacity
                    flexipowerplant_remaining[i] = 0
    
    # Create result DataFrames from simulation data
    storage_df = pd.DataFrame({
        'Datum': dates,
        'Differenz in MWh': differences,
        'Kapazität in MWh': storage_values,
        'Laden/Einspeisen in MWh': charging_values
    })

    # Flexible power plant operation data
    flexipowerplant_df = pd.DataFrame({
        'Datum': dates,
        'Kapazität in MWh': flexipowerplant_capacities,
        'Restkapazität in MWh': flexipowerplant_remaining,
        'Einspeisung in MWh': flexipowerplant_input
    })
    
    # Get renewable energy generation values
    ee_generation = generation_df['Gesamterzeugung_EE']
    
    # Create combined result dataframes for different analysis perspectives
    storage_ee_combined_df = pd.DataFrame({
        'Datum': dates,
        'Produktion EE in MWh': ee_generation,
        'Laden/Einspeisen in MWh': charging_values,
        'Speicher + Erneuerbare in MWh': ee_generation + charging_values,
        'Restenergiebedarf in MWh': differences - charging_values
    })

    all_combined_df = pd.DataFrame({
        'Datum': dates,
        'Produktion EE in MWh': ee_generation,
        'Laden/Einspeisen in MWh': charging_values,
        'Flexipowerplant Einspeisung in MWh': flexipowerplant_input,
        'EE + Speicher + Flexible in MWh': ee_generation + charging_values - flexipowerplant_input
    })

    # Calculate residual energy needs after storage and flexible plant operation
    new_difference_df = pd.DataFrame({
        'Datum': dates,
        'Restenergiebedarf in MWh': differences - charging_values + flexipowerplant_input
    })
    
    # Save results to CSV files
    new_difference_df.to_csv(f'./CSV/Storage_co/{Case}_difference.csv', index=False)
    
    # Calculate key performance metrics
    positive_sum = new_difference_df.loc[new_difference_df['Restenergiebedarf in MWh'] > 0, 'Restenergiebedarf in MWh'].sum()
    max_value = new_difference_df['Restenergiebedarf in MWh'].max() / 0.25
    
    # Return appropriate results based on the analysis case
    if Case == "calculation just storage":
        # For storage-only scenario
        flex_power_demand = max_value / 0.25
        storage_df.to_csv(f'./CSV/Storage_co/{Case}_storage.csv', index=False)
        storage_ee_combined_df.to_csv(f'./CSV/Storage_co/{Case}_storage_ee_combined.csv', index=False)
        return storage_df, storage_ee_combined_df, new_difference_df, flex_power_demand
    elif Case == "calculation Storage + flexipowerplant":
        # For combined storage and flexible power scenario
        storage_df.to_csv(f'./CSV/Storage_co/{Case}_storage.csv', index=False)
        flexipowerplant_df.to_csv(f'./CSV/Storage_co/{Case}_flexipowerplant.csv', index=False)
        storage_ee_combined_df.to_csv(f'./CSV/Storage_co/{Case}_storage_ee_combined.csv', index=False)
        all_combined_df.to_csv(f'./CSV/Storage_co/{Case}_all_combined.csv', index=False)
        return flexipowerplant_df, all_combined_df, new_difference_df
    else:
        # Default case with comprehensive outputs
        storage_df.to_csv(f'./CSV/Storage_co/{Case}_storage.csv', index=False)
        flexipowerplant_df.to_csv(f'./CSV/Storage_co/{Case}_flexipowerplant.csv', index=False)
        storage_ee_combined_df.to_csv(f'./CSV/Storage_co/{Case}_storage_ee_combined.csv', index=False)
        all_combined_df.to_csv(f'./CSV/Storage_co/{Case}_all_combined.csv', index=False)
        return storage_df, flexipowerplant_df, storage_ee_combined_df, all_combined_df, new_difference_df, max_value, positive_sum