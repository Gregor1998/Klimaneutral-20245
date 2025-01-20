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

        
        return difference_df
    else:
        return None

def calculateLongestPeriods(difference_df, Case=None):
    # Überprüfen, ob die Spalte 'Differenz in MWh' existiert, andernfalls 'Restenergiebedarf in MWh' verwenden
    if 'Differenz in MWh' in difference_df.columns:
        energy_column = 'Differenz in MWh'
    elif 'Restenergiebedarf in MWh' in difference_df.columns:
        energy_column = 'Restenergiebedarf in MWh'
    else:
        raise ValueError("Neither 'Differenz in MWh' nor 'Restenergiebedarf in MWh' column found in the DataFrame")

    difference_df['Sign'] = difference_df[energy_column].apply(lambda x: 'Positive' if x > 0 else 'Negative')
    difference_df['Group'] = (difference_df['Sign'] != difference_df['Sign'].shift()).cumsum()

    negative_groups = difference_df[difference_df['Sign'] == 'Negative'].groupby('Group').size()

    if not negative_groups.empty:
        longest_negative_period = negative_groups.idxmax()
    else:
        longest_negative_period = 0    

    positive_groups = difference_df[difference_df['Sign'] == 'Positive'].groupby('Group').size()

    if not positive_groups.empty:
        longest_positive_period = positive_groups.idxmax()
    else:
        longest_positive_period = 0  

        
    longest_negative_df = difference_df[difference_df['Group'] == longest_negative_period] if longest_negative_period is not None else pd.DataFrame()
    longest_positive_df = difference_df[difference_df['Group'] == longest_positive_period] if longest_positive_period is not None else pd.DataFrame()

    # Save the longest periods to separate CSV files
    if not longest_negative_df.empty:
        longest_negative_df.to_csv('./CSV/Storage_co/longest_negative_period.csv', index=False)
    if not longest_positive_df.empty:
        longest_positive_df.to_csv('./CSV/Storage_co/longest_positive_period.csv', index=False)

    # Calculate the sum of the longest negative and positive periods
    sum_longest_negative = longest_negative_df[energy_column].sum() if not longest_negative_df.empty else 0
    sum_longest_positive = longest_positive_df[energy_column].sum() if not longest_positive_df.empty else 0

    if Case == "residual":
        energy_demand = sum_longest_positive
    else:
        energy_demand = abs(sum_longest_negative)
        energy_power = abs(difference_df[energy_column].max() / 0.25)

    # Calculate flex demand
    if sum_longest_negative + sum_longest_positive <= 0:
        further_demand = 0
        further_demand_power = 0
    else:
        further_demand = sum_longest_negative + sum_longest_positive 
        # Count the number of rows in longest_negative_df and longest_positive_df
        t_negativ = len(longest_negative_df) if not longest_negative_df.empty else 1
        t_positiv = len(longest_positive_df) if not longest_positive_df.empty else 1
        negativ_power = sum_longest_negative / (t_negativ / 60)
        positiv_power = sum_longest_positive / (t_positiv / 60)
        further_demand_power = negativ_power + positiv_power if not longest_positive_df.empty else 0

    # Save the sums to a CSV file
    sums_df = pd.DataFrame({
        'Summe der längsten negativen Periode in MWh': [sum_longest_negative],
        'Summe der längsten positiven Periode in MWh': [sum_longest_positive]
    })

    sums_df.to_csv('./CSV/Storage_co/sums_longest_periods.csv', index=False)

    return energy_demand, energy_power, further_demand, further_demand_power

def StorageIntegration(Case, consumption_df, generation_df, difference_df, storage_max_power, storage_capacity, flexipowerplant_power):
    
    storage = 0
    battery_capacity = storage_capacity * 10**3  # in MWh
    storage_max_power = storage_max_power * 10**3  # in MW
    flexipowerplant_power = flexipowerplant_power * 10**3  # in MW
    flexipowerplant_capacity = flexipowerplant_power * (15/60)  # in MWh

    storage_df = pd.DataFrame({
        'Datum': difference_df['Datum'],
        'Differenz in MWh': difference_df['Differenz in MWh'],
        'Kapazität in MWh': 0.0,
        'Laden/Einspeisen in MWh': 0.0
    })

    flexipowerplant_df = pd.DataFrame({
        'Datum': difference_df['Datum'],
        'Kapazität in MWh': flexipowerplant_capacity,
        'Restkapazität in MWh': flexipowerplant_capacity,
        'Einspeisung in MWh': 0.0
    })

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

    storage_ee_combined_df = pd.DataFrame({
        'Datum': storage_df['Datum'],
        'Produktion EE in MWh': generation_df['Gesamterzeugung_EE'],
        'Laden/Einspeisen in MWh': storage_df['Laden/Einspeisen in MWh'],
        'Speicher + Erneuerbare in MWh': generation_df['Gesamterzeugung_EE'] + storage_df['Laden/Einspeisen in MWh'],
        'Restenergiebedarf in MWh': difference_df['Differenz in MWh'] - storage_df['Laden/Einspeisen in MWh']
    })

    all_combined_df = pd.DataFrame({
        'Datum': difference_df['Datum'],
        'Produktion EE in MWh': generation_df['Gesamterzeugung_EE'],
        'Laden/Einspeisen in MWh': storage_df['Laden/Einspeisen in MWh'],
        'Flexipowerplant Einspeisung in MWh': flexipowerplant_df['Einspeisung in MWh'],
        'EE + Speicher + Flexible in MWh': generation_df['Gesamterzeugung_EE'] + storage_df['Laden/Einspeisen in MWh'] - flexipowerplant_df['Einspeisung in MWh']
    })

    new_difference_df = pd.DataFrame({
        'Datum': all_combined_df['Datum'],
        'Restenergiebedarf in MWh': difference_df['Differenz in MWh'] - storage_df['Laden/Einspeisen in MWh'] + flexipowerplant_df['Einspeisung in MWh']
    })
    # Save the new dataframes to CSV
    new_difference_df.to_csv(f'./CSV/Storage_co/{Case}_difference.csv', index=False)

    # Calculate the sum of all positive values in the 'Restenergiebedarf in MWh' column
    positive_sum = new_difference_df[new_difference_df['Restenergiebedarf in MWh'] > 0]['Restenergiebedarf in MWh'].sum()

    # Find the maximum value in the 'Restenergiebedarf in MWh' column
    max_value = new_difference_df['Restenergiebedarf in MWh'].max() / 0.25

    if Case == "calculation just storage":
        flex_power_demand = max_value / 0.25
        storage_df.to_csv(f'./CSV/Storage_co/{Case}_storage.csv')
        storage_ee_combined_df.to_csv(f'./CSV/Storage_co/{Case}_storage_ee_combined.csv')
        return storage_df, storage_ee_combined_df, new_difference_df, flex_power_demand
    elif Case == "calculation Storage + flexipowerplant":
        storage_df.to_csv(f'./CSV/Storage_co/{Case}_storage.csv')
        flexipowerplant_df.to_csv(f'./CSV/Storage_co/{Case}_flexipowerplant.csv')
        storage_ee_combined_df.to_csv(f'./CSV/Storage_co/{Case}_storage_ee_combined.csv')
        all_combined_df.to_csv(f'./CSV/Storage_co/{Case}_all_combined.csv')
        return flexipowerplant_df, all_combined_df, new_difference_df
    else:
        storage_df.to_csv(f'./CSV/Storage_co/{Case}_storage.csv')
        flexipowerplant_df.to_csv(f'./CSV/Storage_co/{Case}_flexipowerplant.csv')
        storage_ee_combined_df.to_csv(f'./CSV/Storage_co/{Case}_storage_ee_combined.csv')
        all_combined_df.to_csv(f'./CSV/Storage_co/{Case}_all_combined.csv')
        return storage_df, flexipowerplant_df, storage_ee_combined_df, all_combined_df, new_difference_df, max_value, positive_sum