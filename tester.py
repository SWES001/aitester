import csv
import json
import os
import time
import importlib
from datetime import datetime

# --- CONFIGURING OUR FOLDER PATHS ---
MODELS_DIR = "models"
DATASETS_DIR = "datasets"
RESULTS_DIR = "results"
DATASET_LINK = "https://github.com/company/datasets/" # Base link for logs

# Ensure the required folders exist right away
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(DATASETS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)


def get_available_models():
    """Dynamically lists all files inside the 'models' folder."""
    files = os.listdir(MODELS_DIR)
    models = [os.path.splitext(f)[0] for f in files if f.endswith('.py') or f.endswith('.bin')]
    return models

def get_available_datasets():
    """Dynamically lists all files inside the 'datasets' folder."""
    files = os.listdir(DATASETS_DIR)
    return [f for f in files if f.endswith('.json') or f.endswith('.csv')]


# --- SIMULATED EVALUATION ENGINE (FOR JSON DATASETS) ---
def run_evaluation(model_name, dataset_file):
    """Reads the chosen JSON dataset and runs it against the chosen model."""
    dataset_path = os.path.join(DATASETS_DIR, dataset_file)
    
    print(f"\n🔄 Loading dataset: {dataset_file}...")
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            test_cases = json.load(f)
    except Exception as e:
        print(f"❌ Error reading dataset: {e}")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = os.path.join(RESULTS_DIR, f"eval_{model_name}_{timestamp}.csv")
    
    print(f"📊 Running {len(test_cases)} tests using model '{model_name}'...")
    
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Model Name", model_name])
        writer.writerow(["Parameters", "Default Server Settings"])
        writer.writerow(["Dataset Name", dataset_file])
        writer.writerow(["Dataset Link", f"{DATASET_LINK}{dataset_file}"])
        writer.writerow([]) 
        writer.writerow(["Input", "Expected Output", "Actual Output", "Time Taken (s)"])
        
        for i, case in enumerate(test_cases, 1):
            prompt = case.get("input", "")
            expected = case.get("expected", "")
            
            start_time = time.time()
            time.sleep(0.4) 
            actual_output = f"[Simulated response from models/{model_name} for prompt]"
            end_time = time.time()
            
            elapsed = round(end_time - start_time, 4)
            writer.writerow([prompt, expected, actual_output, elapsed])
            
    print(f"✅ Evaluation complete! Results saved to: {csv_filename}\n")


def create():
    modelName = input("Model Name (e.g., hy-mt2-1.8b): ").strip().lower()
    
    if not modelName:
        print("❌ Error: Model name cannot be empty.")
        return

    ipAdd = input("IP Address & Port (e.g., 192.168.1.50:8000): ").strip()
    endpoint = input("API Endpoint Route (e.g., /v1/chat/completions): ").strip()
    folderAdd = input("Dataset Folder Address (csv): ").strip()
    dataUrl = input("Dataset URL (Internet, optional): ").strip()
    temp = input("Default Parameter Temperature: ").strip()
    topP = input("Default Parameter Top_P: ").strip()
    topK = input("Default Parameter Top_K: ").strip()
    maxTok = input("Default Parameter Max Tokens: ").strip()
    repPen = input("Default Parameter Repetition Penalty: ").strip()
    prompt = input("Default Prompt Prefix (optional): ").strip()

    existing_data = {}
    if os.path.exists("models.json"):
        try:
            with open("models.json", "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:  
                    existing_data = json.loads(content)
        except Exception as e:
            print(f"⚠️ Warning: Couldn't parse models.json ({e}). Starting fresh.")
            existing_data = {}

    existing_data[modelName] = {
        "ipAddress": ipAdd,
        "endpoint": endpoint,
        "folderAddress": folderAdd,
        "dataurl": dataUrl,
        "parameters": f"temperature={temp},top_p={topP},top_k={topK},max_tokens={maxTok},repetition_penalty={repPen}",
        "prompt": prompt
    }
    
    try:
        with open("models.json", "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=4)
        print(f"✅ Registered '{modelName}' successfully! Total models saved: {len(existing_data)}\n")
    except Exception as e:
        print(f"❌ Critical Error saving data to file: {e}\n")


def edit(modelName, what):
    with open("models.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    if modelName not in data:
        print(f"❌ Model '{modelName}' not found in models.json.")
        return

    what = what.lower()
    if what == "ip":
        new_ip = input("New IP Address: ").strip()
        data[modelName]["ipAddress"] = new_ip
    elif what == "folder":
        new_folder = input("New Dataset Folder Address (csv): ").strip()
        data[modelName]["folderAddress"] = new_folder
    elif what == "url":
        new_url = input("New Dataset URL (Internet): ").strip()
        data[modelName]["dataurl"] = new_url
    elif what == "params":
        temp = input("Default Parameter Temperature: ").strip()
        topP = input("Default Parameter Top_P: ").strip()
        topK = input("Default Parameter Top_K: ").strip()
        maxTok = input("Default Parameter Max Tokens: ").strip()
        repPen = input("Default Parameter Repetition Penalty: ").strip()
        data[modelName]["parameters"] = f"temperature={temp},top_p={topP},top_k={topK},max_tokens={maxTok},repetition_penalty={repPen}"
    elif what == "endpoint":
        new_endpoint = input("New Endpoint Path (e.g., /v1/chat/completions): ").strip()
        data[modelName]["endpoint"] = new_endpoint  # Synchronized key name
    elif what == "prompt":
        new_prompt = input("New Prompt Prefix (optional): ").strip()
        data[modelName]["prompt"] = new_prompt
    else:
        print(f"❌ Unknown edit option '{what}'.")
        return

    with open("models.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"✅ Model '{modelName}' updated successfully.")


def start(modelName, datasetName):
    filename = "models.json"
    
    if not os.path.exists(filename):
        print("❌ Error: models.json missing. Run 'create' first.")
        return
        
    with open(filename, "r", encoding="utf-8") as f:
        models_config = json.load(f)
        
    if modelName not in models_config:
        print(f"❌ Error: Model settings for '{modelName}' not found.")
        return
        
    model_settings = models_config[modelName]
    
    print(f"\n🔌 Loading engine: {MODELS_DIR}/generic_api.py ...")
    try:
        model_module = importlib.import_module("models.generic_api")
    except Exception as e:
        print(f"❌ Error: Could not load 'models/generic_api.py'.\nDetail: {e}")
        return

    dataset_path = os.path.join(DATASETS_DIR, datasetName)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = os.path.join(RESULTS_DIR, f"eval_{modelName}_{timestamp}.csv")
    
    try:
        with open(dataset_path, mode='r', encoding='utf-8') as infile, \
             open(csv_filename, mode='w', newline='', encoding='utf-8') as outfile:
                 
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            
            next(reader, None) # Skip CSV header row
            
            writer.writerow(["Model Name", modelName])
            writer.writerow(["IP Address/Port", model_settings.get("ipAddress")])
            writer.writerow(["Parameters", model_settings.get("parameters")])
            writer.writerow([]) 
            writer.writerow(["Input", "Expected Output", "Actual Output", "Time Taken (s)"])
            
            for i, row in enumerate(reader, 1):
                if not row or len(row) < 2:
                    continue
                    
                raw_input_text = row[0]
                expected = row[1]
                
                # 🛠️ STRATEGY FIX: Build the prompt right here before handing it to the module!
                prefix = model_settings.get("prompt", "").strip()
                if prefix and not prefix.endswith(" "):
                    prefix += " "
                
                final_compiled_prompt = f"{prefix}{raw_input_text}"
                
                print(f" ⏳ Evaluating row {i}...")
                print(f"    [DEBUG SENDING] \"{final_compiled_prompt}\"")
                
                start_time = time.time()
                
                # Send the fully-combined string directly over to the dynamic runner
                actual_output = model_module.generate_response(final_compiled_prompt, model_settings)
                
                end_time = time.time()
                elapsed = round(end_time - start_time, 4)
                
                # Log the original clean input text to the final spreadsheet row
                writer.writerow([raw_input_text, expected, actual_output, elapsed])
                
        print(f"✅ Evaluation complete! Results saved to: {csv_filename}\n")
    except Exception as e:
        print(f"❌ Critical error during run: {e}")


# --- MAIN INTERACTIVE TERMINAL ---
def main():
    print("=====================================================")
    print("🤖 Welcome to the Company Server AI Test Suite 🤖")
    print("Type 'help' to see instructions, or 'exit' to quit.")
    print("=====================================================")
    
    while True:
        user_input = input("tester-app> ").strip()
        if not user_input:
            continue
            
        parts = user_input.split()
        command = parts[0].lower()
        
        if command in ["exit", "quit"]:
            print("Closing application. Goodbye!")
            break

        elif command == "create":
            create()
            
        elif command == "edit":
            entered = input("[name] [ip/folder/url/params/endpoint/prompt]").strip()
            splitted = entered.split()
            if len(splitted) >= 2:
                name = splitted[0].lower()
                what = splitted[1].lower()
                edit(name, what)
            else:
                print("❌ Usage: edit [model_name] [field]")

        elif command == "start":
            entered = input("[model] [dataset]").strip()
            splitted = entered.split()
            if len(splitted) >= 2:
                model = splitted[0].lower()
                dataset = splitted[1].lower()
                start(model, dataset)
            else:
                print("❌ Usage: start [model_name] [dataset_file.csv]")

        elif command == "help":
            print("\nCommands Layout:")
            print("  list               - Scan the folders and show available models & datasets")
            print("  run                - Start a test by selecting a model and a dataset (JSON)")
            print("  start              - Execute direct evaluation on a target CSV dataset file")
            print("  create             - Create a new model entry in models.json")
            print("  edit               - Edit an existing model entry")
            print("  exit               - Close the program")
            
        elif command == "list":
            models = get_available_models()
            datasets = get_available_datasets()
            
            print(f"\n📂 Models found in /{MODELS_DIR}:")
            if models:
                for m in models: print(f"  • {m}")
            else:
                print("  (No files found.)")
                
            print(f"\n📂 Datasets found in /{DATASETS_DIR}:")
            if datasets:
                for d in datasets: print(f"  • {d}")
            else:
                print("  (No files found.)")
            print("")
            
        elif command == "run":
            models = get_available_models()
            datasets = [d for d in get_available_datasets() if d.endswith('.json')]
            
            if not models or not datasets:
                print("❌ Cannot run. You need at least one model and one JSON dataset file.")
                continue
                
            print("\n--- Step 1: Choose a Model ---")
            for idx, m in enumerate(models, 1):
                print(f" [{idx}] {m}")
            try:
                model_choice = int(input("Select model number: ")) - 1
                chosen_model = models[model_choice]
            except (ValueError, IndexError):
                print("❌ Invalid choice. Aborting run.")
                continue

            print("\n--- Step 2: Choose a Dataset ---")
            for idx, d in enumerate(datasets, 1):
                print(f" [{idx}] {d}")
            try:
                dataset_choice = int(input("Select dataset number: ")) - 1
                chosen_dataset = datasets[dataset_choice]
            except (ValueError, IndexError):
                print("❌ Invalid choice. Aborting run.")
                continue
                
            run_evaluation(chosen_model, chosen_dataset)
            
        else:
            print(f"❌ Unknown command: '{user_input}'. Type 'help' for a list of commands.")

if __name__ == "__main__":
    main()