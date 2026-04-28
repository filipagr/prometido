# Prometido — Architecture

## Stack decision

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Backend | Python + FastAPI | Melhor ecosistema para data pipelines e NLP em português |
| Database | SQLite (dev) → PostgreSQL (prod) | Simples para MVP, escalável depois |
| Frontend | Next.js + Tailwind | Rápido de construir, SEO friendly, bom para visualizações |
| NLP | Claude API (claude-sonnet-4-6) | Extracção + validação em duas passagens — mais fiável que modelos open-source para português |
| Hosting | Vercel (frontend) + Railway (backend) | Deploy simples, gratuito para MVP |
| Archive API | Arquivo.pt REST API | Full-text search + URL version history + page fetch |

---

## Arquivo.pt API — endpoints relevantes

```
# Full-text search com filtro de data e site
GET https://arquivo.pt/textsearch
  ?q=<termo>
  &siteSearch=<dominio>          # ex: ps.pt, psd.pt
  &from=<YYYYMMDD>               # ex: 20010101
  &to=<YYYYMMDD>
  &maxItems=50
  &prettyPrint=true

# Versões arquivadas de um URL específico
GET https://arquivo.pt/textsearch
  ?versionHistory=<url>
  &from=<YYYYMMDD>
  &to=<YYYYMMDD>

# Fetch de página arquivada (conteúdo HTML)
GET https://arquivo.pt/noFrame/replay/<timestamp>/<url>

# CDX API — lista de URLs arquivados por domínio (preferir esta para discovery)
GET https://arquivo.pt/wayback/cdx/search/cdx
  ?url=<dominio>/*
  &output=ndjson
  &filter=status:200
  &fl=timestamp,original,mime
  &from=<YYYYMMDD>
  &to=<YYYYMMDD>
```

**Nota:** `textsearch` estava em baixo em abril 2026 — usar CDX API para discovery.
**Cobertura importante:** O Arquivo.pt faz crawls especiais em períodos eleitorais — election-adjacent content é melhor coberto que o normal.

---

## Domínios alvo (Tier 1 e Tier 3)

```python
# Tier 1 — sites dos partidos (fonte primária directa)
# Domínios actualizados com subdomínios de campanha e coligações
PARTY_DOMAINS = {
    "PS":    ["ps.pt", "partido-socialista.pt", "todosdecidem.ps.pt"],
    "PSD":   ["psd.pt", "ppd-psd.pt", "adportugal.pt", "portugalafrente.pt"],
    "BE":    ["bloco.org", "blockesquerda.net"],
    "PCP":   ["pcp.pt", "cdu.pt"],
    "CDS":   ["cds.pt", "partido-cds.pt"],
    "IL":    ["iniciativaliberal.pt", "liberal.pt", "legislativas2024.liberal.pt"],
    "Chega": ["chega.pt"],
    "Livre": ["partidolivre.pt", "programa2019.partidolivre.pt", "programa2022.partidolivre.pt"],
    "PAN":   ["pan.com.pt"],
}

# Tier 3 — sites de notícias (corroboração de promessas)
# Uso: artigos com citação directa do político a fazer a promessa
NEWS_DOMAINS = {
    "Público":            "publico.pt",       # prioridade — Menção Honrosa
    "Expresso":           "expresso.pt",
    "Observador":         "observador.pt",
    "Jornal de Negócios": "jornaldenegocios.pt",
    "RTP":                "rtp.pt",
    "SIC Notícias":       "sicnoticias.pt",
}
```

**Nota sobre coligações:**
- PàF (2015): PSD+CDS — promessas atribuídas ao PSD
- AD (2024, 2025): PSD+CDS — promessas atribuídas ao PSD
- CDU (todas): PCP+Verdes — promessas atribuídas ao PCP

---

## Janelas temporais de recolha

Focar nas semanas antes de cada eleição legislativa (melhor cobertura no arquivo):

| Eleição | Data | Janela de recolha |
|---------|------|-------------------|
| Leg 2002 | Mar 2002 | 2001-12 a 2002-03 |
| Leg 2005 | Feb 2005 | 2004-12 a 2005-02 |
| Leg 2009 | Sep 2009 | 2009-07 a 2009-09 |
| Leg 2011 | Jun 2011 | 2011-04 a 2011-06 |
| Leg 2015 | Oct 2015 | 2015-08 a 2015-10 |
| Leg 2019 | Oct 2019 | 2019-08 a 2019-10 |
| Leg 2022 | Jan 2022 | 2021-11 a 2022-01 |
| Leg 2024 | Mar 2024 | 2024-01 a 2024-03 |
| Leg 2025 | Mai 2025 | 2025-03 a 2025-05 |

**Nota:** IL, Chega, PAN e Livre têm histórico mais curto — só aparecem nas eleições em que já existiam.

---

## Data model

```sql
-- Partido político
CREATE TABLE parties (
    id          TEXT PRIMARY KEY,   -- "PS", "PSD", etc.
    name        TEXT NOT NULL,
    color       TEXT,               -- hex, para UI
    founded     DATE,               -- para saber desde quando têm histórico
    domains     TEXT                -- JSON array de domínios
);

-- Evento eleitoral
CREATE TABLE elections (
    id          TEXT PRIMARY KEY,   -- "leg_2005", "leg_2009", etc.
    type        TEXT,               -- "legislativas"
    date        DATE NOT NULL,
    description TEXT
);

-- Quem governou em cada eleição
CREATE TABLE election_governments (
    election_id TEXT REFERENCES elections(id),
    party_id    TEXT REFERENCES parties(id),
    role        TEXT NOT NULL,  -- 'prime_minister' | 'coalition_partner' | 'confidence_supply'
    PRIMARY KEY (election_id, party_id)
);

-- Página arquivada (raw)
CREATE TABLE archived_pages (
    id              TEXT PRIMARY KEY,   -- hash do URL + timestamp
    url             TEXT NOT NULL,
    archived_url    TEXT NOT NULL,      -- link para arquivo.pt/wayback/... ou web.archive.org/...
    timestamp       DATETIME NOT NULL,
    party_id        TEXT REFERENCES parties(id),
    election_id     TEXT REFERENCES elections(id),
    raw_text        TEXT,
    tier            INTEGER,            -- 1 ou 3
    crawled_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Promessa extraída
CREATE TABLE promises (
    id                  TEXT PRIMARY KEY,
    page_id             TEXT REFERENCES archived_pages(id),
    party_id            TEXT REFERENCES parties(id),
    election_id         TEXT REFERENCES elections(id),
    text                TEXT NOT NULL,      -- a promessa em si
    context             TEXT,               -- frase anterior/seguinte para contexto
    topic               TEXT,               -- "habitação"|"saúde"|"educação"|etc.
    tier                INTEGER,            -- herdado da página
    -- Passo 1 (extracção)
    extraction_confidence   REAL,           -- 0.0 a 1.0
    extraction_model        TEXT,           -- "claude-sonnet-4-6" ou "manual-cowork"
    -- Passo 2 (validação)
    validation_score        REAL,           -- 0.0 a 1.0
    is_valid                BOOLEAN,        -- resultado da validação automática
    needs_human_review      BOOLEAN,        -- true se confiança baixa ou conflito entre passos
    -- Estado
    status          TEXT DEFAULT 'untracked',
                                            -- archived | corroborated | untracked
    -- Metadata
    extracted_at        DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Fontes de corroboração (Tier 3)
CREATE TABLE verification_sources (
    id              TEXT PRIMARY KEY,
    promise_id      TEXT REFERENCES promises(id),
    archived_url    TEXT NOT NULL,      -- link arquivo.pt para o artigo
    source_domain   TEXT,               -- "publico.pt", "expresso.pt", etc.
    source_date     DATE,
    use_type        TEXT DEFAULT 'corroboration',  -- apenas "corroboration" no MVP
    quote           TEXT,               -- citação directa relevante do artigo
    added_by        TEXT DEFAULT 'pipeline'
);

-- Índice de pesquisa full-text (SQLite FTS5)
CREATE VIRTUAL TABLE promises_fts USING fts5(
    text,
    topic,
    content=promises,
    content_rowid=rowid
);
```

---

## Pipeline de dados

```
1. DISCOVERY
   arquivo.pt CDX API → busca por domínio + janela temporal eleitoral
   Domínios: Tier 1 (partidos) + Tier 3 (notícias)
   Output: lista de URLs arquivados relevantes por tier

2. FETCH
   Para cada URL → fetch HTML da página arquivada
   Limpar HTML → texto limpo (trafilatura)
   Output: archived_pages table

3. EXTRACÇÃO — Passo 1 (Claude API ou cowork)
   Para páginas Tier 1 → extrair promessas candidatas
   Para páginas Tier 3 → extrair citações directas
   Cowork: para PDFs — Claude lê directamente, output JSON → import_promises_json.py
   Output: promises table (status=untracked), verification_sources table

4. VALIDAÇÃO — Passo 2 (Claude Haiku)
   Para cada promessa extraída no passo 3:
   → É realmente uma promessa concreta e verificável (não retórica vaga)?
   → A atribuição é directa ao partido ou mediada?
   → Há contexto suficiente?
   Output: validation_score, is_valid, needs_human_review por promessa
   Promessas com is_valid=false são filtradas da interface

5. CURADORIA HUMANA
   Rever apenas promessas com needs_human_review=true (~30-50)
   Confirmar ou rejeitar a classificação do modelo

6. LINKING
   Ligar verification_sources a promises por similaridade semântica
   Actualizar status: untracked → corroborated (se Tier 3 confirma)
   Actualizar status: untracked → archived (se fonte primária confirmada)

7. INDEXING
   Popular FTS5 index
   Calcular stats por partido/eleição/tópico

8. SERVE
   FastAPI endpoints → Next.js frontend
```

---

## Estratégia híbrida de dados

| Fonte | Quando usar | Como linkar ao arquivo |
|-------|-------------|----------------------|
| PDF directo (download) | Partidos recentes (IL, CH, LV, PAN, BE) e eleições 2022-2025 | Link para URL do Arquivo.pt ou Wayback Machine onde o PDF foi arquivado |
| Arquivo.pt CDX | Partidos históricos (PS, PSD, PCP, CDS) 2005-2019 | Link directo para página arquivada |
| Wayback Machine | PDFs não disponíveis no Arquivo.pt | Link para web.archive.org com timestamp |
| Cowork | Extracção de PDFs sem custo de API | extraction_model = "manual-cowork" |

Ver `data/context/program_sources.md` para origem de cada programa.

---

## Prompts Claude API

### Passo 1 — Extracção

```python
EXTRACTION_PROMPT = """
És um analista político a trabalhar com páginas web arquivadas de partidos políticos portugueses.

Contexto:
- Partido: {party_name}
- Data da página: {page_date}
- Eleição relevante: {election}
- Tier da fonte: {tier} (1=site do partido)

Texto da página:
{page_text}

Tarefa:
Identifica todas as promessas eleitorais concretas e verificáveis neste texto.
Uma promessa é uma afirmação prospetiva de uma ação ou resultado que pode ser verificado.
Ignora retórica vaga ("queremos um Portugal melhor") — inclui apenas compromissos específicos.

Para cada promessa, devolve JSON:
{
  "text": "a promessa exata, nas palavras do documento",
  "context": "frase antes e depois para contexto",
  "topic": "habitação|saúde|educação|economia|emprego|ambiente|segurança|justiça|outros",
  "confidence": 0.0 a 1.0,
  "is_direct_quote": true/false
}

Devolve apenas JSON array. Se não houver promessas concretas, devolve [].
"""
```

### Passo 2 — Validação

```python
VALIDATION_PROMPT = """
És um revisor de qualidade de dados políticos. Vais avaliar se uma promessa eleitoral
extraída automaticamente é válida e bem atribuída.

Promessa a avaliar:
- Texto: {promise_text}
- Contexto: {promise_context}
- Partido: {party_name}
- Data: {page_date}
- Tier da fonte: {tier}
- Confiança da extracção: {extraction_confidence}

Avalia com base em:
1. É uma promessa concreta e verificável? (não retórica vaga)
2. A atribuição ao partido é directa? (não parafraseada por jornalista)
3. O contexto é suficiente para compreender a promessa?
4. Há risco de ser tirada fora de contexto?

Devolve JSON:
{
  "is_valid": true/false,
  "validation_score": 0.0 a 1.0,
  "needs_human_review": true/false,
  "reason": "explicação breve se is_valid=false ou needs_human_review=true"
}
"""
```

---

## Estrutura de ficheiros

```
prometido/
├── PROJECT.md
├── ARCHITECTURE.md
├── SCOPE.md
├── SUBMISSION.md
├── PROGRESS.md
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── pipeline/
│   │   ├── discovery.py    ← Arquivo.pt CDX API
│   │   ├── fetch.py        ← HTML fetch + clean (trafilatura)
│   │   ├── extract.py      ← Passo 1: extracção de promessas
│   │   ├── validate.py     ← Passo 2: validação automática (Haiku)
│   │   ├── link.py         ← Linking Tier 3 → promessas
│   │   └── index.py        ← FTS5 indexing
│   ├── api/
│   │   ├── search.py
│   │   ├── parties.py
│   │   ├── promises.py
│   │   ├── elections.py
│   │   └── compare.py
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx            ← homepage / search
│   │   ├── promise/[id]/       ← detalhe da promessa
│   │   ├── party/[id]/         ← overview do partido
│   │   ├── compare/            ← comparação de partidos por tema
│   │   └── como-funciona/      ← metodologia
│   ├── components/
│   │   ├── SearchBar.tsx
│   │   ├── PromiseCard.tsx
│   │   ├── SourceBadge.tsx     ← Tier 1/3
│   │   ├── StatusBadge.tsx     ← archived | corroborated | untracked
│   │   ├── ArchiveLink.tsx     ← badge com timestamp + link para arquivo.pt
│   │   └── CompareView.tsx     ← comparação lado-a-lado
│   └── package.json
│
├── scripts/
│   └── import_promises_json.py ← importar JSON de cowork para DB
│
├── data/
│   ├── seeds/
│   │   ├── parties.json            ← 9 partidos com domínios
│   │   ├── elections.json          ← 9 eleições legislativas 2002-2025
│   │   └── election_governments.json ← quem governou em cada eleição
│   ├── programs/                   ← PDFs e TXTs por ano/partido
│   │   ├── 2002/, 2005/, ..., 2025/
│   └── context/
│       ├── elections_history.md    ← referência histórica
│       ├── prompt_extraction.md    ← prompt para cowork
│       └── program_sources.md      ← origem de cada programa
│
└── .claude/
    └── commands/
        └── extract-pdf.md          ← skill /extract-pdf {PARTIDO} {ANO}
```

---

## API endpoints (FastAPI)

```
GET /api/search
  ?q=<termo>
  &party=<PS|PSD|...>
  &election=<leg_2005|...>
  &topic=<habitação|...>
  &tier=<1|3>
  &status=<archived|corroborated|untracked>
  → lista de promises com metadata e link para arquivo

GET /api/parties
  → lista de partidos com contagem de promessas e eleições cobertas

GET /api/party/{id}
  → partido + promessas por eleição + breakdown de tópicos

GET /api/promise/{id}
  → promessa completa + página original arquivada + verification_sources

GET /api/elections
  → lista de eleições cobertas com stats

GET /api/compare
  ?topic=<habitação|saúde|...>
  &parties=<PS,PSD,BE>
  &election=<leg_2019|...>    # opcional — se omitido, mostra todas
  → promessas agrupadas por partido para o mesmo tema
```

---

## Decisões técnicas tomadas

- **Validação em duas passagens** — self-consistency check com prompts diferentes. Metodologicamente defensável e mencionável na candidatura.
- **needs_human_review** — só os casos ambíguos chegam à curadoria humana (~30-50 em vez de 300-500). Torna o scope completo realizável.
- **Cowork para PDFs** — extracção via Claude sem custo de API. extraction_model = "manual-cowork".
- **Cumprido/não cumprido fora do scope** — verificação é difícil e subjectiva; o valor está na acessibilidade e comparação.
- **SQLite para MVP** — simples, zero config. Migrar para PostgreSQL se o projeto crescer.
- **FTS5** — full-text search nativo do SQLite, suficiente sem Elasticsearch.
- **Next.js** — SEO importante para jornalistas encontrarem o site.
- **Tier system** — baked into data model desde o início. Diferenciação metodológica chave.

---

## Riscos técnicos

| Risco | Probabilidade | Mitigação |
|-------|--------------|-----------|
| Cobertura fraca para partidos mais recentes (Chega, IL, Livre) | Resolvido | PDFs obtidos directamente + Wayback Machine |
| Cobertura fraca para eleições pré-2005 | Média | Testar via Arquivo.pt CDX; documentar limitações |
| Passo 2 de validação com precision baixa | Baixa | Validar com amostra manual; ajustar prompt |
| Custo Claude API acima do estimado | Baixa | Cap de $40 — extracção PDF via cowork não tem custo |

---

## Ambiente de desenvolvimento

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Pipeline
.venv/bin/python3 run_pipeline.py --parties PS --elections leg_2005
.venv/bin/python3 run_pipeline.py --only validate --parties PS --elections leg_2005

# Importar JSON de cowork
.venv/bin/python3 scripts/import_promises_json.py data/programs/2025/PS-leg-2025.json

# Variáveis de ambiente necessárias
ANTHROPIC_API_KEY=...
DATABASE_URL=sqlite:///./prometido.db
```
