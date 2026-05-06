# Prometido — Progress Log

## Estado atual
**Fase:** Semana 2 — Deploy completo. A fazer: validação de links Arquivo.pt + correcção BE 2024 + vídeo + submissão.
**Data:** 5 de maio de 2026
**Próximo passo:** corrigir URL arquivada BE 2024 na DB → vídeo 3 min → submissão até 6 maio 23:59h.
**Totais actuais na DB:** 7.549 promessas válidas · 9 partidos · 9 eleições (2002–2025) · 55 combinações partido×eleição.

**URLs de deploy:**
- Frontend (Vercel): https://frontend-rosy-six-72.vercel.app (subdomínio actual, projecto renomeado de `prometido-app` → `frontend`)
- Backend (Render): https://prometido-api.onrender.com (free tier, adormece após 15 min sem tráfego)

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
- [x] Commitar `data/prometido.db` no git
- [x] Deploy Render (backend) — https://prometido-api.onrender.com
- [x] Deploy Vercel (frontend) — https://prometido-app.vercel.app
- [x] CORS configurado para prometido-app.vercel.app
- [ ] Testar em produção (search, party page, compare)
- [ ] Mobile testing

### Candidatura
- [ ] Atualizar DESCRICAO_SUMARIA.md com números reais (7.549 promessas, 9 partidos, 9 eleições)
- [ ] Vídeo 3 minutos
- [ ] Submissão até 6 maio 23:59h

### Arquivo.pt linking
- [x] `scripts/link_arquivo.py` — 4 camadas: URL exacta → SHA1 → homepage → Wayback
- [x] Todas as 56 combinações partido×eleição ligadas ao Arquivo.pt (+ 1 sem dados)
- 45 com PDF específico confirmado no Arquivo.pt
- 10 com página específica do programa ou listagem oficial
- 1 com homepage apenas (CDS 2011 — PDF não encontrado)
- 1 sem dados: CDS 2002
- Ver tabela completa e todos os links em `data/context/program_sources.md`

---

## Bloqueadores / riscos activos

- **BE 2024 — link actualizado (fonte não oficial):** link do Arquivo.pt estava quebrado. Actualizado para URL directo `https://bloco.org/media/PROGRAMA_BLOCO_2024.pdf` com `source_type = 'direct'`.
- **CDS 2009 — URL corrigida:** link anterior (`asnossasrespostas.pdf`) estava errado. Substituído por PDF do programa eleitoral: `https://arquivo.pt/wayback/20091001090903mp_/http://cds.pt/items/programaeleitoralCDS.pdf`. DB actualizada.
- **CDS 2011 — link actualizado (fonte não oficial):** PDF encontrado em tretas.org (`https://tretas.org/Eleições/Legislativas2011?action=AttachFile&do=get&target=2011-05-14_Programa_Eleitoral_do_CDS-PP.pdf`). DB actualizada com `source_type = 'direct'`.
- **CDS 2019 — link actualizado (fonte não oficial):** o Arquivo.pt arquivou a página do programa (`https://arquivo.pt/wayback/20190908015338/https://fazsentido.cds.pt/programa.html`) mas o PDF falha ao carregar. DB actualizada para apontar ao PDF directamente em ephemerajpp.com (`https://ephemerajpp.com/wp-content/uploads/2019/08/programaeleitoral_legislativascds19.pdf`) — está online e em processo de ser arquivado, mas não é o site oficial do CDS.
- **CDS 2002 — link encontrado mas sem promessas na DB:** `https://arquivo.pt/wayback/20091001090732mp_/http://cds.pt/items/ProgramadeGoverno2002.pdf` — pode ser útil no futuro se se quiser extrair promessas de 2002.

#### CDS — fontes históricas (pré-2002, para expansão futura)

Links encontrados no Arquivo.pt para quando se adicionar eleições anteriores ao 25 de Abril / pós-25 de Abril:

| Ano | URL | Notas |
|-----|-----|-------|
| 1999 | https://arquivo.pt/wayback/20091001090839mp_/http://cds.pt/items/ProgramadeGoverno1999.pdf | — |
| 1995 | https://arquivo.pt/wayback/20091001090743mp_/http://cds.pt/items/ProgramadeGoverno1995.pdf | — |
| 1991 | https://arquivo.pt/wayback/20091001090804mp_/http://cds.pt/items/ProgramaEleitoral1991.pdf | — |
| 1987 | https://arquivo.pt/wayback/20091001090914mp_/http://cds.pt/items/ManifestoEleitoral1987.pdf | — |
| 1985 | https://arquivo.pt/wayback/20091001090941mp_/http://cds.pt/items/ProgramadeGoverno1985.pdf | — |
| 1983 | https://arquivo.pt/wayback/20091001090818mp_/http://cds.pt/items/ManifestoEleitoral1983.pdf | — |
| 1980 | https://arquivo.pt/wayback/20110120234815mp_/http://cds.pt/pdf/mo%E7%F5es/programas/Manifesto_Eleitoral_Legislativas_1980_AD_Revisto.pdf | Coligação AD (com PSD e PPM) |
| 1979 | https://arquivo.pt/wayback/20091001090927mp_/http://cds.pt/items/ProgramaEleitoraldeGovernoAD1979.pdf | Coligação AD (com PSD e PPM) |
| 1976 | https://arquivo.pt/wayback/20091001090852mp_/http://cds.pt/items/ManifestoEleitoralCDS_Alternativa76.pdf | Primeira eleição pós-25 de Abril |
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
- Verificação URL-a-URL de todos os 46 programas via CDX (check exacto por URL canónica)
- 22 PDFs específicos confirmados · 20 páginas específicas · 7 homepages · 1 sem dados (CDS 2002)
- `data/context/program_sources.md` actualizado com todos os links e tipo de evidência
- Commit completo: .gitignore, backend, frontend, DB, scripts → `github.com/filipagr/prometido`
- Frontend deployed: https://prometido-app.vercel.app (Vercel)
- Backend pendente: `railway login && railway up`

### Sessão 8 — 29 abril 2026 (Claude Code)
- Arquivo.pt: upgrade massivo de archived_urls para PDFs específicos
  - PS 2002–2019: PDFs directos (ago 2021) · PS 2005: registo tier-2 inserido
  - PSD 2002–2019: PDFs directos (dez 2020) · PSD 2022/2024: PDFs directos
  - BE 2005/2009/2015: PDFs em bloco.org/media/ (abr 2018, via página de documentos)
  - PCP 2015/2019/2024/2025: PDFs directos em pcp.pt
  - CDS 2019: PDF em ephemerajpp.com (jan 2021)
  - Chega 2024/2025: página documentoschega (mar 2024 / dez 2024)
  - CDS 2011: não encontrado (microsite sem PDF)
- **Total final: 45 PDF específico · 10 página · 1 home · 1 sem dados**
- Backend: Railway abandonado (pede cartão) → Fly.io abandonado (pede cartão) → **Render** (grátis, sem cartão)
- Deploy Render: https://prometido-api.onrender.com ✓
- Fix CORS: adicionado prometido-app.vercel.app
- Fix API URL: hardcoded Render URL como fallback em frontend/lib/api.ts
- Dockerfile criado (bake data/ no image) · fly.toml criado (não usado)

### Sessão 10 — 5 maio 2026 (Cowork)

#### UI — fixes e melhorias
- **Bug: partido não aparecia nos cards de pesquisa** — `backend/api/search.py` não incluía `pt.short_name` no SELECT nem no objeto de resposta (só `name` e `color`). Adicionado `pt.short_name as party_short_name` a ambas as queries (FTS5 e filtros directos) e ao dict de resposta.
- **Hover azul nos cards** — texto da promessa ficava `text-blue-700` no hover, o que ficava estranho. Mudado para `text-neutral-900` em `frontend/components/PromiseCard.tsx`.
- **Badge "T2" removido** — retirado `<SourceBadge>` da página de detalhe de promessa (`frontend/app/promise/[id]/page.tsx`). O tier não tem contexto suficiente para o utilizador final. Import limpo.
- **Card de fonte compactado** — o card "FONTE ARQUIVADA" na página de detalhe passou de bloco vertical com três secções empilhadas para uma linha compacta: label + data à esquerda, botão "Abrir no Arquivo.pt" à direita. Padding e texto reduzidos.
- **Homepage reordenada** — ordem das secções alterada para: Partidos → Pesquisar por tema → Comparar por tema (era: Comparar por tema → Partidos → Pesquisar por tema).
- **"Comparar por tema" normalizado** — título passou de `text-sm font-semibold text-neutral-900` para o mesmo estilo das outras secções (`text-[11px] font-semibold text-neutral-600 uppercase tracking-widest`). Subtítulo "O que prometeram os partidos sobre habitação, saúde ou ambiente?" removido.
- **Footer do comparador simplificado** — cards na página `/compare` mostravam ano + status + link Arquivo.pt. `ArchiveLink` removido — fica só ano + status. Import limpo.

#### Discussão de produto
- **Mostrar vencedor das eleições:** proposta de campo `won: boolean` na relação partido×eleição, com indicador visual subtil nos cards e perfil do partido.
- **Verificação de promessas com Arquivo.pt:** plano de usar a API `textsearch` do Arquivo.pt para pesquisar artigos de imprensa arquivados durante o mandato de cada partido, e propor vereditos com LLM + revisão humana. Hierarquia de evidência: DRE (legislação) > imprensa > ausência de cobertura.
- **Diário da República no Arquivo.pt:** confirmado que o Arquivo.pt cobre o DRE — permite verificação via legislação publicada, mais rigorosa que cobertura jornalística.

#### Validação de links Arquivo.pt — IL
- Todos os links verificados e a funcionar correctamente no Arquivo.pt. ✓

#### Validação de links Arquivo.pt — Livre
- Todos os links verificados e a funcionar correctamente no Arquivo.pt. ✓

#### Validação de links Arquivo.pt — PCP
- Todos os links verificados e a funcionar correctamente no Arquivo.pt. ✓

#### Validação de links Arquivo.pt — PSD
- Restantes anos verificados e a funcionar correctamente. ✓
- **2002:** PDF do arquivo.pt dava erro — actualizado para link directo `https://www.psd.pt/sites/default/files/2020-09/programa-eleitoral-2002.pdf` (`source_type = direct`). Arquivo pedido mas ainda não activo: `https://arquivo.pt/wayback/20260506002354/https://www.psd.pt/sites/default/files/2020-09/programa-eleitoral-2002.pdf` — actualizar DB quando estiver disponível.
- **2025:** link directo `https://www.psd.pt/sites/default/files/2025-10/Programa%20Eleitoral%20AD%20Legislativas%202025.pdf` (`source_type = direct`). Arquivo pedido mas ainda não activo: `https://arquivo.pt/wayback/20260506002134/https://www.psd.pt/sites/default/files/2025-10/Programa%20Eleitoral%20AD%20Legislativas%202025.pdf` — actualizar DB quando estiver disponível.

#### Validação de links Arquivo.pt — PS
- **2002, 2005, 2009, 2011, 2015, 2019:** todos actualizados para PDFs directos em `ps.pt/wp-content/uploads/` — estavam a apontar para a página geral de programas.
- **2022, 2024:** actualizados para PDFs directos em `ps.pt/wp-content/uploads/`.
- **2025:** link directo `https://ps.pt/wp-content/uploads/2025/04/programa-eleitoral.pdf` (`source_type = direct`). Arquivo pedido manualmente mas ainda não activo: `https://arquivo.pt/wayback/20260506001450/https://ps.pt/wp-content/uploads/2025/04/programa-eleitoral.pdf` — actualizar DB quando estiver disponível.

#### PS — fontes históricas (pré-2002, para expansão futura)

| Ano | URL |
|-----|-----|
| 1999 | https://arquivo.pt/wayback/20240310124235mp_/https://ps.pt/wp-content/uploads/2021/03/1999.10.out_Programa.do_.Partido.Socialista.e.da_.Nova_.Maioria.para_.a.Legislatura.1999.2003.pdf |
| 1995 | https://arquivo.pt/wayback/20240310124239mp_/https://ps.pt/wp-content/uploads/2024/01/1995-P-Eleitoral-PS-Nova-Maioria_Legislativas_1995_.pdf |
| 1991 | https://arquivo.pt/wayback/20240310124314mp_/https://ps.pt/wp-content/uploads/2021/03/1991.6.out_Programa.de_.Governo.do_.Partido.Socialista_Eleicoes.Legislativas.1991.pdf |
| 1987 | https://arquivo.pt/wayback/20240310124311mp_/https://ps.pt/wp-content/uploads/2021/03/1987.19.jul_Portugal.para_.Todos_Para.um_.Portugal.Moderno.e.Solidario_Programa.para_.um_.Governo.do_.PS_.pdf |
| 1985 | https://arquivo.pt/wayback/20240310124304mp_/https://ps.pt/wp-content/uploads/2021/03/1985.6.out_Um.Pacto_.de_.Progresso.para_.4.anos_.Governo.1985-9.pdf |
| 1983 | https://arquivo.pt/wayback/20240310124259mp_/https://ps.pt/wp-content/uploads/2021/03/1983.25.abr_A.Resposta.PS_.ao_.Portugal.em_.Crise_Manifesto-Programa.pdf |
| 1980 | https://arquivo.pt/wayback/20240310124245mp_/https://ps.pt/wp-content/uploads/2021/03/1980.5.out_Frente.Repub_.Socialista_Prog.p.um_.Governo.da_.FRS_Garantir.o.Futuro.Governar.p.Todos_.pdf |
| 1979 | https://arquivo.pt/wayback/20240310124240mp_/https://ps.pt/wp-content/uploads/2021/03/1979.12.dez_Intercalar_Mudar.em_.Paz_.a.Vida_.Portuguesa_MedidasparaumGovernoPS_PS.o.Direito.a.Liberdade.pdf |
| 1976 | https://arquivo.pt/wayback/20240310124335mp_/https://ps.pt/wp-content/uploads/2021/03/1976.25.abr_Programa.para_.um_.Governo.PS_Vencer.a.Crise_.Reconstruir.o.Pais_.pdf |

#### Validação de links Arquivo.pt — PAN
- **2015:** actualizado para PDF directo (`legislativas2015.pan.com.pt`) — era homepage do microsite.
- **2024:** actualizado para PDF directo (`pan.com.pt/files/...`) — era página de eleições.
- Restantes anos verificados e a funcionar correctamente. ✓

#### Validação de links Arquivo.pt — Chega
- **Chega 2024:** DB aponta para link directo `https://partidochega.pt/wp-content/uploads/2025/10/Programa_Eleitoral_CHEGA_2024_LQ.pdf` (`source_type = direct`). Link do Arquivo.pt pedido mas ainda não disponível: `https://arquivo.pt/wayback/20260505234226/https://partidochega.pt/wp-content/uploads/2025/10/Programa_Eleitoral_CHEGA_2024_LQ.pdf` — actualizar DB quando estiver a funcionar.
- **Chega 2025:** DB aponta para link directo `https://partidochega.pt/wp-content/uploads/2025/10/Programa-Eleitoral-CHEGA-2025.pdf` (`source_type = direct`). Link do Arquivo.pt pedido mas ainda não disponível: `https://arquivo.pt/wayback/20260505234306/https://partidochega.pt/wp-content/uploads/2025/10/Programa-Eleitoral-CHEGA-2025.pdf` — actualizar DB quando estiver a funcionar.

#### Validação de links Arquivo.pt — BE
- Todos os links verificados e a funcionar correctamente. ✓ (excepto 2024 que é link directo — ver secção BE 2024 acima)

- Em curso: verificação manual dos URLs arquivados programa-a-programa.
- **BE:** todos os links do Bloco de Esquerda estão funcionais **excepto BE 2024**.
  - URL problemática: `https://bloco.org/media/PROGRAMA_BLOCO_2024.pdf` — o visualizador de PDF retorna "Failed to load PDF document".
  - URL original do programa está acessível directamente em `https://bloco.org/media/PROGRAMA_BLOCO_2024.pdf`.
  - A verificar: se está arquivada no Arquivo.pt via CDX API (`https://arquivo.pt/wayback/cdx/search/cdx?url=bloco.org/media/PROGRAMA_BLOCO_2024.pdf&output=json&limit=10`). Se não estiver, actualizar `archived_url` na DB para o URL directo.
- **Arquivo.pt não está na allowlist de rede do sandbox** — pesquisa via CDX API tem de ser feita no browser ou adicionando arquivo.pt em Settings → Capabilities.
- **BE 2024 — corrigido:** Filipa arquivou manualmente o PDF no Arquivo.pt (`https://arquivo.pt/wayback/20260505224129/https://bloco.org/media/PROGRAMA_BLOCO_2024.pdf`). DB actualizada via SQL (`archived_pages` — 1 row). ⚠ Confirmar que o PDF abre correctamente antes da submissão.

### Sessão 9 — 29 abril 2026 (Cowork)
- **Bug:** site mostrava "Não foi possível carregar os dados" — todos os pedidos à API bloqueados por CORS.
- **Causa raiz:** projecto na Vercel foi renomeado de `prometido-app` → `frontend`, com novo subdomínio `frontend-rosy-six-72.vercel.app`. A whitelist do CORS no backend só tinha `prometido-app.vercel.app` explícito.
- **Fix:** adicionado `allow_origin_regex=r"https://([a-z0-9-]+\.)*vercel\.app"` em `backend/main.py` para cobrir qualquer subdomínio `*.vercel.app` (incluindo previews `frontend-*-filipagrs-projects.vercel.app`).
- **Deploy:** commit + push → Render auto-deploy → confirmado live no novo URL.
- **Lição:** mudar o nome do projecto na Vercel rebenta o subdomínio anterior. Para evitar no futuro: comprar um custom domain (o `prometido.pt` já não está disponível) e apontá-lo à Vercel, em vez de depender do `*.vercel.app` gerado automaticamente.
- **Nota:** `https://prometido.pt` continua na whitelist explícita do CORS em `backend/main.py` por inércia — o domínio não está registado, é inofensivo mas pode ser removido ou substituído pelo domínio que vier a ser comprado.
