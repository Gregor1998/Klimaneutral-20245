@echo off
echo Checking for Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python from https://www.python.org/downloads/
    pause
    exit /b
)

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing required packages...
pip install pandas numpy seaborn xlwings papermill plotly scikit-learn openpyxl joblib jupyter kaleido

echo Verifying xlwings installation...
python -c "import xlwings; print('xlwings version:', xlwings.__version__)"

echo Installing xlwings add-in for Excel...
xlwings addin install

echo Setup complete!
pause
