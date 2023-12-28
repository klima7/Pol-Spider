set -e

# input data
tables=$1
dataset_path=$2
db_path=$3
output_path=$4
aux_dir=$5
openai_api=$6

# aux variables
device="0"

# export api key
export OPENAI_API_KEY=$openai_api

# preprocess test set
echo "preprocessing..."
python preprocessing.py \
    --mode "test" \
    --table_path $tables \
    --input_dataset_path $dataset_path \
    --output_dataset_path "${aux_dir}/preprocessed_data.json" \
    --db_path "$db_path" \
    --target_type "sql"

# recall tables
echo "recall tables..."
python table_recall.py \
    --input_dataset_path "${aux_dir}/preprocessed_data.json" \
    --output_recalled_tables_path "${aux_dir}/table_recall.json"

# recall columns
echo "recall columns..."
python column_recall.py \
    --input_dataset_path "${aux_dir}/table_recall.json" \
    --output_recalled_columns_path "${aux_dir}/column_recall.json" \

# generate prompt
echo "generate prompt..."
python prompt_generate.py \
    --input_dataset_path "${aux_dir}/column_recall.json" \
    --output_dataset_path "${aux_dir}/C3_dev.json" \

# run prediction
python generate_sqls_by_gpt3.5.py \
    --input_dataset_path "${aux_dir}/C3_dev.json"  \
    --output_dataset_path $output_path \
    --db_dir $db_path
