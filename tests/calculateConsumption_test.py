from utils.calculateConsumption import calculateConsumption
import pandas as pd

def test_calculateConsumption():
    consumption_development_rate = 0.02
    years_to_check = [2024, 2025, 2026, 2027, 2028, 2029, 2030]
    expected_rows = 365 * 24 * 4

    result = calculateConsumption(consumption_development_rate)

    for year in years_to_check:
        assert result.get(year) is not None, f"Expected result for year {year}, but got None."
        assert len(result.get(year)) == expected_rows, f"Expected {expected_rows} rows for year {year}, but got {len(result.get(year))}."


    