@echo off
set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"

echo ============================================
echo         CONFIGURATION VIRTUALENV
echo ============================================
echo.
echo Entrez le chemin absolu de votre virtualenv
echo Exemple : C:\Users\vous\projets\venv
echo.
set /p VENV_PATH="Chemin du virtualenv : "

:: Verifie que le chemin existe
if not exist "%VENV_PATH%\Scripts\activate.bat" (
    echo.
    echo [ERREUR] Chemin invalide ou virtualenv introuvable :
    echo          %VENV_PATH%\Scripts\activate.bat
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Virtualenv trouve : %VENV_PATH%
echo Lancement des serveurs...
echo.

:: Fenetre 1 — Summarization API (avec venv)
start "Summarization API" cmd /k "call "%VENV_PATH%\Scripts\activate.bat" && cd /d "%ROOT%\summarization-api\api" && python maincolab.py"

:: Fenetre 2 — Django Backend (avec venv)
start "Django Backend" cmd /k "call "%VENV_PATH%\Scripts\activate.bat" && cd /d "%ROOT%\backend" && python manage.py runserver"

:: Fenetre 3 — Frontend (sans venv)
start "Frontend Dev" cmd /k "cd /d "%ROOT%\front-end" && npm run dev"
