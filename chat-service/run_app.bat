@echo off
echo Activating virtual environment...
call .\chat_service_venv\Scripts\activate.bat

echo Starting Flask application...
python main.py

pause