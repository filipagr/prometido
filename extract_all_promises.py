#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IL Electoral Program 2025 - Promise Extraction
Tier 2 source: Official electoral program
Systematically extract all concrete, verifiable promises
"""

import json
import re
from collections import Counter, defaultdict

# Read the complete file
with open('data/programs/2025/IL-leg-2025.txt', 'r', encoding='utf-8') as f:
    text = f.read()

promises = []

def classify_topic(text):
    """Classify promise into topic"""
    text_lower = text.lower()

    topics_map = {
        'administração pública': ['estado', 'administração', 'burocracia', 'desburocratizar', 'funcionários públicos', 'contratação pública', 'governo', 'setor empresarial do estado'],
        'segurança social': ['pensão', 'reforma', 'segurança social', 'desemprego', 'subsídio', 'apoio social', 'deficiência', 'incapacidade'],
        'saúde': ['saúde', 'médico de família', 'hospitais', 'medicamentos', 'doentes', 'sns', 'cirurgia', 'oncologia', 'urgência', 'cuidados'],
        'educação': ['educação', 'escolas', 'alunos', 'ensino', 'universidade', 'formação', 'docentes'],
        'economia': ['impostos', 'irs', 'irc', 'carga fiscal', 'economia', 'fiscal', 'empresas', 'carga tributária'],
        'emprego': ['trabalho', 'emprego', 'salário', 'contrato laboral', 'legislação laboral'],
        'habitação': ['habitação', 'casas', 'arrendamento', 'imóvel', 'construção'],
        'ambiente': ['ambiente', 'energia', 'água', 'verde', 'natureza', 'sustentável'],
        'justiça': ['justiça', 'tribunais', 'processos', 'crime', 'penal'],
        'transportes': ['transportes', 'ferroviário', 'mobilidade', 'ferrovia', 'comboio'],
        'tecnologia': ['digital', 'tecnologia', 'inovação', 'govtech', 'informatização'],
        'agricultura': ['agricultura', 'rural', 'interior', 'mar'],
        'cultura': ['cultura', 'desporto', 'património'],
        'segurança': ['segurança', 'polícia', 'protecção', 'defesa'],
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
        score += 0.25
    if 'D_named' in criteria_met:
        score += 0.15

    return min(score, 1.0)

def meets_criteria(text):
    """Check if text meets at least one concrete promise criterion"""
    criteria = []

    # A) Number/value with unit
    if re.search(r'\d+\s*(?:%|milhões|mil|euros|€|pontos|dias|anos|horas|minutos|segundos)', text, re.IGNORECASE):
        criteria.append('A_number')

    # B) Specific timeframe
    if re.search(r'(?:até|durante|por|em|nos\s+próximos|horizonte\s+de|2030|20\d{2})\s+(?:20\d{2}|\d+\s*(?:anos|meses|dias|semanas))', text, re.IGNORECASE):
        criteria.append('B_timeframe')

    # C) Concrete action verbs
    if re.search(r'\b(?:abolir|rever|eliminar|criar|implementar|fusão|integração|descentralizar|desburocratizar|digitalizar|simplificar|reformar|estabelecer|garantir|assegurar|aumentar|reduzir|propõe|propõem|defender|defende)\b', text, re.IGNORECASE):
        criteria.append('C_action')

    # D) Named law, institution, or measure
    if re.search(r'\b(?:Lei|Decreto|Código|Fundo|Imposto|Entidade|Agência|Programa|Rede|Centro|Comissão|Fundo de Garantia|FGADM|IRS|IRC|ISV|IVA|IUC|IMT|IMI|SNS|SUA-Saúde|AIMA|TMRG|UCCI|IPSS|TAP|CP|RTP|EFACEC|PPP|USF|Conselho)', text):
        criteria.append('D_named')

    return len(criteria) >= 1, criteria

# Find all promise-containing paragraphs
# Split by double newline or numbered/bulleted sections
sections = re.split(r'\n\s*\n+', text)

current_topic = 'outros'
extracted = 0

for section in sections:
    section = section.strip()
    if len(section) < 40:
        continue

    # Update topic based on section headers
    if 'ADMINISTRAÇÃO PÚBLICA' in section:
        current_topic = 'administração pública'
    elif 'SAÚDE' in section:
        current_topic = 'saúde'
    elif 'EDUCAÇÃO' in section:
        current_topic = 'educação'
    elif 'SEGURANÇA SOCIAL' in section or 'APOIO SOCIAL' in section:
        current_topic = 'segurança social'
    elif 'TRABALHO' in section:
        current_topic = 'emprego'
    elif 'HABITAÇÃO' in section:
        current_topic = 'habitação'
    elif 'TRANSPORTES' in section:
        current_topic = 'transportes'
    elif 'AMBIENTE' in section or 'ENERGIA' in section:
        current_topic = 'ambiente'
    elif 'JUSTIÇA' in section:
        current_topic = 'justiça'
    elif 'SEGURANÇA' in section or 'PROTEÇÃO' in section:
        current_topic = 'segurança'
    elif 'CULTURA' in section or 'DESPORTO' in section:
        current_topic = 'cultura'
    elif 'AGRICULTURA' in section or 'RURAL' in section or 'MAR' in section:
        current_topic = 'agricultura'

    # Split section into sentences
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', section)

    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 30:
            continue

        # Must contain proposal words
        if not any(w in sentence.lower() for w in ['propõe', 'propõem', 'defender', 'defende', 'objetivo', 'meta', 'garantir', 'assegurar', 'cria', 'criação', 'programa', 'reforma', 'rever', 'eliminar', 'criamos', 'criará', 'criando']):
            continue

        is_promise, criteria = meets_criteria(sentence)
        if is_promise:
            topic = classify_topic(sentence) or current_topic
            confidence = calculate_confidence(sentence, criteria)

            if len(sentence) <= 300:
                promises.append({
                    'text': sentence,
                    'topic': topic,
                    'confidence': round(confidence, 2),
                    'criteria': criteria
                })
                extracted += 1

# Remove duplicates and near-duplicates
seen_texts = set()
deduped = []
for p in promises:
    text_key = p['text'][:50].lower()
    if text_key not in seen_texts:
        seen_texts.add(text_key)
        deduped.append(p)

promises = deduped

# Statistics
print(f"Total promises extracted: {len(promises)}")
print()

# By topic
topic_counts = Counter(p['topic'] for p in promises)
print("Distribution by topic:")
for topic, count in sorted(topic_counts.items(), key=lambda x: -x[1]):
    print(f"  {topic}: {count}")
print()

# By confidence
conf_counts = Counter(p['confidence'] for p in promises)
print("Distribution by confidence:")
for conf in sorted(conf_counts.keys(), reverse=True):
    print(f"  {conf}: {conf_counts[conf]}")
print()

# By criteria
criteria_counts = defaultdict(int)
for p in promises:
    for c in p['criteria']:
        criteria_counts[c] += 1
print("Criteria met:")
for c in sorted(criteria_counts.keys()):
    print(f"  {c}: {criteria_counts[c]}")

# Save to JSON
output = {
    'source': 'Iniciativa Liberal - Legislativas 2025',
    'tier': 'Tier 2',
    'description': 'Official electoral program',
    'total_promises': len(promises),
    'extraction_date': '2025-04-20',
    'topic_distribution': dict(topic_counts),
    'confidence_distribution': {str(k): v for k, v in sorted(conf_counts.items(), reverse=True)},
    'promises': promises
}

with open('data/programs/2025/IL-leg-2025.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nSaved {len(promises)} promises to data/programs/2025/IL-leg-2025.json")
