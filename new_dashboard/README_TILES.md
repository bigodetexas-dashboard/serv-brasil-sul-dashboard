# Mapa Chernarus - Tiles (Mosaicos)

Este sistema utiliza tiles (mosaicos) para exibir o mapa de Chernarus com alta qualidade e zoom infinito, similar ao Google Maps ou iZurvive.

## Como obter os tiles

### Opção 1: Script Automático (Recomendado)

Execute o script `download_tiles.py` para baixar os tiles diretamente do iZurvive (ou outra fonte configurada).

```bash
python download_tiles.py
```

Isso criará a pasta `static/tiles` com a estrutura correta.

### Opção 2: Download Manual

Se o script falhar (por bloqueio de IP ou mudança na URL), você pode baixar um pacote de tiles pronto.

1. Procure por "DayZ ChernarusPlus Tiles Leaflet" ou use um dos links abaixo (se estiverem ativos):
   - <https://dayz.ginfo.gg/map/tiles/chernarusplus.zip>
   - <https://files.dayzsurvival.info/maps/chernarusplus/tiles.zip>

2. Extraia o conteúdo do ZIP.
3. A estrutura deve ficar assim:

   ```
   new_dashboard/
   ├── static/
   │   ├── tiles/
   │   │   ├── 0/
   │   │   │   └── 0/
   │   │   │       └── 0.png
   │   │   ├── 1/
   │   │   ├── ...
   ```

## Configuração

O arquivo `static/js/heatmap.js` já está configurado para ler os tiles de `/static/tiles/{z}/{x}/{y}.png`.

Se você usar uma fonte externa (URL), edite a linha `L.tileLayer` no `heatmap.js`.
