set -e

# train text2sql-mt5-base-cspider model
python -u text2sql.py \
    --batch_size 2 \
    --gradient_descent_step 16 \
    --device "0" \
    --learning_rate 1e-4 \
    --epochs 128 \
    --seed 42 \
    --save_path "./models/text2sql-mt5-base-polspider" \
    --tensorboard_save_path "./tensorboard_log/polspider_mt5_base" \
    --model_name_or_path "google/mt5-base" \
    --use_adafactor \
    --mode train \
    --train_filepath "./data/preprocessed_data/resdsql_train_polspider.json"
    
# select the best text2sql-mt5-base-cspider ckpt
python -u evaluate_text2sql_ckpts.py \
    --batch_size 8 \
    --device "0" \
    --seed 42 \
    --save_path "./models/text2sql-mt5-base-polspider" \
    --eval_results_path "./eval_results/mt5-base-polspider" \
    --mode eval \
    --dev_filepath "./data/preprocessed_data/resdsql_dev_polspider.json" \
    --original_dev_filepath "./data/pol-spider-train/dev.json" \
    --db_path "./data/pol-spider-train/database" \
    --num_beams 8 \
    --num_return_sequences 8 \
    --target_type "sql"