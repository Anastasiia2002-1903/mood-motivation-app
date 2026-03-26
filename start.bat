@echo off
chcp 65001 >nul
title DAFEU - Digitaler Assistent

echo ============================================
echo   DAFEU - Digitaler Assistent
echo   fuer emotionale Unterstuetzung
echo ============================================
echo.

:: Zum Skript-Verzeichnis wechseln
cd /d "%~dp0"

:: Pruefen ob Python installiert ist
python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python ist nicht installiert!
    echo.
    echo Bitte installiere Python von https://python.org
    echo WICHTIG: Haken bei "Add Python to PATH" setzen!
    echo.
    pause
    exit /b 1
)

:: Virtual Environment erstellen (nur beim ersten Mal)
if not exist "venv" (
    echo Erstelle virtuelle Umgebung (einmalig)...
    python -m venv venv
    echo.
)

:: Virtual Environment aktivieren
call venv\Scripts\activate.bat

:: Abhaengigkeiten installieren (nur beim ersten Mal)
if not exist "venv\.deps_installed" (
    echo Installiere Abhaengigkeiten (einmalig)...
    pip install -r requirements.txt --quiet
    echo. > "venv\.deps_installed"
    echo.
)

echo App wird gestartet...
echo.
echo ============================================
echo   Oeffne im Browser:
echo   http://127.0.0.1:5000
echo ============================================
echo.
echo (Dieses Fenster offen lassen!)
echo (Zum Beenden: STRG+C druecken)
echo.

:: Browser automatisch oeffnen
start http://127.0.0.1:5000

:: App starten
python main.py
