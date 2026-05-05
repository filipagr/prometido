#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IL 2025 - Final Promise Extraction
Extract complete, well-formed promises
"""

import json
import re
from collections import Counter

with open('data/programs/2025/IL-leg-2025.txt', 'r', encoding='utf-8') as f:
    text = f.read()

promises = []

# Strategy: Extract complete sentences/phrases that contain proposal language
# Sentences end with . ! or ? followed by capital letter
# Keep them complete

# Split into proper sentences
sentences = re.split(r'(?<=[.!?])\s+(?=[A-ZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞŸ])', text)

for i, sent in enumerate(sentences):
    sent = sent.strip()
    
    # Must be reasonable length
    if len(sent) < 30 or len(sent) > 350:
        continue
    
    # Must have proposal markers
    has_proposal_marker = any(marker in sent for marker in [
        'A Iniciativa Liberal propõe',
        'A Iniciativa Liberal defende',
        'Defendemos',
        'Propomos',
        'propõe',
        'propõem',
        'criação de',
        'reformar',
        'rever',
        'eliminar',
        'redução',
        'aumento',
        'Garantir',
        'Assegurar',
        'objetivo',
        'programa de'
    ])
    
    if not has_proposal_marker:
        continue
    
    # Must have at least one concrete element
    has_concrete = any([
        re.search(r'\d+\s*%', sent),                           # percentage
        re.search(r'\d+\s*(?:mil|milhões)\s+(?:euros|€)', sent),  # money
        re.search(r'\d+\s*(?:anos|meses|dias)', sent),          # time
        re.search(r'\b(?:Lei|Decreto|Código|Fundo|Programa|Agência|Imposto|IRS|IRC|ISV|IVA|IUC|IMT|IMI|SNS|TMRG|UCCI|FGADM|AMIM|SAPA|BRE|RRC|Pilar|PPP|USF|Conselho|Ministério|Entidade|Reguladora)\b', sent),
        re.search(r'\b(?:abolir|rever|eliminar|criar|implementar|fusão|integração|descentralizar|desburocratizar|digitalizar|reformar)\b', sent, re.I)
    ])
    
    if not has_concrete:
        continue
    
    # Clean the text
    promise_text = ' '.join(sent.split())
    
    # Classify topic
    text_lower = sent.lower()
    if any(w in text_lower for w in ['estado', 'administração', 'burocracia', 'desburocrati', 'funcionário', 'contratação pública', 'descentrali', 'centralismo']):
        topic = 'administração pública'
    elif any(w in text_lower for w in ['pensão', 'reforma', 'segurança social', 'pilar', 'capitalização', 'poupança', 'fgadm', 'amim']):
        topic = 'segurança social'
    elif any(w in text_lower for w in ['saúde', 'médico', 'hospital', 'utente', 'doente', 'sns', 'cuidado', 'cirurgia', 'consulta']):
        topic = 'saúde'
    elif any(w in text_lower for w in ['educação', 'escol', 'alun', 'ensino', 'universidade', 'formação', 'docente', 'professor']):
        topic = 'educação'
    elif any(w in text_lower for w in ['imposto', 'irs', 'irc', 'fiscal', 'tributário', 'empresa', 'economia', 'carga fiscal', 'deduções', 'iva', 'isc']):
        topic = 'economia'
    elif any(w in text_lower for w in ['trabalh', 'emprego', 'salário', 'contrato laboral', 'laboral']):
        topic = 'emprego'
    elif any(w in text_lower for w in ['habitação', 'casa', 'arrendamento', 'imóvel', 'construção', 'licenciamento', 'imt', 'imi']):
        topic = 'habitação'
    elif any(w in text_lower for w in ['ambiente', 'energia', 'água', 'verde', 'sustentável', 'renovável', 'carbono', 'eficiência material']):
        topic = 'ambiente'
    elif any(w in text_lower for w in ['justiça', 'tribunal', 'processo', 'crime', 'penal', 'corrupção', 'celeridade']):
        topic = 'justiça'
    elif any(w in text_lower for w in ['transporte', 'ferroviário', 'mobilidade', 'comboio', 'ferrovia', 'urbana']):
        topic = 'transportes'
    elif any(w in text_lower for w in ['cultura', 'desporto', 'adaptado', 'património', 'histórico']):
        topic = 'cultura'
    elif any(w in text_lower for w in ['segurança', 'polícia', 'protecção', 'defesa', 'militar', 'gendarmeria']):
        topic = 'segurança'
    else:
        topic = 'outros'
    
    # Calculate confidence
    confidence = 0.25  # base for having proposal marker
    
    if re.search(r'\d+\s*%', promise_text):
        confidence += 0.25
    if re.search(r'\d+\s*(?:mil|milhões)\s+euros', promise_text):
        confidence += 0.25
    if re.search(r'\d+\s*(?:anos|meses|dias)', promise_text):
        confidence += 0.20
    if re.search(r'\b(?:Lei|Código|Fundo|Programa|Imposto|IRS|IRC|SNS|PPP|Agência|Entidade|Reguladora)\b', promise_text):
        confidence += 0.15
    if re.search(r'\b(?:abolir|eliminar|criar|rever|fusão|integração)\b', promise_text, re.I):
        confidence += 0.10
    
    confidence = min(confidence, 1.0)
    
    promises.append({
        'text': promise_text,
        'topic': topic,
        'confidence': round(confidence, 2)
    })

# Deduplicate by first 80 chars
seen = set()
deduped = []
for p in promises:
    key = p['text'][:80].lower()
    if key not in seen:
        seen.add(key)
        deduped.append(p)

promises = deduped

# Sort by confidence
promises = sorted(promises, key=lambda x: -x['confidence'])

# Stats
topic_counts = Counter(p['topic'] for p in promises)
conf_counts = Counter(p['confidence'] for p in promises)

print(f"Total promises: {len(promises)}")
print()
print("By topic:")
for t, c in sorted(topic_counts.items(), key=lambda x: -x[1]):
    print(f"  {t:20}: {c:3}")
print()
print("By confidence:")
for c in sorted(conf_counts.keys(), reverse=True):
    print(f"  {c}: {conf_counts[c]}")
print()
print("Top 10 promises (highest confidence):")
for i, p in enumerate(promises[:10], 1):
    print(f"{i:2}. [{p['confidence']}] {p['topic']:20} {p['text'][:75]}")

# Save
output = {
    'source': 'Iniciativa Liberal - Programa Eleitoral Legislativas 2025',
    'tier': 'Tier 2 (official electoral program)',
    'total_promises': len(promises),
    'extraction_date': '2026-04-20',
    'topic_distribution': dict(topic_counts),
    'confidence_distribution': {str(k): v for k, v in sorted(conf_counts.items(), reverse=True)},
    'promises': promises
}

with open('data/programs/2025/IL-leg-2025.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print()
print(f"Saved {len(promises)} promises to IL-leg-2025.json")
