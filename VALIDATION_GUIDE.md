# 🚀 Prometido: Guia de Validação & Testes

**Versão:** 28 abril 2026  
**Estado:** Backend ✅ | Frontend ✅ | DB 5.385 promessas ✅ | Validação ⏳

---

## 📋 Checklist Rápido (ordem de execução)

1. ✅ Criar VALIDATION_PLAN.md ← **feito**
2. ✅ Criar vercel.json ← **feito**
3. ⏳ **Executar validação** (1-2h)
4. ⏳ **Testar localmente** (30 min)
5. ⏳ **Deploy Vercel + Railway** (30 min)
6. ⏳ **Candidatura final** (1h)

---

## 🔧 PASSO 1: Validar Promessas

### Comando
```bash
cd /Users/filiparibeiro/projects/prometido
python run_pipeline.py --only validate
```

### O que acontece
- Claude Haiku valida cada uma das 4.846 promessas não-validadas
- Cada promessa recebe:
  - `is_valid`: 0 ou 1
  - `validation_score`: 0.0 - 1.0
  - `status`: "archived" (padrão)
- FTS5 index é reconstruído
- Esperado: **5-10 min por 1000 promessas** (depende da quota da API)

### Se houver erro
- **Quota de API esgotada?** Esperar e tentar novamente
- **Database locked?** Fechar qualquer outro processo que use a DB
- Logs na consola indicam o progresso

### Verificar resultado
```bash
cd /Users/filiparibeiro/projects/prometido
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('data/prometido.db')
c = conn.cursor()
c.execute("SELECT COUNT(CASE WHEN is_valid=1 THEN 1 END), COUNT(*) FROM promises")
valid, total = c.fetchone()
print(f"✅ {valid} promessas válidas de {total} total ({100*valid//total}%)")
conn.close()
EOF
```

---

## 🖥️ PASSO 2: Testar Localmente

### Terminal 1: Backend
```bash
cd /Users/filiparibeiro/projects/prometido
python -m uvicorn backend.main:app --reload --port 8000
```

**Output esperado:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

**Teste rápido:**
```bash
curl http://localhost:8000/api/health
# {"status":"ok","project":"prometido"}
```

### Terminal 2: Frontend
```bash
cd /Users/filiparibeiro/projects/prometido/frontend
npm run dev
```

**Output esperado:**
```
> dev
> next dev
- ready started server on 0.0.0.0:3000
```

### Abrir no browser
**http://localhost:3000**

### Testes manuais (5 min cada)

#### 1. Homepage
- [ ] Logo + tagline carregam
- [ ] Números aparecem: "5.385 promessas", "9 partidos", "4 eleições"
- [ ] SearchBar funciona (clicável)

#### 2. Procurar "habitação"
- [ ] Clica na search bar
- [ ] Escreve "habitação"
- [ ] Resultados aparecem em < 2s
- [ ] Cada resultado mostra: texto, partido, eleição, confidence

#### 3. Comparar
- [ ] Vai a /compare?topic=habitação
- [ ] Tabela mostra PS, PSD, BE com contagem de promessas
- [ ] Clica num partido → mostra promessas desse partido

#### 4. Detalhe de promessa
- [ ] Clica numa promessa
- [ ] Mostra: texto completo, contexto, fonte, confidence (extraction + validation)
- [ ] Link "Arquivo.pt" é clicável e leva ao arquivo

#### 5. Detalhe de partido
- [ ] Vai a /party/PS
- [ ] Mostra: nome, cor, promessas por eleição
- [ ] Grafo/lista de promessas funciona

#### 6. Mobile (375px)
- [ ] Chrome DevTools: ⌘+⇧+I (Mac) ou F12 (Windows)
- [ ] Clica ☎️ (toggle device)
- [ ] Selecciona "iPhone SE" (375×667)
- [ ] Testa: hero, search, comparar (stack deve ser vertical)

### Se algo não funcionar
1. **Frontend error?** Olha console do browser (F12 > Console)
2. **Backend error?** Olha output do terminal uvicorn
3. **API request falhou?** Verifica CORS em `backend/main.py`

---

## 🌐 PASSO 3: Deploy (Vercel + Railway)

### Pre-requisitos
- Repo GitHub com push de `vercel.json` ← já feito
- Conta Vercel (free tier OK)
- Conta Railway (free tier OK)

### 3a. Deploy Vercel (frontend)
```
1. Vai a vercel.com
2. Clica "New Project" → "Import Git Repository"
3. Selecciona o repo do Prometido
4. Detecção automática: Next.js
5. Environment variables:
   NEXT_PUBLIC_API_URL = https://prometido-api.railway.app/api
6. Clica "Deploy"
```

**Esperado:** Deploy em 2-5 min, URL automática como `https://prometido-XXXX.vercel.app`

### 3b. Deploy Railway (backend)
```
1. Vai a railway.app
2. Clica "New Project" → "Deploy from GitHub"
3. Selecciona o repo do Prometido
4. Configura:
   - Root directory: `/backend` (ou `.`)
   - Start command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
5. Environment:
   - ANTHROPIC_API_KEY = sk-ant-...
   - DATABASE_URL = sqlite:///./data/prometido.db
6. Clica "Deploy"
```

**Esperado:** Deploy em 3-5 min, URL automática como `https://prometido-api-XXX.railway.app`

### 3c. Testar em produção
```bash
# Testar API
curl https://prometido-api-XXX.railway.app/api/health

# Testar frontend
Abre: https://prometido-XXXX.vercel.app
```

### Se CORS falhar
**Erro:** `Access to XMLHttpRequest blocked by CORS`

**Solução em `backend/main.py`:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://prometido-XXXX.vercel.app"  # ← adiciona URL real
    ],
    allow_methods=["GET"],
    allow_headers=["*"],
)
```

Depois faz git push e Railway redeploy automático.

---

## 📄 PASSO 4: Candidatura Final

### Actualizar DESCRICAO_SUMARIA.md
```markdown
# Prometido: O que prometeram. Onde está a prova.

Prometido é uma plataforma de accountability político que rastreia promessas eleitorais 
de partidos portugueses desde 2002.

## Números
- **5.385 promessas** de 9 partidos
- **4 eleições** com cobertura completa (2005, 2022, 2024, 2025)
- **Fonte primária**: Arquivo.pt (archived Portuguese web pages)
- **Validação**: 2 passagens — extracção com Claude Sonnet + validação com Claude Haiku

## Diferenciação
Ao contrário de Memória Política (arquivo passivo), Prometido é ativo:
- Comparação lado-a-lado de promessas por partido/tema/eleição
- Confidence scores para cada promessa (extracção + validação)
- Tier de confiança de fonte (Tier 1: programa original, Tier 3: referência externa)
- UX moderna com busca e filtros

## Tech Stack
- Backend: Python + FastAPI + SQLite (FTS5)
- Frontend: Next.js 16 + TypeScript + Tailwind
- Validation: Claude API (Sonnet + Haiku)
- Infrastructure: Vercel (frontend) + Railway (backend)

[Continuar com histórico, decisões, metodologia...]
```

### Gravar vídeo 3 min
```
1. Abre a app em production
2. Grava screencast com áudio (QuickTime no Mac ou ScreenFlow)
3. Mostra:
   - Homepage com números
   - Procura de "habitação"
   - Comparação PS vs PSD vs BE
   - Detalhe de uma promessa
4. Explica: problema → solução → diferenciação
5. Upload para YouTube (unlisted) ou arquivo local
```

### Submissão
- [ ] Ficheiros na pasta certa
- [ ] DESCRICAO_SUMARIA.md atualizado
- [ ] Vídeo 3 min
- [ ] URL da app (Vercel)
- [ ] URL do GitHub repo (público)
- [ ] Enviar até **6 maio, 23:59h**

---

## 🆘 Troubleshooting

| Problema | Solução |
|----------|---------|
| `ModuleNotFoundError: backend` | `export PYTHONPATH=/Users/filiparibeiro/projects/prometido` |
| `Database is locked` | Fechar outro terminal que usa a DB, ou `rm data/prometido.db-wal` |
| `API_KEY not found` | Verificar `.env` tem `ANTHROPIC_API_KEY` |
| CORS error em produção | Atualizar `allow_origins` em backend + redeploy |
| Frontend mostra "loading..." infinito | Verificar NEXT_PUBLIC_API_URL aponta ao URL correcto de Railway |
| Search não funciona | Verificar FTS5 foi reconstruído (está no passo validate) |

---

## ✅ Checklist Final

Antes de submeter candidatura:

- [ ] Validação completa (python run_pipeline.py --only validate)
- [ ] Backend testa em localhost:8000
- [ ] Frontend testa em localhost:3000
- [ ] Homepage mostra 5.385 promessas
- [ ] Procura funciona
- [ ] Comparar funciona
- [ ] Promise detail funciona
- [ ] Mobile layout OK
- [ ] Deploy Vercel ✓
- [ ] Deploy Railway ✓
- [ ] Testar em produção
- [ ] DESCRICAO_SUMARIA.md atualizado
- [ ] Vídeo 3 min gravado
- [ ] Candidatura submitted

---

## 📞 Dúvidas?

Refer a PROGRESS.md para histórico completo ou VALIDATION_PLAN.md para contexto.
