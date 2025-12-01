# 🛠️ GUIA RÁPIDO: Como Remover os Erros Falsos do init.c

## Problema

Sua IDE está mostrando erros no arquivo `init.c` porque está analisando como C, mas é **Enforce Script** (DayZ).

## ✅ Solução Definitiva (VS Code)

### Passo 1: Criar Arquivo de Configuração

Mesmo que `.vscode` esteja no `.gitignore`, você pode criar localmente (não será commitado):

1. Crie a pasta `.vscode` no diretório do projeto:

   ```powershell
   mkdir .vscode
   ```

2. Crie o arquivo `.vscode\settings.json` com este conteúdo:

   ```json
   {
       "files.associations": {
           "init.c": "plaintext"
       },
       "C_Cpp.errorSquiggles": "disabled",
       "C_Cpp.intelliSenseEngine": "disabled"
   }
   ```

### Passo 2: Recarregar VS Code

Pressione `Ctrl+Shift+P` e digite: `Developer: Reload Window`

## ✅ Solução Alternativa 1: Desabilitar C/C++ Extension

Se você não usa C/C++ para outros projetos:

1. Vá em Extensões (Ctrl+Shift+X)
2. Procure por "C/C++"
3. Clique em "Desabilitar (Workspace)"

## ✅ Solução Alternativa 2: Simplesmente Ignorar

Os erros são **FALSOS POSITIVOS**. O código está correto para DayZ.

Você pode trabalhar normalmente - o servidor DayZ compilará sem problemas.

## 📝 Verificação

Após aplicar a solução, você deve ver:

- ✅ Nenhum erro vermelho no `init.c`
- ✅ Syntax highlighting básico (ou nenhum)
- ✅ Arquivo funciona normalmente no servidor DayZ

## 🔍 Entendendo os "Erros"

Estes NÃO são erros reais:

- ❌ "Use of undeclared identifier 'GetGame'" → ✅ API válida do DayZ
- ❌ "Unknown type name 'class'" → ✅ Enforce Script usa classes
- ❌ "Use of undeclared identifier 'Weather'" → ✅ Classe do DayZ
- ❌ "Return type of 'main' is not 'int'" → ✅ Em Enforce Script é void

## 📚 Mais Informações

Leia: `INIT_README.md` para detalhes completos sobre o sistema de entrega.

---

**Nota:** Se você trabalha com C/C++ em outros projetos, use a Solução Definitiva para desabilitar apenas para este workspace.
