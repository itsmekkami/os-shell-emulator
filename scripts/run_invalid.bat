@echo off

cd /d "%~dp0.."
python src\main.py --script ./scripts/nonexistent.txt
pause