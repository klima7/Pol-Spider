import re

from deepl_utils import translate_sentence


def translate_name(name, container_name, other_container_name=None):
    container_name = re.sub(r'[^a-zA-Z ]', ' ', container_name)
    if not other_container_name:
        text = f"{name} (from {container_name})"
    else:
        other_container_name = re.sub(r'[^a-zA-Z ]', ' ', other_container_name)
        text = f"{name} (from {container_name} and {other_container_name})"
    text_pl = translate_sentence(text)
    paren_idx = text_pl.index('(')
    return text_pl[:paren_idx].strip()


def translate_original_name(name, container, other_container=None):
    natural_text_en = name.replace('_', ' ')
    was_titled = all(word[0]==word[0].upper() and word[1:]==word[1:].lower() for word in natural_text_en.split(' '))
    natural_text_pl = translate_name(natural_text_en, container, other_container)
    if was_titled:
        natural_text_pl = natural_text_pl.title()
    return natural_text_pl.replace(' ', "_")
