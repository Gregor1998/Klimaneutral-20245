from unittest.mock import patch
import os
import pandas as pd # type: ignore

from utils.read_CSV import getData

EXPECTED_COLUMNS_ERZEUGUNG = ["Datum", "Wind Offshore", "Wind Onshore", "Photovoltaik"]
EXPECTED_COLUMNS_VERBRAUCH = ["Datum", "Gesamtverbrauch"]

def test_verbrauch_csv_existence():
    with patch("os.path.exists") as mock_path_exists:
        # Mock os.path.exists to simulate file existence
        mock_path_exists.side_effect = lambda path: "2023" in path

        # Call the function with "Verbrauch" mode
        result = getData("Verbrauch")

        # Check that the result includes 2023 since the file "exists"
        assert 2023 in result, "Expected year 2023 to be in the result."

        # Verify the correct file path was checked
        expected_path = os.path.join(
            "CSV/Verbrauch/",
            "Realisierter_Stromverbrauch_202301010000_202401010000_Viertelstunde.csv"
        )
        mock_path_exists.assert_any_call(expected_path)

        # Verify that no unexpected years were added to the result
        assert len(result) == 1, f"Expected 1 year in the result, got {len(result)}."

def test_read_SMARD_data_erzeugung():
    from utils.read_CSV import read_SMARD_data

    path = "CSV/Realisierte_Erzeugung_202301010000_202401010000_Viertelstunde.csv"
    result = read_SMARD_data(path, "Erzeugung")
    # Tatsächliche Spalten im DataFrame
    result_columns = list(result.columns)

    assert set(EXPECTED_COLUMNS_ERZEUGUNG).issubset(result_columns), "Nicht alle erwarteten Spalten sind im DataFrame enthalten"


def test_read_SMARD_data_verbrauch():
    from utils.read_CSV import read_SMARD_data

    path = "CSV/Verbrauch/Realisierter_Stromverbrauch_202301010000_202401010000_Viertelstunde.csv"
    result = read_SMARD_data(path, "Verbrauch")
    # Tatsächliche Spalten im DataFrame
    result_columns = list(result.columns)

    assert set(EXPECTED_COLUMNS_VERBRAUCH).issubset(result_columns), "Nicht alle erwarteten Spalten sind im DataFrame enthalten"


    
    
