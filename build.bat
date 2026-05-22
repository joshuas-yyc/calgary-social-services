@echo off
REM Build the standalone Calgary Social Services app (Windows)
REM Usage: double-click or run in a terminal: build.bat

echo =^> Installing build tools...
uv add --dev pyinstaller pyinstaller-hooks-contrib

echo =^> Building...
uv run pyinstaller Calgary-Services.spec --clean

echo.
echo =^> Build complete: dist\Calgary-Services\
echo.
echo To distribute:
echo   cd dist
echo   tar -a -c -f Calgary-Services-Windows.zip Calgary-Services\
echo.
echo Recipients: unzip and double-click Calgary-Services.exe
