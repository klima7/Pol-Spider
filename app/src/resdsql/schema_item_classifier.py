import os
import json
import torch

from copy import deepcopy
from torch.utils.data import DataLoader
from transformers import XLMRobertaTokenizerFast
from transformers.trainer_utils import set_seed

from .utils.classifier_model import MyClassifier
from .utils.load_dataset import ColumnAndTableClassifierDataset


def load_classifier_models(save_path, device=None):
    if device:
        os.environ["CUDA_VISIBLE_DEVICES"] = device
    
    # load tokenizer
    tokenizer = XLMRobertaTokenizerFast.from_pretrained(
        save_path,
        add_prefix_space = True,
        torch_dtype=torch.float16,
    )
    
    # initialize model
    model = MyClassifier(
        model_name_or_path = save_path,
        vocab_size = len(tokenizer),
        mode = 'test',
    )
    
    # load fine-tuned params
    model.load_state_dict(torch.load(save_path + "/dense_classifier.pt", map_location=torch.device('cpu')))
    if torch.cuda.is_available():
        model = model.cuda()
    model.eval()
    
    return tokenizer, model

    
def prepare_batch_inputs_and_labels(batch, tokenizer):
    batch_size = len(batch)
    
    batch_questions = [data[0] for data in batch]
    
    batch_table_names = [data[1] for data in batch]
    batch_table_labels = [data[2] for data in batch]

    batch_column_infos = [data[3] for data in batch]
    batch_column_labels = [data[4] for data in batch]
    
    batch_input_tokens, batch_column_info_ids, batch_table_name_ids, batch_column_number_in_each_table = [], [], [], []
    for batch_id in range(batch_size):
        input_tokens = [batch_questions[batch_id]]
        table_names_in_one_db = batch_table_names[batch_id]
        column_infos_in_one_db = batch_column_infos[batch_id]

        batch_column_number_in_each_table.append([len(column_infos_in_one_table) for column_infos_in_one_table in column_infos_in_one_db])

        column_info_ids, table_name_ids = [], []
        
        for table_id, table_name in enumerate(table_names_in_one_db):
            input_tokens.append("|")
            input_tokens.append(table_name)
            table_name_ids.append(len(input_tokens) - 1)
            input_tokens.append(":")
            
            for column_info in column_infos_in_one_db[table_id]:
                input_tokens.append(column_info)
                column_info_ids.append(len(input_tokens) - 1)
                input_tokens.append(",")
            
            input_tokens = input_tokens[:-1]
        
        batch_input_tokens.append(input_tokens)
        batch_column_info_ids.append(column_info_ids)
        batch_table_name_ids.append(table_name_ids)

    # notice: the trunction operation will discard some tables and columns that exceed the max length
    tokenized_inputs = tokenizer(
        batch_input_tokens, 
        return_tensors="pt", 
        is_split_into_words = True, 
        padding = "max_length",
        max_length = 512,
        truncation = True
    )

    batch_aligned_question_ids, batch_aligned_column_info_ids, batch_aligned_table_name_ids = [], [], []
    batch_aligned_table_labels, batch_aligned_column_labels = [], []
    
    # align batch_question_ids, batch_column_info_ids, and batch_table_name_ids after tokenizing
    for batch_id in range(batch_size):
        word_ids = tokenized_inputs.word_ids(batch_index = batch_id)

        aligned_question_ids, aligned_table_name_ids, aligned_column_info_ids = [], [], []
        aligned_table_labels, aligned_column_labels = [], []

        # align question tokens
        for token_id, word_id in enumerate(word_ids):
            if word_id == 0:
                aligned_question_ids.append(token_id)

        # align table names
        for t_id, table_name_id in enumerate(batch_table_name_ids[batch_id]):
            temp_list = []
            for token_id, word_id in enumerate(word_ids):
                if table_name_id == word_id:
                    temp_list.append(token_id)
            # if the tokenizer doesn't discard current table name
            if len(temp_list) != 0:
                aligned_table_name_ids.append(temp_list)
                aligned_table_labels.append(batch_table_labels[batch_id][t_id])

        # align column names
        for c_id, column_id in enumerate(batch_column_info_ids[batch_id]):
            temp_list = []
            for token_id, word_id in enumerate(word_ids):
                if column_id == word_id:
                    temp_list.append(token_id)
            # if the tokenizer doesn't discard current column name
            if len(temp_list) != 0:
                aligned_column_info_ids.append(temp_list)
                aligned_column_labels.append(batch_column_labels[batch_id][c_id])

        batch_aligned_question_ids.append(aligned_question_ids)
        batch_aligned_table_name_ids.append(aligned_table_name_ids)
        batch_aligned_column_info_ids.append(aligned_column_info_ids)
        batch_aligned_table_labels.append(aligned_table_labels)
        batch_aligned_column_labels.append(aligned_column_labels)

    # update column number in each table (because some tables and columns are discarded)
    for batch_id in range(batch_size):
        if len(batch_column_number_in_each_table[batch_id]) > len(batch_aligned_table_labels[batch_id]):
            batch_column_number_in_each_table[batch_id] = batch_column_number_in_each_table[batch_id][ : len(batch_aligned_table_labels[batch_id])]
        
        if sum(batch_column_number_in_each_table[batch_id]) > len(batch_aligned_column_labels[batch_id]):
            truncated_column_number = sum(batch_column_number_in_each_table[batch_id]) - len(batch_aligned_column_labels[batch_id])
            batch_column_number_in_each_table[batch_id][-1] -= truncated_column_number

    encoder_input_ids = tokenized_inputs["input_ids"]
    encoder_input_attention_mask = tokenized_inputs["attention_mask"]
    batch_aligned_column_labels = [torch.LongTensor(column_labels) for column_labels in batch_aligned_column_labels]
    batch_aligned_table_labels = [torch.LongTensor(table_labels) for table_labels in batch_aligned_table_labels]

    # print("\n".join(tokenizer.batch_decode(encoder_input_ids, skip_special_tokens = True)))

    if torch.cuda.is_available():
        encoder_input_ids = encoder_input_ids.cuda()
        encoder_input_attention_mask = encoder_input_attention_mask.cuda()
        batch_aligned_column_labels = [column_labels.cuda() for column_labels in batch_aligned_column_labels]
        batch_aligned_table_labels = [table_labels.cuda() for table_labels in batch_aligned_table_labels]

    return encoder_input_ids, encoder_input_attention_mask, \
        batch_aligned_column_labels, batch_aligned_table_labels, \
        batch_aligned_question_ids, batch_aligned_column_info_ids, \
        batch_aligned_table_name_ids, batch_column_number_in_each_table


def _test(models, dev_filepath, use_contents, add_fk_info, batch_size, seed):
    tokenizer, model = models
    
    if seed:
        set_seed(seed)
    
    dataset = ColumnAndTableClassifierDataset(
        dir_ = dev_filepath,
        use_contents = use_contents,
        add_fk_info = add_fk_info
    )

    dataloder = DataLoader(
        dataset,
        batch_size = batch_size,
        shuffle = False,
        collate_fn = lambda x: x
    )

    table_labels_for_auc, column_labels_for_auc = [], []
    table_pred_probs_for_auc, column_pred_probs_for_auc = [], []

    returned_table_pred_probs, returned_column_pred_probs = [], []

    for batch in dataloder:
        encoder_input_ids, encoder_input_attention_mask, \
            batch_column_labels, batch_table_labels, batch_aligned_question_ids, \
            batch_aligned_column_info_ids, batch_aligned_table_name_ids, \
            batch_column_number_in_each_table = prepare_batch_inputs_and_labels(batch, tokenizer)

        with torch.no_grad():
            model_outputs = model(
                encoder_input_ids,
                encoder_input_attention_mask,
                batch_aligned_question_ids,
                batch_aligned_column_info_ids,
                batch_aligned_table_name_ids,
                batch_column_number_in_each_table
            )
        
        for batch_id, table_logits in enumerate(model_outputs["batch_table_name_cls_logits"]):
            table_pred_probs = torch.nn.functional.softmax(table_logits, dim = 1)
            returned_table_pred_probs.append(table_pred_probs[:, 1].cpu().tolist())
            
            table_pred_probs_for_auc.extend(table_pred_probs[:, 1].cpu().tolist())
            table_labels_for_auc.extend(batch_table_labels[batch_id].cpu().tolist())

        for batch_id, column_logits in enumerate(model_outputs["batch_column_info_cls_logits"]):
            column_number_in_each_table = batch_column_number_in_each_table[batch_id]
            column_pred_probs = torch.nn.functional.softmax(column_logits, dim = 1)
            returned_column_pred_probs.append([column_pred_probs[:, 1].cpu().tolist()[sum(column_number_in_each_table[:table_id]):sum(column_number_in_each_table[:table_id+1])] \
                for table_id in range(len(column_number_in_each_table))])
            
            column_pred_probs_for_auc.extend(column_pred_probs[:, 1].cpu().tolist())
            column_labels_for_auc.extend(batch_column_labels[batch_id].cpu().tolist())
    
    return returned_table_pred_probs, returned_column_pred_probs


def classify_schema_items(models, mode, dev_filepath, output_filepath, use_contents, add_fk_info, batch_size=1, seed=None):
    if mode in ["eval", "test"]:
        total_table_pred_probs, total_column_pred_probs = _test(models, dev_filepath, use_contents, add_fk_info, batch_size, seed)
        
        with open(dev_filepath, "r") as f:
            dataset = json.load(f)
        
        # record predicted probability
        truncated_data_info = []
        for data_id, data in enumerate(dataset):
            table_num = len(data["table_labels"])
            if table_num == len(total_table_pred_probs[data_id]):
                table_pred_probs = total_table_pred_probs[data_id]
            else:
                table_pred_probs = total_table_pred_probs[data_id] + [-1 for _ in range(table_num-len(total_table_pred_probs[data_id]))]
            
            truncated_table_ids = []
            column_pred_probs = []
            for table_id in range(table_num):
                if table_id >= len(total_column_pred_probs[data_id]):
                    truncated_table_ids.append(table_id)
                    column_pred_probs.append([-1 for _ in range(len(data["column_labels"][table_id]))])
                    continue
                if len(total_column_pred_probs[data_id][table_id]) == len(data["column_labels"][table_id]):
                    column_pred_probs.append(total_column_pred_probs[data_id][table_id])
                else:
                    truncated_table_ids.append(table_id)
                    truncated_column_num = len(data["column_labels"][table_id]) - len(total_column_pred_probs[data_id][table_id])
                    column_pred_probs.append(total_column_pred_probs[data_id][table_id] + [-1 for _ in range(truncated_column_num)])
            
            data["column_pred_probs"] = column_pred_probs
            data["table_pred_probs"] = table_pred_probs
            
            if len(truncated_table_ids) > 0:
                truncated_data_info.append([data_id, truncated_table_ids])

        # additionally, we need to consider and predict discarded tables and columns
        while len(truncated_data_info) != 0:
            truncated_dataset = []
            for truncated_data_id, truncated_table_ids in truncated_data_info:
                print(dataset[truncated_data_id]["question"])
                truncated_data = deepcopy(dataset[truncated_data_id])
                truncated_data["db_schema"] = [truncated_data["db_schema"][table_id] for table_id in truncated_table_ids]
                truncated_data["table_labels"] = [truncated_data["table_labels"][table_id] for table_id in truncated_table_ids]
                truncated_data["column_labels"] = [truncated_data["column_labels"][table_id] for table_id in truncated_table_ids]
                truncated_data["table_pred_probs"] = [truncated_data["table_pred_probs"][table_id] for table_id in truncated_table_ids]
                truncated_data["column_pred_probs"] = [truncated_data["column_pred_probs"][table_id] for table_id in truncated_table_ids]
                
                truncated_dataset.append(truncated_data)
            
            with open("./data/pre-processing/truncated_dataset.json", "w") as f:
                f.write(json.dumps(truncated_dataset, indent = 2, ensure_ascii = False))
            
            dev_filepath = "./data/pre-processing/truncated_dataset.json"
            total_table_pred_probs, total_column_pred_probs = _test(models, dev_filepath, use_contents, add_fk_info, batch_size, seed)
            
            for data_id, data in enumerate(truncated_dataset):
                table_num = len(data["table_labels"])
                if table_num == len(total_table_pred_probs[data_id]):
                    table_pred_probs = total_table_pred_probs[data_id]
                else:
                    table_pred_probs = total_table_pred_probs[data_id] + [-1 for _ in range(table_num-len(total_table_pred_probs[data_id]))]

                column_pred_probs = []
                for table_id in range(table_num):
                    if table_id >= len(total_column_pred_probs[data_id]):
                        column_pred_probs.append([-1 for _ in range(len(data["column_labels"][table_id]))])
                        continue
                    if len(total_column_pred_probs[data_id][table_id]) == len(data["column_labels"][table_id]):
                        column_pred_probs.append(total_column_pred_probs[data_id][table_id])
                    else:
                        truncated_column_num = len(data["column_labels"][table_id]) - len(total_column_pred_probs[data_id][table_id])
                        column_pred_probs.append(total_column_pred_probs[data_id][table_id] + [-1 for _ in range(truncated_column_num)])
                
                # fill the predicted probability into the dataset
                truncated_data_id = truncated_data_info[data_id][0]
                truncated_table_ids = truncated_data_info[data_id][1]
                for idx, truncated_table_id in enumerate(truncated_table_ids):
                    dataset[truncated_data_id]["table_pred_probs"][truncated_table_id] = table_pred_probs[idx]
                    dataset[truncated_data_id]["column_pred_probs"][truncated_table_id] = column_pred_probs[idx]
            
            # check if there are tables and columns in the new dataset that have not yet been predicted
            truncated_data_info = []
            for data_id, data in enumerate(dataset):
                table_num = len(data["table_labels"])

                truncated_table_ids = []
                for table_id in range(table_num):
                    # the current table is not predicted
                    if data["table_pred_probs"][table_id] == -1:
                        truncated_table_ids.append(table_id)
                    # some columns in the current table are not predicted
                    if data["table_pred_probs"][table_id] != -1 and -1 in data["column_pred_probs"][table_id]:
                        truncated_table_ids.append(table_id)
                
                if len(truncated_table_ids) > 0:
                    truncated_data_info.append([data_id, truncated_table_ids])
            
            os.remove("./data/pre-processing/truncated_dataset.json")

        with open(output_filepath, "w") as f:
            f.write(json.dumps(dataset, indent = 2, ensure_ascii = False))
