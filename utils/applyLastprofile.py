def apply_lastprofile(df, lastprofil, waermepumpe, operation):
    lastprofile_mapping = {
        '6': {
            'Wohnen': lastprofil['Wohnen']['saturday'],
            'Büro': lastprofil['Büro']['saturday'],
            'Öffentliche_Ladepunkte': lastprofil['Öffentliche_Ladepunkte']['saturday']
        },
        '7': {
            'Wohnen': lastprofil['Wohnen']['sunday'],
            'Büro': lastprofil['Büro']['sunday'],
            'Öffentliche_Ladepunkte': lastprofil['Öffentliche_Ladepunkte']['sunday']
        },
        '1': {
            'Wohnen': lastprofil['Wohnen']['workday'],
            'Büro': lastprofil['Büro']['workday'],
            'Öffentliche_Ladepunkte': lastprofil['Öffentliche_Ladepunkte']['workday']
        },
        '2': {
            'Wohnen': lastprofil['Wohnen']['workday'],
            'Büro': lastprofil['Büro']['workday'],
            'Öffentliche_Ladepunkte': lastprofil['Öffentliche_Ladepunkte']['workday']
        },
        '3': {
            'Wohnen': lastprofil['Wohnen']['workday'],
            'Büro': lastprofil['Büro']['workday'],
            'Öffentliche_Ladepunkte': lastprofil['Öffentliche_Ladepunkte']['workday']
        },
        '4': {
            'Wohnen': lastprofil['Wohnen']['workday'],
            'Büro': lastprofil['Büro']['workday'],
            'Öffentliche_Ladepunkte': lastprofil['Öffentliche_Ladepunkte']['workday']
        },
        '5': {
            'Wohnen': lastprofil['Wohnen']['workday'],
            'Büro': lastprofil['Büro']['workday'],
            'Öffentliche_Ladepunkte': lastprofil['Öffentliche_Ladepunkte']['workday']
        }
    }

    for idx, row in df.iterrows():
        weekday = row['Weekday']
        if weekday not in lastprofile_mapping:
            continue

        lp_wohnen = lastprofile_mapping[weekday]['Wohnen']
        lp_buro = lastprofile_mapping[weekday]['Büro']
        lp_public = lastprofile_mapping[weekday]['Öffentliche_Ladepunkte']

        # Berechnen Sie den Index im Lastprofil-DataFrame
        lastprofil_idx = idx % len(lp_wohnen)

        lp_eautos_sum = lp_wohnen.loc[lastprofil_idx, 'Strombedarf (kWh)'] + lp_buro.loc[lastprofil_idx, 'Strombedarf (kWh)'] + lp_public.loc[lastprofil_idx, 'Strombedarf (kWh)']

        # Fügen Sie den Wert aus dem Lastprofil-DataFrame hinzu oder ziehen Sie ihn ab
        if operation == 'add':
            df.loc[idx, 'Gesamtverbrauch'] += ((lp_eautos_sum / 1000) + waermepumpe.loc[idx, 'Verbrauch'])
        elif operation == 'subtract':
            df.loc[idx, 'Gesamtverbrauch'] -= ((lp_eautos_sum / 1000) + waermepumpe.loc[idx, 'Verbrauch'])
