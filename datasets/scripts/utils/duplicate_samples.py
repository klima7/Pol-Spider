import re

from common import load_json, save_json


def normalize_question(question):
    question_norm = question.lower().strip()
    question_norm = re.sub(r"\s+", " ", question_norm)
    return question_norm


def deduplicate_samples(samples):
    deduplicated_samples = {}
    
    for sample in samples:
        db_id = sample['db_id']
        question = normalize_question(sample['question'])
        key = (db_id, question)
        if key not in deduplicated_samples.keys():
            deduplicated_samples[key] = sample
    deduplicated_samples = list(deduplicated_samples.values())
    
    initial_size = len(samples)
    deduplicated_size = len(deduplicated_samples)
    
    print('Initial size:', initial_size)
    print('Deduplicated size:', deduplicated_size)
    print('Removed', initial_size - deduplicated_size, 'samples')
    
    return deduplicated_samples
    
    
def deduplicate_and_save(path):
    samples = load_json(path)
    deduplciated_samples = deduplicate_samples(samples)
    save_json(path, deduplciated_samples)
