@echo off
setlocal enabledelayedexpansion

:: Find the most recent .html file
for /f "delims=" %%F in ('dir /b /od /a:-d *.html 2^>nul') do set "latest_html=%%F"

:: Check if a file was found
if not defined latest_html (
    echo No HTML files found in the current directory.
    timeout /t 5
    exit /b 1
)

:: Run the Python script with the latest HTML file
molprobity_to_coot.py --column "Rotamer" --filter_text "OUTLIER" "!latest_html!"

:: Delay for 5 seconds before closing
timeout /t 5