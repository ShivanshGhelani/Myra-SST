@echo off
REM Setup script for MyraSTT

echo Setting up MyraSTT...

REM Create virtual environment if it doesn't exist
if not exist "myra_sst" (
    echo Creating virtual environment...
    python -m venv myra_sst
)

REM Activate virtual environment
call myra_sst\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Run directory setup
echo Running directory setup...
python setup_dirs.py

REM Launch application
echo Starting application...
uvicorn api.main:app --reload

echo Done!
