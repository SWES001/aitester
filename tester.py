import csv
import json
import os
import time
from datetime import datetime
from pathlib import Path


#from openai import models

# --- CONFIGURING OUR FOLDER PATHS ---
MODELS_DIR = "models"
DATASETS_DIR = "datasets"
RESULTS_DIR = "results"
DATASET_LINK = "https://github.com/company/datasets/" # Base link for logs

# Ensure the required folders exist on the server right away
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(DATASETS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)


def get_available_models():
    """Dynamically lists all files inside the 'models' folder."""
    files = os.listdir(MODELS_DIR)
    # Only grab python files or model files, and strip the '.py' extension for a clean name
    models = [os.path.splitext(f)[0] for f in files if f.endswith('.py') or f.endswith('.bin')]
    return models

def get_available_datasets():
    """Dynamically lists all JSON files inside the 'datasets' folder."""
    files = os.listdir(DATASETS_DIR)
    return [f for f in files if f.endswith('.json')]


# --- SIMULATED EVALUATION ENGINE ---
def run_evaluation(model_name, dataset_file):
    """Reads the chosen dataset and runs it against the chosen model."""
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
        writer.writerow([]) # Blank spacer row
        writer.writerow(["Input", "Expected Output", "Actual Output", "Time Taken (s)"])
        
        for i, case in enumerate(test_cases, 1):
            prompt = case.get("input", "")
            expected = case.get("expected", "")
            
            # Simulating processing
            start_time = time.time()
            time.sleep(0.4) 
            actual_output = f"[Simulated response from models/{model_name} for prompt]"
            end_time = time.time()
            
            elapsed = round(end_time - start_time, 4)
            writer.writerow([prompt, expected, actual_output, elapsed])
            
    print(f"✅ Evaluation complete! Results saved to: {csv_filename}\n")

def create(modelName):
    mode = input("Model mode (asr-transcription / llm-translation): ").strip().lower()
    modelID = input("Model ID: ").strip()
    ipAdd = input("IP Address: ").strip()
    if mode == "asr-transcription":
        folderAdd = input("Audio Dataset Folder Address: ").strip() 
        transcript_file = input("GroundTruth Transcript File Name (csv): ").strip()
    elif mode == "llm-translation":
        folderAdd = input("Dataset Folder Address (csv): ").strip()
        temp = input("Default Parameter Temperature: ").strip()
        topP = input("Default Parameter Top_P: ").strip()
        topK = input("Default Parameter Top_K: ").strip()
        maxTok = input("Default Parameter Max Tokens: ").strip()
        repPen = input("Default Parameter Repetition Penalty: ").strip()
    dataUrl = input("Dataset URL (Internet): ").strip()
    path = input("Endpoint Path: ").strip()


    with open("models.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    if mode == "asr-transcription":
        data[modelName] = {
            "mode": mode,
            "modelID": modelID,
            "ipAddress": ipAdd,
            "folderAddress": folderAdd,
            "transcriptFile": transcript_file,
            "dataurl": dataUrl,
            "endpointPath": path,
        }
    elif mode == "llm-translation":
        data[modelName] = {
            "mode": mode,
            "modelID": modelID,
            "ipAddress": ipAdd,
            "folderAddress": folderAdd,
            "dataurl": dataUrl,
            "endpointPath": path,
            "parameters": f"temperature={temp},top_p={topP},top_k={topK},max_tokens={maxTok},repetition_penalty={repPen}"
        }
    else:
        print(f"Unknown mode '{mode}'. Model not saved.")
        return

    with open("models.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def delete(name):
    configs = json.load(Path("models.json").open())
    if name in configs:
        del configs[name]
        json.dump(configs, Path("models.json").open("w"), indent=2)
        print("Deleted preset " + name)
    else:
        print("Preset not found")

def edit(modelName, what):
    with open("models.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    if modelName not in data:
        print(f"❌ Model '{modelName}' not found in models.json.")
        return
    mode = data[modelName]["mode"]
    if what == "ip":
        new_ip = input("New IP Address: ").strip()
        data[modelName]["ipAddress"] = new_ip
    elif what == "folder":
        new_folder = input("New Dataset Folder Address: ").strip()
        data[modelName]["folderAddress"] = new_folder
    elif what == "url":
        new_url = input("New Dataset URL (Internet): ").strip()
        data[modelName]["dataurl"] = new_url
    elif what == "path":
        new_path = input("New Endpoint Path: ").strip()
        data[modelName]["endpointPath"] = new_path
    elif what == "modelid":
        new_modelid = input("New Model ID: ").strip()
        data[modelName]["modelID"] = new_modelid
    elif what == "mode":
        new_mode = input("New Mode (asr-transcription / llm-translation): ").strip().lower()
        if new_mode in ["asr-transcription", "llm-translation"]:
            data[modelName]["mode"] = new_mode
        else:
            print(f"Invalid mode.")
            return
    elif what == "transcript" and mode == "asr-transcription":
        new_transcript = input("New GroundTruth Transcript File Name (csv): ").strip()
        data[modelName]["transcriptFile"] = new_transcript
    elif what == "params" and mode == "llm-translation":
        temp = input("Default Parameter Temperature: ").strip()
        topP = input("Default Parameter Top_P: ").strip()
        topK = input("Default Parameter Top_K: ").strip()
        maxTok = input("Default Parameter Max Tokens: ").strip()
        repPen = input("Default Parameter Repetition Penalty: ").strip()
        data[modelName]["parameters"] = f"temperature={temp},top_p={topP},top_k={topK},max_tokens={maxTok},repetition_penalty={repPen}"
    elif what == "params" and mode != "llm-translation":
        print(f"Cannot edit parameters for mode '{mode}'.")
        return
    elif what == "transcript" and mode != "asr-transcription":
        print(f"Cannot edit transcript for mode '{mode}'.")
        return
    else:
        print(f"❌ Unknown edit option '{what}'.")
        return

    with open("models.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Model '{modelName}' updated successfully.")

def list():
    configs = json.load(Path("models.json").open())
    for name, desc in configs.items():
        print(name)
        for item, value in desc.items():
            print("  " + item + ": " + str(value))

# --- MAIN INTERACTIVE TERMINAL ---
def main():
    print("=====================================================")
    print("🤖 Welcome to the Company Server AI Test Suite 🤖")
    print("Type 'help' to see instructions, or 'exit' to quit.")
    print("=====================================================")
    
    while True:

        user_input = input("tester-app> ").strip()
            
        parts = user_input.split()
        command = parts[0].lower()
        
        
        if command in ["exit", "quit"]:
            print("Closing application. Goodbye!")
            break

        elif command == "create":
            name = parts[1].lower()
            create(name)
            
        elif command == "edit":
            name = parts[1].lower()
            what = parts[2].lower() if len(parts) > 2 else None
            edit(name, what)
        
        elif command == "delete":
            name = parts[1].lower()
            delete(name)

        elif command == "help":
            print("\nCommands Layout:")
            print("  list               - Scan the folders and show available models & datasets")
            print("  run                - Start a test by selecting a model and a dataset")
            print("  create <name>      - Create a new model preset with the given name")
            print("  delete <name>      - Delete an existing model preset")
            print("  edit <name> <what> - Edit a model preset's details (ip, folder, url, path, modelid, mode, transcript, params)")
            print("  exit               - Close the program\n")
            
        elif command == "list":
            list()
            
        elif command == "run":
            models = get_available_models()
            datasets = get_available_datasets()
            
            if not models or not datasets:
                print("❌ Cannot run. You need at least one model and one dataset file in their respective folders.")
                continue
                
            # Step-by-step picker for the employee
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
                
            # Trigger execution
            run_evaluation(chosen_model, chosen_dataset)
            
        else:
            print(f"❌ Unknown command: '{user_input}'. Type 'help' for a list of commands.")

if __name__ == "__main__":
    main()