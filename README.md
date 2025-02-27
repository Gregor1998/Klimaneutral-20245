# Klimaneutral-20245
Simulationssoftware für die Erreichung der Klimaziele bis 2030/45. Es können Szenarien definiert und jeweils eine Hochrechnung bis zum Zieljahr (zB. 2030) gemacht werden. Die Parameter werden in der Exceltabelle "simulation_szenario.xlsm" festgelegt.

## Installation

Notwendig zur Ausführung des Programms ist eine 3.x Python-Version auf dem Sytem, sowie Anaconda als Packagemanagement-Umgebung. Das Programm läuft besser in Anaconda eingebettet, und einige Module sind dann bereits installiert und arbeiten besser zusammen.

Per Hand sollten folgende Installationsschritte ausgeführt werden:

```sh
 
python --version
 
python -m pip install --upgrade pip

pip install pandas numpy seaborn xlwings papermill plotly scikit-learn openpyxl joblib jupyter kaleido
python -c "import xlwings; print(xlwings.__version__)"
xlwings addin install
 
```
Dann:

Excel öffnen -> Makros zulassen -> Excelwings sollte in der Funktionsleiste sichtbar sein
 
Gewünschtes Tabellenblatt öffnen -> Button klicken -> Run Simulation


In einer Zelle über dem Button schreibt das Programm "Simulation running..." zum Zeichen, das Python gerade im Hintergrund arbeitet - leider gibt es keinen Fortschrittsbalken.
Ist ein Durchlauf komplett öffnet sich ein neues Tabellenblatt: "xx - Result".

### Alternative Ausführung
Ggf. bietet es sich während der Entwicklung an, das Programm direkt hier zu starten.
In dem Fall kann die python-main auch direkt ausgeführt werden:

**simulation_szenario/simulation_szenario.py** öffnen, und von hier die **main** ausführen, hier ist wiederum im Terminal auch ein Fortschrittsbalken, sowie eine Fehlerausgabe sichtbar.



## Überblick: Struktur

### Haupt-Notebook
Die ursprünglich erstellten Jupyter-Notebooks sind immernoch enthalten:
Das HauptNotebook, das alle Funktionen zusammenhält und aufruft (und von der python-main): **prototyp_2.ipynb**
hier sieht man auch, welche Funktionen alle als utils importiert und genutzt werden.

Der Variablenblock am Start des Notebooks sind alle Variablen, die von Excel an das Notebook zur Berechnung der Simulation übergeben werden, diese werden dort automatisiert hineingeschreiben.

Der Ablauf ist dann linear: Zuerst wird die Erzeugung hochgerechnet, dann der Verbrauch, und dann wird der Speicheralgorithmus darüber gelegt, und es werden die Plots erstellt.
Das Notebook enthält wiederum selbst auch Beschreibungen, die Aufschluss über die einzelnene Codee-Blöcke geben.

Auch von hier kann eine Simulation ausgeführt werden, sofern der Variablenblock am Start des Notebooks bereits Werte enthält -> dies ist insbesondere zum Entwickeln hilfreich.

### python main (simulation_szenario)

Die python main liegt unter **simulation_szenario/simulation_szenario.py**
Von hier kann ein Simulationsdurchgang gestartet werden.
**Dafür muss die Excel-Tabelle des Users geöffnet sein** - das derzeit geöffnete Tabellenblatt wird vom Programm genutzt, und die Szenario-Parameterwerte von dort übernommen.
Ist in der Excel-Tabelle ein Blatt geöffnet, dass geschriebene Ergebnisse eines vorherigen Durchlaufs enthält, funktioniert das Programm nicht, da die Parameter in diesem Tabellenblatt nicht gefunden/ausgelesen werden können.


### Excel-Tabelle (simulation_szenario)
Die Excel Tabelle, die User öffnen und womit sie interagieren liegt unter **simulation_szenario/simulation_szenario.xlsm**
Sie enthält Makros, die beim Öffnen aktiviert werden müssen.
Über den Button "Run Simulation" kann ein Simulationsdurchgang gestartet werden. Von dem Blatt, von dem der Button angeglickt wird, werden auch die Parameter an das Programm übergeben.

### Parameter aus Excel-Tabelle
Die Parameter mit denen eine Simulation berechnet werden soll, können ausschließlich im entsprechenden Excel-Tabellenblatt definiert werden.
Diese werden vom package Papermill aus der Exceltabelle an das Notebook übergeben, daher stammen die großen Variablenblöcke oben im Notebook - nicht schön, leider nicht anders umsetzbar in diesem Projektrahmen.

Damit die Parameter auch von den util-Funktionen genutzt und importiert werden können, werden die Parameter nach der Übergabe durch Papermill nochmal in ein config-Objekt (selbst ein util in **utils/config.py**) geschrieben:

```python
# write all injected parameters to config.py to be able to access them from other modules
from utils import config
from utils.castParmeters import cast_parameters, Params, filter_injected_params

# Filter and cast parameters
params_dict = cast_parameters(filter_injected_params(locals()))


# Convert to a Python object
params = Params(params_dict)

# Update the config with the params object
config.params = params
```



Dieses kann überall importiert werden:
```python
from utils import config
```

Im Code werden die Parameter verwendet als:
```python
config.params.xxx
```


## Utils/Module
Der Code wurde zu umfangreich für ein/mehrere Jupyter-Notebook, und Funktionen wurden deshalb als utils ausgelagert in **utils/...**
Diese könne erweitert werden, um Dopplungen zu vermeiden -> KISS


## Ergebnisse: wo zu finden
Alle Bilder/plots werden in **assets/plots** geschrieben.

Einige Dataframes werden zurück in CSV-Dateien geschrieben, um sie danach an die Excel zurück zu geben, sie liegen in **CSV/Results/...**. Die Dateien sind sprechend benannt und werden für jeden Simulationsdurchlauf überschrieben.

Vom Speicheralgorithmus berechnete Werte liegen am Ende unter **CSV/Storage_co/...**. Hier kann die Auswirkung der Speicher im Programm untersucht werden - beide Jahresverläufe (mit und ohne Speicher) werden vom Programm berechnet (und geplottet, zum Beispiel in den summenhistogrammen "summenhistogramm" vs. "summenhistogramm_ee_storage" vs. "summenhistogramm_all").

## Tests
Es gibt einie Unit-Tests, die grundsätzlich testen, ob gewissen Funktionen, die return-Werte liefern, die erwartet werden, zB. ob die return-Dataframes alle geforderten Spalten enthalten.
Sie können ausgeführt werden über:

```
pytest
```

Dieser Terminal-Befehl führt alle Tests auf einmal aus.

# Infolinks
Manche Packages sind nicht unbedingt bekannt, und können unter diesen Links nachgeschaut werden:

- [SMARD Daten der Bundesnetzagentur](https://www.smard.de/home)

- [Python Dokumentation](https://docs.python.org/3/)
- [Anaconda Dokumentation](https://docs.anaconda.com/)
- [Papermill](https://papermill.readthedocs.io/en/latest/)
- [Xlwings](https://www.xlwings.org/)
- [Pytest](https://docs.pytest.org/en/stable/)

 
