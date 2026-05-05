#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extractor of electoral promises from IL 2025 electoral program
Tier 2 source document
"""

import json
import re
from typing import List, Dict, Optional
import sys

# Read the file
with open('data/programs/2025/IL-leg-2025.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Define patterns that indicate a concrete promise (Tier 2+ criteria)
PROMISE_PATTERNS = [
    # Numbers/percentages
    r'\d+\s*(?:%|milhões|euros|mil)',
    # Reduction/increase verbs with specifics
    r'(?:reduzir|eliminar|criar|aumentar|expandir|desenvolver|implementar|rever)\s+(?:[^.]+?)(?:para|até|em)',
    # Laws/measures mentioned
    r'(?:lei|decreto|código|reforma|programa|fundo|imposto)',
    # Specific terms indicating action
    r'(?:abolir|desburocratizar|descentralizar|digitalizar|fusão|integração)',
]

promises = []

# Split into sentences
sentences = re.split(r'(?<=[.!?])\s+', text)

for i, sentence in enumerate(sentences):
    # Clean sentence
    sentence = sentence.strip()
    if len(sentence) < 20:
        continue

    # Check if matches any promise pattern
    has_promise = any(re.search(pattern, sentence, re.IGNORECASE) for pattern in PROMISE_PATTERNS)

    if has_promise and any(keyword in sentence.lower() for keyword in ['propõe', 'propõem', 'defender', 'defende', 'objetivo', 'meta', 'garantir', 'assegurar']):
        # Extract context (previous/next sentence)
        prev_context = sentences[i-1] if i > 0 else ""
        next_context = sentences[i+1] if i < len(sentences) - 1 else ""

        # Try to classify topic
        topic = classify_topic(sentence)

        # Calculate confidence
        confidence = calculate_confidence(sentence)

        if len(sentence) <= 300:
            promises.append({
                'text': sentence,
                'context': (prev_context[:100] + ' | ' + next_context[:100])[:200],
                'topic': topic,
                'confidence': confidence
            })

def classify_topic(text: str) -> str:
    """Classify promise into one of the predefined topics"""
    topics = {
        'administração pública': ['estado', 'administração', 'burocracia', 'desburocratizar', 'funcionários'],
        'saúde': ['saúde', 'médico', 'hospitais', 'medicamentos', 'doentes'],
        'educação': ['educação', 'escolas', 'alunos', 'ensino', 'universidade'],
        'economia': ['economia', 'impostos', 'fiscal', 'irc', 'irs', 'carga fiscal'],
        'emprego': ['trabalho', 'emprego', 'salários', 'contrato'],
        'habitação': ['habitação', 'casas', 'arrendamento', 'imóvel'],
        'ambiente': ['ambiente', 'energia', 'água', 'verde'],
        'segurança': ['segurança', 'polícia', 'protecção'],
        'justiça': ['justiça', 'tribunais', 'processos'],
        'transportes': ['transportes', 'ferroviário', 'mobilidade'],
        'outros': []
    }

    text_lower = text.lower()
    for topic, keywords in topics.items():
        if topic == 'outros':
            continue
        if any(keyword in text_lower for keyword in keywords):
            return topic
    return 'outros'

def calculate_confidence(text: str) -> float:
    """Calculate confidence score 0.0-1.0 based on specificity"""
    score = 0.0

    # Numbers/values (high confidence)
    if re.search(r'\d+\s*(?:%|milhões|mil|euros)', text):
        score += 0.3

    # Specific timeframes
    if re.search(r'(?:até|por|durante)\s+\d+\s*(?:anos|meses)', text):
        score += 0.2

    # Concrete actions/verbs
    if re.search(r'(?:abolir|rever|eliminar|criar|implementar|fusão)', text, re.IGNORECASE):
        score += 0.2

    # Named laws/institutions
    if re.search(r'(?:lei|código|decreto|fundo|imposto|ministério)', text, re.IGNORECASE):
        score += 0.15

    # Reduction/increase with targets
    if re.search(r'(?:reduzir|aumentar|expandir|cortar)\s+[^.]*(?:em|para|até)\s*\d+', text):
        score += 0.15

    return min(score, 1.0)

# Print stats
print(f"Total promises extracted: {len(promises)}")
print(f"By topic:")
from collections import Counter
topic_dist = Counter(p['topic'] for p in promises)
for topic, count in sorted(topic_dist.items(), key=lambda x: -x[1]):
    print(f"  {topic}: {count}")

print(f"\nBy confidence:")
conf_dist = Counter(round(p['confidence'], 1) for p in promises)
for conf, count in sorted(conf_dist.items(), key=lambda x: -x[1]):
    print(f"  {conf}: {count}")

# Save to JSON
output = {
    'source': 'IL - Legislativas 2025',
    'tier': 'Tier 2 (official electoral program)',
    'total_promises': len(promises),
    'promises': promises
}

with open('data/programs/2025/IL-leg-2025.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nSaved to data/programs/2025/IL-leg-2025.json")
