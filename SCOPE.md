# Prometido — Scope

## Deadline
**6 de maio de 2026** — 2.5 semanas a partir de 18 de abril

## MVP (o que tem de estar pronto para o prémio)

### Dados
- [ ] **Todos os partidos com assento parlamentar:** PS, PSD, BE, PCP, CDS, IL, CH (Chega), PAN, LV (Livre)
- [ ] **Todas as eleições legislativas desde 2002:** 2002, 2005, 2009, 2011, 2015, 2019, 2022, 2024, 2025
- [x] Fonte primária: PDFs dos programas (Tier 2) — cowork por partido/ano com skill `/extract-pdf`
- [x] Fonte histórica: Arquivo.pt (Tier 1) — para PS/PSD/PCP/BE/CDS 2005-2019
- [x] Fonte de corroboração: sites de notícias arquivados (Tier 3) — pipeline implementado
- [x] Validação automática com Claude Haiku (prompt restritivo) — validate.py implementado
- [ ] Curadoria humana dos casos ambíguos (needs_human_review)

### Estratégia de dados por partido
- **PS, PSD, PCP/CDU, BE, CDS** (partidos históricos): PDFs disponíveis para 2002-2025 + Arquivo.pt como evidência de origem
- **IL, CH, LV, PAN** (partidos recentes): PDFs para as eleições em que participaram + Arquivo.pt como evidência
- **Governing vs opposition:** documentado em `data/context/elections_history.md`. Usado para contextualizar as promessas (ex: "este partido governou neste mandato"), mas sem atribuição de cumprido/não cumprido.

### Nota sobre cumprido/não cumprido
**Fora do scope.** Verificar cumprimento é genuinamente difícil e subjectivo. O valor do Prometido está em tornar os programas eleitorais acessíveis e pesquisáveis — muitos partidos não disponibilizam programas antigos online, e precisar do Arquivo.pt para aceder a um programa de 2019 demonstra exactamente o problema que este projecto resolve. A comparação entre eleições e a pesquisa por tema são suficientemente úteis sem a camada de verificação.

### Nota sobre cobertura
Alguns partidos têm histórico mais curto (Chega 2019+, Livre 2019+, IL 2019+, PAN 2015+). BE 2025 publicou apenas um manifesto de 2 páginas. A interface mostra transparentemente a fonte e cobertura de cada promessa.

### Sites de notícias para Tier 3
Servem para **corroboração de promessas** — artigo cita directamente o político a fazer a promessa.

```python
NEWS_DOMAINS = {
    "Público":            "publico.pt",       # prioridade — Menção Honrosa
    "Expresso":           "expresso.pt",
    "Observador":         "observador.pt",
    "Jornal de Negócios": "jornaldenegocios.pt",
    "RTP":                "rtp.pt",
    "SIC Notícias":       "sicnoticias.pt",
}
```

### Sistema de estados de promessas
| Estado | Significado | Como é atribuído |
|--------|-------------|-----------------|
| `archived` | Promessa encontrada, fonte primária disponível | Automático — passo 1 do pipeline |
| `corroborated` | Confirmada por citação directa em Tier 3 | Automático — passo de linking |
| `untracked` | Sem corroboração adicional | Default |

### Funcionalidade
- [x] Pesquisa full-text por termo (ex: "habitação", "salário mínimo") — FTS5 + /api/search
- [x] Filtro por partido, eleição, tópico, estado — implementado
- [x] **Feature de comparação** — /compare implementado, vista lado-a-lado
- [x] Cada promessa tem badge com timestamp + link proeminente para o Arquivo.pt — ArchiveLink
- [x] Página de detalhe da promessa com contexto, fonte primária, fontes de verificação
- [x] Página de partido com promessas por eleição e breakdown de estados
- [x] Homepage com stats e acesso directo à feature de comparação
- [x] Página "Como funciona" — metodologia completa

### Qualidade mínima
- [ ] Funciona em mobile — a testar
- [ ] Carrega em < 3 segundos — a testar com dados reais
- [x] Links para o arquivo.pt funcionam — validado
- [x] Metodologia explicada — /como-funciona completa

---

## Fora do MVP (pós-prémio)

- Verificação de cumprimento de promessas (requer curadoria editorial contínua)
- API pública para investigadores
- Versão em inglês
- Eleições presidenciais e autárquicas
- Alertas / notificações quando nova promessa é adicionada
- Comparação lado-a-lado entre partidos por tópico
- Visualizações temporais avançadas

---

## Calendário de 2.5 semanas

### Semana 1 (18-24 abril) — Pipeline + Dados
- Dias 1-2: Setup do projeto, testar API do Arquivo.pt, validar cobertura dos domínios alvo ✓
- Dias 3-4: Recolha de programas (46 ficheiros) ✓ + cowork de extracção
- Dias 5-6: Cowork de extracção (continuação) + validação automática
- Dia 7: Curadoria humana dos ~30-50 casos ambíguos

### Semana 2 (25 abril - 1 maio) — Dados + Deploy
- Dias 8-9: Arquivo.pt discovery para evidência de origem (Tier 1) + linking Tier 3
- Dias 10-11: Deploy Vercel + Railway + testes com dados reais
- Dias 12-13: Mobile testing, polish, fix de bugs
- Dia 14: Buffer

### Semana 3 (2-6 maio) — Submissão
- Dias 15-16: Testes com utilizadores reais, fix de bugs críticos
- Dias 17-18: Escrever descrição do trabalho (2000 palavras) com Cowork
- Dia 19: Gravar vídeo (3 minutos)
- Dia 20 (6 maio): Submeter candidatura antes das 23:59h

---

## Critério de go/no-go

**Fim da semana 1:** Se o volume de promessas extraídas for demasiado baixo (<200), investigar qualidade do prompt de extracção — ajustar antes de avançar para deploy.

**Dia 4 maio:** Se houver riscos na candidatura, priorizar a submissão sobre o polish final.

---

## Estimativa de custos Claude API

| Fase | Volume estimado | Custo estimado |
|------|----------------|----------------|
| Passo 1 — Extracção via Arquivo.pt | PS/PSD × 2005-2019 | ~$10-15 |
| Passo 2 — Validação | Promessas extraídas | ~$5-10 |
| Linking Tier 3 | Notícias arquivadas | ~$5-10 |
| **Total** | | **~$20-35** |

Nota: extracção dos PDFs via cowork — sem custo de API.
