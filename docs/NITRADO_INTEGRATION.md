# 🌐 Integração Nitrado - BigodeTexas

## Visão Geral

O sistema BigodeBot se integra completamente com servidores Nitrado DayZ para:
- 📥 **Download automático de logs** via FTP
- 📊 **Parsing de eventos** (kills, deaths, logins, construções)
- 🔄 **Sincronização em tempo real** com banco de dados
- 📡 **WebSocket para dashboard** ao vivo
- 🛡️ **Anti-cheat e detecção de alts**

---

## 🔧 Configuração Inicial

### Passo 1: Obter Credenciais FTP Nitrado

1. Acesse [https://server.nitrado.net](https://server.nitrado.net)
2. Selecione seu servidor DayZ
3. Vá em **Configurações → FTP**
4. Copie:
   - **Host**: `brspXXX.gamedata.io`
   - **Porta**: `21`
   - **Usuário**: `niXXXXXXX_X`
   - **Senha**: (gerada pelo Nitrado)

### Passo 2: Configurar .env

Edite o arquivo `.env` na raiz do BigodeBot:

```env
# ===== FTP NITRADO =====
FTP_HOST=brsp012.gamedata.io
FTP_PORT=21
FTP_USER=ni3622181_1
FTP_PASS=sua_senha_aqui
# Caminho do log ADM no servidor (deixe vazio para auto-detect)
FTP_LOG_PATH=
```

### Passo 3: Encontrar Caminho do Log

Execute o script de diagnóstico:

```bash
cd "d:\dayz xbox\BigodeBot"
python scripts/nitrado_diagnostics.py
```

**Saída Esperada**:
```
============================================================
           DIAGNÓSTICO NITRADO FTP
============================================================

1. Verificando Credenciais
✓ Host: brsp012.gamedata.io:21
✓ Usuário: ni3622181_1
✓ Senha: ********

2. Testando Conexão FTP
→ Conectando a brsp012.gamedata.io:21...
✓ Conexão estabelecida
→ Autenticando como ni3622181_1...
✓ Autenticação bem-sucedida

3. Explorando Estrutura de Diretórios
→ Mapeando estrutura do servidor (max 3 níveis)...

📁 profile/
  📄 DayZServer_2026_02_07.ADM [LOG ADM]
  📄 DayZServer_2026_02_06.ADM [LOG ADM]

📁 dayzxb/
  📁 profile/
    📄 DayZServer_2026_02_07.ADM [LOG ADM]

4. Procurando Arquivos de Log
→ Buscando arquivos .ADM, .RPT e .LOG...

✓ Encontrados 3 arquivo(s) de log:

  [ADM] /profile/DayZServer_2026_02_07.ADM
  [ADM] /profile/DayZServer_2026_02_06.ADM
  [ADM] /dayzxb/profile/DayZServer_2026_02_07.ADM

6. Recomendações
✓ Caminho recomendado (ADM): /profile/DayZServer_2026_02_07.ADM

Para usar este caminho, adicione ao .env:

  FTP_LOG_PATH=/profile/DayZServer_2026_02_07.ADM
```

### Passo 4: Atualizar .env com Caminho Correto

Baseado no resultado do diagnóstico, atualize:

```env
FTP_LOG_PATH=/profile/DayZServer_2026_02_07.ADM
```

**Nota**: Se você deixar `FTP_LOG_PATH` vazio, o sistema usará **auto-detect** para encontrar o arquivo de log mais recente automaticamente.

---

## 📡 Como Funciona

### 1. Ciclo de Parsing de Logs

```
┌─────────────────────────────────────────────────┐
│  1. Conexão FTP Nitrado                         │
│     ↓                                            │
│  2. Download do arquivo ADM.log                 │
│     ↓                                            │
│  3. Parsing de eventos:                         │
│     - Player Login/Logout                       │
│     - Kills (PvP e PvE)                         │
│     - Deaths                                     │
│     - Base Building                             │
│     - Item Placement                            │
│     ↓                                            │
│  4. Atualização do Banco de Dados               │
│     ↓                                            │
│  5. Envio via WebSocket para Dashboard          │
│     ↓                                            │
│  6. Aguarda 60s e repete                        │
└─────────────────────────────────────────────────┘
```

### 2. Eventos Capturados

#### 🔫 PvP Kills
```
[LOG PARSER] Kill: Jogador1 matou Jogador2 com M4A1
→ Atualiza deaths_log
→ Incrementa kills/deaths dos jogadores
→ Verifica se há guerra ativa entre clãs
→ Envia notificação ao Discord
```

#### 🧟 Zombie Kills
```
[LOG PARSER] Jogador1 matou zombie com Machete
→ Incrementa zombie_kills (futuro)
```

#### 🔐 Login/Logout
```
[LOG PARSER] Jogador1 conectou (IP: 192.168.1.1)
→ Registra em connection_logs
→ Verifica anti-cheat (ban list, alts)
→ Atualiza last_seen no banco
```

#### 🏗️ Base Building
```
[LOG PARSER] Jogador1 colocou Fence (15m de altura)
→ Verifica altura permitida
→ Detecta spam de construção (lag machine)
→ Auto-ban se necessário
```

---

## 🛠️ Manutenção

### Verificar Status do Parser

```bash
# Ver logs em tempo real
tail -f server_logs.txt

# Verificar última execução
cat last_execution.log
```

### Reiniciar Parser de Logs

O parser roda automaticamente quando o dashboard está ativo:

```bash
cd "d:\dayz xbox\BigodeBot\new_dashboard"
python app.py
```

**Log de Inicialização**:
```
[SYSTEM] Iniciando Robô de Logs Autônomo...
========================================
   BIGODETEXAS - ROBÔ DE LOGS ATIVO
        Status: MODO AUTÔNOMO
========================================
[2026-02-07 19:00:00] Iniciando ciclo autônomo de logs...
[LOG PARSER] Conectando ao FTP: brsp012.gamedata.io
[LOG PARSER] ✓ Caminho configurado encontrado!
[LOG PARSER] → Baixando: /profile/DayZServer_2026_02_07.ADM
[LOG PARSER] ✓ Log baixado com sucesso (1.2 MB)
[LOG PARSER] Parsing de 5,342 linhas...
[LOG PARSER] Processados: 23 kills, 45 logins, 12 construções
```

### Troubleshooting

#### ❌ Erro: "550 No such file or directory"

**Causa**: Caminho do log incorreto ou arquivo não existe.

**Solução**:
1. Execute `python scripts/nitrado_diagnostics.py`
2. Atualize `FTP_LOG_PATH` no `.env`
3. Ou deixe vazio para auto-detect

#### ❌ Erro: "530 Login incorrect"

**Causa**: Credenciais FTP inválidas.

**Solução**:
1. Verifique usuário e senha no painel Nitrado
2. Atualize `.env`
3. Reinicie o dashboard

#### ❌ Erro: "Timeout"

**Causa**: Firewall ou conexão lenta.

**Solução**:
1. Verifique conexão com internet
2. Aumente timeout em `log_parser.py` (linha 54):
   ```python
   ftp.connect(self.ftp_host, self.ftp_port, timeout=60)  # 60 segundos
   ```

#### ⚠️ Warning: "Auto-detect não encontrou logs"

**Causa**: Servidor Nitrado não está gerando logs ADM.

**Solução**:
1. No painel Nitrado, vá em **Configurações → Logs**
2. Ative **Admin Log (ADM)**
3. Reinicie o servidor DayZ
4. Aguarde 10-15 minutos para logs serem gerados

---

## 🔄 Auto-Recovery

O sistema possui **auto-recovery** automático:

```python
[AUTO-RECOVERY] Falha detectada. Reiniciando em 60s...
[AUTO-RECOVERY] Falha detectada. Reiniciando em 120s...
[AUTO-RECOVERY] Falha detectada. Reiniciando em 180s...
```

- **1ª falha**: Aguarda 60s
- **2ª falha**: Aguarda 120s (2min)
- **3ª falha**: Aguarda 180s (3min)
- **4ª falha**: Aguarda 240s (4min)
- **5ª falha**: Aguarda 300s (5min - máximo)

Após recuperação bem-sucedida, o intervalo volta para 60s.

---

## 📊 Monitoramento

### Dashboard Web

Acesse: http://127.0.0.1:5001

**Seções em Tempo Real**:
- 🎯 **Killfeed**: Kills em tempo real
- 👥 **Players Online**: Quem está conectado
- 📈 **Leaderboard**: Rankings atualizados
- ⚔️ **Clan Wars**: Placares de guerra
- 🛡️ **Anti-Cheat Alerts**: Detecções suspeitas

### Discord Notifications

Configure webhook no `.env`:

```env
NOTIFICATION_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

**Notificações Enviadas**:
- Kill importante (headshot, longa distância)
- Jogador banido (anti-cheat)
- Guerra iniciada/finalizada
- Servidor online/offline

---

## 🔐 Segurança

### Credenciais FTP

**NUNCA compartilhe**:
- ❌ Não commite `.env` no GitHub
- ❌ Não compartilhe senha FTP
- ❌ Não poste logs com credenciais

**Boas Práticas**:
- ✅ Use `.env` para credenciais
- ✅ Adicione `.env` ao `.gitignore`
- ✅ Use FTP_TLS se disponível (futuro)
- ✅ Rotacione senhas regularmente

### Validação de Dados

O parser **valida todos os dados** antes de inserir no banco:
- IP addresses
- Player names (anti-injection)
- Coordenadas (anti-exploit)
- Alturas de construção (anti-fly hack)

---

## 📚 Referências

- **Nitrado API Docs**: https://doc.nitrado.net
- **DayZ Server Logs**: https://community.bistudio.com/wiki/DayZ:Server_Configuration
- **BigodeBot Docs**: [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)

---

**Documentação Atualizada**: 2026-02-07
**Versão do Sistema**: v2.3.0
