import pandas as pd

def cleanse_dataframes(df1, df2):
    """
    Cleanses and synchronizes two dataframes by ensuring they have matching timestamps.
    This function converts date columns to datetime format, filters both dataframes to include
    only common timestamps, removes duplicates, and resets indexes.
    
    Parameters:
    df1 (DataFrame): First pandas dataframe to cleanse
    df2 (DataFrame): Second pandas dataframe to cleanse
    
    Returns:
    tuple: A pair of cleansed dataframes with matching timestamps
    """
    # Konvertieren der 'Datum'-Spalte in ein Datetime-Format
    # Ensures dates are in a consistent format for comparison
    df1['Datum'] = pd.to_datetime(df1['Datum'], format='%Y-%m-%d %H:%M')
    df2['Datum'] = pd.to_datetime(df2['Datum'], format='%Y-%m-%d %H:%M')

    # Finden der gemeinsamen Zeitstempel
    # Identifies timestamps that exist in both dataframes to sync the data
    common_dates = pd.merge(df1[['Datum']], df2[['Datum']], on='Datum', how='inner')

    # Filtern der DataFrames basierend auf den gemeinsamen Zeitstempeln
    # Keep only rows with timestamps that appear in both dataframes
    df1 = df1[df1['Datum'].isin(common_dates['Datum'])]
    df2 = df2[df2['Datum'].isin(common_dates['Datum'])]

    # Entfernen doppelter Einträge in der 'Datum'-Spalte
    # Ensures each timestamp appears only once in each dataframe
    df1 = df1.drop_duplicates(subset=['Datum'])
    df2 = df2.drop_duplicates(subset=['Datum'])

    # Zurücksetzen des Indexes, um die Lücken zu schließen
    # Reindex to ensure continuous integer indices after filtering
    df1.reset_index(drop=True, inplace=True)
    df2.reset_index(drop=True, inplace=True)

    return df1, df2