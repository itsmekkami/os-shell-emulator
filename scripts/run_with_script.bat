@echo off

cd /d "%~dp0.."
python src\main.py --vfs ./vfs/deep.xml --script ./scripts/startup.txt
pause