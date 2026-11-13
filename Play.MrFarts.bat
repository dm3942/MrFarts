@echo off
cd /d "%~dp0"
call :serve
start msedge --new-window "http://127.0.0.1:8123/index.html"
exit /b

:serve
rem Reuse the server if one is already listening on 8123, otherwise start it minimized.
netstat -ano | findstr /r /c:"127.0.0.1:8123 .*LISTENING" >nul && exit /b
start "Mr Farts server" /min python -m http.server 8123 --bind 127.0.0.1
ping -n 2 127.0.0.1 >nul
exit /b
