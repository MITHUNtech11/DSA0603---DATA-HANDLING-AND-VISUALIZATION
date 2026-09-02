@echo off
title Social Media Misinformation React Dashboard - DSA0603 Capstone
echo =========================================================================
echo  Launching React Dashboard for Misinformation Spread Visualization...
echo =========================================================================
cd /d "%~dp0frontend"
npm run dev -- --open
pause
