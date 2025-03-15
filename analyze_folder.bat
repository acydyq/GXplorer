@echo off
set "output_file=folder_structure.txt"

:: Check if a folder is provided as an argument; if not, default to the current directory
if "%1"=="" (
    set "folder=%CD%"
) else (
    set "folder=%1"
)

:: Verify if the folder exists
if not exist "%folder%" (
    echo Error: Folder "%folder%" does not exist.
    exit /b 1
)

:: Inform the user that the folder structure is being generated
echo Generating folder structure for "%folder%"...

:: Generate the folder structure and save it to the output file
(
    echo %folder%
    dir /s /b /a:d "%folder%"
    dir /s /b /a:-d "%folder%"
) | sort > "%output_file%"

:: Check if the operation was successful
if %errorlevel%==0 (
    echo Folder structure saved to "%output_file%"
) else (
    echo An error occurred while generating the folder structure.
)