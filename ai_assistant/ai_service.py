import logging
import json
import re
from django.conf import settings

logger = logging.getLogger('ai_assistant')


def _truncate_text(text, max_chars=4000):
    """Truncate text for API calls."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + '\n...[truncated]'


def generate_summary_with_ai(text, title=''):
    """
    Generate a summary using LLM API if configured, else use fallback extraction.
    Returns dict with: summary, key_points, suggested_tags, suggested_category,
                       is_ai_generated, model_used, fallback_reason
    """
    if settings.LLM_API_KEY:
        try:
            return _call_llm_for_summary(text, title)
        except Exception as e:
            logger.error(f'LLM summary failed, using fallback: {e}')
            return _fallback_summary(text, title, fallback_reason=str(e))
    else:
        return _fallback_summary(text, title, fallback_reason='No LLM API key configured.')


def generate_tags_with_ai(text, title=''):
    """
    Generate tags using LLM API if configured, else use fallback keyword extraction.
    Returns dict with: tags, is_ai_generated
    """
    if settings.LLM_API_KEY:
        try:
            return _call_llm_for_tags(text, title)
        except Exception as e:
            logger.error(f'LLM tag generation failed, using fallback: {e}')
            return _fallback_tags(text, title)
    else:
        return _fallback_tags(text, title)


def _call_llm_for_summary(text, title=''):
    """Call LLM API (OpenAI-compatible) for summarisation."""
    import urllib.request
    import urllib.error

    truncated = _truncate_text(text, 4000)
    prompt = f"""Analyze the following document and provide:
1. A concise summary (2-4 sentences)
2. Up to 5 key points as a bullet list
3. Up to 8 relevant tags (single words or short phrases)
4. A suggested category (one of: Finance, Legal, HR, Technical, Marketing, Operations, Research, General)

Document title: {title}

Document content:
{truncated}

Respond in valid JSON format:
{{
  "summary": "...",
  "key_points": ["point1", "point2", ...],
  "suggested_tags": ["tag1", "tag2", ...],
  "suggested_category": "..."
}}"""

    payload = json.dumps({
        'model': settings.LLM_MODEL,
        'messages': [
            {'role': 'system', 'content': 'You are a document analysis assistant. Always respond with valid JSON.'},
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.3,
        'max_tokens': 1000,
    }).encode('utf-8')

    req = urllib.request.Request(
        f'{settings.LLM_API_BASE}/chat/completions',
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {settings.LLM_API_KEY}',
        },
        method='POST'
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode('utf-8'))

    content = result['choices'][0]['message']['content']
    # Extract JSON from response
    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    if json_match:
        data = json.loads(json_match.group())
    else:
        data = json.loads(content)

    return {
        'summary': data.get('summary', ''),
        'key_points': data.get('key_points', []),
        'suggested_tags': data.get('suggested_tags', []),
        'suggested_category': data.get('suggested_category', ''),
        'is_ai_generated': True,
        'model_used': settings.LLM_MODEL,
        'fallback_reason': '',
    }


def _call_llm_for_tags(text, title=''):
    """Call LLM API for tag generation."""
    import urllib.request

    truncated = _truncate_text(text, 2000)
    prompt = f"""Extract up to 10 relevant tags/keywords from this document.
Title: {title}
Content: {truncated}

Respond with JSON: {{"tags": ["tag1", "tag2", ...]}}"""

    payload = json.dumps({
        'model': settings.LLM_MODEL,
        'messages': [
            {'role': 'system', 'content': 'You are a document tagging assistant. Always respond with valid JSON.'},
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.2,
        'max_tokens': 200,
    }).encode('utf-8')

    req = urllib.request.Request(
        f'{settings.LLM_API_BASE}/chat/completions',
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {settings.LLM_API_KEY}',
        },
        method='POST'
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode('utf-8'))

    content = result['choices'][0]['message']['content']
    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    data = json.loads(json_match.group() if json_match else content)
    return {'tags': data.get('tags', []), 'is_ai_generated': True}


def _fallback_summary(text, title='', fallback_reason=''):
    """Fallback: extract summary using simple NLP heuristics."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s.strip() for s in sentences if len(s.strip()) > 30]

    summary = ' '.join(sentences[:3]) if sentences else (text[:500] if text else 'No content available.')

    # Key points: first 5 meaningful sentences
    key_points = sentences[3:8] if len(sentences) > 3 else sentences[:5]

    # Tags: extract frequent meaningful words
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    stopwords = {'this', 'that', 'with', 'from', 'have', 'been', 'will', 'more', 'they',
                 'their', 'there', 'were', 'when', 'what', 'which', 'your', 'about',
                 'also', 'into', 'than', 'then', 'them', 'these', 'some', 'such',
                 'each', 'just', 'over', 'both', 'only', 'after', 'before', 'through'}
    word_freq = {}
    for w in words:
        if w not in stopwords:
            word_freq[w] = word_freq.get(w, 0) + 1
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    suggested_tags = [w for w, _ in sorted_words[:8]]

    return {
        'summary': summary,
        'key_points': key_points,
        'suggested_tags': suggested_tags,
        'suggested_category': 'General',
        'is_ai_generated': False,
        'model_used': 'fallback-heuristic',
        'fallback_reason': fallback_reason,
    }


def _fallback_tags(text, title=''):
    """Fallback: keyword extraction for tags."""
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    stopwords = {'this', 'that', 'with', 'from', 'have', 'been', 'will', 'more',
                 'they', 'their', 'there', 'were', 'when', 'what', 'which', 'your'}
    word_freq = {}
    for w in words:
        if w not in stopwords:
            word_freq[w] = word_freq.get(w, 0) + 1
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return {'tags': [w for w, _ in sorted_words[:10]], 'is_ai_generated': False}
