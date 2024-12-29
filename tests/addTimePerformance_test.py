import unittest
import pandas as pd
from utils.addTimePerformance import addTimePerformance

class TestAddTimePerformance(unittest.TestCase):

    def setUp(self):
        # Beispiel-Daten für den DataFrame
        self.df = pd.DataFrame({
            'Value': [1] * 35040  # Beispielwerte für ein Jahr mit 15-Minuten-Intervallen
        })

    def test_addTimePerformance(self):
        year = 2017
        result = addTimePerformance(self.df.copy(), year)
        
        # Überprüfe, ob das Ergebnis ein DataFrame ist
        self.assertIsInstance(result, pd.DataFrame)
        
        # Überprüfe, ob die Spalte 'Datum' im Ergebnis enthalten ist
        self.assertIn('Datum', result.columns)
        
        # Überprüfe, ob die Anzahl der Zeilen im DataFrame korrekt ist
        self.assertEqual(len(result), 35040)
        
        # Überprüfe, ob die Zeitreihe korrekt erstellt wurde
        expected_start_date = pd.Timestamp(f'{year}-01-01 00:00:00')
        expected_end_date = pd.Timestamp(f'{year}-12-31 23:45:00')
        self.assertEqual(result['Datum'].iloc[0], expected_start_date)
        self.assertEqual(result['Datum'].iloc[-1], expected_end_date)
        
        # Überprüfe, ob der 29. Februar entfernt wurde
        self.assertFalse(((result['Datum'].dt.month == 2) & (result['Datum'].dt.day == 29)).any())

    def test_length_mismatch(self):
        # Beispiel-Daten für den DataFrame mit falscher Länge
        df_mismatch = pd.DataFrame({
            'Value': [1] * 35000  # Falsche Anzahl von Zeilen
        })
        year = 2017
        
        with self.assertRaises(ValueError) as context:
            addTimePerformance(df_mismatch, year)
        
        self.assertTrue('Length of DataFrame and Time Range do not match' in str(context.exception))

if __name__ == '__main__':
    unittest.main()