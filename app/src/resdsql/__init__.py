from .schema_item_classifier import load_classifier_models
from .text2sql import load_text2sql_models
from .predict import predict_sql


__all__ = ['ResdsqlModel']


class ResdsqlModel:
    
    def __init__(
            self,
            classifier_path,
            text2sql_path,
            classifier_device,
            text2sql_device,
            num_beams=8,
            num_return_sequences=8
        ):
        self.classifier_models = load_classifier_models(classifier_path, classifier_device)
        self.text2sql_models = load_text2sql_models(text2sql_path, text2sql_device)
        self.num_beams = num_beams
        self.num_return_sequences = num_return_sequences
        
    def __call__(self, question, db_path, sem_names=None, seed=None):
        return predict_sql(
            self.classifier_models,
            self.text2sql_models,
            question,
            db_path,
            sem_names,
            self.num_beams,
            self.num_return_sequences,
            seed,
        )
