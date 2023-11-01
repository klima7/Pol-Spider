import os
import sys

import requests
import stanza


class CoreNLP:
    def __init__(self):
        self.nlps = {}

    def annotate(self, text, lang='en'):
        nlp = self._get_nlp(lang)
        doc = nlp(text)
        return self._get_result(doc)
    
    def _get_nlp(self, lang):
        if lang not in self.nlps:
            stanza.download(lang)
            nlp = stanza.Pipeline(lang, processors=['tokenize', 'mwt', 'lemma'], use_gpu=False) 
            self.nlps[lang] = nlp
        return self.nlps[lang]
    
    def _get_result(self, doc):
        results = []
        for sentence in doc.sentences:
            sentence_result = []
            results.append(sentence_result)
            for tokens in sentence.tokens:
                tokens = tokens.to_dict()
                if len(tokens) == 1:
                    sentence_result.append({
                        'text': tokens[0]['text'],
                        'lemma': tokens[0]['lemma'],
                    })
                elif len(tokens) > 1:
                    sentence_result.append({
                        'text': tokens[0]['text'],
                        'lemma': tokens[1]['lemma'],
                    })
        return results
        

_singleton = None


def annotate(text, lang='en'):
    global _singleton
    if not _singleton:
        _singleton = CoreNLP()
    return _singleton.annotate(text, lang)
