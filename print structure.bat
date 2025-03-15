@echo off
if "%1"=="" (
    set "folder=%CD%"
) else (
    set "folder=%1"
)
(
    echo %folder%
    dir /s /b /a:d "%folder%"
    dir /s /b /a:-d "%folder%"
) | sort