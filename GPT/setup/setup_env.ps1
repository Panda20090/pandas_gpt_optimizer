# Ensure the project root directory is set
if (-not $env:PROJECT_ROOT) {
    Write-Host "PROJECT_ROOT environment variable is not set."
    exit 1
  }
  
  # Navigate to the GPT directory
  Set-Location "$env:PROJECT_ROOT\GPT" -ErrorAction Stop
  
  # Check if the virtual environment exists
  if (-not (Test-Path -Path "setup\venv")) {
    # Create a new virtual environment if it does not exist
    python -m venv setup\venv
  }
  
  # Activate the virtual environment
  if (Test-Path -Path "setup\venv\Scripts\activate.ps1") {
    . "setup\venv\Scripts\activate.ps1"
  } else {
    Write-Host "Could not find the virtual environment activation script."
    exit 1
  }
  
  # Install necessary dependencies
  pip install -r requirements.txt
  pip install openai flask
  
  # Append to the project's requirements.txt
  Get-Content requirements.txt | Add-Content "$env:PROJECT_ROOT\requirements.txt"
  
  Write-Host "Environment setup complete."
  