import sys
import subprocess
import re
from datetime import datetime
import os

# Cores ANSI para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header():
    """Imprime cabeçalho moderno do bot"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print()
    print("   " + "="*78)
    print("   " + Colors.OKGREEN + Colors.BOLD + "BIGODEBOT ATIVO - MONITORANDO SERVIDOR DAYZ" + Colors.ENDC)
    print("   " + "="*78)
    print()

def format_log_line(line):
    """Formata linhas de log para serem mais legíveis"""
    
    # Remover caracteres de controle
    line = line.strip()
    
    # Detectar tipo de mensagem
    if "logging in using static token" in line.lower():
        timestamp = datetime.now().strftime("%H:%M:%S")
        return f"   [{Colors.OKGREEN}{timestamp}{Colors.ENDC}] {Colors.OKGREEN}✓{Colors.ENDC} Autenticando no Discord..."
    
    elif "has connected to Gateway" in line:
        timestamp = datetime.now().strftime("%H:%M:%S")
        session_match = re.search(r'Session ID: ([a-f0-9]+)', line)
        session_id = session_match.group(1)[:8] if session_match else "unknown"
        return f"   [{Colors.OKGREEN}{timestamp}{Colors.ENDC}] {Colors.OKGREEN}✓{Colors.ENDC} Conectado ao Discord (Sessão: {session_id}...)"
    
    elif "Running on" in line:
        if "127.0.0.1" in line:
            url_match = re.search(r'(http://[^\s]+)', line)
            url = url_match.group(1) if url_match else "http://127.0.0.1:3000"
            return f"   [{Colors.OKCYAN}WEB{Colors.ENDC}] Dashboard disponível em: {Colors.BOLD}{url}{Colors.ENDC}"
        elif "192.168" in line:
            url_match = re.search(r'(http://[^\s]+)', line)
            url = url_match.group(1) if url_match else ""
            return f"   [{Colors.OKCYAN}LAN{Colors.ENDC}] Acesso na rede local: {url}"
        else:
            return None
    
    elif "Serving Flask app" in line:
        return f"   [{Colors.OKBLUE}INFO{Colors.ENDC}] Servidor web iniciado"
    
    elif "WARNING" in line and "development server" in line:
        return None  # Ocultar warning de dev server
    
    elif "Press CTRL+C to quit" in line:
        return f"\n   {Colors.WARNING}Pressione CTRL+C para parar o bot{Colors.ENDC}\n"
    
    elif "[INFO" in line:
        # Outras mensagens INFO
        msg = line.split("]", 2)[-1].strip() if "]" in line else line
        timestamp = datetime.now().strftime("%H:%M:%S")
        return f"   [{Colors.OKBLUE}{timestamp}{Colors.ENDC}] {msg}"
    
    elif "[WARNING" in line:
        msg = line.split("]", 2)[-1].strip() if "]" in line else line
        timestamp = datetime.now().strftime("%H:%M:%S")
        return f"   [{Colors.WARNING}{timestamp}{Colors.ENDC}] ⚠ {msg}"
    
    elif "[ERROR" in line or "[ERRO" in line:
        msg = line.split("]", 2)[-1].strip() if "]" in line else line
        timestamp = datetime.now().strftime("%H:%M:%S")
        return f"   [{Colors.FAIL}{timestamp}{Colors.ENDC}] ✗ {msg}"
    
    else:
        # Linha genérica
        if line and not line.startswith("*"):
            return f"   {line}"
        return None

def run_bot():
    """Executa o bot com formatação de saída"""
    print_header()
    
    print(f"   [{Colors.OKBLUE}INIT{Colors.ENDC}] Iniciando BigodeBot...")
    print()
    
    # Executar bot_main.py
    process = subprocess.Popen(
        [sys.executable, "bot_main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    try:
        for line in process.stdout:
            formatted = format_log_line(line)
            if formatted:
                print(formatted)
                sys.stdout.flush()
    
    except KeyboardInterrupt:
        print()
        print(f"   [{Colors.WARNING}STOP{Colors.ENDC}] Parando bot...")
        process.terminate()
        process.wait()
        print(f"   [{Colors.OKGREEN}DONE{Colors.ENDC}] Bot encerrado com sucesso")
        print()
    
    except Exception as e:
        print()
        print(f"   [{Colors.FAIL}ERRO{Colors.ENDC}] Erro ao executar bot: {e}")
        print()

if __name__ == "__main__":
    run_bot()
