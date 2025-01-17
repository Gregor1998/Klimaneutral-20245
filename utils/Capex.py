import pandas as pd
from utils import config

def capex():

  #Dataframe, um die Kosten zu speichern
  costs_df = pd.DataFrame(columns=['PV-Kosten [Mrd. €]', 'Onshore-Kosten [Mrd. €]', 'Offshore-Kosten [Mrd. €]', 'Speicher-Kosten [Mrd. €]', 'Flexipowerplant-Kosten [Mrd €]', 'Gesamtkosten [Mrd. €]'])

  #Pfade zu den CSV-Dateien, je nach Case
  filepath_PV = f'CSV/Installed/PV_projections.csv'
  filepath_Onshore = f'CSV/Installed/Onshore_projections.csv'
  filepath_Offshore = f'CSV/Installed/Offshore_projections.csv'

  df_PV = pd.read_csv(filepath_PV)
  df_Onshore = pd.read_csv(filepath_Onshore)
  df_Offshore = pd.read_csv(filepath_Offshore)
    

  PV_growth = (df_PV.loc[df_PV['year'] == config.params.end_year_simulation, 'projected_capacity'].values[0]-df_PV.loc[df_PV['year'] == config.params.start_year_simulation - 1, 'projected_capacity'].values[0]) * 1000 #Umrechnung in kW
  Onshore_growth = (df_Onshore.loc[df_Onshore['year'] == config.params.end_year_simulation, 'projected_capacity'].values[0]-df_Onshore.loc[df_Onshore['year'] == config.params.start_year_simulation - 1, 'projected_capacity'].values[0]) * 1000 #Umrechnung in kW
  Offshore_growth = (df_Offshore.loc[df_Offshore['year'] == config.params.end_year_simulation, 'projected_capacity'].values[0]-df_Offshore.loc[df_Offshore['year'] == config.params.start_year_simulation - 1, 'projected_capacity'].values[0]) * 1000 #Umrechnung in kW
  storage_growth = (config.params.max_power_storage - config.params.max_power_storage_start_year)*1000000 #Umrechnung in kW
  flexipowerplant_growth = (config.params.max_power_flexipowerplant - config.params.max_power_flexipowerplant_start_year)* 1000000 #Umrechnung in kW

  #Kostenberechnung
  PV_costs = PV_growth * (config.params.capex_percentage_Dach_Kleinanlgage * config.params.capex_PV_Dach_Kleinanlagen +  #Kostenberechnung für PV mit den Verteilungen je Sektor
    config.params.capex_percentage_Dach_Großanlagen * config.params.capex_PV_Dach_Großanlagen + 
    config.params.capex_percentage_Freifläche * config.params.capex_PV_Freifläche + 
    config.params.capex_percentage_Agri_PV * config.params.capex_Agri_PV)/1000000000 #Umrechnung in Mrd. €
    
  Onshore_costs = Onshore_growth * config.params.capex_Onshore/1000000000 #Kostenberechnung für Onshore in Mrd. €

  Offshore_costs = Offshore_growth * config.params.capex_Offshore /1000000000 #Kostenberechnung für Offshore in Mrd. €

  Storage_costs = storage_growth * (config.params.capex_percentage_Bat_PV_klein * config.params.capex_Bat_PV_klein +  #Kostenberechnung für Speicher mit den Verteilungen je Sektor
    config.params.capex_percentage_Bat_PV_groß * config.params.capex_Bat_PV_groß + 
    config.params.capex_percentage_Bat_PV_frei * config.params.capex_Bat_PV_frei)/1000000000 #Umrechnung in Mrd. €
    
  Flexipowerplant_costs = flexipowerplant_growth * (config.params.capex_H2_Gasturbine * config.params.capex_percentage_H2_Gasturbine + config.params.capex_H2_GuD * config.params.capex_percentage_H2_GuD) /1000000000 #Kostenberechnung für Flexipowerplant
  
  total_costs = PV_costs + Onshore_costs + Offshore_costs + Storage_costs + Flexipowerplant_costs #Gesamtkostenberechnung

#Zuweisung der Kosten zu dem Dataframe
  costs_df.loc[0] = [PV_costs, Onshore_costs, Offshore_costs, Storage_costs, Flexipowerplant_costs, total_costs]
  
  return costs_df


def capex_theoretically_storage():
  
  costs_df = pd.DataFrame(columns=['Speicher-Kosten [Mrd. €]'] )

  df = pd.read_csv
    

