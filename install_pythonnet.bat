@echo off
REM Instalar pythonnet para habilitar TOM
REM YPF - Equipo RTIC

echo ========================================
echo Instalando pythonnet para TOM
echo ========================================
echo.

REM Configurar proxy
set HTTPS_PROXY=http://proxy-azure
set HTTP_PROXY=http://proxy-azure

echo [INFO] Proxy configurado
echo.

echo [INFO] Instalando pythonnet...
pip install pythonnet

if errorlevel 1 (
    echo.
    echo [ERROR] Fallo la instalacion
    pause
    exit /b 1
)

echo.
echo ========================================
echo pythonnet instalado correctamente
echo ========================================
echo.
echo Ahora puedes usar el TOM para:
echo - Leer tablas del modelo
echo - Listar medidas DAX
echo - Consultar relaciones
echo - Modificar el modelo
echo.
echo Reinicia la aplicacion para aplicar los cambios
echo.
pause
