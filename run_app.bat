@echo off
title Menjalankan Sistem Manajemen Gudang Enterprise
echo =======================================================
echo    MENJALANKAN APLIKASI SISTEM GUDANG ENTERPRISE
echo =======================================================
echo Memulai program...
echo.

:: 1. Coba menggunakan path absolut Python Anda
"C:\Users\farra\AppData\Local\Python\pythoncore-3.14-64\python.exe" main.py
if %errorlevel% equ 0 goto end

:: 2. Fallback ke launcher bawaan Windows 'py' jika path di atas berubah
echo Mencoba metode cadangan 1 (py)...
py main.py
if %errorlevel% equ 0 goto end

:: 3. Fallback ke perintah standard 'python'
echo Mencoba metode cadangan 2 (python)...
python main.py
if %errorlevel% equ 0 goto end

echo.
echo =======================================================
echo ERROR: Gagal menjalankan aplikasi.
echo Pastikan Python dan CustomTkinter sudah terinstal.
echo =======================================================
pause

:end
