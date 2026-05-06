# Arquivo Eleitoral — Descrição Sumária
### Candidatura ao Prémio Arquivo.pt 2026

---

## 1. Introdução e motivação

Em fevereiro de 2005, o Partido Socialista publicou no seu site as *Bases Programáticas* para as eleições legislativas desse ano — um documento de dezenas de páginas com compromissos concretos sobre habitação, saúde, educação, economia. Esse documento já não existe no site atual do PS. O partido redesenhou o seu site, mudou de plataforma, e as páginas antigas desapareceram. O mesmo aconteceu com o PSD, com o Bloco de Esquerda, com o PCP. Em cada ciclo eleitoral, os programas do ciclo anterior tornam-se inacessíveis.

O Arquivo.pt capturou essas páginas. O programa eleitoral do PS de 2005 está acessível em `arquivo.pt/noFrame/replay/20050127000000/http://www.ps.pt/bases/bases_programaticas.pdf` — congelado no momento em que foi publicado, com o timestamp visível, inalterado.

**O Arquivo Eleitoral usa esta capacidade única do Arquivo.pt para criar o primeiro sistema português de documentação e pesquisa de promessas eleitorais baseado em fontes primárias arquivadas.**

O utilizador pesquisa por tema ("habitação", "salário mínimo", "SNS"), por partido, ou por eleição. Para cada promessa encontrada, existe um link directo para a página original no Arquivo.pt — não uma citação jornalística, não uma memória de segunda mão. A própria página do partido, congelada no tempo, com o toolbar do arquivo visível. O utilizador verifica por si.

A feature central do Arquivo Eleitoral é a comparação: "O que prometeram PS, PSD e Bloco de Esquerda sobre habitação entre 2015 e 2022?" — as promessas dos três partidos aparecem lado a lado, cada uma com a sua fonte arquivada. É a ferramenta que um jornalista usa na véspera de eleições. É o que um cidadão partilha nas redes sociais quando quer confrontar um político com o que disse.

---

## 2. Originalidade e posicionamento

Em oito edições do Prémio Arquivo.pt, nenhum projeto focou especificamente promessas eleitorais como objeto de estudo e ferramenta de *accountability* democrático.

O projeto mais próximo, **Memória Política** (2023, 3.º lugar), é um motor de pesquisa de discurso político genérico: indexa e pesquisa conteúdo publicado pelos partidos, com análise de sentimento e reconhecimento de entidades. É uma biblioteca passiva — útil para investigação, mas sem foco em promessas, sem comparação entre partidos, sem verificação de cumprimento, sem *accountability*. O Memória Política já não está online.

O **Museu de Promessas Quebradas** (Portugal, 2025) é curadoria manual de cerca de 20 promessas, sem fonte primária arquivada, sem pesquisa, sem comparação sistemática.

Internacionalmente, ferramentas como o **PolitiFact** (EUA) ou o **Polimeter** (Canadá) dependem de *newsrooms* permanentes com jornalistas dedicados a rever cada promessa manualmente. São caras, lentas, e não existem para Portugal.

O Arquivo Eleitoral resolve o problema de uma forma diferente: em vez de curadoria humana exaustiva, usa o Arquivo.pt como fonte primária e automação (Claude API) para extracção e validação. A curadoria humana fica reservada para os casos ambíguos — uma fracção do total.

**O gap que preenchemos:** nenhum projeto existente combina promessas eleitorais portuguesas + fontes primárias arquivadas + comparação entre partidos + evidência de implementação. É o primeiro.

---

## 3. Metodologia

### Hierarquia de fontes

O Arquivo Eleitoral usa uma hierarquia de três tiers de confiança de fonte, visível na interface para cada promessa:

| Tier | Fonte | Uso |
|------|-------|-----|
| **Tier 1** | Sites oficiais dos partidos — programas eleitorais, press releases | Fonte primária de promessas |
| **Tier 2** | Sites governamentais — programas de governo oficiais | Fonte primária + evidência de implementação |
| **Tier 3** | Sites de notícias — citações directas entre aspas | Corroboração + verificação de cumprimento |

Não usamos artigos que parafraseiam posições partidárias — o risco de atribuição incorrecta é demasiado alto. Incluímos apenas citações directas entre aspas, atribuídas explicitamente ao partido ou ao seu líder.

A definição operacional de promessa: *declaração verificável com intenção futura explícita, atribuída directamente ao partido ou programa eleitoral, não parafraseada por jornalista.* Inclui "vamos criar", "iremos implementar", "comprometemo-nos a". Exclui retórica vaga ("queremos um Portugal melhor") e diagnósticos sobre a situação atual.

### Pipeline técnico

O pipeline corre em sete passos:

**1. Discovery** — A API CDX do Arquivo.pt é consultada por domínio e janela temporal eleitoral (ex: `ps.pt/*` entre dezembro de 2004 e fevereiro de 2005). Para cada eleição legislativa desde 2002, existe uma janela de recolha centrada nas semanas antes da data do acto eleitoral — período de maior cobertura no arquivo.

**2. Fetch** — Para cada URL descoberto, o HTML é obtido via `arquivo.pt/noFrame/replay/` e o texto é extraído com a biblioteca trafilatura, que detecta automaticamente o encoding da página (crucial para páginas antigas em ISO-8859-1).

**3. Extracção (Passo 1)** — Claude API analisa cada página e extrai promessas candidatas com um score de confiança. Textos longos (o programa do PS de 2005 tem 299.000 caracteres) são divididos em segmentos de 8.000 caracteres com sobreposição de 500 caracteres para não perder promessas nos limites.

**4. Validação (Passo 2)** — Um segundo prompt independente avalia cada promessa candidata: é concreta e verificável? A atribuição ao partido é directa? Há contexto suficiente? O resultado inclui `is_valid`, `validation_score`, e `needs_human_review`. Esta segunda passagem é a salvaguarda metodológica central — promessas identificadas com baixa confiança ou contradição entre os dois passos são marcadas para revisão humana.

**5. Curadoria humana** — Apenas as promessas marcadas como `needs_human_review=true` chegam à revisão manual — uma fracção do total (estimativa: 30-50 em centenas). Os restantes casos são resolvidos automaticamente.

**6. Linking** — Artigos de Tier 3 (Público, Expresso, RTP, Observador) são associados a promessas por partido, eleição e tema. Artigos contemporâneos da campanha servem de corroboração; artigos posteriores podem conter evidência de cumprimento ou não-cumprimento.

**7. Indexação** — FTS5 (full-text search nativo do SQLite) é populado para pesquisa instantânea.

### Transparência de limitações

O Arquivo Eleitoral comunica as suas limitações directamente na interface. O Bloco de Esquerda em 2005 é um exemplo: o site `bloco.org` não foi crawlado pelo Arquivo.pt na janela eleitoral desse ano, pelo que não existe fonte Tier 1 disponível. Esta lacuna está documentada na página de partido e na página "Como funciona" — não escondemos o que não sabemos.

### Stack técnica

Python + FastAPI + SQLite (FTS5) no backend. Next.js + Tailwind CSS no frontend. Claude API (claude-sonnet-4-6 para extracção, claude-haiku para validação) para o pipeline de dados. Deploy: Railway (backend) + Vercel (frontend).

---

## 4. Resultados

O Arquivo Eleitoral cobre **9 partidos** nas **9 eleições legislativas de 2002 a 2025** — a cobertura completa do parlamento português nas últimas duas décadas.

| Partido | Promessas |
|---------|-----------|
| PS | 2 785 |
| PAN | 2 322 |
| PSD / AD | 1 331 |
| Chega | 1 314 |
| BE | 1 302 |
| IL | 1 085 |
| PCP | 840 |
| CDS | 723 |
| Livre | 313 |
| **Total** | **12 015** |

Cada promessa está ligada à página original arquivada no Arquivo.pt. Exemplo do programa do PS de 2005 (Bases Programáticas, arquivado a 27 de janeiro de 2005):

> *"O PS compromete-se a aumentar o salário mínimo nacional para 450 euros até ao final da legislatura."*

Fonte: `arquivo.pt/noFrame/replay/20050127000000/http://www.ps.pt/bases/bases_programaticas.pdf` — acessível hoje, como estava em 2005.

---

## 5. Impacto social e científico

### Para jornalistas

Um jornalista que cobre a campanha eleitoral de 2025 pode pesquisar "habitação" e ver, lado a lado, o que PS, PSD, BE e IL prometeram sobre o tema nas últimas nove eleições — com a fonte primária arquivada para cada promessa. O tempo de pesquisa que antes levava horas (procurar programas antigos, verificar se existem no arquivo, ler documentos longos) reduz-se a segundos.

### Para cidadãos

Um cidadão que viu um político na televisão a prometer "construir 50.000 casas" pode verificar se essa promessa foi feita antes, em que contexto, e se há evidência de implementação — tudo com fonte arquivada, verificável, não editável.

### Para investigadores

O dataset estruturado — promessas com partido, eleição, tópico, tier de fonte, score de confiança, e link para o arquivo — é um recurso único para investigação em ciência política, análise de discurso político e comunicação eleitoral. É o tipo de dataset que normalmente requer anos de codificação manual e raramente existe para países fora dos EUA e Reino Unido.

### Sustentabilidade

O Arquivo Eleitoral não depende de uma equipa editorial permanente. O pipeline de extracção pode ser re-executado para novas eleições com configuração mínima. A arquitectura foi desenhada para crescer: suporta todos os partidos com assento parlamentar e todas as eleições desde 2002, com cobertura condicionada pelo que o Arquivo.pt preservou.

---

## 6. Conclusão e próximos passos

O Arquivo Eleitoral demonstra que é possível construir infraestrutura de *accountability* democrático usando o Arquivo.pt como fonte primária e automação para escalar o que antes seria impossível sem uma redacção permanente.

A versão submetida cobre os nove partidos com assento parlamentar e todas as eleições legislativas desde 2002, com metodologia documentada e revisão humana dos casos ambíguos.

O passo seguinte natural é a abertura de uma API pública para investigadores, que permitiria a outros projectos construir sobre este dataset. A médio prazo, a extensão a eleições presidenciais e autárquicas alargaria o âmbito do projecto.

O Arquivo.pt torna possível um tipo de memória democrática que não existia. O Arquivo Eleitoral usa essa memória para criar accountability. *O que prometeram. Onde está a prova.*

---

*Nota sobre o Público:* O Arquivo Eleitoral usa o Público como fonte prioritária de Tier 3 — artigos do Público arquivados são usados tanto para corroboração de promessas (citação directa do partido a prometer) como para verificação de cumprimento (reportagem posterior sobre o que aconteceu). A distinção entre citação directa e paráfrase jornalística, central à metodologia do Arquivo Eleitoral, é particularmente relevante para o jornalismo de qualidade do Público.

---

**Contagem de palavras:** ~1950 palavras
