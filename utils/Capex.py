# =============================================================================
# Capital Expenditure (CAPEX) Calculation Module
# =============================================================================
# This module calculates the investment costs (CAPEX) for different energy systems
# including photovoltaic (PV), onshore wind, offshore wind, energy storage systems,
# and flexible power plants. The calculations are based on capacity growth projections
# and specific cost parameters defined in the configuration.
# =============================================================================

import pandas as pd
from utils import config

def capex():
  """
  Calculate the capital expenditure for energy systems based on projected capacity growth.
  Returns a DataFrame with costs in billions of euros.
  """

  # Create DataFrame to store cost calculations for each technology
  costs_df = pd.DataFrame(columns=['PV-Kosten [Mrd. €]', 'Onshore-Kosten [Mrd. €]', 'Offshore-Kosten [Mrd. €]', 
                  'Speicher-Kosten [Mrd. €]', 'Flexipowerplant-Kosten [Mrd €]', 'Gesamtkosten [Mrd. €]'])

  # Define file paths for capacity projection data
  filepath_PV = f'CSV/Installed/PV_projections.csv'
  filepath_Onshore = f'CSV/Installed/Onshore_projections.csv'
  filepath_Offshore = f'CSV/Installed/Offshore_projections.csv'

  # Load projection data from CSV files
  df_PV = pd.read_csv(filepath_PV)
  df_Onshore = pd.read_csv(filepath_Onshore)
  df_Offshore = pd.read_csv(filepath_Offshore)
  
  # Calculate capacity growth for each technology (end year minus start year)
  # Converting units to kilowatts (kW) for consistent calculations
  PV_growth = (df_PV.loc[df_PV['year'] == config.params.end_year_simulation, 'projected_capacity'].values[0] - 
        df_PV.loc[df_PV['year'] == config.params.start_year_simulation - 1, 'projected_capacity'].values[0]) * 1000
  
  Onshore_growth = (df_Onshore.loc[df_Onshore['year'] == config.params.end_year_simulation, 'projected_capacity'].values[0] - 
            df_Onshore.loc[df_Onshore['year'] == config.params.start_year_simulation - 1, 'projected_capacity'].values[0]) * 1000
  
  Offshore_growth = (df_Offshore.loc[df_Offshore['year'] == config.params.end_year_simulation, 'projected_capacity'].values[0] - 
            df_Offshore.loc[df_Offshore['year'] == config.params.start_year_simulation - 1, 'projected_capacity'].values[0]) * 1000
  
  # Calculate storage and flexible power plant growth from configuration
  storage_growth = (config.params.max_power_storage - config.params.max_power_storage_start_year) * 1000000
  flexipowerplant_growth = (config.params.max_power_flexipowerplant - config.params.max_power_flexipowerplant_start_year) * 1000000

  # === Cost calculations for each technology ===
  
  # PV costs: weighted average across different PV installation types (roof small, roof large, ground, agri)
  PV_costs = PV_growth * (
    config.params.capex_percentage_Dach_Kleinanlgage * config.params.capex_PV_Dach_Kleinanlagen +
    config.params.capex_percentage_Dach_Großanlagen * config.params.capex_PV_Dach_Großanlagen + 
    config.params.capex_percentage_Freifläche * config.params.capex_PV_Freifläche + 
    config.params.capex_percentage_Agri_PV * config.params.capex_Agri_PV
  ) / 1000000000  # Convert to billions of euros
  
  # Onshore wind costs
  Onshore_costs = Onshore_growth * config.params.capex_Onshore / 1000000000
  
  # Offshore wind costs
  Offshore_costs = Offshore_growth * config.params.capex_Offshore / 1000000000
  
  # Storage costs: weighted average across different battery storage types
  Storage_costs = storage_growth * (
    config.params.capex_percentage_Bat_PV_klein * config.params.capex_Bat_PV_klein +
    config.params.capex_percentage_Bat_PV_groß * config.params.capex_Bat_PV_groß + 
    config.params.capex_percentage_Bat_PV_frei * config.params.capex_Bat_PV_frei
  ) / 1000000000
  
  # Flexible power plant costs: weighted average of H2 gas turbine and combined cycle plant
  Flexipowerplant_costs = flexipowerplant_growth * (
    config.params.capex_H2_Gasturbine * config.params.capex_percentage_H2_Gasturbine + 
    config.params.capex_H2_GuD * config.params.capex_percentage_H2_GuD
  ) / 1000000000
  
  # Calculate total costs across all technologies
  total_costs = PV_costs + Onshore_costs + Offshore_costs + Storage_costs + Flexipowerplant_costs

  # Add calculated costs to the DataFrame
  costs_df.loc[0] = [PV_costs, Onshore_costs, Offshore_costs, Storage_costs, Flexipowerplant_costs, total_costs]
  
  return costs_df


def capex_theoretically_storage():
  """
  Function stub for calculating theoretical storage costs.
  Currently incomplete.
  """
  costs_df = pd.DataFrame(columns=['Speicher-Kosten [Mrd. €]'])
  
  # This function appears to be incomplete
  df = pd.read_csv
