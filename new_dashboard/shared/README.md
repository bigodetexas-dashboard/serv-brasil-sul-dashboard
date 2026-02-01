# Shared Modules

Módulos compartilhados entre bot_service e web_service.

## Estrutura

```
shared/
├── repositories/        # Camada de acesso a dados
│   ├── base_repository.py
│   ├── player_repository.py
│   ├── clan_repository.py
│   ├── bounty_repository.py
│   ├── item_repository.py
│   └── connection_pool.py
├── utils/               # Utilitários comuns
│   ├── cache.py
│   ├── helpers.py
│   ├── decorators.py
│   ├── nitrado.py
│   └── ftp_helpers.py
├── models/              # Modelos de dados (futuro)
└── bigodebot.db        # Banco de dados SQLite
```

## Uso

Ambos os serviços importam deste diretório:

```python
# No bot_service ou web_service
import sys
sys.path.append('../shared')

from repositories.player_repository import PlayerRepository
from utils.cache import cached
```

## Banco de Dados

O banco `bigodebot.db` fica aqui para ser acessado por ambos os serviços.

## Sincronização

Ambos os serviços devem usar as mesmas versões dos módulos compartilhados.
Qualquer alteração aqui afeta ambos os serviços.
