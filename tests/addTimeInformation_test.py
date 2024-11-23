from utils.addTimeInformation import addTimeInformation
import pandas as pd

def test_addTimeInformation():
    expected_columns = [
        'Datum', 'Time', 'Month', 'Year Month', 'Year Month Day',
        'Day', 'Year', 'Weekday', 'Week'
    ]

    # Create a DataFrame with a 'Datum' and on one day
    data = {
            'Datum': pd.to_datetime(['2024-11-23 14:30:00', '2024-11-24 16:45:00'])
        }
    df = pd.DataFrame(data)

    # Call the function
    updated_df = addTimeInformation(df)

    # Check that the columns were added
    assert set(expected_columns).issubset(updated_df.columns), "Not all expected columns were added to the DataFrame."

    # Check that the added values make sense, just for this one day
    assert updated_df['Time'][0] == pd.to_datetime('14:30:00').time(), "Time column is incorrect."
    assert updated_df['Month'][0] == 'Nov', "Month column is incorrect."
    assert updated_df['Year Month'][0] == '2024 11', "Year Month column is incorrect."
    assert updated_df['Year Month Day'][0] == '2024 11 23', "Year Month Day column is incorrect."
    assert updated_df['Day'][0] == '23', "Day column is incorrect."
    assert updated_df['Year'][0] == '2024', "Year column is incorrect."
    assert updated_df['Weekday'][0] == '6', "Weekday column is incorrect."
    assert updated_df['Weekday'][1] == '7', "Weekday column is incorrect." # check cross day as well/ example date switches from 23. to 14. of november
    assert updated_df['Week'][0] == '47', "Week column is incorrect."
