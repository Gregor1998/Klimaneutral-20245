import pandas as pd

def cleanse_dataframes(df1, df2):
    # Konvertieren der 'Datum'-Spalte in ein Datetime-Format
    df1['Datum'] = pd.to_datetime(df1['Datum'], format='%Y-%m-%d %H:%M')
    df2['Datum'] = pd.to_datetime(df2['Datum'], format='%Y-%m-%d %H:%M')

    # Finden der gemeinsamen Zeitstempel
    common_dates = pd.merge(df1[['Datum']], df2[['Datum']], on='Datum', how='inner')

    # Filtern der DataFrames basierend auf den gemeinsamen Zeitstempeln
    df1 = df1[df1['Datum'].isin(common_dates['Datum'])]
    df2 = df2[df2['Datum'].isin(common_dates['Datum'])]

    # Entfernen doppelter Einträge in der 'Datum'-Spalte
    df1 = df1.drop_duplicates(subset=['Datum'])
    df2 = df2.drop_duplicates(subset=['Datum'])

    # Zurücksetzen des Indexes, um die Lücken zu schließen
    df1.reset_index(drop=True, inplace=True)
    df2.reset_index(drop=True, inplace=True)

    return df1, df2