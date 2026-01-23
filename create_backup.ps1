# Script para criar backup compactado do BigodeBot

$sourcePath = "d:\dayz xbox\BigodeBot"
$destinationPath = "C:\Users\Wellyton\Desktop\BigodeTexas_Bot_v2.1_COMPLETO.zip"
$tempPath = "C:\Users\Wellyton\AppData\Local\Temp\BigodeBot_Backup"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CRIANDO BACKUP DO BIGODEBOT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Criar pasta temporária
Write-Host "[1/4] Preparando arquivos..." -ForegroundColor Yellow
if (Test-Path $tempPath) {
    Remove-Item $tempPath -Recurse -Force
}
New-Item -ItemType Directory -Path $tempPath -Force | Out-Null

# Copiar arquivos (excluindo .git, __pycache__, etc)
Write-Host "[2/4] Copiando projeto..." -ForegroundColor Yellow
$excludeDirs = @('.git', '__pycache__', 'node_modules', '.vscode')
$excludeFiles = @('*.pyc', '*.log', '*.db', '.env')

Get-ChildItem -Path $sourcePath -Recurse | Where-Object {
    $item = $_
    $exclude = $false
    
    # Verificar se está em pasta excluída
    foreach ($dir in $excludeDirs) {
        if ($item.FullName -like "*\$dir\*") {
            $exclude = $true
            break
        }
    }
    
    # Verificar se é arquivo excluído
    if (-not $exclude -and $item -is [System.IO.FileInfo]) {
        foreach ($pattern in $excludeFiles) {
            if ($item.Name -like $pattern) {
                $exclude = $true
                break
            }
        }
    }
    
    -not $exclude
} | ForEach-Object {
    $targetPath = $_.FullName.Replace($sourcePath, $tempPath)
    $targetDir = Split-Path $targetPath -Parent
    
    if (-not (Test-Path $targetDir)) {
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    }
    
    if ($_ -is [System.IO.FileInfo]) {
        Copy-Item $_.FullName -Destination $targetPath -Force
    }
}

# Criar arquivo README no backup
Write-Host "[3/4] Criando documentacao..." -ForegroundColor Yellow
$readmeContent = @"
# BIGODEBOT v2.1 - BACKUP COMPLETO

Data do Backup: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## CONTEÚDO

Este arquivo contém o backup completo do projeto BigodeBot v2.1 com:

- Sistema de tiles do mapa (5.461 tiles)
- Interface modernizada
- Avatar personalizado
- Launcher com ícone customizado
- Documentação completa
- Todos os scripts e configurações

## COMO RESTAURAR

1. Extraia este arquivo ZIP em uma pasta de sua escolha
2. Abra o terminal na pasta extraída
3. Execute: launcher.bat

## REQUISITOS

- Python 3.8 ou superior
- Bibliotecas: discord.py, requests, flask, pillow
- Conta Discord com bot configurado

## DOCUMENTAÇÃO

Leia os arquivos .md na raiz do projeto para mais informações:
- PROJETO_FINALIZADO.md - Resumo completo
- TILES_IMPLEMENTATION_COMPLETE.md - Sistema de tiles
- INTERFACE_MODERNIZATION.md - Interface
- COMO_ATUALIZAR_AVATAR.md - Avatar do bot

## SUPORTE

Para mais informações, consulte a documentação incluída.

Versão: 2.1 Production
Status: Completo e Testado
"@

Set-Content -Path "$tempPath\README_BACKUP.txt" -Value $readmeContent -Encoding UTF8

# Compactar
Write-Host "[4/4] Compactando arquivo..." -ForegroundColor Yellow
if (Test-Path $destinationPath) {
    Remove-Item $destinationPath -Force
}

Compress-Archive -Path "$tempPath\*" -DestinationPath $destinationPath -CompressionLevel Optimal

# Limpar temporários
Remove-Item $tempPath -Recurse -Force

# Resultado
$fileSize = (Get-Item $destinationPath).Length / 1MB
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  BACKUP CRIADO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Arquivo: $destinationPath" -ForegroundColor Cyan
Write-Host "Tamanho: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "O arquivo foi salvo no seu Desktop!" -ForegroundColor Yellow
Write-Host ""
