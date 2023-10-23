## BRIDGE

## General
1. Enter [`TabularSemanticParsing`](rat-sql) directory.
2. Run container with:
    ```
    docker compose up --build
    ```
3. Enter container with command:
    ```
    docker exec -it bridge bash
    ```

## Training

1. Place spider dataset under [`data/spider`](rat-sql/data/spider)
2. Run dataset repair:
    ```
    python3 data/scripts/amend_missing_foreign_keys.py data/spider
    ```
3. Run dataset preprocessing:
    ```
    ./experiment-bridge.sh configs/bridge/spider-bridge-bert-large.sh --process_data 0
    ```
4. Run training:
    ```
    ./experiment-bridge.sh configs/bridge/spider-bridge-bert-large.sh --train 0
    ```

## Inference
1. Run command:
    ```
    ./experiment-bridge.sh configs/bridge/spider-bridge-bert-large.sh --inference 0
    ```
