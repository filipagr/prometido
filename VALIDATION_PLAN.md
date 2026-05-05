# Plano de Validação e Deployment — Prometido

**Data:** 28 abril 2026  
**Estado:** Backend ✅ | Frontend ✅ | DB ✅ | Validação ⏳

---

## 📊 Estado atual

### Database
- **Total:** 5.385 promessas
  - leg_2025: 1.539 (cowork)
  - leg_2024: 1.026 (cowork)
  - leg_2022: 1.557 (cowork)
  - leg_2005: 1.263 (pipeline Arquivo.pt)
- **Validadas:** 539 (10% — apenas leg_2005)
- **Pendentes:** 4.846 (não foram por `validate` step)

### Backend
- ✅ FastAPI app (main.py)
- ✅ SQLite com FTS5
- ✅ 7 routers (search, parties, promises, elections, compare)
- ✅ Teste: todos os endpoints funcionam, dados servem correctamente

### Frontend
- ✅ Next.js 16
- ✅ 6 páginas (homepage, search, compare, party, promise, como-funciona)
- ✅ Compilado (.next/ existe)
- ✅ Ligações à API correctamente configuradas

### Deployment
- ✅ railway.toml (backend)
- ❌ vercel.json (frontend — precisa ser criado/verificado)

---

## 🎯 O que fazer (por prioridade)

### PASSO 1: Validar promessas (1-2 horas)
```bash
cd /Users/filiparibeiro/projects/prometido
python run_pipeline.py --only validate
```

**O que faz:**
- Passa todas as 4.846 promessas por validação automática (Claude Haiku)
- Marca `is_valid = 0/1` e `validation_score` para cada uma
- Rebuild FTS5 index

**Resultado esperado:**
- Todas as promessas com status de validação
- Alguma heterogeneidade (2025 PSD pode ter scores mais altos/baixos que PS, por exemplo)

### PASSO 2: Testar frontend + backend localmente (30 min)
```bash
# Terminal 1: Backend
cd /Users/filiparibeiro/projects/prometido
python -m uvicorn backend.main:app --reload --port 8000

# Terminal 2: Frontend
cd /Users/filiparibeiro/projects/prometido/frontend
npm run dev
# ou: yarn dev

# Abrir: http://localhost:3000
```

**Testes manuais:**
1. Homepage carrega com números correctos (5.385 promessas, 9 partidos, 4 eleições com dados)
2. Procurar "habitação" — resultados aparecem
3. Clicar num partido (ex: PS) — detalhes carregam
4. Clicar numa promessa — detalhes com fonte mostram
5. Comparar — PS vs PSD vs BE por "saúde"
6. Mobile: resize window para 375px (iPhone) — layout funciona

### PASSO 3: Criar vercel.json (10 min)
Se não existir:
```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/.next",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/"
    }
  ]
}
```

### PASSO 4: Configurar variáveis de ambiente para deploy
**Vercel (frontend):**
- `NEXT_PUBLIC_API_URL` = `https://prometido-api.railway.app/api` (ou qual for o URL do Railway)

**Railway (backend):**
- `DATABASE_URL` = local sqlite (já configurado)
- Port: 8000

### PASSO 5: Deploy
**Vercel:**
```bash
# Conectar repo GitHub
# Vercel detecta Next.js e faz build automático
# Deploy: https://prometido.vercel.app
```

**Railway:**
```bash
# Conectar repo GitHub + seleccionar /backend como root
# Deploy: https://prometido-api.railway.app
```

### PASSO 6: Testes finais
1. Testar frontend em production (vercel.app)
2. Testar API em production (railway.app)
3. Verificar CORS (frontend em prometido.vercel.app consegue chamar API em prometido-api.railway.app)
4. Testar em mobile (Chrome DevTools)

---

## ⚠️ Questões abertas / riscos

1. **Validação heterogénea:** As promessas de 2025/2024/2022 podem ter scores de validação muito díspares (esperado). Precisas revisar se há outliers?

2. **Dados históricos 2019-2002:** Ainda não foram extraídos via cowork. Para MVP, estamos com:
   - 2025 ✓
   - 2024 ✓
   - 2022 ✓
   - 2005 ✓
   - 2019-2002: Faltam (decisão: pospor para post-MVP)

3. **CORS em production:** Verifiez que `allow_origins` em `backend/main.py` está correcto:
   ```python
   allow_origins=["http://localhost:3000", "https://prometido.vercel.app"]
   ```

4. **Mobile:** Layout Tailwind foi feito com responsive em mente. Testa em iPhone SE (375px).

---

## 📝 Checklist final

- [ ] Validação pipeline executado (`python run_pipeline.py --only validate`)
- [ ] Backend testa em `localhost:8000` com dados
- [ ] Frontend testa em `localhost:3000` com backend
- [ ] Homepage mostra 5.385 promessas, 9 partidos, 4 eleições
- [ ] Search funciona (test: "habitação")
- [ ] Compare funciona (PS vs PSD vs BE)
- [ ] Promise detail mostra fonte + confidence
- [ ] Mobile layout OK (375px)
- [ ] vercel.json criado/verificado
- [ ] CORS configurado
- [ ] Deploy Vercel
- [ ] Deploy Railway
- [ ] Testar produção

---

## 🚀 Timeline

- **Hoje (28 abril):** Validação + testes locais (2-3 horas)
- **Amanhã (29 abril):** Deploy + testes finais (1 hora)
- **30 abril-6 maio:** Candidatura + vídeo + submissão

**Deadline:** 6 maio, 23:59h
