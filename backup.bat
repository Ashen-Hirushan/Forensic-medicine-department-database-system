@echo off
setlocal
set DB_NAME=forensic_dept_db
set DB_USER=root
set DB_PASS=
set BACKUP_FILE=forensic_dept_db_backup.sql

echo ════════════════════════════════════════════════════
echo FORENSIC MEDICINE DB - BACKUP ^& RECOVERY TOOL
echo ════════════════════════════════════════════════════
echo.
echo 1. Backup Local Database
echo 2. Restore Local Database
echo 3. Exit
echo.
set /p choice="Select an option (1-3): "

if "%choice%"=="1" (
    echo.
    echo Running database backup...
    if "%DB_PASS%"=="" (
        mysqldump -u %DB_USER% %DB_NAME% > %BACKUP_FILE%
    ) else (
        mysqldump -u %DB_USER% -p%DB_PASS% %DB_NAME% > %BACKUP_FILE%
    )
    if %ERRORLEVEL% equ 0 (
        echo.
        echo [SUCCESS] Backup saved to %BACKUP_FILE%
    ) else (
        echo.
        echo [ERROR] Backup failed.
    )
    pause
    goto end
)

if "%choice%"=="2" (
    echo.
    echo Running database restore...
    if not exist %BACKUP_FILE% (
        echo [ERROR] Backup file %BACKUP_FILE% not found!
        pause
        goto end
    )
    if "%DB_PASS%"=="" (
        mysql -u %DB_USER% %DB_NAME% < %BACKUP_FILE%
    ) else (
        mysql -u %DB_USER% -p%DB_PASS% %DB_NAME% < %BACKUP_FILE%
    )
    if %ERRORLEVEL% equ 0 (
        echo.
        echo [SUCCESS] Database successfully restored from %BACKUP_FILE%
    ) else (
        echo.
        echo [ERROR] Restore failed.
    )
    pause
    goto end
)

:end
endlocal
