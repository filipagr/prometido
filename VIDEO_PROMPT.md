# Prompt — Ajuda a criar o vídeo do Arquivo Eleitoral

## Contexto do projeto

Estou a candidatar o **Arquivo Eleitoral** ao Prémio Arquivo.pt 2026. O Arquivo Eleitoral é a primeira base de dados de promessas eleitorais portuguesas — pesquisável, comparável, com ligação directa aos programas originais arquivados.

**URL:** arquivoeleitoral.pt  
**Tagline:** *O que prometeram. Onde está a prova.*

**O que faz:**
- Indexa 12 015 promessas de 9 partidos em 9 eleições legislativas (2002–2025)
- Cada promessa tem link directo para a página original no Arquivo.pt — com timestamp visível, inalterada
- O utilizador pode pesquisar por tema ("habitação", "SNS", "salário mínimo"), filtrar por partido e eleição, e comparar o que diferentes partidos prometeram sobre o mesmo tema lado a lado

**O problema que resolve:**
Partidos apagam os seus programas eleitorais quando redesenham o site. O programa da Iniciativa Liberal de 2019 já não existe no site actual do partido — foi recuperado do Arquivo.pt. O programa do PAN de 2015 tinha o PDF com erro 500 no servidor original — recuperado de 8 secções arquivadas do microsite de campanha. O Arquivo Eleitoral usa esta capacidade única do Arquivo.pt para tornar os programas eleitorais acessíveis, pesquisáveis e comparáveis pela primeira vez em Portugal.

**Tecnologia:** Python + FastAPI + SQLite (FTS5) + Next.js + Claude API para extracção automática + revisão humana dos casos ambíguos.

---

## O vídeo

**Duração:** máximo 3 minutos  
**Língua:** Português (obrigatório — é um requisito da candidatura)  
**Audiência:** Júri do Prémio Arquivo.pt — pessoas familiarizadas com o Arquivo.pt e com o seu valor para a preservação da memória digital portuguesa  
**Tom:** Sério, cívico, acessível. Não é um pitch de startup. É uma ferramenta democrática.  
**Formato esperado:** Demo do produto com narração em voz-off + texto sobreposto nos momentos-chave

---

## Storyboard (já definido — preciso de ajuda a executar)

### 0:00 – 0:30 — O problema

Mostrar: abrir o site actual da Iniciativa Liberal → tentar aceder ao programa eleitoral de 2019 → não existe (ou não encontra).  
Mostrar: a mesma informação no Arquivo.pt — o PDF existe, com o toolbar do arquivo visível, com a data de captura.  
Narração: *"Para aceder ao programa eleitoral de um partido de há apenas 7 anos, precisamos do Arquivo.pt. O que foi prometido desaparece. O Arquivo guarda."*

### 0:30 – 1:30 — A solução (demo do produto)

Mostrar o Arquivo Eleitoral:
1. Pesquisar "habitação" → aparecem promessas de vários partidos e eleições, com badges de partido e ano
2. Clicar numa promessa → página de detalhe com contexto + badge "Arquivo.pt" com link + data de captura
3. Clicar no badge → abre a página original do partido no Arquivo.pt, congelada no tempo  
4. Feature de comparação: seleccionar PS + PSD + BE + "habitação" → vista lado-a-lado das promessas dos três partidos

Narração: *"O Arquivo Eleitoral permite pesquisar, comparar e verificar o que cada partido prometeu — com a prova arquivada para cada promessa."*

### 1:30 – 2:15 — A metodologia (brevemente)

Mostrar a página "Como funciona" do site.  
Mencionar: pipeline automático com IA, validação em duas passagens, revisão humana dos casos ambíguos, hierarquia de tiers de fontes.  
Narração: *"12 015 promessas. 9 partidos. 9 eleições. 2002 a 2025. Extraídas dos programas originais, validadas, e ligadas às páginas arquivadas."*

### 2:15 – 2:45 — O impacto

Caso de uso concreto: um jornalista na véspera de eleições que pesquisa "saúde" e vê, lado a lado, o que PS, PSD e BE prometeram sobre o tema nas últimas quatro eleições.  
Narração: *"É a ferramenta que um jornalista usa na véspera de eleições. É o que um cidadão partilha quando quer confrontar um político com o que disse. É infraestrutura democrática."*

### 2:45 – 3:00 — Call to action

Mostrar o URL do site.  
Texto final em ecrã: **"O que prometeram. Onde está a prova."**  
URL: **arquivoeleitoral.pt**

---

## O que tenho disponível

- O site em produção (arquivoeleitoral.pt) — posso fazer screen recordings de qualquer fluxo
- Dados reais: 12 015 promessas, pesquisa funcional, comparação funcional, links para o Arquivo.pt a funcionar
- Exemplos concretos de promessas para usar na demo:
  - "Assegurar às famílias o regresso do IVA Zero nos produtos essenciais do cabaz alimentar" (PS 2025)
  - "Reduzir em pelo menos 20% o IUC dos veículos até média cilindrada" (PS 2025)
  - Promessas de habitação do PS, PSD e BE em múltiplas eleições para a feature de comparação

---

## O que preciso de ti

**Ajuda-me a:**

1. **Roteiro completo com narração** — texto exacto de cada faixa de narração (em português), sincronizado com o storyboard acima. Tom: directo, cívico, sem hipérbole.

2. **Guião de gravação de ecrã** — lista precisa dos passos a executar no site para cada segmento, com o que mostrar em cada momento (que página abrir, que pesquisa fazer, em que elemento clicar, quanto tempo mostrar cada coisa).

3. **Texto para sobreposições / intertítulos** — frases curtas para aparecer sobrepostas no ecrã nos momentos-chave (ex: "12 015 promessas. 9 partidos. 9 eleições.").

4. **Sugestões de ritmo e edição** — onde fazer cortes, onde usar slow-motion ou zoom-in, onde usar música (ou silêncio).

5. **Sugestões de música de fundo** — que tipo de música usar, onde pode ser encontrada (royalty-free), como deve variar ao longo do vídeo.

**Restrições:**
- Máximo 3 minutos (180 segundos)
- Em português — toda a narração, todo o texto sobreposto
- Sem animações elaboradas — o produto fala por si, a edição deve ser limpa e directa
- Sem voz sintética — a narração será gravada por mim

---

## Referências de tom e estilo

Não é um vídeo de startup com música energética e cuts rápidos. É mais próximo de um vídeo de produto de uma ferramenta de jornalismo — como os vídeos de apresentação do NYT Wirecutter, do Pudding, ou do trabalho do ProPublica. Sóbrio, confiante, com substância.

A emoção do vídeo não é "isto é incrível" — é "isto devia existir, e agora existe".
