# Script para iniciar o dashboard e abrir no navegador
Write-Host "Iniciando BigodeTexas Dashboard..." -ForegroundColor Green

# Navegar para o diretório
Set-Location "new_dashboard"

# Iniciar o servidor em background
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python app.py" -WindowStyle Normal

# Aguardar o servidor iniciar
Write-Host "Aguardando servidor iniciar..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Abrir navegador
Write-Host "Abrindo navegador..." -ForegroundColor Green
Start-Process "http://localhost:5001"

Write-Host "`nDashboard iniciado com sucesso!" -ForegroundColor Green
Write-Host "URL: http://localhost:5001" -ForegroundColor Cyan
Write-Host "`nPara parar o servidor, feche a janela do PowerShell que foi aberta." -ForegroundColor Yellow