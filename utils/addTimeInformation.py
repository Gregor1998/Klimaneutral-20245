def addTimeInformation(df):
    df['Time'] = df['Datum'].dt.time
    df['Month'] = df['Datum'].dt.strftime('%b')
    df['Year Month'] = df['Datum'].dt.strftime('%Y %m')
    df['Year Month Day'] = df['Datum'].dt.strftime('%Y %m %d')
    df['Day'] = df['Datum'].dt.strftime('%d')
    df['Year'] = df['Datum'].dt.strftime('%Y')
    df['Weekday'] = df['Datum'].dt.strftime('%u')
    df['Week'] = df['Datum'].dt.strftime('%W')
    return df