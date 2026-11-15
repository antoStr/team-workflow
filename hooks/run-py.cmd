: << 'CMDBLOCK'
@echo off
REM Runs skills/team/scripts/<script> with the first Python that really runs, on cmd and on
REM POSIX shells alike (this file is both a batch file and a shell script). A fixed `python3`
REM fails on Windows, where it is often the Microsoft Store alias that only prints a message.
REM Usage: run-py.cmd <script.py> [args...]
setlocal
set "PY="
if defined SystemRoot for %%P in (python3 python py) do if not defined PY for /f "delims=" %%F in ('"%SystemRoot%\System32\where.exe" $PATH:%%P 2^>nul') do if not defined PY if /i not "%%~dpF"=="%LOCALAPPDATA%\Microsoft\WindowsApps\" set "PY=%%F"
REM No Python: exit quietly, the app keeps working without the hook
if not defined PY exit /b 0
"%PY%" "%~dp0..\skills\team\scripts\%~1" %2 %3 %4 %5 %6 %7 %8 %9
exit /b %ERRORLEVEL%
CMDBLOCK

# POSIX shells, Git Bash on Windows included
case "$0" in
  */*|*\\*) DIR="${0%[/\\]*}" ;;
  *) DIR="." ;;
esac
SCRIPT="$1"
shift
for py in python3 python py; do
  # the Store alias exits non-zero; </dev/null keeps the hook's input for the real run
  if command -v "$py" >/dev/null 2>&1 && "$py" -c "" </dev/null >/dev/null 2>&1; then
    exec "$py" "$DIR/../skills/team/scripts/$SCRIPT" "$@"
  fi
done
exit 0
