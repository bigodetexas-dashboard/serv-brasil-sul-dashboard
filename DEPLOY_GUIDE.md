# Guia Rápido: Deploy no Render

## ✅ Passo a Passo

### 1. Acesse o Dashboard do Render

URL: <https://dashboard.render.com/web/srv-d4jrhp8gjchc739odl2g>

### 2. Inicie o Deploy Manual

- Clique em **"Manual Deploy"** (botão azul no topo direito)
- Selecione **"Deploy latest commit"**
- Confirme

### 3. Aguarde o Deploy

- Tempo estimado: **5-10 minutos** (muitos arquivos)
- Você verá logs em tempo real
- Procure por: `Build successful` e `Live`

### 4. Teste o Resultado

Acesse: <https://bigodetexas-dashboard.onrender.com/checkout>

**O que você deve ver:**

- ✅ Mapa com grid
- ✅ Nomes de cidades (Elektro, Cherno, etc.)
- ✅ Zoom funcional
- ✅ Click para coordenadas

---

## 🤖 Alternativa: Monitor Automático

Se quiser acompanhar automaticamente, rode:

```bash
python monitor_deploy.py
```

O script vai:

- Verificar quando o serviço voltar online
- Confirmar quando os tiles estiverem disponíveis
- Te avisar quando estiver pronto

---

## ⚠️ Se Der Problema

### Deploy Falhou?

- Verifique os logs no Render
- Procure por erros em vermelho
- Tamanho dos tiles pode causar timeout (normal, tente novamente)

### Tiles Não Aparecem?

- Limpe cache: Ctrl + Shift + R
- Verifique console do navegador (F12)
- Confirme que `/static/tiles/0/0/0.png` carrega

---

## 📊 Commits Enviados

- `5e7c03b` - Sistema de fallback
- `d09fdbd` - 5.461 tiles com cidades ← **ESTE**

---

**Tudo pronto do meu lado! Só falta você clicar em "Deploy" no Render.** 🚀
