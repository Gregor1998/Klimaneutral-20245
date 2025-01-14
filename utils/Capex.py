import pandas as pd
from szenarioDefinition.szenario import *

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
    

  PV_growth = (df_PV.loc[df_PV['year'] == end_year_simulation, 'predicted_capacity'].values[0]-df_PV.loc[df_PV['year'] == start_year_simulatuion - 1, 'predicted_capacity'].values[0]) * 1000 #Umrechnung in kW
  Onshore_growth = (df_Onshore.loc[df_Onshore['year'] == end_year_simulation, 'predicted_capacity'].values[0]-df_Onshore.loc[df_Onshore['year'] == start_year_simulatuion - 1, 'predicted_capacity'].values[0]) * 1000 #Umrechnung in kW
  Offshore_growth = (df_Offshore.loc[df_Offshore['year'] == end_year_simulation, 'projected_capacity'].values[0]-df_Offshore.loc[df_Offshore['year'] == start_year_simulatuion - 1, 'projected_capacity'].values[0]) * 1000 #Umrechnung in kW
  storage_growth = (max_power_storage - max_power_storage_start_year)*1000000 #Umrechnung in kW
  flexipowerplant_growth = (max_power_flexipowerplant - max_power_flexipowerplant_start_year)* 1000000 #Umrechnung in kW

  #Kostenberechnung
  PV_costs = PV_growth * (capex_percentage_Dach_Kleinanlgage * capex_PV_Dach_Kleinanlagen +  #Kostenberechnung für PV mit den Verteilungen je Sektor
    capex_percentage_Dach_Großanlagen * capex_PV_Dach_Großanlagen + 
    capex_percentage_Freifläche * capex_PV_Freifläche + 
    capex_percentage_Agri_PV * capex_Agri_PV)/1000000000 #Umrechnung in Mrd. €
    
  Onshore_costs = Onshore_growth * capex_Onshore/1000000000 #Kostenberechnung für Onshore in Mrd. €

  Offshore_costs = Offshore_growth * capex_Offshore /1000000000 #Kostenberechnung für Offshore in Mrd. €

  Storage_costs = storage_growth * (capex_percentage_Bat_PV_klein * capex_Bat_PV_klein +  #Kostenberechnung für Speicher mit den Verteilungen je Sektor
    capex_percentage_Bat_PV_groß * capex_Bat_PV_groß + 
    capex_percentage_Bat_PV_frei * capex_Bat_PV_frei)/1000000000 #Umrechnung in Mrd. €
    
  Flexipowerplant_costs = flexipowerplant_growth * (capex_H2_Gasturbine * capex_percentage_H2_Gasturbine + capex_H2_GuD * capex_percentage_H2_GuD) /1000000000 #Kostenberechnung für Flexipowerplant
  
  total_costs = PV_costs + Onshore_costs + Offshore_costs + Storage_costs + Flexipowerplant_costs #Gesamtkostenberechnung

#Zuweisung der Kosten zu dem Dataframe
  costs_df.loc[0] = [PV_costs, Onshore_costs, Offshore_costs, Storage_costs, Flexipowerplant_costs, total_costs]
  
  print(costs_df)
    

