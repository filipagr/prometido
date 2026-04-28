# Prometido — Candidatura Prémio Arquivo.pt 2026

## Informação da candidatura

- **Formulário:** https://forms.gle/57zWjTFxhirsNAT86 (requer conta Google)
- **Deadline:** 6 de maio de 2026 às 23:59h (Lisboa)
- **Língua:** Português (obrigatório)
- **Responsável:** Filipa [apelido]

### Ficheiros a submeter
1. Descrição Sumária — máx. 2000 palavras, seguir template: https://sobre.arquivo.pt/wp-content/uploads/DescriçãoSumaria-CandidaturaPremioArquivoPT.docx
2. Vídeo — máx. 3 minutos, ver requisitos técnicos: https://sobre.arquivo.pt/pt/colabore/premios-arquivo-pt/requisitos-tecnicos-dos-videos-para-a-candidatura-aos-premios-arquivo-pt/
3. Todos os materiais referenciados têm de estar acessíveis até ao anúncio dos vencedores

---

## Critérios de avaliação e como responder a cada um

### 1. Impacto social
**Argumento principal:** Em democracia, os cidadãos precisam de poder confrontar políticos com o que prometeram. Esse confronto só é possível se as promessas estiverem preservadas, acessíveis, e comparáveis. O Prometido torna isso possível pela primeira vez em Portugal: pesquisa de promessas por tema e partido, comparação lado-a-lado entre partidos, e prova arquivada com link directo para a página original — não em memória jornalística, não em curadoria humana. É infraestrutura democrática.

**Público:** Jornalistas (comparam rapidamente o que diferentes partidos prometeram sobre o mesmo tema), cidadãos (verificam e partilham a prova), investigadores (dataset estruturado sobre discurso político).

**Argumento forte:** O facto de precisar do Arquivo.pt para aceder a um programa eleitoral de 2019 — há apenas 7 anos — demonstra o problema de forma indesmentível. O Prometido não é um projeto de nicho: é uma infraestrutura que devia existir.

### 2. Originalidade
**Argumento:** Em 8 edições do Prémio Arquivo.pt, nenhum projeto focou especificamente em promessas eleitorais como objeto de estudo e ferramenta de accountability. O projeto mais próximo — Memória Política (2023, 3º lugar) — é um motor de pesquisa de discurso político genérico. O Prometido tem um foco específico (promessas verificáveis), uma metodologia de atribuição (hierarquia de tiers), e um ângulo de accountability que nenhum projeto anterior desenvolveu. Internacionalmente, ferramentas equivalentes (PolitiFact, Polimeter) requerem newsrooms permanentes e curadoria humana intensiva. Este projeto automatiza o processo usando o Arquivo.pt como fonte primária.

### 3. Relevância do Arquivo.pt
**Argumento central:** O Arquivo.pt é insubstituível neste projeto — e isso é demonstrável de forma concreta. Partidos apagam e redesenham os seus sites após as eleições. Durante a construção do Prometido, verificámos que:
- O programa eleitoral da IL de 2019 já não existe no site actual do partido — foi recuperado do Wayback Machine
- O programa eleitoral do PAN de 2015 tinha o PDF original com erro 500 no arquivo — o conteúdo foi recuperado de 8 secções do site de campanha arquivado
- Múltiplos programas históricos (PCP 2009, Chega 2022) só existem em versões arquivadas

O Arquivo.pt realiza crawls especiais em períodos eleitorais — a cobertura é particularmente boa precisamente nos momentos mais relevantes para este projeto. Cada promessa no Prometido tem um link directo para a página original arquivada, com timestamp visível. O utilizador não precisa de confiar na nossa extracção — pode verificar a fonte por si.

### 4. Qualidade técnica
**Argumento:** Pipeline automatizado (Python + Claude API) que recolhe, processa e extrai promessas de páginas arquivadas. Validação em duas passagens (Sonnet para extracção, Haiku para validação). Sistema de pesquisa full-text (FTS5). Frontend em Next.js com ligação direta a cada página arquivada. Metodologia de atribuição transparente com fonte visível para cada promessa. Estratégia híbrida: PDFs para eleições recentes, Arquivo.pt para histórico.

### 5. Grau de maturidade
**Argumento honesto:** MVP funcional com [X] promessas de [Y] partidos e [Z] eleições (2002-2025). O projeto está desenhado para crescer — a arquitectura suporta todos os partidos e todas as eleições. A versão submetida é um ponto de partida deliberadamente focado, não um protótipo incompleto. A verificação de cumprimento é a próxima feature — optámos por não a incluir no MVP porque é genuinamente difícil de fazer bem, e um produto honesto é mais valioso que um produto com dados de qualidade duvidosa.

### 6. Impacto científico
**Argumento:** Cria um dataset estruturado de promessas eleitorais portuguesas com metadados (partido, eleição, tópico, tier de fonte, link para arquivo). Útil para investigadores de ciência política, linguística e comunicação política. Potencialmente o maior corpus anotado de promessas eleitorais portuguesas.

---

## Estrutura da descrição (2000 palavras)

### 1. Introdução e motivação (~300 palavras)
- O problema: programas eleitorais desaparecem da web — exemplo concreto com IL 2019
- O Arquivo.pt como solução única e insubstituível
- O que o projeto faz: pesquisa, comparação, prova arquivada

### 2. Originalidade e posicionamento (~300 palavras)
- Diferença do Memória Política (conhecido pelo júri — abordar diretamente)
- Diferença de soluções internacionais (PolitiFact, Polimeter)
- O gap que preenchemos: promessas + fontes primárias + comparação

### 3. Metodologia (~400 palavras)
- Hierarquia de tiers de fontes (Tier 1: partidos, Tier 3: notícias)
- Estratégia híbrida: PDFs recentes + Arquivo.pt histórico
- Pipeline técnico (discovery → fetch → extract → validate → link → serve)
- Validação em duas passagens — como resolvemos o problema de atribuição
- Limitações e como as comunicamos ao utilizador

### 4. Resultados (~300 palavras)
- Números: X promessas, Y partidos, Z eleições
- Exemplos concretos de promessas encontradas
- Screenshots do interface (pesquisa, comparação, detalhe com badge de arquivo)

### 5. Impacto social e científico (~300 palavras)
- Casos de uso: jornalista (véspera de eleições), cidadão (partilha nas redes), investigador (dataset)
- O argumento da acessibilidade: não precisar do Arquivo.pt para aceder a um programa de 7 anos atrás não devia ser excepcional — devia ser o mínimo
- Dataset aberto para investigação

### 6. Conclusão e próximos passos (~200 palavras)
- O que está fora do MVP: verificação de cumprimento (feature pós-prémio), API pública, eleições presidenciais
- Visão a longo prazo: infraestrutura permanente de accountability eleitoral português

---

## Estrutura do vídeo (3 minutos)

### 0:00 - 0:30 — O problema
Mostrar um exemplo concreto: procurar o programa eleitoral da IL de 2019 no site actual — não existe. Mostrar a mesma informação no Arquivo.pt — existe. *"Precisámos do Arquivo.pt para aceder a um programa de há 7 anos."*

### 0:30 - 1:30 — A solução
Demo do produto: pesquisar "habitação" → aparecem promessas de vários partidos e eleições. Clicar no badge do Arquivo.pt → abre a página original do partido, congelada no tempo, com o timestamp visível. Mostrar a feature de comparação: "PS vs PSD vs BE sobre habitação" → vista lado-a-lado.

### 1:30 - 2:15 — A metodologia
Explicar brevemente o sistema de tiers. Mostrar o badge "Tier 1 — Site do Partido". Mostrar a página "Como funciona" — pipeline, validação automática, transparência de fonte.

### 2:15 - 2:45 — O impacto
Caso de uso de um jornalista em véspera de eleições. *"O Prometido é o primeiro sistema de accountability eleitoral português baseado em fontes primárias arquivadas."*

### 2:45 - 3:00 — Call to action
URL do projeto. *"O que prometeram. Onde está a prova."*

---

## Menção Honrosa Jornal Público
Incluir na demo e na descrição: pesquisa de promessas corroboradas pelo Público (Tier 3 — citações directas em artigos do Público arquivados). Mostrar uma promessa com citação direta num artigo do Público como fonte de corroboração.

---

## Checklist final antes de submeter

- [ ] Descrição em português, máx. 2000 palavras
- [ ] Números reais inseridos ([X] promessas, [Y] partidos, [Z] eleições)
- [ ] Vídeo máx. 3 minutos, requisitos técnicos cumpridos
- [ ] URL do projeto acessível publicamente (Vercel)
- [ ] Backend a correr (Railway)
- [ ] Todas as páginas do Arquivo.pt referenciadas estão acessíveis
- [ ] Nome completo e email correto no formulário
- [ ] Submetido antes das 23:59h de 6 de maio (Lisboa)
