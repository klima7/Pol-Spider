set -e

# train text2sql-mt5-large (CSpider version) model
python -u text2sql.py \
    --batch_size 1 \
    --gradient_descent_step 32 \
    --device "0" \
    --learning_rate 5e-5 \
    --epochs 128 \
    --seed 42 \
    --save_path "./models/text2sql-mt5-large-polspider" \
    --tensorboard_save_path "./tensorboard_log/polspider_mt5_large" \
    --model_name_or_path "google/mt5-large" \
    --use_adafactor \
    --mode train \
    --train_filepath "./data/preprocessed_data/resdsql_train_polspider.json"

# select the best text2sql-mt5-large (CSpider version) ckpt
python -u evaluate_text2sql_ckpts.py \
    --batch_size 1 \
    --device "0" \
    --seed 42 \
    --save_path "./models/mt5-large-polspider" \
    --eval_results_path "./eval_results/mt5-large-polspider" \
    --mode eval \
    --dev_filepath "./data/preprocessed_data/resdsql_dev_polspider.json" \
    --original_dev_filepath "./data/pol-spider-train/dev.json" \
    --db_path "./data/pol-spider-train/database" \
    --num_beams 8 \
    --num_return_sequences 8 \
    --target_type "sql"