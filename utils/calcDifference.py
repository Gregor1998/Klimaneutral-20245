import pandas as pd # type: ignore

# Verbrauch - Produktion
def differenceBetweenDataframes(df1, df2):
    
    if df1['Datum'].equals(df2['Datum']):
        # Berechne die Differenz zwischen Verbrauch und Produktion
        difference_df = pd.DataFrame()
        difference_df['Datum'] = df1['Datum']
        difference_df['Differenz'] =  df1['Gesamtverbrauch']- df2['Gesamterzeugung_EE']

        difference_df['Year Month'] = difference_df['Datum'].dt.strftime('%Y %m')
        difference_df['Day'] = difference_df['Datum'].dt.strftime('%d')
        
        #print(difference_df)
        return difference_df
    else:
        #print("Die Zeitachsen der DataFrames stimmen nicht überein.")
        return None
    
"""def StorageIntegration(difference_df, storage_capacity, threshold):
    
        Integrates storage based on the difference dataframe, storage capacity, and threshold.
        Parameters:
        difference_df (pd.DataFrame): DataFrame containing 'Datum' and 'Differenz' columns.
        storage_capacity (int): Maximum storage capacity.
        threshold (int): Threshold value for difference.
        Returns:
        pd.DataFrame: DataFrame with 'Datum', 'Differenz', and 'Speicher' columns, where 'Speicher' represents the storage values.
        
        storage = 0
        storage_df = pd.DataFrame()
        storage_df['Datum'] = difference_df['Datum']
        storage_df['Differenz'] = difference_df['Differenz']
        storage_df['Speicher'] = 0

        for i in range(len(difference_df)):
            if difference_df.loc[i, 'Differenz'] > threshold:
                if storage + difference_df.loc[i, 'Differenz'] - threshold <= storage_capacity:
                   #storage += difference_df.loc[i, 'Differenz'] - threshold
                    storage = storage_capacity
                    storage_df.loc[i, 'Speicher'] = difference_df.loc[i, 'Differenz'] - storage 
                else:
                    storage = storage_capacity
                    storage_df.loc[i, 'Speicher'] = storage
            else:
                storage_df.loc[i, 'Speicher'] = storage

        return storage_df"""

def StorageIntegration(difference_df, storage_capacity):
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

    return storage_df

