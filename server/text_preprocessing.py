import re
import unicodedata
from num2words import num2words
from dateutil import parser as dateparser

MAX_CHUNK_LENGTH = 500

def convert_currency(text):
    return re.sub(
        r'(\$|\u20ac|\u00a3)(\d+\.?\d*)',
        lambda m: f"{num2words(float(m.group(2)))} {'dollars' if m.group(1) == '$' else 'euros' if m.group(1) == '€' else 'pounds'}",
        text
    )

def convert_percentages(text):
    return re.sub(r'(\d+)%', lambda m: num2words(int(m.group(1))) + " percent", text)

def convert_ordinals(text):
    return re.sub(
        r'\b(\d+)(st|nd|rd|th)\b',
        lambda m: num2words(int(m.group(1)), to='ordinal'), 
        text
    )

def convert_time(text):
    return re.sub(
        r'\b(\d{1,2}):(\d{2})\b',
        lambda m: f"{num2words(int(m.group(1)))} {num2words(int(m.group(2)))}", 
        text
    )

def convert_dates(text):
    date_matches = re.findall(r'\b\d{4}-\d{2}-\d{2}\b', text)
    for date_str in date_matches:
        try:
            dt = dateparser.parse(date_str)
            spoken = dt.strftime('%B %-d, %Y')
            text = text.replace(date_str, spoken)
        except Exception:
            continue
    return text

def split_into_chunks(ssml_text, max_len=MAX_CHUNK_LENGTH):
    sentences = re.split(r'(?<=[.?!])\s+', ssml_text)
    chunks = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) < max_len:
            current += sentence + " "
        else:
            chunks.append(current.strip())
            current = sentence + " "
    if current:
        chunks.append(current.strip())
    return chunks

def preprocess_for_tts(text):

    if not text or not text.strip():
        return []
        
    text = unicodedata.normalize("NFKC", text)
    text = convert_currency(text)
    text = convert_percentages(text)
    text = convert_ordinals(text)
    text = convert_time(text)
    text = convert_dates(text)
    text = re.sub(r'\b\d+\b', lambda x: num2words(int(x.group())), text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    if not text.endswith(('.', '?', '!')):
        text += '.'
        
    return split_into_chunks(text)