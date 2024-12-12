import unittest
import pandas as pd
from utils.determinePerformanceSzenarios import determinePerformanceSzenarios

class TestDeterminePerformanceSzenarios(unittest.TestCase):

    def setUp(self):
        # Beispiel-Daten für directory_performance
        self.directory_performance = {
            2017: pd.DataFrame({
                'Datum': pd.date_range(start='2017-01-01 00:00:00', end='2017-12-31 23:45:00', freq='15T'),
                'Photovoltaik': [1] * 35040,
                'Wind Onshore': [2] * 35040,
                'Wind Offshore': [3] * 35040
            }),
            2018: pd.DataFrame({
                'Datum': pd.date_range(start='2018-01-01 00:00:00', end='2018-12-31 23:45:00', freq='15T'),
                'Photovoltaik': [1.5] * 35040,
                'Wind Onshore': [2.5] * 35040,
                'Wind Offshore': [3.5] * 35040
            })
        }

    def test_determinePerformanceSzenarios(self):
        result = determinePerformanceSzenarios(self.directory_performance)
        
        # Überprüfe, ob das Ergebnis ein Dictionary ist
        self.assertIsInstance(result, dict)
        
        # Überprüfe, ob die Schlüssel "BestCase", "WorstCase" und "AverageCase" im Ergebnis enthalten sind
        self.assertIn("BestCase", result)
        self.assertIn("WorstCase", result)
        self.assertIn("AverageCase", result)
        
        # Überprüfe, ob die Werte für "BestCase", "WorstCase" und "AverageCase" DataFrames sind
        self.assertIsInstance(result["BestCase"], pd.DataFrame)
        self.assertIsInstance(result["WorstCase"], pd.DataFrame)
        self.assertIsInstance(result["AverageCase"], pd.DataFrame)
        
        # Überprüfe, ob die Spalten im DataFrame korrekt sind
        self.assertListEqual(list(result["BestCase"].columns), ["Photovoltaik", "Wind Onshore", "Wind Offshore"])
        self.assertListEqual(list(result["WorstCase"].columns), ["Photovoltaik", "Wind Onshore", "Wind Offshore"])
        self.assertListEqual(list(result["AverageCase"].columns), ["Photovoltaik", "Wind Onshore", "Wind Offshore"])
        
        # Überprüfe, ob die Anzahl der Zeilen im DataFrame korrekt ist
        self.assertEqual(len(result["BestCase"]), 35040)
        self.assertEqual(len(result["WorstCase"]), 35040)
        self.assertEqual(len(result["AverageCase"]), 35040)

if __name__ == '__main__':
    unittest.main()