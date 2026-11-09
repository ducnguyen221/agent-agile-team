@echo off
rem Shim gh (thu nghiem SPR-16b) cho PowerShell/cmd: chi chan khi AGENT_AGILE_SHIM=1; khong thi chay gh.exe that ngay.
if not defined AGENT_AGILE_SHIM goto passthru
if "%AGENT_AGILE_SHIM%"=="0" goto passthru
set "AGENT_SHIM_DIR=%~dp0"
if "%AGENT_SHIM_DIR:~-1%"=="\" set "AGENT_SHIM_DIR=%AGENT_SHIM_DIR:~0,-1%"
python "%~dp0..\scripts\git_shim.py" gh %*
exit /b %ERRORLEVEL%
:passthru
for /f "delims=" %%G in ('where gh.exe 2^>nul') do "%%G" %* & exit /b
echo git-shim: khong tim thay gh.exe that tren PATH 1>&2
exit /b 127
