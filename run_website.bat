@echo off
title Smart Waste Classification System - SRMIST
echo =====================================================================
echo  SMART WASTE CLASSIFICATION SYSTEM USING DEEP LEARNING (SRMIST)
echo  Course: 21CSP302L - Project Viva / Demonstration
echo  Students: B S Vikashsrikanth, S Ravi prakash, A Griffin George
echo  Supervisor: Dr. N Kanimozhi (Dept of Computational Intelligence)
echo =====================================================================
echo.
echo Starting Web Server on http://127.0.0.1:5000 ...
echo Opening web browser in 3 seconds...
start "" http://127.0.0.1:5000
python waste_app\server.py
pause
