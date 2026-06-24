import json
from pathlib import Path

def delete():
    configs = json.load(Path("models.json").open())
    print("Running delete.py")
    target = input("Which preset would you like to delete? ")
    if target in configs:
        del configs[target]
        json.dump(configs, Path("models.json").open("w"), indent=1)
        print("Deleted preset " + target)
    else:
        print("Preset not found")

delete()