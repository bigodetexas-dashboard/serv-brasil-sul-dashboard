# 🗺️ NOTA SOBRE O MAPA DO CHERNARUS

## Status Atual

Atualmente estamos usando um **mapa gerado por IA** localizado em:

```text
/static/images/chernarus_map.png
```text

## ⚠️ Próximo Passo Recomendado

Para ter o **mapa EXATO e OFICIAL** do DayZ Chernarus, você tem 3 opções:

### Opção 1: Baixar Manualmente do iZurvive

1. Acesse: <https://www.izurvive.com/chernarusplustopographic>
2. Tire um screenshot em alta resolução (4096x4096 se possível)
3. Salve como `chernarus_map.png` em `d:\dayz xbox\BigodeBot\new_dashboard\static\images\`

### Opção 2: Usar Tiles do DayZ SA Maps

1. Acesse: <https://dayz.ginfo.gg/>
2. Baixe o mapa completo
3. Salve como `chernarus_map.png`

### Opção 3: Extrair do Jogo

Se você tem o DayZ instalado, pode extrair o mapa oficial dos arquivos do jogo:

```text
C:\Program Files (x86)\Steam\steamapps\common\DayZ\dta\
```text

## 🎨 Mapa Atual (Gerado por IA)

O mapa atual foi gerado com as seguintes características:

- ✅ Topografia realista
- ✅ Florestas, campos, estradas
- ✅ Landmarks principais (NWAF, Tisy, Cherno, Elektro, Berezino)
- ✅ Grid de coordenadas
- ⚠️ Pode não ser 100% preciso com o mapa real

## 🔄 Como Substituir

Quando tiver o mapa oficial, basta:

1. Substituir o arquivo:

   ```bash
   copy "seu_mapa_oficial.png" "d:\dayz xbox\BigodeBot\new_dashboard\static\images\chernarus_map.png"
```text

1. Reiniciar o dashboard:

   ```bash
   python new_dashboard/app.py
```text

1. Validar coordenadas no modo debug:

   ```text
   http://localhost:5001/heatmap?debug=true
```text

   Os landmarks amarelos devem aparecer nas posições corretas.

---

### O sistema já está 100% funcional com o mapa atual!

A substituição é apenas para ter a versão oficial exata. ✅
