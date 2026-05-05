#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IL Electoral Program 2025 - Final Promise Extraction
Clean extraction with proper text normalization
"""

import json
import re
from collections import Counter

# Read file
with open('data/programs/2025/IL-leg-2025.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Normalize text (remove excessive whitespace while preserving structure)
text = re.sub(r'\s+', ' ', text)
text = re.sub(r'(\s+-\s+|•\s+)', '\n• ', text)
text = re.sub(r'(\d+\.\s+)', '\n\1', text)

def normalize_text(s):
    """Clean up extracted text"""
    s = ' '.join(s.split())
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

def classify_topic(text):
    """Classify by keywords"""
    text_lower = text.lower()

    if any(w in text_lower for w in ['estado', 'administração', 'burocracia', 'desburocratizar', 'funcionários', 'contratação pública', 'governo', 'central', 'descentrali']):
        return 'administração pública'
    elif any(w in text_lower for w in ['pensão', 'reforma', 'segurança social', 'pilar', 'capitalização', 'poupança', 'investimento', 'fundo de garantia']):
        return 'segurança social'
    elif any(w in text_lower for w in ['saúde', 'médico', 'hospital', 'utente', 'doente', 'sns', 'cuidado', 'cirurgia']):
        return 'saúde'
    elif any(w in text_lower for w in ['educação', 'escol', 'alun', 'ensino', 'universidade', 'formação', 'docente']):
        return 'educação'
    elif any(w in text_lower for w in ['imposto', 'irs', 'irc', 'fiscal', 'tributário', 'empresa', 'economia', 'investimento']):
        return 'economia'
    elif any(w in text_lower for w in ['trabalh', 'emprego', 'salário', 'contrato laboral']):
        return 'emprego'
    elif any(w in text_lower for w in ['habitação', 'casa', 'arrendamento', 'imóvel', 'construção', 'licenciamento']):
        return 'habitação'
    elif any(w in text_lower for w in ['ambiente', 'energia', 'água', 'verde', 'sustentável', 'carbono', 'renovável']):
        return 'ambiente'
    elif any(w in text_lower for w in ['justiça', 'tribunal', 'processo', 'crime', 'penal', 'corrupção']):
        return 'justiça'
    elif any(w in text_lower for w in ['transporte', 'ferroviário', 'mobilidade', 'comboio']):
        return 'transportes'
    elif any(w in text_lower for w in ['digital', 'tecnologia', 'inovação', 'govtech']):
        return 'tecnologia'
    elif any(w in text_lower for w in ['agricultur', 'rural', 'interior', 'mar', 'pesca']):
        return 'agricultura'
    elif any(w in text_lower for w in ['cultura', 'desporto', 'património']):
        return 'cultura'
    elif any(w in text_lower for w in ['segurança', 'polícia', 'protecção', 'defesa']):
        return 'segurança'
    else:
        return 'outros'

def extract_promises():
    """Extract all concrete promises"""
    promises = []

    # Key promise patterns - look for bulleted items and numbered items with concrete content
    lines = text.split('\n')

    for i, line in enumerate(lines):
        line = line.strip()

        # Skip empty or short lines
        if len(line) < 20:
            continue

        # Skip headers and generic lines
        if line.isupper() or len(line.split()) < 5:
            continue

        # Look for:
        # 1) Lines with bullets followed by concrete content
        # 2) Lines with proposal verbs
        # 3) Lines with numbers/percentages

        has_proposal = any(w in line.lower() for w in [
            'propõe', 'propõem', 'defende', 'defendemos', 'criação', 'criar',
            'reforma', 'rever', 'eliminar', 'implementar', 'garantir', 'assegurar',
            'redução', 'aumento', 'descentralizar', 'desburocratizar', 'digitalizar'
        ])

        has_concrete = any(p.search(line) for p in [
            re.compile(r'\d+\s*(?:%|milhões|mil|euros|€)'),
            re.compile(r'(?:até|em|por|durante)\s+\d+\s*(?:anos|meses|dias)'),
            re.compile(r'\b(?:Lei|Código|Fundo|Agência|Programa|Imposto|IRS|IRC|SNS)\b'),
            re.compile(r'\b(?:abolir|rever|fusão|integração|eliminação)\b', re.IGNORECASE)
        ])

        if has_proposal and has_concrete:
            text_clean = normalize_text(line)
            if len(text_clean) > 30 and len(text_clean) <= 300:
                # Get prev/next for context
                prev_context = normalize_text(lines[i-1]) if i > 0 else ""
                next_context = normalize_text(lines[i+1]) if i < len(lines)-1 else ""
                context = (prev_context[:100] + " | " + next_context[:100])[:200]

                topic = classify_topic(text_clean)

                # Calculate confidence
                confidence = 0.25
                if re.search(r'\d+\s*(?:%|milhões|mil|euros)', text_clean):
                    confidence += 0.25
                if re.search(r'(?:até|em|por)\s+\d+', text_clean):
                    confidence += 0.20
                if re.search(r'\b(?:Lei|Código|Fundo|Programa)\b', text_clean):
                    confidence += 0.15
                if re.search(r'\b(?:abolir|rever|eliminar|criar)\b', text_clean, re.IGNORECASE):
                    confidence += 0.15
                confidence = min(confidence, 1.0)

                promises.append({
                    'text': text_clean,
                    'context': context,
                    'topic': topic,
                    'confidence': round(confidence, 2)
                })

    # Deduplicate
    seen = set()
    deduped = []
    for p in promises:
        key = p['text'][:50].lower()
        if key not in seen:
            seen.add(key)
            deduped.append(p)

    return deduped

# Extract
promises = extract_promises()

# Stats
topic_counts = Counter(p['topic'] for p in promises)
conf_counts = Counter(p['confidence'] for p in promises)

print(f"Total promises: {len(promises)}")
print()
print("By topic:")
for t, c in sorted(topic_counts.items(), key=lambda x: -x[1]):
    print(f"  {t}: {c}")
print()
print("By confidence:")
for c in sorted(conf_counts.keys(), reverse=True):
    print(f"  {c}: {conf_counts[c]}")

# Save
output = {
    'source': 'Iniciativa Liberal - Programa Eleitoral Legislativas 2025',
    'tier': 'Tier 2',
    'total_promises': len(promises),
    'date_extraction': '2026-04-20',
    'topic_distribution': dict(topic_counts),
    'confidence_distribution': {str(k): v for k, v in sorted(conf_counts.items(), reverse=True)},
    'promises': promises
}

with open('data/programs/2025/IL-leg-2025.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print()
print(f"Saved to data/programs/2025/IL-leg-2025.json")
print()
print("Sample top promises by confidence:")
for p in sorted(promises, key=lambda x: -x['confidence'])[:5]:
    print(f"  [{p['confidence']}] {p['topic']}: {p['text'][:90]}")
EOF
