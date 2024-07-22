@echo off

REM Ensure the project root directory is set
IF "%PROJECT_ROOT%"=="" (
  echo PROJECT_ROOT environment variable is not set.
  exit /b 1
)

REM Navigate to the GPT directory
IF NOT EXIST "%PROJECT_ROOT%\GPT" (
  echo GPT directory does not exist in the specified PROJECT_ROOT.
  exit /b 1
)

cd /d "%PROJECT_ROOT%\GPT" || exit /b 1

REM Check if the virtual environment exists
IF NOT EXIST "setup\venv" (
  REM Create a new virtual environment if it does not exist
  python -m venv setup\venv
)

REM Activate the virtual environment
IF EXIST "setup\venv\Scripts\activate.bat" (
  call "setup\venv\Scripts\activate.bat"
) ELSE (
  echo Could not find the virtual environment activation script.
  exit /b 1
)

REM Install necessary dependencies
pip install -r requirements.txt
pip install openai flask

REM Append to the project's requirements.txt
IF EXIST "%PROJECT_ROOT%\requirements.txt" (
  type requirements.txt >> "%PROJECT_ROOT%\requirements.txt"
) ELSE (
  copy requirements.txt "%PROJECT_ROOT%\requirements.txt"
)

echo Environment setup complete.
