import pandas as pd # type: ignore

# Verbrauch - Produktion
def differenceBetweenDataframes(df1, df2):
    
    if df1['Datum'].equals(df2['Datum']):
        # Berechne die Differenz zwischen Verbrauch und Produktion
        difference_df = pd.DataFrame()
        difference_df['Datum'] = df1['Datum']
        difference_df['Differenz in MWh'] =  df1['Gesamtverbrauch']- df2['Gesamterzeugung_EE']

        difference_df['Year Month'] = difference_df['Datum'].dt.strftime('%Y %m')
        difference_df['Day'] = difference_df['Datum'].dt.strftime('%d')
        
        #print(difference_df)
        return difference_df
    else:
        #print("Die Zeitachsen der DataFrames stimmen nicht überein.")
        return None
    

def StorageIntegration(generation_df, difference_df, storage_capacity, flexipowerplant_power):
    """
    Integrates storage based on the difference dataframe, storage capacity, and threshold.
    Parameters:
    difference_df (pd.DataFrame): DataFrame containing 'Datum' and 'Differenz' columns.
    storage_capacity (int): Maximum storage capacity.
    threshold (int): Threshold value for difference.
    Returns:
    pd.DataFrame: DataFrame with 'Datum', 'Differenz', 'Speicher', and 'Netz' columns, where 'Speicher' represents the storage values and 'Netz' represents the net energy flow.
    """
    storage = 0
    flexipowerplant = 0
    battery_capacity = storage_capacity * 10**3# in Mwh
    #pumpstorage_capacity = pumpstorage_capacity * 10**6
    flexipowerplant_power = flexipowerplant_power * 10**3# in MW
    flexipowerplant_capacity = flexipowerplant_power * (15/60) # in Mwh

    storage_df = pd.DataFrame()
    storage_df['Datum'] = difference_df['Datum']
    storage_df['Differenz in MWh'] = difference_df['Differenz in MWh']
    storage_df['Kapazität in MWh'] = 0.0
    storage_df['Laden/Einspeisen in MWh'] = 0.0

    """pumpstorage_df = pd.DataFrame()
    pumpstorage_df['Datum'] = difference_df['Datum']
    pumpstorage_df['Einspeisung in MWh'] = 0.0"""

    flexipowerplant_df = pd.DataFrame()
    flexipowerplant_df['Datum'] = difference_df['Datum']
    flexipowerplant_df['Kapazität in MWh'] = flexipowerplant_capacity
    flexipowerplant_df['Restkapazität in MWh'] = flexipowerplant_capacity
    flexipowerplant_df['Einspeisung in MWh'] = 0.0

    for i in range(len(difference_df)):
        diff = difference_df.loc[i, 'Differenz in MWh']
        
        if diff < 0:  # Überschussenergie
            if storage < battery_capacity:
                if storage + abs(diff) > battery_capacity:
                    storage = battery_capacity
                    storage_df.loc[i, 'Kapazität in MWh'] = storage
                    storage_df.loc[i, 'Laden/Einspeisen in MWh'] = (-1)*diff
                else:
                    storage += abs(diff)
                    storage_df.loc[i, 'Kapazität in MWh'] = storage
                    storage_df.loc[i, 'Laden/Einspeisen in MWh'] = (-1)*diff
            else:
                storage_df.loc[i, 'Kapazität in MWh'] = storage
                storage_df.loc[i, 'Laden/Einspeisen in MWh'] = 0
        else:  # Energiedefizit
            if storage > 0:
                if storage - diff < 0:
                    storage_df.loc[i, 'Kapazität in MWh'] = storage
                    storage_df.loc[i, 'Laden/Einspeisen in MWh'] = (-1)*storage
                    flexipowerplant_df.loc[i, 'Einspeisung in MWh'] = storage - diff
                    flexipowerplant_df.loc[i, 'Restkapazität in MWh'] = flexipowerplant_capacity - abs(storage - diff)
                    storage = 0
                else :
                    storage -= diff
                    storage_df.loc[i, 'Kapazität in MWh'] = storage
                    storage_df.loc[i, 'Laden/Einspeisen in MWh'] = (-1)*diff
            else:
                storage_df.loc[i, 'Kapazität in MWh'] = 0
                storage_df.loc[i, 'Laden/Einspeisen in MWh'] = 0
                if flexipowerplant_capacity - abs(diff) > 0:
                    flexipowerplant_df.loc[i, 'Einspeisung in MWh'] = (-1)*diff
                    flexipowerplant_df.loc[i, 'Restkapazität in MWh'] = flexipowerplant_capacity - abs(storage - diff)
                else: 
                    flexipowerplant_df.loc[i, 'Einspeisung in MWh'] = (-1)*flexipowerplant_capacity
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

    return storage_df, flexipowerplant_df, storage_ee_combined_df, all_combined_df

"""def StorageIntegration(difference_df, storage_capacity):
    
    Integrates storage based on the difference dataframe, storage battery_capacity, and threshold.
    Parameters:
    difference_df (pd.DataFrame): DataFrame containing 'Datum' and 'Differenz' columns.
    storage_capacity (int): Maximum storage capacity.
    threshold (int): Threshold value for difference.
    Returns:
    pd.DataFrame: DataFrame with 'Datum', 'Differenz', 'Speicher', and 'Netz' columns, where 'Speicher' represents the storage values and 'Netz' represents the net energy flow.
    
    storage = 0
    storage_df = pd.DataFrame()
    storage_df['Datum'] = difference_df['Datum']
    storage_df['Differenz'] = difference_df['Differenz']
    storage_df['Speicher'] = 0
    storage_df['Netz'] = 0

    for i in range(len(difference_df)):
        diff = difference_df.loc[i, 'Differenz']
        
        if diff > 0:  # Überschussenergie
            if storage + diff <= storage_capacity:
                storage += diff
                storage_df.loc[i, 'Speicher'] = storage
            else:
                storage_df.loc[i, 'Netz'] = storage + diff - storage_capacity
                storage = storage_capacity
                storage_df.loc[i, 'Speicher'] = storage
        else:  # Energiedefizit
            if storage + diff >= 0:
                storage += diff
                storage_df.loc[i, 'Speicher'] = storage
            else:
                storage_df.loc[i, 'Netz'] = storage + diff
                storage = 0
                storage_df.loc[i, 'Speicher'] = storage

    return storage_df"""