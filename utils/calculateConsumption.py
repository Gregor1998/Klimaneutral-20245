import pandas as pd
from utils.read_CSV import getData
from utils.combineDataFrames import combineDataFrames
from utils.extraploation_class import Extrapolation, Extrapolation_Consumption
from utils.addTimeInformation import addTimeInformation
#from szenarioDefinition.szenario import*
from utils import config

def calculateConsumption(consumption_development_per_year, lastprofile_dict, directory_heatpump_consumption): 
    consumption_year = config.params.consumption_year
    directory_yearly_consumption = getData("Consumption", consumption_year)
    addTimeInformation(directory_yearly_consumption[consumption_year])
    base_heatpump_lp = directory_heatpump_consumption.get(consumption_year + 1)





    # Helper function to apply lastprofile values (subtract or add)
    def apply_lastprofile(df, lastprofile, heatpump_profile, mode="subtract"):
        # Define mapping of weekdays to profiles
        profile_mapping = {
            "6": "saturday",
            "7": "sunday",
            "1": "workday",
            "2": "workday",
            "3": "workday",
            "4": "workday",
            "5": "workday"
        }

        # Map weekdays to profile names
        df['profile'] = df['Weekday'].map(profile_mapping)

        # Drop rows with weekdays not in the mapping
        df = df[df['profile'].notna()]

        # Function to compute the adjustment value for each row
        def compute_adjustment(row):
            profile_name = row['profile']
            lastprofil_idx = row.name % len(lastprofile['Wohnen'][profile_name])
            
            lp_wohnen = lastprofile['Wohnen'][profile_name].loc[lastprofil_idx, 'Strombedarf (kWh)']
            lp_buro = lastprofile['Büro'][profile_name].loc[lastprofil_idx, 'Strombedarf (kWh)']
            lp_public = lastprofile['Öffentliche_Ladepunkte'][profile_name].loc[lastprofil_idx, 'Strombedarf (kWh)']

            lp_eautos_sum = lp_wohnen + lp_buro + lp_public
            adjustment_value = (lp_eautos_sum / 1000) + heatpump_profile.loc[row.name, 'Verbrauch in MWh']

            if mode == "subtract":
                return row['Gesamtverbrauch'] - adjustment_value
            elif mode == "add":
                return row['Gesamtverbrauch'] + adjustment_value
            else:
                return row['Gesamtverbrauch']  # No adjustment if mode is invalid

        # Apply the adjustment computation function
        df['Gesamtverbrauch'] = df.apply(compute_adjustment, axis=1)

        # Drop the temporary profile column
        df.drop(columns=['profile'], inplace=True)

        return df

    # **Step 1: Subtract lastprofile from base year**
    directory_yearly_consumption[consumption_year] = apply_lastprofile(
        directory_yearly_consumption[consumption_year],
        lastprofile_dict[consumption_year],
        base_heatpump_lp,
        mode="subtract"
    )

    directory_yearly_consumption[consumption_year].to_csv("CSV/testing/consumption_2023.csv")



    # **Step 2: Extrapolate for all years**
    for year in range(config.params.start_year_simulation, config.params.end_year_simulation + 1):
        prev_year_df = directory_yearly_consumption.get(year - 1).copy()

        print("PREV", prev_year_df)
        print("FAKTOR", consumption_development_per_year.get(year - 1))

        

        extrapolated_data = Extrapolation_Consumption(
            prev_year_df, year, None, None, None, consumption_development_per_year.get(year)
        )

        
        directory_yearly_consumption[extrapolated_data.year] = extrapolated_data.df

        print("UPDATE", directory_yearly_consumption[extrapolated_data.year])

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
        # Define mapping of weekdays to profiles
        profile_mapping = {
            "6": "saturday",
            "7": "sunday",
            "1": "workday",
            "2": "workday",
            "3": "workday",
            "4": "workday",
            "5": "workday"
        }

        # Map weekdays to profile names
        df['profile'] = df['Weekday'].map(profile_mapping)

        # Drop rows with weekdays not in the mapping
        df = df[df['profile'].notna()]

        # Function to compute the adjustment value for each row
        def compute_adjustment(row):
            profile_name = row['profile']
            lastprofil_idx = row.name % len(lastprofile['Wohnen'][profile_name])
            
            lp_wohnen = lastprofile['Wohnen'][profile_name].loc[lastprofil_idx, 'Strombedarf (kWh)']
            lp_buro = lastprofile['Büro'][profile_name].loc[lastprofil_idx, 'Strombedarf (kWh)']
            lp_public = lastprofile['Öffentliche_Ladepunkte'][profile_name].loc[lastprofil_idx, 'Strombedarf (kWh)']

            lp_eautos_sum = lp_wohnen + lp_buro + lp_public
            adjustment_value = (lp_eautos_sum / 1000) + heatpump_profile.loc[row.name, 'Verbrauch in MWh']

            if mode == "subtract":
                return row['Gesamtverbrauch'] - adjustment_value
            elif mode == "add":
                return row['Gesamtverbrauch'] + adjustment_value
            else:
                return row['Gesamtverbrauch']  # No adjustment if mode is invalid

        # Apply the adjustment computation function
        df['Gesamtverbrauch'] = df.apply(compute_adjustment, axis=1)

        # Drop the temporary profile column
        df.drop(columns=['profile'], inplace=True)

        return df

    # **Step 1: Subtract lastprofile from base year**
    directory_yearly_consumption[consumption_year] = apply_lastprofile(
        directory_yearly_consumption[consumption_year],
        lastprofile_dict[consumption_year],
        base_heatpump_lp,
        mode="subtract"
    )

    directory_yearly_consumption[consumption_year].to_csv("CSV/testing/consumption_2023.csv")



    # **Step 2: Extrapolate for all years**
    for year in range(config.params.start_year_simulation, config.params.end_year_simulation + 1):
        prev_year_df = directory_yearly_consumption.get(year - 1).copy()

        print("PREV", prev_year_df)
        print("FAKTOR", consumption_development_per_year.get(year - 1))

        

        extrapolated_data = Extrapolation_Consumption(
            prev_year_df, year, None, None, None, consumption_development_per_year.get(year)
        )

        
        directory_yearly_consumption[extrapolated_data.year] = extrapolated_data.df

        print("UPDATE", directory_yearly_consumption[extrapolated_data.year])
        directory_yearly_consumption[extrapolated_data.year].to_csv(f"CSV/testing/consumption_after_hochrechnung_{year}.csv")

    


    # **Step 3: Add back lastprofile to each year after extrapolation**
    for year in range(config.params.start_year_simulation, config.params.end_year_simulation + 1):
        directory_yearly_consumption[year] = apply_lastprofile(
            directory_yearly_consumption[year],
            lastprofile_dict[year],
            directory_heatpump_consumption.get(year, base_heatpump_lp),
            mode="add"
        )
        directory_yearly_consumption[year].to_csv(f"CSV/testing/consumption_final_mit_lp_{year}.csv")

    return directory_yearly_consumption
