import tempfile
import shutil
import json
import re
from pathlib import Path

import sqlparse
from tqdm import tqdm

from deepl_utils import translate_phrase, translate_sentence


def translate_question(question):
    stage1 = translate_sentence(question)
    stage2 = _translate_quotes(stage1)
    return stage2


def translate_query(query):
    statement = sqlparse.parse(query)[0]
    tokens = _find_tokens_to_translate(statement)

    for token in tokens:
        _translate_token(token)
        
    return str(statement)


def _find_tokens_to_translate(statement):
    tokens = [token for token in statement.flatten() if str(token).strip() != '']
    
    tokens_to_translate = []
    for i in range(len(tokens)):
        if str(tokens[i].ttype).startswith('Token.Literal.String'):
            if i > 0 and str(tokens[i-1]).lower() == 'like':
                continue
            tokens_to_translate.append(tokens[i])
        
    return tokens_to_translate


def _translate_token(token):
    assert "'" in token.value or '"' in token.value
    value_en = token.value.strip("'\" ")
    value_pl = translate_phrase(value_en)
    token.value = f'"{value_pl}"'


def _translate_quotes(sentence):
    matches = re.finditer(r"['\"](.*?)['\"]", sentence)
    sentence = list(sentence)
    for match in reversed(list(matches)):
        start, end = match.start(), match.end()
        text = ''.join(sentence[start:end])
        text_pl = translate_phrase(text)
        sentence[start:end] = text_pl
    return ''.join(sentence)
