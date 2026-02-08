# -*- coding: utf-8 -*-
"""
Diagnóstico de Conexão Nitrado FTP
BigodeTexas v2.3

Este script ajuda a encontrar o caminho correto dos logs no servidor Nitrado.
"""
import os
import sys
from ftplib import FTP
from dotenv import load_dotenv

# Adicionar raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# Cores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")


def print_ok(text):
    print(f"{Colors.GREEN}[OK]{Colors.RESET} {text}")


def print_error(text):
    print(f"{Colors.RED}[X]{Colors.RESET} {text}")


def print_info(text):
    print(f"{Colors.CYAN}-->{Colors.RESET} {text}")


def print_warning(text):
    print(f"{Colors.YELLOW}[!]{Colors.RESET} {text}")


def list_directory(ftp, path="/", indent=0, max_depth=3):
    """Lista recursivamente diretórios e arquivos"""
    if indent >= max_depth:
        return

    try:
        ftp.cwd(path)
        items = []

        try:
            items = ftp.nlst()
        except Exception:
            return

        for item in items:
            # Ignorar . e ..
            if item in [".", ".."]:
                continue

            item_path = f"{path}/{item}" if path != "/" else f"/{item}"
            indent_str = "  " * indent

            try:
                # Tentar entrar (é um diretório)
                ftp.cwd(item_path)
                print(f"{indent_str}{Colors.CYAN}[DIR] {item}/{Colors.RESET}")

                # Recursivamente listar subdiretórios
                list_directory(ftp, item_path, indent + 1, max_depth)

                # Voltar ao diretório anterior
                ftp.cwd(path)
            except:
                # É um arquivo
                file_upper = item.upper()

                # Destacar arquivos importantes
                if file_upper.endswith('.ADM'):
                    print(f"{indent_str}{Colors.GREEN}[FILE] {item} {Colors.BOLD}[LOG ADM]{Colors.RESET}")
                elif file_upper.endswith('.RPT'):
                    print(f"{indent_str}{Colors.YELLOW}[FILE] {item} [LOG RPT]{Colors.RESET}")
                elif file_upper.endswith('.LOG'):
                    print(f"{indent_str}{Colors.YELLOW}[FILE] {item} [LOG]{Colors.RESET}")
                elif file_upper.endswith('.XML'):
                    print(f"{indent_str}[FILE] {item} [XML]")
                elif file_upper.endswith('.JSON'):
                    print(f"{indent_str}[FILE] {item} [JSON]")
                else:
                    print(f"{indent_str}[FILE] {item}")

    except Exception as e:
        print_error(f"Erro ao acessar {path}: {e}")


def find_log_files(ftp, search_path="/"):
    """Procura especificamente por arquivos de log"""
    log_files = []

    try:
        ftp.cwd(search_path)
        items = ftp.nlst()

        for item in items:
            item_path = f"{search_path}/{item}" if search_path != "/" else f"/{item}"

            try:
                # Tentar entrar (é um diretório)
                ftp.cwd(item_path)

                # Recursivamente procurar
                sub_logs = find_log_files(ftp, item_path)
                log_files.extend(sub_logs)

                # Voltar
                ftp.cwd(search_path)
            except:
                # É um arquivo
                file_upper = item.upper()
                if file_upper.endswith('.ADM') or file_upper.endswith('.RPT') or file_upper.endswith('.LOG'):
                    log_files.append(item_path)

    except Exception:
        pass

    return log_files


def diagnose_nitrado():
    """Executa diagnóstico completo da conexão Nitrado"""

    print_header("DIAGNÓSTICO NITRADO FTP")

    # 1. Verificar credenciais
    print(f"{Colors.BOLD}1. Verificando Credenciais{Colors.RESET}")

    ftp_host = os.getenv("FTP_HOST")
    ftp_user = os.getenv("FTP_USER")
    ftp_pass = os.getenv("FTP_PASS")
    ftp_port = int(os.getenv("FTP_PORT", 21))
    ftp_log_path = os.getenv("FTP_LOG_PATH")

    if not ftp_host or not ftp_user or not ftp_pass:
        print_error("Credenciais FTP incompletas no .env")
        print_info("Certifique-se de que FTP_HOST, FTP_USER e FTP_PASS estão configurados")
        return False

    print_ok(f"Host: {ftp_host}:{ftp_port}")
    print_ok(f"Usuário: {ftp_user}")
    print_ok(f"Senha: {'*' * len(ftp_pass)}")

    if ftp_log_path:
        print_ok(f"Caminho Configurado: {ftp_log_path}")
    else:
        print_warning("FTP_LOG_PATH não configurado (usando auto-detect)")

    # 2. Testar conexão
    print(f"\n{Colors.BOLD}2. Testando Conexão FTP{Colors.RESET}")

    try:
        print_info(f"Conectando a {ftp_host}:{ftp_port}...")
        ftp = FTP()
        ftp.connect(ftp_host, ftp_port, timeout=30)
        print_ok("Conexão estabelecida")

        print_info(f"Autenticando como {ftp_user}...")
        ftp.login(ftp_user, ftp_pass)
        print_ok("Autenticação bem-sucedida")

        # 3. Listar diretório raiz
        print(f"\n{Colors.BOLD}3. Explorando Estrutura de Diretórios{Colors.RESET}")
        print_info("Mapeando estrutura do servidor (max 3 níveis)...\n")

        list_directory(ftp, "/", 0, 3)

        # 4. Procurar arquivos de log
        print(f"\n{Colors.BOLD}4. Procurando Arquivos de Log{Colors.RESET}")
        print_info("Buscando arquivos .ADM, .RPT e .LOG...\n")

        log_files = find_log_files(ftp, "/")

        if log_files:
            print_ok(f"Encontrados {len(log_files)} arquivo(s) de log:\n")

            for log_file in log_files:
                file_type = "ADM" if log_file.upper().endswith('.ADM') else (
                    "RPT" if log_file.upper().endswith('.RPT') else "LOG"
                )

                color = Colors.GREEN if file_type == "ADM" else Colors.YELLOW
                print(f"  {color}[{file_type}]{Colors.RESET} {log_file}")
        else:
            print_warning("Nenhum arquivo de log encontrado")

        # 5. Testar caminho configurado
        if ftp_log_path:
            print(f"\n{Colors.BOLD}5. Testando Caminho Configurado{Colors.RESET}")

            try:
                print_info(f"Verificando: {ftp_log_path}")
                ftp.cwd("/")
                size = ftp.size(ftp_log_path)
                print_ok(f"Arquivo encontrado! Tamanho: {size:,} bytes")
            except Exception as e:
                print_error(f"Arquivo não encontrado: {e}")
                print_warning("Atualize FTP_LOG_PATH no .env com um dos caminhos acima")

        # 6. Recomendações
        print(f"\n{Colors.BOLD}6. Recomendações{Colors.RESET}")

        if log_files:
            # Priorizar .ADM files
            adm_files = [f for f in log_files if f.upper().endswith('.ADM')]

            if adm_files:
                recommended = adm_files[0]
                print_ok(f"Caminho recomendado (ADM): {Colors.BOLD}{recommended}{Colors.RESET}")
            else:
                recommended = log_files[0]
                print_ok(f"Caminho recomendado: {Colors.BOLD}{recommended}{Colors.RESET}")

            print_info("\nPara usar este caminho, adicione ao .env:")
            print(f"\n  {Colors.CYAN}FTP_LOG_PATH={recommended}{Colors.RESET}\n")
        else:
            print_warning("Configure o servidor para gerar logs ADM")

        ftp.quit()
        print_ok("\nDiagnóstico concluído com sucesso!")
        return True

    except Exception as e:
        print_error(f"Erro durante diagnóstico: {e}")
        return False


if __name__ == "__main__":
    print(f"{Colors.BOLD}BigodeTexas - Diagnóstico Nitrado FTP{Colors.RESET}")
    print("Este script irá mapear o servidor FTP e encontrar os logs.\n")

    success = diagnose_nitrado()

    sys.exit(0 if success else 1)
