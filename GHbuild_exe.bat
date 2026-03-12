@echo off
REM GHbuild_exe.bat - Build wrapper for GithubTool (GHT_env venv, verbose pip, logging)
REM Usage:
REM   GHbuild_exe.bat [version] [--clean] [--stamp]
REM Example:
REM   GHbuild_exe.bat 1.0.0 --clean --stamp

setlocal enabledelayedexpansion

REM -------------------------
REM Config
REM -------------------------
set "SPEC_FILE=GithubTool.spec"
set "GHT_VERSION_FILE=ght.version"
set "DEFAULT_VERSION=0.0.0"
set "DIST_ROOT=%~dp0dist\GithubTool_build"
set "VENV_DIR=%~dp0GHT_env"
set "BUILD_LOG=%~dp0build.log"
set "PIP_UPGRADE_LOG=%~dp0pip_upgrade.log"
set "PIP_INSTALL_LOG=%~dp0pip_install.log"
set "ICON_FILE=%~dp0app.ico"

REM -------------------------
REM Parse args
REM -------------------------
set "BUILD_VERSION=%~1"
if "%BUILD_VERSION%"=="" set "BUILD_VERSION=%DEFAULT_VERSION%"

set "CLEAN_FLAG=0"
set "STAMP_FLAG=0"
:parse_args
if "%~2"=="" goto args_done
if /I "%~2"=="--clean" set "CLEAN_FLAG=1"
if /I "%~2"=="--stamp" set "STAMP_FLAG=1"
shift
goto parse_args
:args_done

echo ===== Build started at %date% %time% > "%BUILD_LOG%"
echo Version: %BUILD_VERSION% >> "%BUILD_LOG%"
echo Clean: %CLEAN_FLAG%  Stamp: %STAMP_FLAG% >> "%BUILD_LOG%"
echo. >> "%BUILD_LOG%"

REM -------------------------
REM Sanity: spec exists
REM -------------------------
if not exist "%~dp0%SPEC_FILE%" (
    echo ERROR: Spec file "%SPEC_FILE%" not found. | tee "%BUILD_LOG%"
    exit /b 1
)

REM -------------------------
REM Check for icon file
REM -------------------------
if exist "%ICON_FILE%" (
    echo Icon file found: %ICON_FILE% >> "%BUILD_LOG%"
) else (
    echo WARNING: Icon file not found at %ICON_FILE% >> "%BUILD_LOG%"
    echo Executable will use default Python icon. >> "%BUILD_LOG%"
)

REM -------------------------
REM Optional stamping
REM -------------------------
if "%STAMP_FLAG%"=="1" (
    echo Stamping %GHT_VERSION_FILE% with version %BUILD_VERSION% ... >> "%BUILD_LOG%"
    set "GIT_COMMIT=unknown"
    set "GIT_BRANCH=unknown"
    for /f "delims=" %%H in ('git rev-parse --short HEAD 2^>nul') do set "GIT_COMMIT=%%H"
    for /f "delims=" %%B in ('git rev-parse --abbrev-ref HEAD 2^>nul') do set "GIT_BRANCH=%%B"

    > "%~dp0%GHT_VERSION_FILE%" echo version=%BUILD_VERSION%
    >> "%~dp0%GHT_VERSION_FILE%" echo build_time=%date% %time%
    >> "%~dp0%GHT_VERSION_FILE%" echo git_commit=%GIT_COMMIT%
    >> "%~dp0%GHT_VERSION_FILE%" echo git_branch=%GIT_BRANCH%

    if errorlevel 1 (
        echo ERROR: Failed to write %GHT_VERSION_FILE% >> "%BUILD_LOG%"
        exit /b 1
    )
    echo Wrote %GHT_VERSION_FILE% >> "%BUILD_LOG%"
) else (
    if exist "%~dp0%GHT_VERSION_FILE%" (
        echo Found existing %GHT_VERSION_FILE% >> "%BUILD_LOG%"
    ) else (
        echo No %GHT_VERSION_FILE% found and --stamp not provided >> "%BUILD_LOG%"
    )
)

REM -------------------------
REM Optional clean
REM -------------------------
if "%CLEAN_FLAG%"=="1" (
    echo Cleaning previous build artifacts... >> "%BUILD_LOG%"
    if exist "%~dp0build" rd /s /q "%~dp0build"
    if exist "%~dp0dist" rd /s /q "%~dp0dist"
    if exist "%~dp0__pycache__" rd /s /q "%~dp0__pycache__"
    if exist "%VENV_DIR%" rd /s /q "%VENV_DIR%"
    echo Clean complete. >> "%BUILD_LOG%"
)

REM -------------------------
REM Create virtualenv if missing
REM -------------------------
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Creating virtual environment in "%VENV_DIR%" ... >> "%BUILD_LOG%"
    python -m venv "%VENV_DIR%" >> "%BUILD_LOG%" 2>&1
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment. See %BUILD_LOG% >> "%BUILD_LOG%"
        exit /b 2
    )
) else (
    echo Virtual environment already exists at "%VENV_DIR%" >> "%BUILD_LOG%"
)

REM -------------------------
REM Activate venv
REM -------------------------
echo Activating virtual environment... >> "%BUILD_LOG%"
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment. >> "%BUILD_LOG%"
    exit /b 3
)

REM -------------------------
REM Upgrade pip (verbose, no cache, log)
REM -------------------------
echo Upgrading pip, setuptools, wheel... >> "%BUILD_LOG%"
"%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel --no-cache-dir --default-timeout=120 -v --log "%PIP_UPGRADE_LOG%" >> "%BUILD_LOG%" 2>&1
if errorlevel 1 (
    echo WARNING: pip upgrade failed; see %PIP_UPGRADE_LOG% and %BUILD_LOG% >> "%BUILD_LOG%"
)

REM -------------------------
REM Install runtime/build deps (verbose, no cache, log)
REM -------------------------
echo Installing requests and pyinstaller (this may take a while)... >> "%BUILD_LOG%"
"%VENV_DIR%\Scripts\python.exe" -m pip install requests pyinstaller --no-cache-dir --default-timeout=300 -v --log "%PIP_INSTALL_LOG%" >> "%BUILD_LOG%" 2>&1
if errorlevel 1 (
    echo ERROR: pip install failed. Check %PIP_INSTALL_LOG% and %BUILD_LOG% >> "%BUILD_LOG%"
    type "%PIP_INSTALL_LOG%" >> "%BUILD_LOG%" 2>&1
    exit /b 4
)

REM -------------------------
REM Run PyInstaller using venv python
REM -------------------------
echo Running PyInstaller with spec: %SPEC_FILE% ... >> "%BUILD_LOG%"
"%VENV_DIR%\Scripts\python.exe" -m PyInstaller --clean --noconfirm "%SPEC_FILE%" >> "%BUILD_LOG%" 2>&1
if errorlevel 1 (
    echo ERROR: PyInstaller build failed. See %BUILD_LOG% >> "%BUILD_LOG%"
    exit /b 5
)

REM -------------------------
REM Collect artifacts
REM -------------------------
set "OUT_DIR=%DIST_ROOT%\%BUILD_VERSION%"
echo Preparing output directory: %OUT_DIR% >> "%BUILD_LOG%"
if exist "%OUT_DIR%" rd /s /q "%OUT_DIR%"
mkdir "%OUT_DIR%"

if exist "%~dp0dist\GithubTool" (
    xcopy /e /i /y "%~dp0dist\GithubTool" "%OUT_DIR%" >> "%BUILD_LOG%" 2>&1
) else if exist "%~dp0dist\GitCloneTool" (
    xcopy /e /i /y "%~dp0dist\GitCloneTool" "%OUT_DIR%" >> "%BUILD_LOG%" 2>&1
) else (
    xcopy /e /i /y "%~dp0dist" "%OUT_DIR%" >> "%BUILD_LOG%" 2>&1
)

if exist "%~dp0%GHT_VERSION_FILE%" (
    copy /y "%~dp0%GHT_VERSION_FILE%" "%OUT_DIR%\" >> "%BUILD_LOG%" 2>&1
) else (
    echo Note: no %GHT_VERSION_FILE% to copy into output. >> "%BUILD_LOG%"
)

if exist "%ICON_FILE%" (
    copy /y "%ICON_FILE%" "%OUT_DIR%\" >> "%BUILD_LOG%" 2>&1
    echo Copied icon file to output directory. >> "%BUILD_LOG%"
)

copy /y "%~dp0%SPEC_FILE%" "%OUT_DIR%\" >> "%BUILD_LOG%" 2>&1

echo Build artifacts copied to: %OUT_DIR% >> "%BUILD_LOG%"
echo Build completed successfully at %date% %time% >> "%BUILD_LOG%"

REM -------------------------
REM Deactivate venv (best-effort)
REM -------------------------
if exist "%VENV_DIR%\Scripts\deactivate.bat" (
    call "%VENV_DIR%\Scripts\deactivate.bat" >nul 2>&1
)

endlocal
exit /b 0