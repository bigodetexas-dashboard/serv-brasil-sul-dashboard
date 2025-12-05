#!/usr/bin/env python3
"""
Sistema de Backup Automático - BigodeBot
Salva automaticamente cada modificação positiva do projeto
"""

import os
import shutil
import json
from datetime import datetime
import hashlib

BACKUP_DIR = "backups/auto_saves"
BACKUP_INDEX = "backups/backup_index.json"

def get_file_hash(filepath):
    """Calcula hash MD5 do arquivo"""
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except:
        return None

def load_backup_index():
    """Carrega índice de backups"""
    if os.path.exists(BACKUP_INDEX):
        with open(BACKUP_INDEX, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"backups": [], "file_hashes": {}}

def save_backup_index(index):
    """Salva índice de backups"""
    os.makedirs(os.path.dirname(BACKUP_INDEX), exist_ok=True)
    with open(BACKUP_INDEX, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

def create_backup(description="Backup automático"):
    """Cria um backup completo do projeto"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{timestamp}"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    
    # Criar diretório de backup
    os.makedirs(backup_path, exist_ok=True)
    
    # Arquivos importantes para backup
    important_files = [
        "new_dashboard/app.py",
        "new_dashboard/templates/*.html",
        "new_dashboard/static/js/*.js",
        "new_dashboard/static/css/*.css",
        "bot_main.py",
        "database.py",
        "items.json",
        ".env"
    ]
    
    # Copiar arquivos
    backed_up_files = []
    index = load_backup_index()
    
    for pattern in important_files:
        if '*' in pattern:
            # Padrão com wildcard
            base_dir = os.path.dirname(pattern)
            ext = os.path.basename(pattern)
            if os.path.exists(base_dir):
                for file in os.listdir(base_dir):
                    if file.endswith(ext.replace('*', '')):
                        src = os.path.join(base_dir, file)
                        dst_dir = os.path.join(backup_path, base_dir)
                        os.makedirs(dst_dir, exist_ok=True)
                        dst = os.path.join(dst_dir, file)
                        
                        # Verificar se arquivo mudou
                        file_hash = get_file_hash(src)
                        if src not in index["file_hashes"] or index["file_hashes"][src] != file_hash:
                            shutil.copy2(src, dst)
                            backed_up_files.append(src)
                            index["file_hashes"][src] = file_hash
        else:
            # Arquivo específico
            if os.path.exists(pattern):
                dst_dir = os.path.join(backup_path, os.path.dirname(pattern))
                os.makedirs(dst_dir, exist_ok=True)
                dst = os.path.join(backup_path, pattern)
                
                # Verificar se arquivo mudou
                file_hash = get_file_hash(pattern)
                if pattern not in index["file_hashes"] or index["file_hashes"][pattern] != file_hash:
                    shutil.copy2(pattern, dst)
                    backed_up_files.append(pattern)
                    index["file_hashes"][pattern] = file_hash
    
    # Salvar informações do backup
    backup_info = {
        "timestamp": timestamp,
        "description": description,
        "files": backed_up_files,
        "path": backup_path
    }
    
    # Adicionar ao índice (NUNCA sobrescrever backups anteriores)
    index["backups"].append(backup_info)
    save_backup_index(index)
    
    print(f"[OK] Backup criado: {backup_name}")
    print(f"[INFO] Arquivos salvos: {len(backed_up_files)}")
    print(f"[INFO] Local: {backup_path}")
    print(f"[INFO] Total de backups: {len(index['backups'])}")
    
    return backup_path

def list_backups():
    """Lista todos os backups disponíveis"""
    index = load_backup_index()
    print("\n[BACKUPS DISPONIVEIS]:\n")
    for i, backup in enumerate(reversed(index["backups"]), 1):
        print(f"{i}. {backup['timestamp']} - {backup['description']}")
        print(f"   Arquivos: {len(backup['files'])}")
        print(f"   Local: {backup['path']}\n")

def restore_backup(backup_index):
    """Restaura um backup específico"""
    index = load_backup_index()
    backups = list(reversed(index["backups"]))
    
    if backup_index < 1 or backup_index > len(backups):
        print("[ERRO] Backup invalido!")
        return
    
    backup = backups[backup_index - 1]
    backup_path = backup["path"]
    
    print(f"\n[AVISO] RESTAURANDO BACKUP: {backup['timestamp']}")
    print(f"[INFO] Descricao: {backup['description']}")
    
    confirm = input("\n[AVISO] Tem certeza? Isso vai sobrescrever os arquivos atuais! (s/n): ")
    if confirm.lower() != 's':
        print("[CANCELADO] Restauracao cancelada.")
        return
    
    # Restaurar arquivos
    for file in backup["files"]:
        src = os.path.join(backup_path, file)
        if os.path.exists(src):
            os.makedirs(os.path.dirname(file), exist_ok=True)
            shutil.copy2(src, file)
            print(f"[OK] Restaurado: {file}")
    
    print(f"\n[SUCESSO] Backup restaurado com sucesso!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            description = sys.argv[2] if len(sys.argv) > 2 else "Backup manual"
            create_backup(description)
        
        elif command == "list":
            list_backups()
        
        elif command == "restore":
            if len(sys.argv) < 3:
                print("[ERRO] Uso: python auto_backup.py restore <numero>")
            else:
                restore_backup(int(sys.argv[2]))
        
        else:
            print("[ERRO] Comando invalido!")
            print("Uso:")
            print("  python auto_backup.py create [descricao]")
            print("  python auto_backup.py list")
            print("  python auto_backup.py restore <numero>")
    else:
        # Criar backup automático
        create_backup("Backup automatico - Correcao do ranking")
