from utils.performance_factors import performance_factors
import pandas as pd
import unittest

class TestPerformanceFactors(unittest.TestCase): #Testklasse für die Funktion performance_factors

    def setUp(self):
    #Bespieldaten für directoryGeneration und directoryInstalled
        self.directoryGeneration = {
            2017: pd.DataFrame({
                'Datum': pd.date_range(start='2017-01-01 00:00:00', end='2017-12-31 23:45:00', freq='15min'),
                'Photovoltaik': [1] * 8760,
                'Wind Onshore': [2] * 8760,
                'Wind Offshore': [3] * 8760
            }),
            2018: pd.DataFrame({
                'Datum': pd.date_range(start='2018-01-01 00:00:00', end='2018-12-31 23:45:00', freq='15min'),
                'Photovoltaik': [1.5] * 8784,
                'Wind Onshore': [2.5] * 8784,
                'Wind Offshore': [3.5] * 8784
            })
        }

        self.directoryInstalled = {
            2017: pd.DataFrame({
                'Photovoltaik': [1000],
                'Wind Onshore': [2000],
                'Wind Offshore': [3000]
            }),
            2018: pd.DataFrame({
                'Photovoltaik': [1500],
                'Wind Onshore': [2500],
                'Wind Offshore': [3500]
            })
        }

    def test_performance_factors(self):
        result = performance_factors(self.directoryGeneration, self.directoryInstalled)
        
        # Überprüfe, ob das Ergebnis ein Dictionary ist
        self.assertIsInstance(result, dict)
        
        # Überprüfe, ob das Jahr 2017 im Ergebnis enthalten ist
        self.assertIn(2017, result)
        
        # Überprüfe, ob das Ergebnis für 2015 ein DataFrame ist
        self.assertIsInstance(result[2017], pd.DataFrame)
        
        # Überprüfe, ob die Spalten im DataFrame korrekt sind
        self.assertListEqual(list(result[2017].columns), ["Datum", "Photovoltaik", "Wind Onshore", "Wind Offshore"])
        
        # Überprüfe, ob die Anzahl der Zeilen im DataFrame korrekt ist
        self.assertEqual(len(result[2017]), 35040)
        
        # Überprüfe einige Werte im DataFrame
        self.assertAlmostEqual(result[2017]["Photovoltaik"].iloc[0], 1 / (1000 * 0.25))
        self.assertAlmostEqual(result[2017]["Wind Onshore"].iloc[0], 2 / (2000 * 0.25))
        self.assertAlmostEqual(result[2017]["Wind Offshore"].iloc[0], 3 / (3000 * 0.25))

if __name__ == '__main__':
    unittest.main()