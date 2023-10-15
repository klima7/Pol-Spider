import deepl


translator = deepl.Translator(input("Enter DeepL API key"))


def translate_sentence(question_en):
    return translator.translate_text(
        question_en,
        source_lang="EN",
        target_lang="PL",
        formality='prefer_less'
    ).text
    
    
def translate_phrase(value_en):
    if value_en.strip() == '':
        return ''
    
    return translator.translate_text(
        value_en,
        source_lang="EN",
        target_lang="PL",
        preserve_formatting=True,
        split_sentences='off',
        formality='prefer_less'
    ).text
