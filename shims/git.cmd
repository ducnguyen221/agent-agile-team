@echo off
rem Shim git (thu nghiem SPR-16b) cho PowerShell/cmd: kiem argv that roi moi chay git that.
set "AGENT_SHIM_DIR=%~dp0"
if "%AGENT_SHIM_DIR:~-1%"=="\" set "AGENT_SHIM_DIR=%AGENT_SHIM_DIR:~0,-1%"
python "%~dp0..\scripts\git_shim.py" git %*
exit /b %ERRORLEVEL%
