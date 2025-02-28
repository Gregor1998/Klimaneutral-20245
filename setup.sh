#!/bin/bash
echo "Checking for Python installation..."
if ! command -v python3 &> /dev/null
then
    echo "Python is not installed. Please install Python 3 from https://www.python.org/downloads/"
    exit 1
fi

echo "Upgrading pip..."
python3 -m pip install --upgrade pip

echo "Installing required packages..."
pip install pandas numpy seaborn xlwings papermill plotly scikit-learn openpyxl joblib jupyter kaleido

echo "Verifying xlwings installation..."
python3 -c "import xlwings; print('xlwings version:', xlwings.__version__)"

echo "Installing xlwings add-in for Excel..."
xlwings addin install

echo "Setup complete!"
