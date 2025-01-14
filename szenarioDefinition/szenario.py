import pandas as pd
import xlwings as xw
import matplotlib.pyplot as plt
from openpyxl import load_workbook
from openpyxl.drawing.image import Image
import os

# Alle Tabellen aus der Excel-Datei laden
excel_file = pd.ExcelFile('szenarioDefinition/szenario_parameter_test1.xlsx')
szenarien = {}
# Excel-Datei lesen
df = pd.read_excel('szenarioDefinition/szenario_parameter_test1.xlsx')

# Variablen zuweisen
general_scenario_name = df.loc[df['Variable'] == 'scenario_name', 'Wert'].values[0]
PV_scenario = df.loc[df['Variable'] == 'pv_scenario', 'Wert'].values[0]
Onshore_scenario = df.loc[df['Variable'] == 'onshore_scenario', 'Wert'].values[0]
Offshore_scenario = df.loc[df['Variable'] == 'offshore_scenario', 'Wert'].values[0]
consumption_development_per_year = df.set_index('Jahr')['Verbrauchsentwicklung'].dropna().to_dict()
onshore_development_rate = df.loc[df['Variable'] == 'onshore_development_rate', 'Wert'].values[0]
offshore_development_rate = df.loc[df['Variable'] == 'offshore_development_rate', 'Wert'].values[0]
pv_development_rate = df.loc[df['Variable'] == 'pv_development_rate', 'Wert'].values[0]
CO2_factor_Kohle = df.loc[df['Variable'] == 'CO2_factor_Kohle', 'Wert'].values[0]
CO2_factor_Gas = df.loc[df['Variable'] == 'CO2_factor_Gas', 'Wert'].values[0]
share_coal = df.loc[df['Variable'] == 'share_coal', 'Wert'].values[0]
share_gas = df.loc[df['Variable'] == 'share_gas', 'Wert'].values[0]
IST_installierte_waermepumpen = df.loc[df['Variable'] == 'IST_installierte_waermepumpen', 'Wert'].values[0]
SOLL_installierte_waermepumpen = df.loc[df['Variable'] == 'SOLL_installierte_waermepumpen', 'Wert'].values[0]
gridlost = df.loc[df['Variable'] == 'gridlost', 'Wert'].values[0]
consumption_year = int(df.loc[df['Variable'] == 'consumption_year', 'Wert'].values[0]) # getDate in read_CSV consumption year of smard data
start_year_ee = int(df.loc[df['Variable'] == 'start_year_ee', 'Wert'].values[0]) # getDate in read_CSV start year of smard data
end_year_ee = int(df.loc[df['Variable'] == 'end_year_ee', 'Wert'].values[0]) # getDate in read_CSV end year of smard data
end_year_extrapolation_installed_power = int(df.loc[df['Variable'] == 'end_year_extrapolation_installed_power', 'Wert'].values[0]) # end year of trend extrapolation for installed power 
growth_rate_PV = df.loc[df['Variable'] == 'growth_rate_pv', 'Wert'].values[0]
growth_rate_Onshore = df.loc[df['Variable'] == 'growth_rate_onshore', 'Wert'].values[0]
growth_rate_Offshore = df.loc[df['Variable'] == 'growth_rate_offshore', 'Wert'].values[0]
case_performance_factor = "BestCase"  #oder AverageCase oder WorstCase 
start_year_simulatuion = 2024 # start year of simulation
end_year_simulation = 2030 # end year of simulation
base_year_generation = 2023 #Basisjahr für den Verlauf von Wasserkraft, Sonstige Erneuerbare und Biomasse
case_Temperature = "BestCase" #oder AverageCase oder WorstCase
selected_week_plot = '22' # selected week for comparison of load profile + consumption and consumption
selected_year_plot = '2030' # selected year for comparison of load profile + consumption and consumption
max_power_storage_start_year = 7.8
max_power_storage = 83
max_storage_capicity = 47
max_power_flexipowerplant = 45
max_power_flexipowerplant_start_year = 30 
capex_Onshore = 1300 #€/kW Bad Case = 1900 €/kW
capex_Offshore = 2200 #€/kW Bad Case = 3400 €/kW
capex_PV_Dach_Kleinanlagen = 1000 #€/kW Bad Case = 2500 €/kW
capex_PV_Dach_Großanlagen = 900 #€/kW Bad Case = 1600 €/kW
capex_PV_Freifläche = 700 #€/kW Bad Case = 900 €/kW
capex_Agri_PV = 900 #€/kW Bad Case = 1700 €/kW
capex_percentage_Dach_Kleinanlgage = 0.25 #Beispielwert
capex_percentage_Dach_Großanlagen = 0.25 #Beispielwert
capex_percentage_Freifläche = 0.25 #Beispielwert
capex_percentage_Agri_PV = 0.25 #Beispielwert
capex_Bat_PV_klein = 500 #€/kWh Bad Case = 1000 €/kWh
capex_Bat_PV_groß = 450 #€/kWh Bad Case = 850 €/kWh
capex_Bat_PV_frei = 400 #€/kWh Bad Case = 600 €/kWh
capex_percentage_Bat_PV_klein = 0.33 #Beispielwert
capex_percentage_Bat_PV_groß = 0.33 #Beispielwert
capex_percentage_Bat_PV_frei = 0.33 #Beispielwert
capex_H2_Gasturbine = 550 #€/kW Bad Case = 1200 €/kW
capex_H2_GuD = 1100 #€/kW Bad Case = 2400 €/kW
capex_percentage_H2_Gasturbine = 0.5 #Beispielwert
capex_percentage_H2_GuD = 0.5 #Beispielwert
 

# Ausgabe zur Überprüfung
print(consumption_development_per_year)
print(onshore_development_rate)
print(offshore_development_rate)
print(pv_development_rate)
print(CO2_factor_Kohle)
print(CO2_factor_Gas)
print(share_coal)
print(share_gas)
print(IST_installierte_waermepumpen)
print(SOLL_installierte_waermepumpen)
print(gridlost)
print(consumption_year)
print(start_year_ee)
print(end_year_ee)
