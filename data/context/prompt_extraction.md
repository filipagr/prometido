# Prompt para extracção manual de promessas (sessões cowork)

Usar este prompt em cada sessão de extracção de PDF.
Substituir os valores entre `{}` antes de enviar.

---

## Prompt

```
És um analista político especializado em programas eleitorais portugueses.

Contexto:
- Partido: {NOME_PARTIDO} ({ID_PARTIDO})
- Eleição: Legislativas {ANO}
- Tipo de fonte: programa eleitoral oficial (Tier 2)

Texto a analisar:
{TEXTO_DO_PDF}

Tarefa:
Identifica TODAS as promessas eleitorais concretas e verificáveis neste texto.

Para ser uma promessa válida, tem de ter pelo menos um destes elementos:
A) Um número ou valor concreto (ex: "aumentar para X%", "criar Y postos de trabalho", "investir Z milhões")
B) Um prazo específico (ex: "até 2013", "nos primeiros 100 dias", "durante a legislatura")
C) Uma acção singular e identificável (ex: "criar o programa X", "eliminar a taxa Y", "construir Z hospitais")
D) Uma lei, instituição ou medida nomeada concretamente

Excluir:
- Declarações de intenção vagas: "vamos apoiar", "iremos promover"
- Valores genéricos: "acreditamos em", "defendemos"
- Diagnósticos ou críticas sem proposta concreta
- Retórica política: "um Portugal melhor", "mais justo"

Para cada promessa, devolve um objecto JSON com:
- "text": a promessa nas palavras exactas do documento (máx. 300 chars)
- "context": frase anterior/seguinte para contextualizar (máx. 200 chars)
- "topic": um de ["habitação", "saúde", "educação", "economia", "emprego", "ambiente", "segurança", "justiça", "transportes", "tecnologia", "agricultura", "cultura", "desporto", "administração pública", "outros"]
- "confidence": float 0.0 a 1.0

Devolve APENAS um JSON array. Se não houver promessas concretas, devolve [].
```

---

## Formato de output esperado

```json
[
  {
    "text": "Criar 50.000 novos lugares em creches até 2013",
    "context": "No domínio da família e das políticas sociais, o PS compromete-se a",
    "topic": "outros",
    "confidence": 0.95
  },
  ...
]
```

---

## Depois de ter o JSON — inserir na DB

Guarda o output como `data/programs/{ANO}/{ID_PARTIDO}-leg-{ANO}.json` e corre:

```bash
.venv/bin/python3 scripts/import_promises_json.py data/programs/{ANO}/{ID_PARTIDO}-leg-{ANO}.json
```

---

## Valores para cada ficheiro

| Ficheiro | ID_PARTIDO | NOME_PARTIDO | ANO |
|----------|-----------|--------------|-----|
| PS-leg-2002.pdf | PS | Partido Socialista | 2002 |
| PS-leg-2005.pdf | PS | Partido Socialista | 2005 |
| PS-leg-2009.pdf | PS | Partido Socialista | 2009 |
| PS-leg-2011.pdf | PS | Partido Socialista | 2011 |
| PS-leg-2015.pdf | PS | Partido Socialista | 2015 |
| PS-leg-2019.pdf | PS | Partido Socialista | 2019 |
| PS-leg-2022.pdf | PS | Partido Socialista | 2022 |
| PS-leg-2024.pdf | PS | Partido Socialista | 2024 |
| PS-leg-2025.pdf | PS | Partido Socialista | 2025 |
| AD-leg-2025.pdf | PSD | Aliança Democrática (PSD+CDS) | 2025 |
| BE-leg-2025.pdf | BE | Bloco de Esquerda | 2025 |
| CDU-leg-2025.pdf | PCP | CDU (PCP+Verdes) | 2025 |
| CH-leg-2025.pdf | CH | Chega | 2025 |
| IL-leg-2025.pdf | IL | Iniciativa Liberal | 2025 |
| LV-leg-2025.pdf | LV | Livre | 2025 |
| PAN-leg-2025.pdf | PAN | Pessoas-Animais-Natureza | 2025 |
