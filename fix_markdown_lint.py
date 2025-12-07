"""
Script para corrigir automaticamente problemas comuns de linting em arquivos Markdown.

Este script corrige os seguintes problemas:
- MD022: Adiciona linhas em branco ao redor de headings
- MD031: Adiciona linhas em branco ao redor de code blocks
- MD032: Adiciona linhas em branco ao redor de listas
- MD040: Adiciona linguagens aos code blocks quando possível

Uso:
    python fix_markdown_lint.py [arquivo.md]
    python fix_markdown_lint.py --all  # Corrige todos os .md no projeto
"""

import re
import sys
from pathlib import Path


def fix_blanks_around_headings(content: str) -> str:
    """Adiciona linhas em branco antes e depois de headings."""
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Verifica se é um heading
        if line.strip().startswith('#'):
            # Adiciona linha em branco antes (se não for a primeira linha)
            if i > 0 and fixed_lines and fixed_lines[-1].strip() != '':
                fixed_lines.append('')
            
            fixed_lines.append(line)
            
            # Adiciona linha em branco depois (se não for a última linha)
            if i < len(lines) - 1 and lines[i + 1].strip() != '':
                fixed_lines.append('')
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_blanks_around_fences(content: str) -> str:
    """Adiciona linhas em branco ao redor de code blocks."""
    lines = content.split('\n')
    fixed_lines = []
    in_code_block = False
    
    for i, line in enumerate(lines):
        if line.strip().startswith('```'):
            if not in_code_block:
                # Início do code block - adiciona linha antes
                if i > 0 and fixed_lines and fixed_lines[-1].strip() != '':
                    fixed_lines.append('')
                in_code_block = True
            else:
                # Fim do code block
                in_code_block = False
                fixed_lines.append(line)
                # Adiciona linha depois
                if i < len(lines) - 1 and lines[i + 1].strip() != '':
                    fixed_lines.append('')
                continue
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_blanks_around_lists(content: str) -> str:
    """Adiciona linhas em branco ao redor de listas."""
    lines = content.split('\n')
    fixed_lines = []
    in_list = False
    
    for i, line in enumerate(lines):
        is_list_item = line.strip().startswith(('-', '*', '+')) or \
                      (len(line.strip()) > 0 and line.strip()[0].isdigit() and '.' in line)
        
        if is_list_item and not in_list:
            # Início da lista - adiciona linha antes
            if i > 0 and fixed_lines and fixed_lines[-1].strip() != '':
                fixed_lines.append('')
            in_list = True
        elif not is_list_item and in_list and line.strip() != '':
            # Fim da lista - adiciona linha depois
            if fixed_lines and fixed_lines[-1].strip() != '':
                fixed_lines.append('')
            in_list = False
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def add_code_block_languages(content: str) -> str:
    """Adiciona linguagens aos code blocks quando possível."""
    # Detecta code blocks sem linguagem e tenta inferir
    patterns = {
        r'```\s*\n\s*{': 'json',
        r'```\s*\n\s*import ': 'python',
        r'```\s*\n\s*def ': 'python',
        r'```\s*\n\s*class ': 'python',
        r'```\s*\n\s*<!DOCTYPE': 'html',
        r'```\s*\n\s*<html': 'html',
        r'```\s*\n\s*function': 'javascript',
        r'```\s*\n\s*const ': 'javascript',
        r'```\s*\n\s*let ': 'javascript',
        r'```\s*\n\s*npm ': 'bash',
        r'```\s*\n\s*python ': 'bash',
        r'```\s*\n\s*cd ': 'bash',
        r'```\s*\n\s*git ': 'bash',
        r'```\s*\n\s*[A-Z_]+\s*=': 'env',
    }
    
    for pattern, lang in patterns.items():
        content = re.sub(pattern, f'```{lang}\n', content, flags=re.MULTILINE)
    
    return content


def fix_markdown_file(filepath: Path) -> bool:
    """Corrige um arquivo markdown."""
    try:
        print(f"[*] Processando: {filepath}")
        
        # Lê o conteúdo
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Aplica correções
        content = fix_blanks_around_headings(content)
        content = fix_blanks_around_fences(content)
        content = fix_blanks_around_lists(content)
        content = add_code_block_languages(content)
        
        # Remove múltiplas linhas em branco consecutivas
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Salva apenas se houve mudanças
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   [OK] Corrigido!")
            return True
        else:
            print(f"   [INFO] Nenhuma correcao necessaria")
            return False
            
    except Exception as e:
        print(f"   [ERRO] {e}")
        return False


def main():
    """Função principal."""
    if len(sys.argv) < 2:
        print("Uso: python fix_markdown_lint.py [arquivo.md]")
        print("     python fix_markdown_lint.py --all")
        sys.exit(1)
    
    if sys.argv[1] == '--all':
        # Processa todos os arquivos .md no projeto
        project_root = Path(__file__).parent
        md_files = list(project_root.rglob('*.md'))
        
        print(f"[*] Encontrados {len(md_files)} arquivos markdown")
        print()
        
        fixed_count = 0
        for md_file in md_files:
            if fix_markdown_file(md_file):
                fixed_count += 1
        
        print()
        print(f"[OK] Concluido! {fixed_count}/{len(md_files)} arquivos corrigidos")
    else:
        # Processa arquivo específico
        filepath = Path(sys.argv[1])
        if not filepath.exists():
            print(f"[ERRO] Arquivo nao encontrado: {filepath}")
            sys.exit(1)
        
        fix_markdown_file(filepath)


if __name__ == '__main__':
    main()
