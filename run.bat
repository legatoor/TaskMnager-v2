@echo off
echo Activating virtual environment...
call .\env\Scripts\activate.bat
echo.

echo Starting Daphne ASGI server...
daphne -p 8000 -b 0.0.0.0 taskmanager.asgi:application

pause
