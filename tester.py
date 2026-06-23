import csv
import json
import os
import time
from datetime import datetime

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
            
        elif command == "help":
            print("\nCommands Layout:")
            print("  list               - Scan the folders and show available models & datasets")
            print("  run                - Start a test by selecting a model and a dataset")
            print("  exit               - Close the program\n")
            
        elif command == "list":
            models = get_available_models()
            datasets = get_available_datasets()
            
            print(f"\n📂 Models found in /{MODELS_DIR}:")
            if models:
                for m in models: print(f"  • {m}")
            else:
                print("  (No files found. Drop a model file into the 'models' folder!)")
                
            print(f"\n📂 Datasets found in /{DATASETS_DIR}:")
            if datasets:
                for d in datasets: print(f"  • {d}")
            else:
                print("  (No .json files found. Drop a dataset file into the 'datasets' folder!)")
            print("")
            
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