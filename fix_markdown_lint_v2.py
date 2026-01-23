"""
Script aprimorado para corrigir problemas de linting em arquivos Markdown.
Versão 2.0 - Correções mais agressivas.
"""

import re
import sys
from pathlib import Path


def fix_code_block_languages_aggressive(content: str) -> str:
    """Adiciona linguagens aos code blocks de forma mais agressiva."""
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Detecta code block sem linguagem
        if line.strip() == '```':
            # Olha a próxima linha para inferir a linguagem
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                
                # Inferências baseadas no conteúdo
                if next_line.startswith('{') or next_line.startswith('['):
                    fixed_lines.append('```json')
                elif next_line.startswith('import ') or next_line.startswith('def ') or next_line.startswith('class '):
                    fixed_lines.append('```python')
                elif next_line.startswith('<!DOCTYPE') or next_line.startswith('<html'):
                    fixed_lines.append('```html')
                elif next_line.startswith('function') or next_line.startswith('const ') or next_line.startswith('let '):
                    fixed_lines.append('```javascript')
                elif any(cmd in next_line for cmd in ['npm ', 'python ', 'cd ', 'git ', 'pip ', 'node ']):
                    fixed_lines.append('```bash')
                elif '=' in next_line and next_line.isupper():
                    fixed_lines.append('```env')
                elif next_line.startswith('http://') or next_line.startswith('https://'):
                    fixed_lines.append('```text')
                elif any(word in next_line for word in ['PORT', 'DATABASE', 'SECRET', 'API']):
                    fixed_lines.append('```env')
                else:
                    # Default para text se não conseguir inferir
                    fixed_lines.append('```text')
            else:
                fixed_lines.append('```text')
        else:
            fixed_lines.append(line)
        
        i += 1
    
    return '\n'.join(fixed_lines)


def fix_duplicate_headings(content: str) -> str:
    """Adiciona contexto a headings duplicados."""
    lines = content.split('\n')
    heading_counts = {}
    fixed_lines = []
    
    for line in lines:
        if line.strip().startswith('#'):
            heading_text = line.strip()
            
            # Conta ocorrências
            if heading_text in heading_counts:
                heading_counts[heading_text] += 1
                # Não modifica, apenas registra (correção manual necessária)
            else:
                heading_counts[heading_text] = 1
            
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_ordered_lists(content: str) -> str:
    """Corrige numeração de listas ordenadas."""
    lines = content.split('\n')
    fixed_lines = []
    in_list = False
    list_counter = 1
    current_indent = 0
    
    for i, line in enumerate(lines):
        # Detecta item de lista ordenada
        match = re.match(r'^(\s*)(\d+)\.\s+(.+)$', line)
        
        if match:
            indent = len(match.group(1))
            
            # Nova lista ou mudança de indentação
            if not in_list or indent != current_indent:
                list_counter = 1
                current_indent = indent
                in_list = True
            
            # Reconstrói a linha com numeração correta
            fixed_lines.append(f"{match.group(1)}{list_counter}. {match.group(3)}")
            list_counter += 1
        else:
            # Não é item de lista
            if line.strip() == '':
                # Linha vazia pode resetar a lista
                in_list = False
            elif not line.strip().startswith('#'):
                # Texto normal reseta a lista
                in_list = False
            
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_emphasis_as_heading(content: str) -> str:
    """Converte ênfase usada como heading em heading real."""
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Detecta linha que é só negrito/itálico (possível heading)
        if re.match(r'^\*\*[^*]+\*\*\s*$', line) or re.match(r'^__[^_]+__\s*$', line):
            # Verifica contexto (se está isolada, provavelmente é heading)
            prev_empty = i == 0 or lines[i-1].strip() == ''
            next_empty = i == len(lines)-1 or (i+1 < len(lines) and lines[i+1].strip() == '')
            
            if prev_empty and next_empty:
                # Converte para heading nível 3
                text = re.sub(r'\*\*|__', '', line).strip()
                fixed_lines.append(f"### {text}")
                continue
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_markdown_file_v2(filepath: Path) -> bool:
    """Versão 2 - Correções mais agressivas."""
    try:
        print(f"[*] Processando: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Aplica correções
        content = fix_code_block_languages_aggressive(content)
        content = fix_ordered_lists(content)
        content = fix_emphasis_as_heading(content)
        
        # Remove múltiplas linhas em branco
        content = re.sub(r'\n{3,}', '\n\n', content)
        
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
        print("Uso: python fix_markdown_lint_v2.py [arquivo.md]")
        print("     python fix_markdown_lint_v2.py --all")
        sys.exit(1)
    
    if sys.argv[1] == '--all':
        project_root = Path(__file__).parent
        md_files = list(project_root.rglob('*.md'))
        
        print(f"[*] Encontrados {len(md_files)} arquivos markdown")
        print()
        
        fixed_count = 0
        for md_file in md_files:
            if fix_markdown_file_v2(md_file):
                fixed_count += 1
        
        print()
        print(f"[OK] Concluido! {fixed_count}/{len(md_files)} arquivos corrigidos")
    else:
        filepath = Path(sys.argv[1])
        if not filepath.exists():
            print(f"[ERRO] Arquivo nao encontrado: {filepath}")
            sys.exit(1)
        
        fix_markdown_file_v2(filepath)


if __name__ == '__main__':
    main()
