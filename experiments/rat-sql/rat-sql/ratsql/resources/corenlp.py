import os
import sys

import requests
import stanza


class CoreNLP:
    def __init__(self):
        self.nlps = {}

    def annotate(self, text, lang='en'):
        nlp = self._get_nlp(lang)
        return nlp(text).to_dict()
    
    def _get_nlp(self, lang):
        if lang not in self.nlps:
            stanza.download(lang)
            nlp = stanza.Pipeline(lang, processors=['tokenize', 'mwt', 'lemma'], use_gpu=False) 
            self.nlps[lang] = nlp
        return self.nlps[lang]
        

_singleton = None


def annotate(text, lang='en'):
    global _singleton
    if not _singleton:
        _singleton = CoreNLP()
    return _singleton.annotate(text, lang)
