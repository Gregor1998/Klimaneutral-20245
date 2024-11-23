from utils.calcDifference import differenceBetweenDataframes

import pandas as pd

def test_differenceBetweenDataframes():
    data1 = {
        'Datum': pd.date_range(start='2023-01-01', periods=5, freq='D'),
        'Gesamtverbrauch': [100, 200, 150, 130, 180]
    }
    data2 = {
        'Datum': pd.date_range(start='2023-01-01', periods=5, freq='D'),
        'Gesamterzeugung_EE': [80, 190, 120, 100, 170]
    }

    df1 = pd.DataFrame(data1)
    df2 = pd.DataFrame(data2)

    result = differenceBetweenDataframes(df1, df2)

    assert result is not None, "Expected a result, got None."
    assert ((len(result) == len(df1)) and (len(result) == len(df2)))

