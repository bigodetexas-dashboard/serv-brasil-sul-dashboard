# 🌐 Configuração do Dashboard - BigodeTexas

Este documento registra a configuração estável alcançada para o site e o projeto, servindo como guia para os próximos assistentes.

## 📁 Estrutura Unificada

O Dashboard moderno agora reside na pasta `new_dashboard/`, mas depende de recursos compartilhados com o Bot na raiz.

### Sincronização de Recursos

Para o servidor Flask funcionar corretamente e encontrar os arquivos estáticos (CSS/JS) e templates (HTML), os diretórios `static` e `templates` da raiz do projeto devem ser espelhados dentro de `new_dashboard/`.

**Comando de Sincronização (PowerShell):**

```powershell
Copy-Item -Path templates -Destination new_dashboard\templates -Recurse -Force
Copy-Item -Path static -Destination new_dashboard\static -Recurse -Force
```

## 🗄️ Base de Dados (SQLite Unificado)

* **Arquivo:** `bigode_unified.db` (Localizado na raiz).
* **Acesso Dashboard:** O `app.py` está configurado para buscar o banco um nível acima (`..`).
* **Single Source of Truth:** O Bot e o Site agora usam exclusivamente este arquivo, eliminando todos os JSONs e o PostgreSQL antigo.

## 🚀 Como Rodar Localmente

1. **Dashboard:**
    * Navegue até `new_dashboard/`.
    * Execute: `python app.py`.
    * Acesso em: `http://localhost:5000`.
2. **Bot:**
    * Navegue até a raiz.
    * Execute: `python bot_main.py`.

## 🛠️ Endpoints de API Implementados

* `/api/user/stats`: Kills, Deaths, KD, Best Streak, Playtime.
* `/api/clan/my`: Info do clã, Membros e **Guerras Ativas**.
* `/api/leaderboard**: Rankings reais vindos do SQLite.
* `/api/heatmap`: Coordenadas de kills PvP reais.

## ⚠️ Observações de Deploy

Ao subir para o Render, o `Root Directory` deve ser `new_dashboard`, mas como o banco de dados é local (SQLite), ele deve ser comitado no Git ou persistido em um volume (Disk) se for necessário manter os dados após deploys.

---
*Configuração Validada em: 11/01/2026*
