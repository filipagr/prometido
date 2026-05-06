# Arquivo Eleitoral

Base de dados de promessas eleitorais de partidos políticos portugueses — pesquisável, comparável, com ligação directa aos programas originais.

**[arquivoeleitoral.pt](https://arquivoeleitoral.pt)**

---

## O que é

O Arquivo Eleitoral extrai e indexa promessas de programas eleitorais portugueses desde 2002, tornando-as pesquisáveis e comparáveis. Cada promessa está ligada ao documento original, arquivado no [Arquivo.pt](https://arquivo.pt) sempre que possível.

## Estado actual

| | |
|---|---|
| **Promessas** | 10 907 |
| **Partidos** | 9 |
| **Eleições** | 9 legislativas (2002–2025) |

### Promessas por partido

| Partido | Promessas |
|---|---|
| PAN | 2 322 |
| PS | 1 802 |
| PSD / AD | 1 331 |
| IL | 1 184 |
| Chega | 1 159 |
| BE | 1 117 |
| PCP | 899 |
| CDS | 723 |
| Livre | 370 |

## Stack

- **Backend** — FastAPI (Python), SQLite, hospedado no Render
- **Frontend** — Next.js 15, Tailwind CSS, hospedado no Vercel
- **Pipeline** — extracção com LLM (Claude), revisão manual, importação via script

## Estrutura

```
backend/          FastAPI + SQLite
frontend/         Next.js app
data/
  prometido.db    Base de dados principal
  programs/       PDFs e HTMLs dos programas eleitorais
  reviews/        Ficheiros de revisão do pipeline (JSON)
  context/        Notas sobre fontes e ligações
scripts/          Scripts de importação e manutenção
```

## Pipeline de extracção

1. Download do programa eleitoral (via Arquivo.pt ou ligação directa)
2. Extracção de promessas com LLM → ficheiro `.full.json`
3. Revisão manual → ficheiro `.reviewed.json`
4. Importação para a base de dados via `scripts/add_promises.py`

## Desenvolvimento local

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Fontes

Os programas eleitorais são maioritariamente arquivados no [Arquivo.pt](https://arquivo.pt). Alguns documentos recentes (Chega 2024/2025, AD 2025, BE 2024) são ligações directas aos PDFs oficiais dos partidos, por não estarem disponíveis no arquivo.

Consulta a página [Como funciona](https://arquivoeleitoral.pt/como-funciona) para mais detalhes sobre a metodologia.
