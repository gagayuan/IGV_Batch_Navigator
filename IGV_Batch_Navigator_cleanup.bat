@echo off
title IGV Batch Navigator - Registry Cleanup

echo.
echo ================================================
echo   IGV Batch Navigator - Registry Cleanup Tool
echo ================================================
echo.
echo This will delete the following registry key:
echo   HKEY_CURRENT_USER\Software\IGV\BatchNavigator
echo.
echo Settings stored: Python path, column names, batch sizes, genome list, etc.
echo.
echo Press any key to delete. Close this window to cancel.
pause >nul

echo.
echo Deleting...
reg delete "HKEY_CURRENT_USER\Software\IGV" /f >nul 2>&1

if %errorlevel% equ 0 (
    echo [OK] IGV Batch Navigator Registry cleanup completed.
) else (
    echo Registry key not found or already cleaned.
)

echo.
pause