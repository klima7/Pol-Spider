set -e

device="0"

if [ $1 = "base" ]
then
    text2sql_model_save_path="./models/text2sql-mt5-base-polspider/checkpoint-best"
    text2sql_model_bs=6
else
    echo "The first arg must in [base, large, 3b]."
    exit
fi

model_name="resdsql_$1"

if [ $2 = "spider" ]
then
    # spider's dev set
    table_path="./data/pol-spider-train/tables.json"
    input_dataset_path="./data/pol-spider-train/dev.json"
    db_path="./data/pol-spider-train/database"
    output="./predictions/polspider-train/$model_name/pred.sql"
elif [ $2 = "pol_spider" ]
then
    table_path="./data/pol_spider/tables.json"
    input_dataset_path="./data/pol_spider/dev.json"
    db_path="./data/pol_spider/database"
    output="./predictions/polish/$model_name/pol_spider.sql"
elif [ $2 = "pol_spider_pl" ]
then
    table_path="./data/pol_spider_pl/tables.json"
    input_dataset_path="./data/pol_spider_pl/dev.json"
    db_path="./data/pol_spider_pl/database"
    output="./predictions/polish/$model_name/pol_spider_pl.sql"
elif [ $2 = "pol_spider_en" ]
then
    table_path="./data/pol_spider_en/tables.json"
    input_dataset_path="./data/pol_spider_en/dev.json"
    db_path="./data/pol_spider_en/database"
    output="./predictions/polish/$model_name/pol_spider_en.sql"
elif [ $2 = "en_spider" ]
then
    table_path="./data/en_spider/tables.json"
    input_dataset_path="./data/en_spider/dev.json"
    db_path="./data/en_spider/database"
    output="./predictions/polish/$model_name/en_spider.sql"
elif [ $2 = "mix_spider" ]
then
    table_path="./data/mix_spider/tables.json"
    input_dataset_path="./data/mix_spider/dev.json"
    db_path="./data/mix_spider/database"
    output="./predictions/polish/$model_name/mix_spider.sql"
elif [ $2 = "pol_cosql" ]
then
    table_path="./data/pol_cosql/tables.json"
    input_dataset_path="./data/pol_cosql/dev.json"
    db_path="./data/pol_cosql/database"
    output="./predictions/polish/$model_name/pol_cosql.sql"
elif [ $2 = "pol_sparc" ]
then
    table_path="./data/pol_sparc/tables.json"
    input_dataset_path="./data/pol_sparc/dev.json"
    db_path="./data/pol_sparc/database"
    output="./predictions/polish/$model_name/pol_sparc.sql"
elif [ $2 = "pol_spiderdk" ]
then
    table_path="./data/pol_spiderdk/tables.json"
    input_dataset_path="./data/pol_spiderdk/dev.json"
    db_path="./data/pol_spiderdk/database"
    output="./predictions/polish/$model_name/pol_spiderdk.sql"
elif [ $2 = "pol_spidersyn" ]
then
    table_path="./data/pol_spidersyn/tables.json"
    input_dataset_path="./data/pol_spidersyn/dev.json"
    db_path="./data/pol_spidersyn/database"
    output="./predictions/polish/$model_name/pol_spidersyn.sql"
else
    echo "The second arg is invalid"
    exit
fi

# preprocess test set
python preprocessing.py \
    --mode "test" \
    --table_path $table_path \
    --input_dataset_path $input_dataset_path \
    --output_dataset_path "./data/preprocessed_data/preprocessed_test.json" \
    --db_path $db_path \
    --target_type "sql"

# predict probability for each schema item
python schema_item_classifier.py \
    --batch_size 32 \
    --device $device \
    --seed 42 \
    --save_path "./models/polspider_schema_item_classifier" \
    --dev_filepath "./data/preprocessed_data/preprocessed_test.json" \
    --output_filepath "./data/preprocessed_data/test_with_probs.json" \
    --use_contents \
    --add_fk_info \
    --mode "test"

# generate text2sql test set
python text2sql_data_generator.py \
    --input_dataset_path "./data/preprocessed_data/test_with_probs.json" \
    --output_dataset_path "./data/preprocessed_data/resdsql_test.json" \
    --topk_table_num 4 \
    --topk_column_num 5 \
    --mode "test" \
    --use_contents \
    --add_fk_info \
    --output_skeleton \
    --target_type "sql"

# inference using the best text2sql ckpt
python text2sql.py \
    --batch_size $text2sql_model_bs \
    --device $device \
    --seed 42 \
    --save_path $text2sql_model_save_path \
    --mode "eval" \
    --dev_filepath "./data/preprocessed_data/resdsql_test.json" \
    --original_dev_filepath $input_dataset_path \
    --db_path $db_path \
    --num_beams 8 \
    --num_return_sequences 8 \
    --target_type "sql" \
    --output $output