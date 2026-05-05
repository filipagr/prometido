#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IL Electoral Program 2025 - Promise Extraction (Refined)
Add context and validate each promise carefully
"""

import json
import re
from collections import Counter, defaultdict

# Read the complete file
with open('data/programs/2025/IL-leg-2025.txt', 'r', encoding='utf-8') as f:
    text = f.read()

def classify_topic(text):
    """Classify promise into topic"""
    text_lower = text.lower()

    topics_map = {
        'administração pública': ['estado', 'administração', 'burocracia', 'desburocratizar', 'funcionários públicos', 'contratação pública', 'governo', 'setor empresarial', 'público', 'centralismo', 'descentralizar'],
        'segurança social': ['pensão', 'reforma', 'segurança social', 'desemprego', 'subsídio', 'apoio social', 'deficiência', 'incapacidade', 'pilar', 'capitalização', 'poupança'],
        'saúde': ['saúde', 'médico de família', 'hospitais', 'medicamentos', 'doentes', 'sns', 'cirurgia', 'oncologia', 'urgência', 'cuidados', 'utentes'],
        'educação': ['educação', 'escolas', 'alunos', 'ensino', 'universidade', 'formação', 'docentes', 'literacia'],
        'economia': ['impostos', 'irs', 'irc', 'carga fiscal', 'economia', 'fiscal', 'empresas', 'carga tributária', 'investimento'],
        'emprego': ['trabalho', 'emprego', 'salário', 'contrato laboral', 'legislação laboral', 'trabalhadores'],
        'habitação': ['habitação', 'casas', 'arrendamento', 'imóvel', 'construção', 'licenciamento'],
        'ambiente': ['ambiente', 'energia', 'água', 'verde', 'natureza', 'sustentável', 'eficiência material'],
        'justiça': ['justiça', 'tribunais', 'processos', 'crime', 'penal', 'celeridade', 'corrupção'],
        'transportes': ['transportes', 'ferroviário', 'mobilidade', 'ferrovia', 'comboio', 'mobilidade urbana'],
        'tecnologia': ['digital', 'tecnologia', 'inovação', 'govtech', 'informatização'],
        'agricultura': ['agricultura', 'rural', 'interior', 'mar', 'pescas', 'água'],
        'cultura': ['cultura', 'desporto', 'património', 'desporto adaptado'],
        'segurança': ['segurança', 'polícia', 'protecção', 'defesa', 'militar'],
        'outros': []
    }

    for topic, keywords in topics_map.items():
        if topic == 'outros':
            continue
        if any(kw in text_lower for kw in keywords):
            return topic
    return 'outros'

def calculate_confidence(text, criteria_met):
    """Calculate confidence 0.0-1.0"""
    score = 0.0
    if 'A_number' in criteria_met:
        score += 0.35
    if 'B_timeframe' in criteria_met:
        score += 0.25
    if 'C_action' in criteria_met:
        score += 0.20
    if 'D_named' in criteria_met:
        score += 0.20
    return min(score, 1.0)

def meets_criteria(text):
    """Check criteria and return list of met ones"""
    criteria = []
    if re.search(r'\d+\s*(?:%|milhões|mil|euros|€|pontos|dias|anos|horas|minutos|segundos|limite|tecto|máximo|mínimo)', text, re.IGNORECASE):
        criteria.append('A_number')
    if re.search(r'(?:até|durante|por|em|nos\s+próximos|horizonte\s+de|2030|20\d{2})\s+(?:20\d{2}|\d+\s*(?:anos|meses|dias|semanas))', text, re.IGNORECASE):
        criteria.append('B_timeframe')
    if re.search(r'\b(?:abolir|rever|eliminar|criar|implementar|fusão|integração|descentralizar|desburocratizar|digitalizar|simplificar|reformar|estabelecer|garantir|assegurar|aumentar|reduzir|propõe|propõem|defende|defendemos|cria|criação|reformar|reforçar)\b', text, re.IGNORECASE):
        criteria.append('C_action')
    if re.search(r'\b(?:Lei|Decreto|Código|Fundo|Imposto|Entidade|Agência|Programa|Rede|Centro|Comissão|Ministério|Organismo|IRS|IRC|ISV|IVA|IUC|IMT|IMI|SNS|SUA-Saúde|AIMA|TMRG|UCCI|IPSS|TAP|CP|RTP|EFACEC|PPP|USF|Conselho|BRE|RRC|Pilar|FGADM|AMIM|SAPA)\b', text):
        criteria.append('D_named')
    return len(criteria) >= 1, criteria

# Split text into sentences, keeping context
sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)

promises = []
seen_texts = set()

for i, sentence in enumerate(sentences):
    sentence = sentence.strip()
    if len(sentence) < 30:
        continue

    # Check if it contains proposal language
    if not any(w in sentence.lower() for w in ['propõe', 'propõem', 'defende', 'defendemos', 'objetivo', 'meta', 'garantir', 'assegurar', 'cria', 'criação', 'programa', 'reforma', 'rever', 'eliminar', 'reforço', 'reforçar']):
        continue

    is_promise, criteria = meets_criteria(sentence)
    if not is_promise:
        continue

    # Get context
    prev_sent = sentences[i-1][:150] if i > 0 else ""
    next_sent = sentences[i+1][:150] if i < len(sentences) - 1 else ""
    context = (prev_sent + " | " + next_sent).strip(' |')

    topic = classify_topic(sentence)
    confidence = calculate_confidence(sentence, criteria)

    # Keep text under 300 chars
    promise_text = sentence if len(sentence) <= 300 else sentence[:297] + "..."

    # Avoid exact duplicates
    text_key = promise_text[:60].lower()
    if text_key in seen_texts:
        continue
    seen_texts.add(text_key)

    promises.append({
        'text': promise_text,
        'context': context[:200],
        'topic': topic,
        'confidence': round(confidence, 2),
        'criteria_met': criteria
    })

# Remove lowest-confidence ones that are purely ideological
filtered = []
for p in promises:
    # Keep if confidence >= 0.25 OR (has multiple criteria)
    if p['confidence'] >= 0.25 or len(p['criteria_met']) >= 2:
        filtered.append(p)

promises = filtered

# Statistics
print(f"Total promises after filtering: {len(promises)}")
print()

topic_counts = Counter(p['topic'] for p in promises)
print("Distribution by topic:")
for topic, count in sorted(topic_counts.items(), key=lambda x: -x[1]):
    print(f"  {topic}: {count}")
print()

conf_counts = Counter(p['confidence'] for p in promises)
print("Distribution by confidence:")
for conf in sorted(conf_counts.keys(), reverse=True):
    print(f"  {conf}: {conf_counts[conf]}")
print()

# Save results
output = {
    'source': 'Iniciativa Liberal - Legislativas 2025',
    'tier': 'Tier 2 (official electoral program)',
    'total_promises': len(promises),
    'extraction_date': '2025-04-20',
    'topic_distribution': dict(topic_counts),
    'confidence_distribution': {str(k): v for k, v in sorted(conf_counts.items(), reverse=True)},
    'promises': [
        {
            'text': p['text'],
            'context': p['context'],
            'topic': p['topic'],
            'confidence': p['confidence'],
            'criteria_met': p['criteria_met']
        }
        for p in promises
    ]
}

with open('data/programs/2025/IL-leg-2025.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nSaved to data/programs/2025/IL-leg-2025.json")
print(f"\nSample promises (top 5 by confidence):")
for p in sorted(promises, key=lambda x: -x['confidence'])[:5]:
    print(f"  [{p['confidence']}] {p['text'][:80]}...")
