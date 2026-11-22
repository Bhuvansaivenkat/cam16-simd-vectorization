@echo off
title CAM16 SIMD Vectorization - Live Web Deployment
echo =====================================================================
echo   CAM16 SIMD Vectorization (COA Research Project)
echo   Launching Interactive Web Application...
echo =====================================================================
cd /d "%~dp0"
set PATH=C:\msys64\ucrt64\bin;%PATH%
python -m streamlit run app.py --server.headless=false
pause
