set -e

# preprocess train_cspider dataset
python preprocessing.py \
    --mode "train" \
    --table_path "./data/pol-spider-train/tables.json" \
    --input_dataset_path "./data/pol-spider-train/train.json" \
    --output_dataset_path "./data/preprocessed_data/preprocessed_train_polspider.json" \
    --db_path "./data/pol-spider-train/database" \
    --target_type "sql"

# preprocess dev dataset
python preprocessing.py \
    --mode "eval" \
    --table_path "./data/pol-spider-train/tables.json" \
    --input_dataset_path "./data/pol-spider-train/dev.json" \
    --output_dataset_path "./data/preprocessed_data/preprocessed_dev_polspider.json" \
    --db_path "./data/pol-spider-train/database" \
    --target_type "sql"