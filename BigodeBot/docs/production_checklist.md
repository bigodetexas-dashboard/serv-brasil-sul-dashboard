# Checklist de Produção - Bigode Texas (Windows)

Siga estes passos para implantar o Bigode Texas no seu servidor Windows.

## 1. Preparação do Ambiente

- [ ] Instalar Python: [python.org](https://www.python.org/downloads/) (Certifique-se de marcar "Add Python to PATH").
- [ ] Instalar Git: [git-scm.com](https://git-scm.com/download/win).

## 2. Configuração do Projeto

- [ ] Abrir o PowerShell ou CMD na pasta do projeto.
- [ ] Criar ambiente virtual: `python -m venv venv`
- [ ] Ativar venv: `.\venv\Scripts\activate`
- [ ] Instalar dependências: `pip install -r requirements.txt`
- [ ] Configurar o arquivo `.env` (use o `.env.example` como base).

## 3. Inicialização e Persistência

Você tem duas opções para manter o Bot e o Dashboard rodando:

### Opção A: Agendador de Tarefas (Simples)

- [ ] Criar um arquivo `.bat` para o Bot e outro para o Dashboard.
- [ ] Configurar no Agendador de Tarefas para iniciar "Ao inicializar o computador".

### Opção B: NSSM (Recomendado para VPS Windows)

- [ ] Baixar o [NSSM](https://nssm.cc/download).
- [ ] Instalar o Dashboard como serviço: `nssm install BigodeTexasDashboard`
- [ ] Instalar o Bot como serviço: `nssm install BigodeTexasBot`

## 4. Servidor Web (Acesso Externo)

- [ ] Abrir a porta **5000** no Firewall do Windows.
- [ ] Se tiver um domínio, você pode usar o Nginx para Windows ou simplesmente redirecionar o tráfego.

## 5. Manutenção e Backup

- [ ] Backup manual ou via script .ps1 do arquivo `database.db`.

> [!IMPORTANT]
> No Windows, o comando para rodar o dashboard Local é: `python -m waitress --port=5000 new_dashboard.app:app` (ou similar) em vez de Gunicorn.
