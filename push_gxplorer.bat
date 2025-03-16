@echo off
cd /d "C:\Users\YourName\Documents\GXplorer"
git add .
git commit -m "Auto-commit GXplorer - %date% %time%"
git push -u origin master
