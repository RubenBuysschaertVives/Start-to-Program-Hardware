@echo off
echo ============================================
echo Building Strudel Pattern Generator Executable
echo ============================================
echo.

REM Install PyInstaller if not already installed
echo Checking for PyInstaller...
python -m pip install --upgrade pyinstaller

echo.
echo Building executable...
python -m PyInstaller --onefile --windowed --name "StrudelPatternGenerator" --icon=NONE pattern_generator_gui.py

echo.
echo ============================================
if exist "dist\StrudelPatternGenerator.exe" (
    echo Build successful!
    echo Executable location: dist\StrudelPatternGenerator.exe
    echo.
    echo You can now run StrudelPatternGenerator.exe without Python installed
) else (
    echo Build failed! Check the output above for errors.
)
echo ============================================
pause
