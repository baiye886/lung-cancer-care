@echo off
chcp 65001 >nul
echo ==================================================
echo   肺康守护 (Recovery Atlas) 本地启动服务
echo   访问网址: http://127.0.0.1:8000
echo ==================================================
cd /d "%~dp0"
python server.py
pause
