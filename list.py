import json
from pathlib import Path
def list():
    configs = json.load(Path("models.json").open())
    for name, desc in configs.items():
        print(name)
        for item, value in desc.items():
            print("  " + item + ": " + str(value))

list()
