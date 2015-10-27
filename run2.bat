@echo off
set PATH=C:\Program Files\Andor SOLIS;%PATH%
set PYTHONPATH=%PYTHONPATH%;C:\Users\Public\Documents;"C:\Users\Public\Documents\Andor SDK3"
set PY=C:\Python27\python.exe
%PY% dummyCam.py