@echo off
echo ============================================================
echo RMBG-2.0 Token Setup
echo ============================================================
echo.
echo First, get your Hugging Face token:
echo 1. Visit: https://huggingface.co/briaai/RMBG-2.0
echo 2. Click "Agree and access repository"
echo 3. Go to: https://huggingface.co/settings/tokens
echo 4. Create a new token and copy it
echo.
echo ============================================================
echo.

set /p HF_TOKEN="Paste your Hugging Face token here: "

echo.
echo Token set! Now you can use RMBG-2.0.
echo.
echo Example commands:
echo   python main.py images -w --use-ai --ai-model rmbg
echo   python main.py images -b white --use-ai --ai-model rmbg
echo.
echo ============================================================
echo.

REM Run a test command if user wants
set /p RUN_TEST="Do you want to test it now? (y/n): "
if /i "%RUN_TEST%"=="y" (
    echo.
    echo Running test...
    python main.py images -w --use-ai --ai-model rmbg
)

pause
