from pathlib import Path

from common import load_json, save_json, sort_dict
from common.constants import *


class Dataset:
    
    def __init__(self, train_spider=None, train_others=None, dev=None):
        self.splits_dict = {
            'train_spider': train_spider,
            'train_others': train_others,
            'dev': dev
        }
        
    @classmethod
    def load(cls, dir_path):
        dir_path = Path(dir_path)
        return cls(
            train_spider = cls._load_aux(dir_path / 'train_spider.json'),
            train_others = cls._load_aux(dir_path / 'train_others.json'),
            dev = cls._load_aux(dir_path / 'dev.json')
        )
        
    @classmethod
    def load_by_name(cls, name):
        path = SAMPLES_PATH / name
        if not path.exists():
            raise Exception(f"Unable to find dataset named '{name}'")
        return cls.load(path)
        
    @staticmethod
    def _load_aux(path):
        if path.exists():
            return Samples.load(path)
        else:
            return None
        
    def __repr__(self):
        train_spider = len(self.train_spider) if self.train_spider else 0
        train_others = len(self.train_others) if self.train_others else 0
        dev = len(self.dev) if self.dev else 0
        return f'<Dataset spider:{train_spider}, others:{train_others}, dev:{dev}>'
        
    def __getitem__(self, split_name):
        return self.splits_dict[split_name]
    
    def __iter__(self):
        return iter(self.splits_names)
    
    @property
    def splits_names(self):
        return [split_name for split_name, split in self.splits_dict.items() if split is not None]
        
    @property
    def train_spider(self):
        return self.splits_dict['train_spider']
    
    @property
    def train_others(self):
        return self.splits_dict['train_others']
    
    @property
    def dev(self):
        return self.splits_dict['dev']
        
    @property
    def train(self):
        train_samples = []
        for samples in [self.train_spider, self.train_others]:
            if samples:
                train_samples.extend(samples)
        return Samples(train_samples)
    
    def save(self, path):
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        for split_name in self.splits_names:
            save_json(path / (split_name + '.json'), self[split_name].to_json())
            
    def save_by_name(self, name):
        self.save(SAMPLES_PATH / name)
        
        

class Samples:
    
    def __init__(self, samples):
        self.samples = samples
        
    @classmethod
    def from_json(cls, samples_json):
        samples = [Sample(sample_json) for sample_json in samples_json]
        return cls(samples)
        
    @classmethod
    def load(cls, path):
        samples_json = load_json(path)
        return cls.from_json(samples_json)
        
    def __getitem__(self, key):
        return self.samples[key]
    
    def __iter__(self):
        return iter(self.samples)
    
    def __len__(self):
        return len(self.samples)
    
    def __repr__(self):
        return f'<{len(self.samples)} Samples>'
    
    def to_json(self):
        return [sample.to_json() for sample in self.samples]
    
    def save(self, path):
        save_json(path, self.to_json())


class Sample:
    
    def __init__(self, sample_json):
        self.db_id = sample_json['db_id']
        self.question = sample_json['question']
        self.query = sample_json['query']
        self.extras = {
            key: value for key, value in sample_json.items() 
            if key not in ['db_id', 'question', 'query']
        }
        
    def __repr__(self):
        return f'<Sample>'
        
    def to_json(self):
        json = {}
        json['db_id'] = self.db_id
        for extra_key in self.extras:
            json[extra_key] = self.extras[extra_key]
        json['question'] = sort_dict(self.question)
        json['query'] = sort_dict(self.query)
        return json
