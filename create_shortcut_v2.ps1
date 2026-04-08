$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut("$env:USERPROFILE\Desktop\Power BI Bot 2.0.lnk")
$sc.TargetPath = "C:\Windows\System32\cmd.exe"
$sc.Arguments = '/c "cd /d ""c:\Users\SE46958\1 - Claude - Proyecto viz\BI - BOT\powerbi-bot"" && streamlit run app_v2.py --server.port 8520"'
$sc.WorkingDirectory = "c:\Users\SE46958\1 - Claude - Proyecto viz\BI - BOT\powerbi-bot"
$sc.Description = "Power BI Bot 2.0 - Buscador de Reportes del Tenant"
$sc.IconLocation = "$env:USERPROFILE\Downloads\Bi Bot.ico"
$sc.Save()
Write-Host "Acceso directo creado en el Escritorio"
