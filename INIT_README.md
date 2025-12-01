# init.c - Sistema de Entrega de Itens DayZ

## ⚠️ IMPORTANTE: Este é um arquivo Enforce Script, NÃO é C

Este arquivo usa **Enforce Script**, a linguagem de scripting do DayZ. Se você está vendo erros na IDE como:

- "Use of undeclared identifier 'GetGame'"
- "Unknown type name 'class'"
- "Use of undeclared identifier 'Weather'"

**Esses erros são FALSOS!** Sua IDE está analisando o arquivo como C padrão, mas o código está correto para DayZ.

## ✅ Como Resolver os Erros Falsos

### Opção 1: Ignorar os Erros

O código está correto e funcionará no servidor DayZ. Você pode simplesmente ignorar os erros da IDE.

### Opção 2: Desabilitar Análise C/C++ (VS Code)

Crie o arquivo `.vscode/settings.json` (mesmo que esteja no .gitignore) com:

```json
{
    "files.associations": {
        "init.c": "plaintext"
    },
    "C_Cpp.errorSquiggles": "disabled"
}
```

### Opção 3: Instalar Extensão DayZ

Procure por extensões "DayZ" ou "Enforce Script" no marketplace da sua IDE.

## 📋 O Que Este Arquivo Faz

Este `init.c` implementa:

1. **Inicialização do Clima** - Configura nebulosidade, chuva e neblina
2. **Inicialização da Economia** - Cria o Hive e inicializa o sistema de loot
3. **Reset de Data** - Mantém a data do servidor em 20 de setembro
4. **Sistema de Entrega de Itens** - Integração com o BigodeBot

## 🔄 Sistema de Entrega (BigodeBot)

O sistema funciona assim:

1. **Bot recebe pedido** - Jogador compra item no dashboard
2. **Bot cria spawns.json** - Arquivo com itens e coordenadas
3. **Bot envia via FTP** - Upload para `$profile:spawns.json` no servidor
4. **Servidor processa** - A cada 60 segundos, verifica se existe o arquivo
5. **Itens são spawnados** - Cria os objetos nas coordenadas especificadas
6. **Arquivo é deletado** - Para não spawnar novamente

## 📝 Formato do spawns.json

```json
{
    "items": [
        {
            "name": "AKM",
            "coords": "7500.0 5500.0"
        },
        {
            "name": "Mag_AKM_30Rnd",
            "coords": "7500.0 0.0 5500.0"
        }
    ]
}
```

**Coordenadas:**

- Formato 2D: `"X Z"` - O Y (altura) é calculado automaticamente
- Formato 3D: `"X Y Z"` - Altura manual

## 🛠️ Classes Definidas

### `SpawnItem`

Representa um item a ser spawnado:

- `name` - Nome da classe do item (ex: "AKM")
- `coords` - Coordenadas no formato string

### `SpawnData`

Container para a lista de itens:

- `items` - Array de SpawnItem

### `CustomMission`

Missão customizada que herda de MissionServer:

## 📚 Referências

- [DayZ Modding Wiki](https://community.bistudio.com/wiki/DayZ:Enforce_Script_Syntax)
- [Enforce Script Documentation](https://community.bistudio.com/wiki/Enforce_Script)
- Documentação do BigodeBot: `DELIVERY_SYSTEM.md`

## ⚙️ Integração com BigodeBot

Este arquivo trabalha em conjunto com:

- `spawn_system.py` - Gerencia a fila de entregas
- `delivery_processor.py` - Processa pedidos e cria o JSON
- `bot_main.py` - Comandos Discord e lógica principal

---

**Nota:** Este arquivo deve estar localizado em `mpmissions/[sua_missao]/init.c` no servidor DayZ.
