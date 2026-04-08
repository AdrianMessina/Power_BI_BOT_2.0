@echo off
REM Script de inicio rápido para Power BI Bot
REM YPF - Equipo RTIC

echo ========================================
echo Power BI Bot - Asistente Conversacional
echo ========================================
echo.

REM Verificar si existe .env
if not exist .env (
    echo [ERROR] Archivo .env no encontrado
    echo.
    echo Por favor, copia .env.example a .env y configura tu ANTHROPIC_API_KEY:
    echo   copy .env.example .env
    echo   notepad .env
    echo.
    pause
    exit /b 1
)

REM Configurar proxy
set HTTPS_PROXY=http://proxy-azure
set HTTP_PROXY=http://proxy-azure

echo [INFO] Proxy corporativo configurado
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado en PATH
    pause
    exit /b 1
)

echo [INFO] Python encontrado
echo.

REM Verificar dependencias
echo [INFO] Verificando dependencias...
python -c "import anthropic, mcp, streamlit" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Algunas dependencias no están instaladas
    echo Instalando dependencias...
    pip install -r requirements.txt
)

echo [OK] Dependencias verificadas
echo.

REM Verificar Power BI Desktop
echo [INFO] Verificando conexión a Power BI Desktop...
python -c "from core.xmla_connector import quick_connect; conn = quick_connect(); exit(0 if conn else 1)" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] No se detectó Power BI Desktop abierto
    echo.
    echo Para usar la aplicación:
    echo   1. Abre un archivo .pbix en Power BI Desktop
    echo   2. Ejecuta este script nuevamente
    echo.
    echo ¿Deseas continuar de todas formas? (S/N)
    set /p continue=
    if /i not "%continue%"=="S" exit /b 0
) else (
    echo [OK] Power BI Desktop detectado
)

echo.
echo ========================================
echo   Iniciando Power BI Bot...
echo ========================================
echo.
echo La aplicación se abrirá en tu navegador
echo URL: http://localhost:8501
echo.
echo Presiona Ctrl+C para detener la aplicación
echo.

REM Iniciar Streamlit
streamlit run app.py

pause
