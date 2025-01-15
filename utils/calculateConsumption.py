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
    consumption_year =  config.params.consumption_year
    directory_yearly_consumption = getData("Consumption", consumption_year) #Baisjahr für den Verbrauch
    addTimeInformation(directory_yearly_consumption[consumption_year])
    base_heatpump_lp = directory_heatpump_consumption.get(consumption_year + 1)
    

    # lastprofil abziehen
    charging_areas = ['Wohnen', 'Büro', 'Öffentliche_Ladepunkte']
    base_lastprofile_eauto = lastprofile_dict[consumption_year].copy()
    saturday = ["6"]  # Samstag
    sunday = ["7"]  # Sonntag
    workday = ["1", "2", "3", "4", "5"]  # Montag bis Freitag

    #consumption_e_auto_year_df = pd.DataFrame(columns="Verbrauch in MWh")

    for idx, row in directory_yearly_consumption[consumption_year].iterrows():
        weekday = row['Weekday']
        lp_wohnen, lp_buro, lp_public = None, None, None
        
        if weekday in saturday:
            lp_wohnen = base_lastprofile_eauto['Wohnen']['saturday']
            lp_buro = base_lastprofile_eauto['Büro']['saturday']
            lp_public = base_lastprofile_eauto['Öffentliche_Ladepunkte']['saturday']
        elif weekday in sunday:
            lp_wohnen = base_lastprofile_eauto['Wohnen']['sunday']
            lp_buro = base_lastprofile_eauto['Büro']['sunday']
            lp_public = base_lastprofile_eauto['Öffentliche_Ladepunkte']['sunday']
        elif weekday in workday:
            lp_wohnen = base_lastprofile_eauto['Wohnen']['workday']
            lp_buro = base_lastprofile_eauto['Büro']['workday']
            lp_public = base_lastprofile_eauto['Öffentliche_Ladepunkte']['workday']
        else:
            continue


        # Berechnen Sie den Index im Lastprofil-DataFrame
        lastprofil_idx = idx % len(lp_wohnen)

        # aufsummieren -> aus allen drei lastprofiltypen soll der gesamtverbrauch abgezogen werden
        lp_eautos_sum = lp_wohnen.loc[lastprofil_idx, 'Strombedarf (kWh)'] + lp_buro.loc[lastprofil_idx, 'Strombedarf (kWh)'] + lp_public.loc[lastprofil_idx, 'Strombedarf (kWh)']
        #jetzt eautos lastprofile und danach wärmepumpen vom Gesamtverbrauch abziehen
        row['Gesamtverbrauch'] -= ((lp_eautos_sum/1000) + base_heatpump_lp.loc[idx, 'Verbrauch in MWh'])

        #consumption_e_auto_year_df = consumption_e_auto_year_df.append(row['Gesamtverbrauch'], ignore_index=True)




    for year in range(config.params.start_year_simulation, config.params.end_year_simulation + 1):
        prev_year_df = directory_yearly_consumption.get(year-1).copy()    #Kopie des Dataframe des letzten Jahres
        lastprofil_waermepumpe_year = directory_heatpump_consumption.get(year) #Lastprofil für Wärmepumpe
        lastprofil_eAuto_year = lastprofile_dict[year] #Lastprofil für eAuto

        extrapolated_data = Extrapolation_Consumption(prev_year_df, year, None, None, None, consumption_development_per_year.get(year-1), lastprofil_eAuto_year, lastprofil_waermepumpe_year)        #Erstellung eines neuen Objekts, mit einem DataFrame
        directory_yearly_consumption[extrapolated_data.year] = extrapolated_data.df   #DataFrame in das Erzeugungsverzeichnis gespeichert wird

    
    return directory_yearly_consumption
