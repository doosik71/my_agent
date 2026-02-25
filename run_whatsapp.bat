@echo off
rem Run the Flask server for WhatsApp integration
echo Starting my_agent WhatsApp Server...

rem Set Flask environment variables
set FLASK_APP=src/whatsapp.py
set FLASK_ENV=development

rem Run the Flask application
flask run --host=0.0.0.0 --port=5000

pause