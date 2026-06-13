@echo off
echo Starting Expense Tracker...

:: Activate virtual environment
call venv\Scripts\activate

:: Start Backend in new window
start cmd /k "call venv\Scripts\activate && cd backend && uvicorn main:app --reload"

:: Wait 3 seconds for backend to start
timeout /t 3

:: Start Frontend in new window
start cmd /k "call venv\Scripts\activate && cd frontend && streamlit run app.py"

echo Both servers are starting...
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:8501
echo Docs:     http://localhost:8000/docs
pause