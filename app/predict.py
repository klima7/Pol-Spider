import time
import random


def predict_sql():
    time.sleep(1)
    return random.choice([
        "SELECT * FROM student",
        "SELECT imie FROM student",
    ])
