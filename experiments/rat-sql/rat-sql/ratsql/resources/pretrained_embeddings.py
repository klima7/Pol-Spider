import abc
import functools
import os
import time

import bpemb
import torch
import torchtext
from gensim.models import KeyedVectors

from ratsql.resources import stanza
from ratsql.utils import registry


class Embedder(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def tokenize(self, sentence):
        '''Given a string, return a list of tokens suitable for lookup.'''
        pass

    @abc.abstractmethod
    def untokenize(self, tokens):
        '''Undo tokenize.'''
        pass

    @abc.abstractmethod
    def lookup(self, token):
        '''Given a token, return a vector embedding if token is in vocabulary.

        If token is not in the vocabulary, then return None.'''
        pass

    @abc.abstractmethod
    def contains(self, token):
        pass

    @abc.abstractmethod
    def to(self, device):
        '''Transfer the pretrained embeddings to the given device.'''
        pass


@registry.register('word_emb', 'glove')
class GloVe(Embedder):

    def __init__(self, kind, lemmatize=False):
        cache = os.path.join(os.environ.get('CACHE_DIR', os.getcwd()), '.vector_cache')
        self.glove = torchtext.vocab.GloVe(name=kind, cache=cache)
        self.dim = self.glove.dim
        self.vectors = self.glove.vectors
        self.lemmatize = lemmatize
        self.corenlp_annotators = ['tokenize', 'ssplit']
        if lemmatize:
            self.corenlp_annotators.append('lemma')

    @functools.lru_cache(maxsize=1024)
    def tokenize(self, text):
        ann = stanza.annotate(text)
        keyword = 'lemma' if self.lemmatize else 'text'
        return [tok[keyword].lower() for sent in ann for tok in sent]
    
    @functools.lru_cache(maxsize=1024)
    def tokenize_for_copying(self, text):
        ann = stanza.annotate(text)
        keyword = 'lemma' if self.lemmatize else 'text'
        text = [tok[keyword].lower() for sent in ann for tok in sent]
        text_for_copying = [tok['text'].lower() for sent in ann for tok in sent]
        return text, text_for_copying

    def untokenize(self, tokens):
        return ' '.join(tokens)

    def lookup(self, token):
        i = self.glove.stoi.get(token)
        if i is None:
            return None
        return self.vectors[i]

    def contains(self, token):
        return token in self.glove.stoi

    def to(self, device):
        self.vectors = self.vectors.to(device)


@registry.register('word_emb', 'bpemb')
class BPEmb(Embedder):
    def __init__(self, dim, vocab_size, lang='en'):
        self.bpemb = bpemb.BPEmb(lang=lang, dim=dim, vs=vocab_size)
        self.dim = dim
        self.vectors = torch.from_numpy(self.bpemb.vectors)

    def tokenize(self, text):
        return self.bpemb.encode(text)

    def untokenize(self, tokens):
        return self.bpemb.decode(tokens)

    def lookup(self, token):
        i = self.bpemb.spm.PieceToId(token)
        if i == self.bpemb.spm.unk_id():
            return None
        return self.vectors[i]

    def contains(self, token):
        return self.lookup(token) is not None

    def to(self, device):
        self.vectors = self.vectors.to(device)


@registry.register('word_emb', 'glove_pl')
class GloVePolish(Embedder):

    def __init__(self, lemmatize=False):
        cache = os.path.join(os.environ.get('CACHE_DIR', os.getcwd()), 'glove_polish', 'glove_300_3_polish.txt')
        print('Loading GloVe')
        self.kv = KeyedVectors.load_word2vec_format(cache)
        self.dim = self.kv.vectors.shape[1]
        self.lemmatize = lemmatize

    @functools.lru_cache(maxsize=1024)
    def tokenize(self, text):
        ann = stanza.annotate(text)
        keyword = 'lemma' if self.lemmatize else 'text'
        return [tok[keyword].lower() for sent in ann for tok in sent]
    
    @functools.lru_cache(maxsize=1024)
    def tokenize_for_copying(self, text):
        ann = stanza.annotate(text)
        keyword = 'lemma' if self.lemmatize else 'text'
        text = [tok[keyword].lower() for sent in ann for tok in sent]
        text_for_copying = [tok['text'].lower() for sent in ann for tok in sent]
        return text, text_for_copying

    def untokenize(self, tokens):
        return ' '.join(tokens)

    def lookup(self, token):
        try:
            return torch.from_numpy(self.kv[token])
        except KeyError:
            return None

    def contains(self, token):
        return token in self.kv

    def to(self, device):
        print('Moving GloVePolish to', device)