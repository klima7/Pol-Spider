set -e

name=$1

tables="./data/${name}/tables.json"
dataset_path="./data/${name}/dev.json"
db_dir="./data/${name}/database"
output_dataset_path="predictions/${name}.txt"

processed_dataset_path="./generate_datasets/C3_dev.json"

# preprocess data
bash scripts/prepare_dataset.sh $tables $dataset_path $db_dir $processed_dataset_path
# run prediction
python src/generate_sqls_by_gpt3.5.py --input_dataset_path $processed_dataset_path  --output_dataset_path $output_dataset_path --db_dir $db_dir

