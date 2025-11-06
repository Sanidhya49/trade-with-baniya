@echo off
echo Starting Streamlit App...
cd /d "%~dp0"
call myvenv\Scripts\activate.bat
streamlit run streamlit_app.py
pause

