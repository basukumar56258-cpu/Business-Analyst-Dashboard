@echo off
echo ==========================================
echo Business Analytics Dashboard
echo ==========================================
echo.
echo Installing required packages...
python -m pip install -r requirements.txt
echo.
echo Starting Streamlit...
python -m streamlit run app.py
pause
