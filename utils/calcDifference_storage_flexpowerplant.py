import pandas as pd # type: ignore

# Verbrauch - Produktion
def differenceBetweenDataframes(df1, df2):
    
    if df1['Datum'].equals(df2['Datum']):
        # Berechne die Differenz zwischen Verbrauch und Produktion
        difference_df = pd.DataFrame()
        difference_df['Datum'] = df1['Datum']
        difference_df['Differenz in MWh'] = df1['Gesamtverbrauch'] - df2['Gesamterzeugung_EE']

        difference_df['Year Month'] = difference_df['Datum'].dt.strftime('%Y %m')
        difference_df['Day'] = difference_df['Datum'].dt.strftime('%d')
        
        # Find the longest period of negative and positive differences
        difference_df['Sign'] = difference_df['Differenz in MWh'].apply(lambda x: 'Positive' if x > 0 else 'Negative')
        difference_df['Group'] = (difference_df['Sign'] != difference_df['Sign'].shift()).cumsum()

        longest_negative_period = difference_df[difference_df['Sign'] == 'Negative'].groupby('Group').size().idxmax()
        longest_positive_period = difference_df[difference_df['Sign'] == 'Positive'].groupby('Group').size().idxmax()

        longest_negative_df = difference_df[difference_df['Group'] == longest_negative_period]
        longest_positive_df = difference_df[difference_df['Group'] == longest_positive_period]

        # Save the longest periods to separate CSV files
        longest_negative_df.to_csv('./CSV/Storage_co/longest_negative_period.csv', index=False)
        longest_positive_df.to_csv('./CSV/Storage_co/longest_positive_period.csv', index=False)

        # Calculate the sum of the longest negative and positive periods
        sum_longest_negative = longest_negative_df['Differenz in MWh'].sum()
        sum_longest_positive = longest_positive_df['Differenz in MWh'].sum()

        # Save the sums to a CSV file
        sums_df = pd.DataFrame({
            'Summe der längsten negativen Periode in MWh': [sum_longest_negative],
            'Summe der längsten positiven Periode in MWh': [sum_longest_positive]
        })

        sums_df.to_csv('./CSV/Storage_co/sums_longest_periods.csv', index=False)

        return difference_df, longest_negative_df, longest_positive_df, sums_df
    else:
        return None
    

def StorageIntegration(generation_df, difference_df, storage_max_power, storage_capacity, flexipowerplant_power):
    """
    Integrates storage based on the difference dataframe, storage capacity, and threshold.
    Parameters:
    difference_df (pd.DataFrame): DataFrame containing 'Datum' and 'Differenz' columns.
    storage_capacity (int): Maximum storage capacity.
    storage_max_power (int): Maximum power for charging/discharging the storage.
    flexipowerplant_power (int): Maximum power for the flexible power plant.
    Returns:
    pd.DataFrame: DataFrame with 'Datum', 'Differenz', 'Speicher', and 'Netz' columns, where 'Speicher' represents the storage values and 'Netz' represents the net energy flow.
    """
    
    storage = 0
    flexipowerplant = 0
    battery_capacity = storage_capacity * 10**3  # in MWh
    storage_max_power = storage_max_power * 10**3  # in MW
    flexipowerplant_power = flexipowerplant_power * 10**3  # in MW
    flexipowerplant_capacity = flexipowerplant_power * (15/60)  # in MWh

    storage_df = pd.DataFrame()
    storage_df['Datum'] = difference_df['Datum']
    storage_df['Differenz in MWh'] = difference_df['Differenz in MWh']
    storage_df['Kapazität in MWh'] = 0.0
    storage_df['Laden/Einspeisen in MWh'] = 0.0

    flexipowerplant_df = pd.DataFrame()
    flexipowerplant_df['Datum'] = difference_df['Datum']
    flexipowerplant_df['Kapazität in MWh'] = flexipowerplant_capacity
    flexipowerplant_df['Restkapazität in MWh'] = flexipowerplant_capacity
    flexipowerplant_df['Einspeisung in MWh'] = 0.0

    for i in range(len(difference_df)):
        diff = difference_df.loc[i, 'Differenz in MWh']
        power_diff = diff / 0.25  # Convert MWh to MW for 15 minutes

        if diff < 0:  # Überschussenergie
            if storage < battery_capacity:
                charge_power = min(abs(power_diff), storage_max_power)
                charge_energy = charge_power * 0.25  # Convert MW back to MWh

                if storage + charge_energy > battery_capacity:
                    charge_energy = battery_capacity - storage
                    storage = battery_capacity
                else:
                    storage += charge_energy

                storage_df.loc[i, 'Kapazität in MWh'] = storage
                storage_df.loc[i, 'Laden/Einspeisen in MWh'] = -charge_energy
            else:
                storage_df.loc[i, 'Kapazität in MWh'] = storage
                storage_df.loc[i, 'Laden/Einspeisen in MWh'] = 0
        else:  # Energiedefizit
            discharge_power = min(power_diff, storage_max_power)
            discharge_energy = discharge_power * 0.25  # Convert MW back to MWh

            if storage > 0:
                if storage - discharge_energy < 0:
                    discharge_energy = storage
                    storage = 0
                else:
                    storage -= discharge_energy

                storage_df.loc[i, 'Kapazität in MWh'] = storage
                storage_df.loc[i, 'Laden/Einspeisen in MWh'] = discharge_energy
            else:
                storage_df.loc[i, 'Kapazität in MWh'] = 0
                storage_df.loc[i, 'Laden/Einspeisen in MWh'] = 0
                if flexipowerplant_capacity - abs(diff) > 0:
                    flexipowerplant_df.loc[i, 'Einspeisung in MWh'] = -discharge_energy
                    flexipowerplant_df.loc[i, 'Restkapazität in MWh'] = flexipowerplant_capacity - abs(discharge_energy)
                else:
                    flexipowerplant_df.loc[i, 'Einspeisung in MWh'] = -flexipowerplant_capacity
                    flexipowerplant_df.loc[i, 'Restkapazität in MWh'] = 0

    storage_ee_combined_df = pd.DataFrame()
    storage_ee_combined_df['Datum'] = storage_df['Datum']
    storage_ee_combined_df['Produktion EE in MWh'] = generation_df['Gesamterzeugung_EE']
    storage_ee_combined_df['Laden/Einspeisen in MWh'] = storage_df['Laden/Einspeisen in MWh']
    storage_ee_combined_df['Speicher + Erneuerbare in MWh'] = storage_ee_combined_df['Produktion EE in MWh'] - storage_ee_combined_df['Laden/Einspeisen in MWh']

    all_combined_df = pd.DataFrame()
    all_combined_df['Datum'] = difference_df['Datum']
    all_combined_df['Produktion EE in MWh'] = generation_df['Gesamterzeugung_EE']
    all_combined_df['Laden/Einspeisen in MWh'] = storage_df['Laden/Einspeisen in MWh']
    all_combined_df['Flexipowerplant Einspeisung in MWh'] = flexipowerplant_df['Einspeisung in MWh']
    all_combined_df['EE + Speicher + Flexible in MWh'] = all_combined_df['Produktion EE in MWh'] - all_combined_df['Laden/Einspeisen in MWh'] - all_combined_df['Flexipowerplant Einspeisung in MWh']

    storage_df.to_csv('./CSV/Storage_co/storage.csv')
    flexipowerplant_df.to_csv('./CSV/Storage_co/flexipowerplant.csv')
    storage_ee_combined_df.to_csv('./CSV/Storage_co/storage_ee_combined.csv')
    all_combined_df.to_csv('./CSV/Storage_co/all_combined.csv')

    #return storage_df, flexipowerplant_df, storage_ee_combined_df, all_combined_df
    # Calculate the new difference after storage and flexible power plant integration
    new_difference_df = pd.DataFrame()
    new_difference_df['Datum'] = all_combined_df['Datum']
    new_difference_df['Restenergiebedarf in MWh'] = difference_df['Differenz in MWh'] - all_combined_df['EE + Speicher + Flexible in MWh']

    # Calculate the new difference after storage integration only
    new_difference_storage_only_df = pd.DataFrame()
    new_difference_storage_only_df['Datum'] = storage_ee_combined_df['Datum']
    new_difference_storage_only_df['Restenergiebedarf in MWh'] = difference_df['Differenz in MWh'] - storage_ee_combined_df['Speicher + Erneuerbare in MWh']

    # Save the new dataframes to CSV
    new_difference_df.to_csv('./CSV/Storage_co/new_difference.csv', index=False)
    new_difference_storage_only_df.to_csv('./CSV/Storage_co/new_difference_storage_only.csv', index=False)

    return storage_df, flexipowerplant_df, storage_ee_combined_df, all_combined_df, new_difference_df, new_difference_storage_only_df
    # Find the maximum values in the new difference dataframes
    max_new_difference = new_difference_df['Restenergiebedarf in MWh'].max()
    max_new_difference_storage_only = new_difference_storage_only_df['Restenergiebedarf in MWh'].max()

    # Save the maximum values to a CSV file
    max_values_df = pd.DataFrame({
        'Max Restenergiebedarf in MWh': [max_new_difference, max_new_difference_storage_only],
        'Type': ['With Flexible Power Plant', 'Storage Only']
    })

    max_values_df.to_csv('./CSV/Storage_co/max_values.csv', index=False)