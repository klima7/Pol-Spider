import os
import torch

from tqdm import tqdm
from tokenizers import AddedToken

from torch.utils.data import DataLoader
from transformers import T5TokenizerFast, MT5ForConditionalGeneration
from transformers.trainer_utils import set_seed

from .utils.load_dataset import Text2SQLDataset
from .utils.text2sql_decoding_utils import decode_sqls


def load_models(save_path, device):
    os.environ["CUDA_VISIBLE_DEVICES"] = device

    # initialize tokenizer
    tokenizer = T5TokenizerFast.from_pretrained(
        save_path,
        add_prefix_space = True,
        torch_dtype=torch.float16
    )
    
    if isinstance(tokenizer, T5TokenizerFast):
        tokenizer.add_tokens([AddedToken(" <="), AddedToken(" <")])
        
    model_class = MT5ForConditionalGeneration

    # initialize model
    model = model_class.from_pretrained(save_path)
    if torch.cuda.is_available():
        model = model.cuda()

    model.eval()
    
    return tokenizer, model


tokenizer, model = load_models('/app/models/generator', "0")


def generate_sql(
        batch_size=8,
        seed=42,
        mode="train",
        dev_filepath="data/preprocessed_data/resdsql_dev.json",
        db_path="database",
        num_beams=8,
        num_return_sequences=8,
        target_type="sql",
        output="predicted_sql.txt",
    ):
    set_seed(seed)

    import time
    start_time = time.time()
    
    dev_dataset = Text2SQLDataset(
        dir_ = dev_filepath,
        mode = mode
    )

    dev_dataloder = DataLoader(
        dev_dataset, 
        batch_size = batch_size, 
        shuffle = False,
        collate_fn = lambda x: x,
        drop_last = False
    )

    predict_sqls = []
    for batch in tqdm(dev_dataloder):
        batch_inputs = [data[0] for data in batch]
        batch_db_ids = [data[1] for data in batch]
        batch_tc_original = [data[2] for data in batch]

        tokenized_inputs = tokenizer(
            batch_inputs, 
            return_tensors="pt",
            padding = "max_length",
            max_length = 512,
            truncation = True
        )
        
        encoder_input_ids = tokenized_inputs["input_ids"]
        encoder_input_attention_mask = tokenized_inputs["attention_mask"]
        if torch.cuda.is_available():
            encoder_input_ids = encoder_input_ids.cuda()
            encoder_input_attention_mask = encoder_input_attention_mask.cuda()

        with torch.no_grad():
            model_outputs = model.generate(
                input_ids = encoder_input_ids,
                attention_mask = encoder_input_attention_mask,
                max_length = 256,
                decoder_start_token_id = model.config.decoder_start_token_id,
                num_beams = num_beams,
                num_return_sequences = num_return_sequences
            )

            model_outputs = model_outputs.view(len(batch_inputs), num_return_sequences, model_outputs.shape[1])
            if target_type == "sql":
                predict_sqls += decode_sqls(
                    db_path, 
                    model_outputs, 
                    batch_db_ids, 
                    batch_inputs, 
                    tokenizer, 
                    batch_tc_original
                )
            else:
                raise ValueError()
    
    new_dir = "/".join(output.split("/")[:-1]).strip()
    if new_dir != "":
        os.makedirs(new_dir, exist_ok = True)
    
    # save results
    with open(output, "w", encoding = 'utf-8') as f:
        for pred in predict_sqls:
            f.write(pred + "\n")
    
    end_time = time.time()
    print("Text-to-SQL inference spends {}s.".format(end_time-start_time))