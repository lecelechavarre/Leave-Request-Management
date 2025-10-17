@echo off
echo Starting Leave Request Manager...
if not exist .venv (
    python -m venv .venv
)
call .venv\Scripts\activate
pip install -r requirements.txt
python main.py
pause
