import json


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, json_obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(json_obj, f, indent=4, ensure_ascii=False)


def load_txt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def save_txt(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
