# Prometido — Project Master Document

## O que é

Uma plataforma web que usa o Arquivo.pt como fonte primária para documentar, pesquisar e confrontar promessas eleitorais de partidos políticos portugueses desde 2002. Cobre todos os partidos com assento parlamentar e todas as eleições legislativas. O utilizador pode pesquisar por tema, partido ou legislatura, comparar o que diferentes partidos prometeram sobre o mesmo tema, e ver a prova arquivada — com link directo para a página original congelada no tempo.

**Tagline:** *O que prometeram. Onde está a prova.*
**Domínio:** prometido.pt

---

## Tese central

O Arquivo.pt é o único lugar onde páginas que já não existem continuam acessíveis. Partidos apagam programas eleitorais depois das eleições. Governos redesenham sites. O arquivo congela o momento. Este projeto usa essa capacidade única para criar o primeiro sistema de accountability político baseado em fontes primárias arquivadas — as próprias páginas dos partidos, corroboradas por cobertura jornalística arquivada.

**Nota:** A verificação de cumprimento (cumprido/não cumprido) está fora do scope do MVP. É genuinamente difícil e subjectiva, e o argumento de candidatura é mais forte sem essa camada: o facto de precisar do Arquivo.pt para aceder a um programa eleitoral de 2019 já demonstra o problema que o Prometido resolve. A verificação de cumprimento é uma feature pós-prémio.

---

## Diferenciação de projetos anteriores

### Memória Política (2023, 3º lugar)
- **O que faz:** Indexa e pesquisa o conteúdo publicado pelos partidos. Motor de pesquisa + sentimento + NER. Biblioteca passiva. Já não está online.
- **O que não faz:** Não identifica promessas. Não compara partidos. Não tem accountability. Não usa notícias como verificação.
- **O nosso projeto vai mais longe:** Ferramenta activa de democracia vs arquivo passivo. Posicionamo-nos explicitamente além dele na candidatura.

### Museu de Promessas Quebradas (Portugal, 2025)
- Curadoria manual, ~20 promessas, sem fonte primária arquivada, sem pesquisa, sem comparação.

### Observa PEC — TI Portugal
- Focado apenas em anti-corrupção, forward-looking, não histórico.

### PolitiFact / Polimeter (internacional)
- Curadoria humana intensiva, requer newsroom permanente, não existem para Portugal, não usam arquivo web.

**Gap real:** Nenhum projeto existente combina promessas eleitorais portuguesas + fontes primárias arquivadas + comparação entre partidos. O nosso é o primeiro.

---

## Hierarquia de fontes (metodologia)

| Tier | Fonte | Uso |
|------|-------|-----|
| 1 | Sites dos partidos — programas eleitorais, press releases | Fonte primária de promessas |
| 2 | Sites de notícias — citações directas entre aspas | Corroboração de promessas |
| ✗ | Artigos que parafraseiam posições | Não usado — risco de atribuição incorrecta |

**Definição operacional de promessa:**
> Declaração verificável com intenção futura explícita, atribuída directamente ao partido ou programa eleitoral, não parafraseada por jornalista.

A interface mostra sempre o tier e um link proeminente para a página original no Arquivo.pt — com o timestamp visível. O utilizador verifica por si.

**Sites de notícias (Tier 3):** Público (prioridade), Expresso, Observador, Jornal de Negócios, RTP, SIC Notícias.

---

## Validação automática em duas passagens

Para tornar o scope completo (9 partidos × 9 eleições) realizável:

**Passo 1 — Extracção:** Claude API extrai promessas candidatas com `extraction_confidence`.

**Passo 2 — Validação:** Segundo prompt avalia: é concreta e verificável? A atribuição é directa? Há contexto suficiente? Resultado: `validation_score`, `is_valid`, `needs_human_review`.

**Curadoria humana:** Apenas casos com `needs_human_review=true` (~30-50) chegam à revisão manual.

Metodologia documentada na candidatura e na página "Como funciona" do site, incluindo exemplo end-to-end e estimativa de taxa de erro.

---

## Sistema de estados de promessas

Framing de documentação, não de julgamento:

| Estado | Atribuição |
|--------|-----------|
| `archived` | Automático — promessa encontrada em fonte primária (PDF ou Arquivo.pt) |
| `corroborated` | Automático — confirmada por citação directa em notícia arquivada |
| `untracked` | Default — sem corroboração adicional |

Verificação de cumprimento (fulfilled/broken/partial) está fora do scope — feature pós-prémio.

---

## UX — momento "wow"

O produto não pode parecer apenas uma base de dados com links. O momento diferenciador é a **feature de comparação**:

> "O que prometeram PS, PSD e BE sobre habitação entre 2015 e 2022?"

Esta feature transforma o produto de ferramenta de pesquisa em ferramenta de análise política. É o que um jornalista usa em véspera de eleições. É o que um cidadão partilha nas redes sociais.

**Link para o Arquivo.pt:** Cada promessa tem um link proeminente e clicável para a página original arquivada — estilizado como badge com timestamp, não escondido como footnote. O utilizador abre a página original numa nova tab e vê a fonte com o wayback toolbar do arquivo visível. Não há iframe ou preview — o link directo é mais credível e mais robusto.

---

## Prémio Arquivo.pt 2026

### Deadline
**6 de maio de 2026 às 23:59h (Lisboa)**

### Submissão requer
1. Descrição do Trabalho — máx. 2000 palavras
2. Vídeo — máx. 3 minutos

### Critérios de avaliação
1. Impacto social — **ponto forte**
2. Originalidade — **ponto forte**
3. Relevância do Arquivo.pt — **ponto forte** (Tier 1 e 2 são do arquivo; PDFs recentes linkados ao arquivo)
4. Qualidade técnica — **ponto forte** (validação em duas passagens, metodologia clara)
5. Grau de maturidade — **médio** (scope ambicioso mas realizável com automação)
6. Impacto científico — **secundário**

### Menção Honrosa Público
Público é Tier 3 prioritário — usar explicitamente na candidatura.

### Júri relevante
- **Pedro Coelho** (Jornalismo) — aprecia o ângulo de accountability e a distinção citação directa vs paráfrase
- **Paulo Nuno Vicente** (Tecnologia) — aprecia a validação em duas passagens e a metodologia de tiers
- **Pedro Vaz Pinto** (Biologia) — menos relevante

---

## Prioridades do projeto

1. **Útil a longo prazo** — ferramenta que jornalistas e cidadãos usam repetidamente
2. **Ganhar o prémio** — MVP funcional e convincente em 2.5 semanas
3. **Aprendizagem pessoal**
4. **Velocidade de execução**

---

## O que NÃO é este projeto

- Não é fact-checking — verificação de cumprimento está fora do scope do MVP
- Não é análise de sentimento ou NLP complexo
- Não é uma plataforma de notícias
- Não cobre eleições presidenciais ou autárquicas no MVP

---

## Público-alvo

1. **Jornalistas** — encontram e comparam promessas com fonte primária arquivada
2. **Cidadãos** — verificam o que foi prometido e comparam entre partidos
3. **Investigadores** — dataset estruturado com metadados completos

---

## Arquivos de referência

- `ARCHITECTURE.md` — stack técnica, data model, pipeline
- `SCOPE.md` — MVP, calendário, custos
- `SUBMISSION.md` — candidatura, estrutura da descrição, vídeo
- `PROGRESS.md` — log de decisões e estado actual
- `data/context/program_sources.md` — origem de cada programa eleitoral
- `data/context/elections_history.md` — histórico eleitoral e quem governou
