import pandas as pd
from utils.read_CSV import getData
from utils.combineDataFrames import combineDataFrames
from utils.extraploation_class import Extrapolation, Extrapolation_Consumption
from utils.addTimeInformation import addTimeInformation
#from szenarioDefinition.szenario import*
from utils import config

def calculateConsumption(consumption_development_per_year): 
    directory_yearly_consumption = getData("Consumption", config.params.consumption_year)

    for year in range(config.params.start_year_simulation, config.params.end_year_simulation + 1):
        prev_year_df =directory_yearly_consumption.get(year-1).copy()    #Kopie des Dataframe des letzten Jahres
        extrapolated_data = Extrapolation(prev_year_df, year, None, None, None, consumption_development_per_year.get(year-1))        #Erstellung eines neuen Objekts, mit einem DataFrame
        directory_yearly_consumption[extrapolated_data.year]= extrapolated_data.df   #DataFrame in das Erzeugungsverzeichnis gespeichert wird

    
    return directory_yearly_consumption




def getConsumptionYear(year, data_df):
    return data_df.get(year)


def calculateConsumption_lastprofile(consumption_development_per_year, lastprofile_dict, directory_heatpump_consumption):
    consumption_year = config.params.consumption_year
    directory_yearly_consumption = getData("Consumption", consumption_year)
    addTimeInformation(directory_yearly_consumption[consumption_year])
    base_heatpump_lp = directory_heatpump_consumption.get(consumption_year + 1)

    # Helper function to apply lastprofile values (subtract or add)
    def apply_lastprofile(df, lastprofile, heatpump_profile, mode="subtract"):
        saturday = ["6"]
        sunday = ["7"]
        workday = ["1", "2", "3", "4", "5"]

        for idx, row in df.iterrows():
            weekday = row['Weekday']
            lp_wohnen, lp_buro, lp_public = None, None, None

            if weekday in saturday:
                lp_wohnen = lastprofile['Wohnen']['saturday']
                lp_buro = lastprofile['Büro']['saturday']
                lp_public = lastprofile['Öffentliche_Ladepunkte']['saturday']
            elif weekday in sunday:
                lp_wohnen = lastprofile['Wohnen']['sunday']
                lp_buro = lastprofile['Büro']['sunday']
                lp_public = lastprofile['Öffentliche_Ladepunkte']['sunday']
            elif weekday in workday:
                lp_wohnen = lastprofile['Wohnen']['workday']
                lp_buro = lastprofile['Büro']['workday']
                lp_public = lastprofile['Öffentliche_Ladepunkte']['workday']
            else:
                continue

            lastprofil_idx = idx % len(lp_wohnen)
            lp_eautos_sum = (
                lp_wohnen.loc[lastprofil_idx, 'Strombedarf (kWh)'] +
                lp_buro.loc[lastprofil_idx, 'Strombedarf (kWh)'] +
                lp_public.loc[lastprofil_idx, 'Strombedarf (kWh)']
            )

            # Adjust 'Gesamtverbrauch' based on the mode
            adjustment_value = (lp_eautos_sum / 1000) + heatpump_profile.loc[idx, 'Verbrauch in MWh']
            if mode == "subtract":
                df.loc[idx, 'Gesamtverbrauch'] -= adjustment_value
            elif mode == "add":
                df.loc[idx, 'Gesamtverbrauch'] += adjustment_value

        return df

    # **Step 1: Subtract lastprofile from base year**
    directory_yearly_consumption[consumption_year] = apply_lastprofile(
        directory_yearly_consumption[consumption_year],
        lastprofile_dict[consumption_year],
        base_heatpump_lp,
        mode="subtract"
    )

    # **Step 2: Extrapolate for all years**
    for year in range(config.params.start_year_simulation, config.params.end_year_simulation + 1):
        prev_year_df = directory_yearly_consumption.get(year - 1).copy()
        extrapolated_data = Extrapolation_Consumption(
            prev_year_df, year, None, None, None, consumption_development_per_year.get(year - 1)
        )
        directory_yearly_consumption[extrapolated_data.year] = extrapolated_data.df

    # **Step 3: Add back lastprofile to each year after extrapolation**
    for year in range(config.params.start_year_simulation, config.params.end_year_simulation + 1):
        directory_yearly_consumption[year] = apply_lastprofile(
            directory_yearly_consumption[year],
            lastprofile_dict[year],
            directory_heatpump_consumption.get(year, base_heatpump_lp),
            mode="add"
        )

    return directory_yearly_consumption
