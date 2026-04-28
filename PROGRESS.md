# Prometido — Progress Log

## Estado atual
**Fase:** Semana 2 — Deploy feito. A fazer: Railway (backend) + testes em produção.
**Data:** 28 de abril de 2026
**Próximo passo:** `railway login && railway up` → testar em produção → actualizar URL backend no Vercel → vídeo + submissão até 6 maio 23:59h.
**Totais actuais na DB:** 7.549 promessas válidas · 9 partidos · 9 eleições (2002–2025) · 55 combinações partido×eleição.

**URLs de deploy:**
- Frontend (Vercel): https://prometido-app.vercel.app
- Backend (Railway): pendente — `railway login && railway up` no repo raiz

---

## Decisões tomadas

### 18 abril 2026
- **Nome do projeto:** Prometido
- **Tagline:** "O que prometeram. Onde está a prova."
- **Stack:** Python + FastAPI + SQLite + Next.js + Claude API
- **Escopo MVP:** PS, PSD, BE, PCP × eleições 2005, 2009, 2015, 2019
- **Metodologia de tiers:** 3 tiers de confiança de fonte — baked into data model
- **Diferenciação do Memória Política:** accountability ativo vs arquivo passivo — abordar directamente na candidatura
- **Prioridade 1:** utilidade a longo prazo. Prioridade 2: ganhar o prémio.
- **Ferramentas:** Chat (arquitectura/decisões) → Claude Code (build) → Cowork (submissão)

### 19 abril 2026
- **API CDX confirmada:** NDJSON, campo `mime` (não `mimetype`), campo `status` (não `statuscode`), filtro `status:200` funciona
- **Rate limit:** conta nova tem limite baixo — dois processos paralelos causam 429s. Correr um de cada vez.
- **Dry-run PS/2005:** 578 promessas encontradas no bp.htm (299K chars). Passo 2 vai filtrar para ~100-200 concretas.
- **Encoding:** trafilatura com bytes detecta charset automaticamente — acentos portugueses correctos.
- **Model choices:** Sonnet para extracção, Haiku para validação/linking — ~10x diferença de custo.
- **dotenv:** load_dotenv precisa de `override=True` para não ser bloqueado por variáveis de ambiente do sistema.
- **Governing vs opposition:** só partidos que governaram têm promessas verificáveis. Tabela `election_governments` criada. Documentado em `data/context/elections_history.md`.
- **Abordagem híbrida de dados:** Arquivo.pt para partidos históricos (PS/PSD/PCP/BE/CDS 2005-2019) + PDFs directos para partidos recentes e eleições 2022-2025. O link Arquivo.pt serve como evidência de origem mesmo quando a extracção vem do PDF.
- **Cowork para extracção de PDFs:** sem custos de API — Claude lê o PDF directamente e extrai promessas. Script `scripts/import_promises_json.py` insere na DB. Skill `/extract-pdf` criada.
- **Partido CDU:** promessas atribuídas a `party_id = 'PCP'`. Domínio `cdu.pt` já incluído.
- **PSD em coligação:** domínios `adportugal.pt` e `portugalafrente.pt` adicionados. Promessas AD/PàF atribuídas ao PSD.
- **CDS:** removido de eleições onde correu em coligação (2015, 2022, 2024, 2025).
- **PS 2019:** programa eleitoral em `todosdecidem.ps.pt` — domínio adicionado.
- **ADN:** decidido não incluir (2 mandatos, marginal, sem valor para accountability).
- **BE 2025:** só publicou manifesto de 2 páginas, sem programa completo — reflecte escolha do partido.
- **Chega:** incluído com ID `CH`.
- **Livre:** incluído com ID `LV`.

### 20 abril 2026
- **IL 2025:** substituído resumo pelo programa completo (461K chars).
- **AD 2025:** substituído sumário pelo programa completo (560K chars).
- **IL 2024:** PDF encontrado no Wayback Machine (481K chars) — URL original expirada, arquivada em `web.archive.org`.
- **IL 2019:** PDF encontrado no Wayback Machine (30K chars) — alojado em `portugal.liberal.pt` (plataforma de membros), não indexável directamente.
- **PAN 2015:** PDF original não recuperável (status 500 no arquivo). Conteúdo compilado de 8 secções do site de campanha `legislativas2015.pan.com.pt` via Wayback Machine — 207K chars.
- **CDU 2009:** PDF recuperado do Wayback Machine (`pcp.pt/dmfiles/programa-eleitoral-ar2009.pdf`) — 173K chars.
- **CDU 2011:** "Compromisso eleitoral" (não programa completo) — o PCP reutilizou o programa de 2009 e complementou com 6 temas focados na crise/troika. Usar ambos no cowork.
- **Chega 2022:** programa publicado como página web + Programa Político 2021 de fundo. Ambos guardados como `.txt`.
- **Chega 2022 — Programa Político 2021:** recuperado do Wayback Machine (49K chars) — URL original expirada.
- **Fontes guardadas:** `data/context/program_sources.md` — registo completo de origem de cada programa.

---

## Implementado

### Backend Python
- [x] `backend/database.py` — schema SQLite com FTS5, triggers, seed loader, tabela `election_governments`
- [x] `backend/pipeline/discovery.py` — CDX API, Tier 1/2/3, CLI com flags
- [x] `backend/pipeline/fetch.py` — fetch HTML + extracção de texto com trafilatura
- [x] `backend/pipeline/extract.py` — extracção de promessas com Claude Sonnet
- [x] `backend/pipeline/validate.py` — validação automática com Claude Haiku (prompt restritivo)
- [x] `backend/pipeline/link.py` — linking Tier 3 → promessas
- [x] `backend/pipeline/index.py` — rebuild FTS5 + stats
- [x] `backend/main.py` — FastAPI app
- [x] `backend/api/` — 5 routers (search, parties, promises, elections, compare)
- [x] `run_pipeline.py` — orquestrador com `--reset-validation`, normalização de party_ids para uppercase

### Frontend Next.js
- [x] `frontend/` — Next.js 16 + Tailwind
- [x] 6 páginas: homepage, search, compare, party/[id], promise/[id], como-funciona
- [x] 5 componentes: PromiseCard, SourceBadge, StatusBadge, ArchiveLink, SearchBar
- [x] Build TypeScript sem erros ✓

### Infra e scripts
- [x] `vercel.json` + `railway.toml` — deploy config
- [x] `scripts/import_promises_json.py` — importar JSON de cowork para DB
- [x] `scripts/extract_pdf_api.py` — extracção em batch via Claude API (PDFs nativos + pypdf para ficheiros grandes + recuperação de JSON truncado)
- [x] `.claude/commands/extract-pdf.md` — skill `/extract-pdf {PARTIDO} {ANO}`

### Seeds e contexto
- [x] `data/seeds/parties.json` — 9 partidos com domínios corrigidos
- [x] `data/seeds/elections.json` — 9 eleições (2002-2025)
- [x] `data/seeds/election_governments.json` — quem governou em cada eleição
- [x] `data/context/elections_history.md` — referência histórica completa
- [x] `data/context/prompt_extraction.md` — prompt padrão para cowork
- [x] `data/context/program_sources.md` — origem de cada programa (links Wayback, PDFs, sites)

### Candidatura
- [x] `DESCRICAO_SUMARIA.md` — texto corrido ~1950 palavras

---

## Dados — Estado actual

### Programas recolhidos (prontos para cowork)

| Partido | Eleição | Ficheiro | Chars | Fonte |
|---------|---------|---------|-------|-------|
| PS | leg_2002 | PS-leg-2002.pdf | — | ps.pt |
| PS | leg_2005 | PS-leg-2005.pdf | — | ps.pt |
| PS | leg_2009 | PS-leg-2009.pdf | — | ps.pt |
| PS | leg_2011 | PS-leg-2011.pdf | — | ps.pt |
| PS | leg_2015 | PS-leg-2015.pdf | — | ps.pt |
| PS | leg_2019 | PS-leg-2019.pdf | — | ps.pt (todosdecidem.ps.pt) |
| PS | leg_2022 | PS-leg-2022.pdf | — | ps.pt |
| PS | leg_2024 | PS-leg-2024.pdf | — | ps.pt |
| PS | leg_2025 | PS-leg-2025.pdf | — | ps.pt |
| PSD | leg_2002 | PSD-leg-2002.pdf | — | psd.pt |
| PSD | leg_2005 | PSD-leg-2005.pdf | — | psd.pt |
| PSD | leg_2009 | PSD-leg-2009.pdf | — | psd.pt |
| PSD | leg_2011 | PSD-leg-2011.pdf | — | psd.pt |
| PSD | leg_2015 | PaF-leg-2015.pdf | — | portugalafrente.pt (PàF) |
| PSD | leg_2019 | PSD-leg-2019.pdf | — | psd.pt |
| PSD | leg_2022 | PDS-leg-2022.pdf | — | psd.pt |
| PSD | leg_2024 | AD-leg-2024.pdf | — | adportugal.pt (AD) |
| PSD | leg_2025 | AD-leg-2025.pdf | 560K | adportugal.pt (AD) — programa completo |
| BE | leg_2019 | BE-leg-2019.pdf | — | bloco.org |
| BE | leg_2022 | BE-leg-2022.pdf | — | bloco.org |
| BE | leg_2024 | BE-leg-2024.pdf | — | bloco.org |
| BE | leg_2025 | BE-leg-2025.pdf | — | bloco.org — manifesto 2 pág ⚠ |
| CDU | leg_2009 | CDU-leg-2009.pdf | 173K | Wayback Machine (pcp.pt) |
| CDU | leg_2011 | CDU-leg-2011.pdf | 32K | pcp.pt — compromisso eleitoral (complemento ao de 2009) |
| CDU | leg_2015 | PCP-leg-2015.pdf | — | pcp.pt/cdu.pt |
| CDU | leg_2019 | CDU-leg-2019.pdf | — | pcp.pt/cdu.pt |
| CDU | leg_2022 | CDU-leg-2022.pdf | — | pcp.pt/cdu.pt |
| CDU | leg_2025 | CDU-leg-2025.pdf | — | pcp.pt/cdu.pt |
| IL | leg_2019 | IL-leg-2019.pdf | 30K | Wayback Machine (portugal.liberal.pt) |
| IL | leg_2022 | IL-leg-2022.pdf | — | iniciativaliberal.pt |
| IL | leg_2024 | IL-leg-2024.pdf | 481K | Wayback Machine (iniciativaliberal.pt) |
| IL | leg_2025 | IL-leg-2025.pdf | 461K | iniciativaliberal.pt — programa completo |
| CH | leg_2019 | CH-leg-2019.pdf | — | chega.pt |
| CH | leg_2022 | CH-leg-2022.txt | 26K | partidochega.pt (página web) |
| CH | leg_2022 | CH-programa-politico-2021.txt | 49K | Wayback Machine — Programa Político 2021 (fundo) |
| CH | leg_2024 | CH-leg-2024.pdf | — | chega.pt |
| CH | leg_2025 | CH-leg-2025.pdf | — | chega.pt |
| LV | leg_2019 | LV-leg-2019.pdf | — | programa2019.partidolivre.pt |
| LV | leg_2022 | LV-leg-2022.pdf | — | programa2022.partidolivre.pt |
| LV | leg_2024 | LV-leg-2024.pdf | — | partidolivre.pt |
| LV | leg_2025 | LV-leg-2025.pdf | — | partidolivre.pt |
| PAN | leg_2015 | PAN-leg-2015.txt | 207K | Wayback Machine (legislativas2015.pan.com.pt, 8 secções) |
| PAN | leg_2019 | PAN-leg-2019.pdf | — | pan.com.pt |
| PAN | leg_2022 | PAN-leg-2022.pdf | — | pan.com.pt |
| PAN | leg_2024 | PAN-leg-2024.pdf | — | pan.com.pt |
| PAN | leg_2025 | PAN-leg-2025.pdf | — | pan.com.pt |
| CDS | leg_2019 | CDS-leg-2019.pdf | — | cds.pt — última eleição autónoma |

**Total: 46 programas recolhidos** (PDFs + TXTs)

### Extracção completa via API — 28 abril 2026

Todas as eleições extraídas com `scripts/extract_pdf_api.py` (Claude API, PDFs nativos + pypdf para ficheiros grandes).

| Eleição | Promessas | Partidos |
|---------|-----------|---------|
| leg_2002 | 443 | PS (79), PCP (83), PSD (281) |
| leg_2005 | 857 | PS (1263→539 via Arquivo.pt + 74 BE + 82 CDS + 85 PCP + 77 PSD) |
| leg_2009 | 427 | BE (86), CDS (98), PCP (81), PS (88), PSD (74) |
| leg_2011 | 278 | BE (48), CDS (56), PCP (24), PS (72), PSD (78) |
| leg_2015 | 400 | BE (97), PAN (137), PCP (75), PS (18), PSD (73) |
| leg_2019 | 1022 | BE (79), CDS (447), Chega (67), IL (50), Livre (67), PAN (94), PCP (63), PS (83), PSD (72) |
| leg_2022 | 1557 | via cowork |
| leg_2024 | 1026 | via cowork |
| leg_2025 | 1539 | via cowork |

**Total válidas na DB: 7.549 promessas** (is_valid=1, tier 2)

### Observações técnicas da extracção via API (28 abril)
- **`scripts/extract_pdf_api.py`** criado — processa todos os PDFs/TXTs em `data/programs/` em batch
- **PDFs grandes (>10MB):** extraídos com pypdf e divididos em chunks de 60K chars
- **JSON truncado:** recuperação automática dos objectos completos antes do corte
- **PSD 2002:** PDF digitalizado (sem texto seleccionável) — Filipa fez OCR online, PDF substituído (101MB, 298K chars extraídos, 281 promessas)
- **is_valid:** todas as promessas tier 2 marcadas como is_valid=1 (UPDATE em massa + fix no insert)
- **CDS 2002:** sem PDF disponível — ignorado

### Em falta / notas
- CDS leg_2002: sem dados (partido não tinha arquivo digital acessível em 2002)
- PS leg_2015: apenas 18 promessas (PDF pouco denso em promessas concretas com critério 2/4)
- PCP leg_2011: apenas 24 (era compromisso eleitoral, não programa completo)

### Frontend e deploy
- [x] Frontend build sem erros (TypeScript)
- [x] Backend a responder com dados reais (7.549 promessas)
- [x] Commitar `data/prometido.db` no git (commit 6c9e4ab)
- [ ] Deploy Railway (backend + DB) — `railway login && railway up`
- [x] Deploy Vercel (frontend) — https://prometido-app.vercel.app
- [ ] Testar em produção (search, party page, compare)
- [ ] Mobile testing

### Candidatura
- [ ] Atualizar DESCRICAO_SUMARIA.md com números reais (7.549 promessas, 9 partidos, 9 eleições)
- [ ] Vídeo 3 minutos
- [ ] Submissão até 6 maio 23:59h

### Arquivo.pt linking
- [x] `scripts/link_arquivo.py` — 4 camadas: URL exacta → SHA1 → homepage → Wayback
- [x] Todas as 55 combinações partido×eleição ligadas ao Arquivo.pt
- 9 com link directo ao PDF ou página específica do programa
- 46 com homepage do partido na data da eleição (fallback de 3ª camada)
- Ver tabela completa em `data/context/program_sources.md`

---

## Bloqueadores / riscos activos

- **BE 2025:** só manifesto de 2 páginas — poucas promessas extraídas, reflecte escolha do partido.
- **CDU 2011:** não é um programa completo — 24 promessas (compromisso eleitoral).
- **Cumprido/não cumprido:** fora do scope (decisão 20 abril) — ver SCOPE.md.

---

## Log de sessões

### Sessão 1 — 18 abril 2026 (chat claude.ai)
- Brainstorming, research, definição do conceito
- Criação dos ficheiros PROJECT.md, ARCHITECTURE.md, SCOPE.md, SUBMISSION.md, PROGRESS.md
- Scope expandido (9×9), sistema de estados, validação em duas passagens, Tier 3

### Sessão 2 — 19 abril 2026 (Claude Code, tarde)
- Validação de cobertura Arquivo.pt
- Build completo: pipeline Python + FastAPI backend + Next.js frontend
- Deploy config, orquestrador, candidatura

### Sessão 3 — 19 abril 2026 (Claude Code, noite)
- Extract PS/2005 via Arquivo.pt: 1263 candidatas → 539 válidas (prompt restritivo)
- Decisão: governing vs opposition promises — tabela `election_governments`
- Análise eleições Wikipedia: coligações, quem governou 2002-2025
- Seeds actualizados: domínios PSD (AD, PàF), CDS removido de eleições em coligação
- PDFs 2025 analisados: 9 partidos, 3 com problemas (IL resumo, BE manifesto, AD sumário)
- Abordagem híbrida decidida: PDFs para partidos recentes, Arquivo.pt para históricos
- Script `import_promises_json.py` + skill `/extract-pdf` criados
- `data/context/elections_history.md` e `prompt_extraction.md` criados

### Sessão 4 — 20 abril 2026 (Claude Code)
- IL 2025 e AD 2025: substituídos resumos por programas completos
- IL 2024: recuperado do Wayback Machine (481K chars)
- IL 2019: recuperado do Wayback Machine via portugal.liberal.pt (30K chars)
- PAN 2015: compilado de 8 secções do site de campanha via Wayback (207K chars)
- CDU 2009: recuperado do Wayback Machine (173K chars)
- CDU 2011: "compromisso eleitoral" obtido directamente de pcp.pt (32K chars)
- CH 2022: programa web + Programa Político 2021 do Wayback (49K chars)
- `data/context/program_sources.md` criado — registo completo de todas as fontes
- Total: 46 programas recolhidos, prontos para cowork

### Sessão 6 — 28 abril 2026 (Claude Code)
- `scripts/extract_pdf_api.py` criado — extracção em batch via Claude API (PDFs nativos + pypdf + recuperação JSON)
- Todas as eleições 2002–2019 extraídas: 31 PDFs/TXTs → 2.411 promessas novas
- PSD 2002: Filipa fez OCR online, PDF substituído (101MB) → 281 promessas
- Fix `is_valid`: UPDATE em massa de 7010 promessas tier 2 para is_valid=1
- Frontend build confirmado sem erros; backend a responder correctamente
- **Total DB: 7.549 promessas válidas · 9 partidos · 9 eleições**
- Próximo: deploy Railway + Vercel

### Sessão 5 — 21 abril 2026 (Cowork)
- Extracção cowork das 8 eleições 2024: PS (71), PSD/AD (122), BE (169), PCP/CDU (102), Chega (106), IL (72), Livre (141), PAN (243) = **1.026 promessas**
- Topics canónicos aplicados desde o início (prompt restritivo 2/4). Normalização pontual em AD (diversidade/natalidade/transparência → canónicos)
- Import script executado com `python3` do sistema (`.venv` é Mac-Homebrew, broken symlink no Linux sandbox)
- Mapeamento de ficheiros: cópias AD→PSD, CDU→PCP, CH→Chega, LV→Livre antes de importar
- BE 2011: PDF adicionado (190K)
- CDS 2011: pesquisa bloqueada por egress proxy em todos os domínios PT-relacionados; recuperado manualmente pela Filipa
- PROGRESS.md actualizado com secção 2024

### Sessão 7 — 28 abril 2026 (Claude Code)
- `scripts/link_arquivo.py` criado — 4 camadas de ligação ao Arquivo.pt (URL exacta → SHA1 → homepage → Wayback)
- SHA1 match confirmado para: BE/2025, IL/2025, PAN/2025, PCP/2009, PCP/2011, IL/2019, IL/2024, Chega/2022, PAN/2015
- Restantes 46 combinações: homepage do partido na data da eleição
- Commit completo: .gitignore, backend, frontend, DB, scripts → `github.com/filipagr/prometido`
- Frontend deployed: https://prometido-app.vercel.app (Vercel)
- Backend pendente: `railway login && railway up`
