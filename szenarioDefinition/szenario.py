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
