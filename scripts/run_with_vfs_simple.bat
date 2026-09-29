@echo off

cd /d "%~dp0.."
python src\main.py --vfs ./vfs/simple.xml
pause