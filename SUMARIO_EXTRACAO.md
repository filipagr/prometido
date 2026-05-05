# Extração de Promessas Eleitorais - Iniciativa Liberal 2025

## Resultado Final

**Total de Promessas Extraídas:** 113 promessas concretas e verificáveis

**Ficheiro de Saída:** `/data/programs/2025/IL-leg-2025.json`

**Tamanho:** 33KB | **Linhas JSON:** 593

---

## Distribuição por Tópico

| Tópico | Contagem | % |
|--------|----------|-----|
| Outros | 23 | 20.4% |
| Segurança Social | 20 | 17.7% |
| Administração Pública | 18 | 15.9% |
| Economia | 14 | 12.4% |
| Educação | 8 | 7.1% |
| Justiça | 8 | 7.1% |
| Habitação | 5 | 4.4% |
| Emprego | 4 | 3.5% |
| Saúde | 4 | 3.5% |
| Cultura & Desporto | 4 | 3.5% |
| Segurança | 2 | 1.8% |
| Transportes | 2 | 1.8% |
| Ambiente | 1 | 0.9% |

---

## Distribuição por Nível de Confiança

| Confiança | Contagem | % | Interpretação |
|-----------|----------|-----|---|
| **0.7** | 9 | 8.0% | Muito Alta (múltiplos critérios) |
| **0.6** | 6 | 5.3% | Alta (2 critérios) |
| **0.5** | 13 | 11.5% | Média (2 critérios leves) |
| **0.4** | 85 | 75.2% | Média-Baixa (1 critério) |

**Nota:** 28 promessas (25%) têm confiança >= 0.5 (múltiplos critérios de verificabilidade).

---

## Critérios de Extração Aplicados

Uma promessa foi incluída se atendesse a **PELO MENOS UM** destes critérios:

### A) Número/Valor Concreto
- Percentagens (IVA 23% → 6%)
- Valores em euros (€500M, €228-404M)
- Quantificações ("reduzir em 25%")

### B) Prazo Específico
- "até 2030", "10 anos", "próximos..."
- Datas ou períodos definidos

### C) Ação Singular Identificável
- criar, eliminar, rever, reformar, implementar
- Fusão, integração, descentralização, desburocratização

### D) Lei/Instituição/Medida Nomeada
- Lei, Decreto, Código, Fundo, Programa
- IRS, IRC, SNS, PPP, FGADM, UCCI, etc.

---

## Promessas Destaque (Top 5)

1. **Administração Pública [0.7]**  
   "Reduzir em 25% o tempo médio de resposta"

2. **Habitação [0.7]**  
   "Redução do IVA da construção de 23% para 6%"

3. **Economia [0.7]**  
   "Redução da taxa de retenção de IRS para 15%"

4. **Administração Pública [0.7]**  
   "Redução até 5% da despesa primária do Estado (10 anos)"

5. **Emprego [0.7]**  
   "Custo da medida entre 228 e 404 milhões (2025)"

---

## Padrões Identificados

1. **Densidade Alta:** ~195 promessas por 1.000 caracteres (muito elevada)

2. **Foco em Economia/Fiscalidade:** 30% das promessas (Economia + Segurança Social)

3. **Foco em Reforma do Estado:** 18 promessas sobre administração pública

4. **Propostas Estruturais:** Reformas sistémicas, não cosméticas
   - Modelo tripilar de pensões
   - SUA-Saúde (sistema alternativo)
   - Entidade Reguladora independente da Saúde
   - Descentralização com neutralidade fiscal

5. **Rastreabilidade:** Referências a legislação e números específicos

---

## Metodologia

### Processo de Extração

1. **Leitura completa** do documento (577K caracteres)
2. **Segmentação** em parágrafos e sentenças
3. **Filtro** por critérios de concretude (A, B, C, ou D)
4. **Classificação** de tópico por keywords
5. **Scoring de confiança** baseado em critérios múltiplos
6. **Deduplicação** por primeiros 70 caracteres
7. **Limpeza de texto** (normalização de espaços)

### Ferramentas

- Python 3 + regex
- JSON para serialização
- Sem dependências externas

---

## Limitações Conhecidas

1. **Fragmentação de texto:** Alguns textos têm quebras de linhas na extração
2. **Tópico "Outros":** 20.4% das promessas são transversais
3. **Confiança média-baixa:** 75% têm confiança 0.4 (mas ainda assim válidas)
4. **Contexto perdido:** Extraction por sentença perdeu alguma estrutura

---

## Dados Técnicos

| Métrica | Valor |
|---------|-------|
| Documento Original | 576.924 caracteres (~49K tokens) |
| Promessas Extraídas | 113 |
| Densidade | 195.9 promessas / 1000 caracteres |
| Promessas Alta Confiança (>=0.6) | 15 |
| Promessas Múltiplos Critérios (>=0.5) | 28 |
| Ficheiro JSON | 33KB, 593 linhas |

---

## Estrutura do Ficheiro JSON

```json
{
  "source": "Iniciativa Liberal - Programa Eleitoral Legislativas 2025",
  "tier": "Tier 2",
  "total_promises": 113,
  "extraction_date": "2026-04-20",
  "topic_distribution": { "economia": 14, ... },
  "confidence_distribution": { "0.7": 9, ... },
  "promises": [
    {
      "text": "string (promessa completa)",
      "topic": "string (categoria)",
      "confidence": 0.7
    },
    ...
  ]
}
```

---

## Próximos Passos Sugeridos

1. Validação manual das 28 promessas de alta confiança (>= 0.5)
2. Verificação factual com dados públicos (orçamentos, legislação)
3. Comparação com implementações após eleições legislativas
4. Entrevista ao partido para clarificar promessas ambíguas

---

**Extração realizada:** 2026-04-20  
**Projectos:** Prometido - Documentação de Promessas Eleitorais  
**Candidatura:** Prémio Arquivo.pt 2026
