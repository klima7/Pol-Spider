set -e

tables="./data/pol_spider_10/tables.json"
dataset_path="./data/pol_spider_10/dev.json"
db_dir="./data/pol_spider_10/database"
output_dataset_path="predicted_sql.txt"

processed_dataset_path="./generate_datasets/C3_dev.json"

# preprocess data
bash scripts/prepare_dataset.sh $tables $dataset_path $db_dir $processed_dataset_path
# run prediction
python src/generate_sqls_by_gpt3.5.py --input_dataset_path $processed_dataset_path  --output_dataset_path $output_dataset_path --db_dir $db_dir

