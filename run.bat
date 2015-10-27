@echo off
set PATH=Andor SDK3;%PATH%;
set PYTHONPATH=%PYTHONPATH%;"Andor SDK3";
set PY=C:\Python27\python.exe
%PY% camera.py