import csv
import importlib
import json
import os
from pathlib import Path
import time
from datetime import datetime
import statistics
import requests
from jiwer import (
    Compose,
    RemoveMultipleSpaces,
    RemovePunctuation,
    Strip,
    ToLowerCase,
    wer,
)

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

def start(modelName):
    filename = "models.json"

    if not os.path.exists(filename):
        print("Error: models.json missing.")
        return

    with open(filename, "r", encoding="utf-8") as f:
        models_config = json.load(f)

    if modelName not in models_config:
        print(f"Model settings for '{modelName}' not found.")
        return

    model_settings = models_config[modelName]
    mode = model_settings.get("mode")

    if mode == "asr-transcription":
        print(f"Starting ASR benchmark for {modelName}...")

        run_benchmark(
            model=model_settings["model_id"],
            ip=model_settings["ipAddress"],
            dataset=model_settings["folderAddress"],
            manifest=model_settings["transcriptFile"],
            endpoint=model_settings["endpoint"],
            parameters = model_settings.get("parameters", {}),
            runs=model_settings.get("runs", 5)
        )

    elif mode == "llm-translation":
        print(f"Starting LLM translation benchmark for {modelName}...")

        dataset_file = model_settings["folderAddress"]
        run_evaluation(modelName, dataset_file)

    else:
        print(f"Unknown mode '{mode}'")

def load_manifest(manifest_csv):
    manifest = {}
    manifest_path = Path(manifest_csv)

    if not manifest_path.exists():
        return manifest

    with manifest_path.open("r", encoding="utf-8", newline="") as infile:
        # reader = csv.DictReader(infile, fieldnames=["sample_id", "audio_path", "reference_text", "audio_duration"])
        reader = csv.DictReader(infile)
        
        for row in reader:
            audio_name = Path(row["audio_path"]).name
            manifest[audio_name] = row

    return manifest


def stats(values):
    if not values:
        return None, None, None
    return min(values), statistics.median(values), max(values)


def transcribe(api_url, model, audio_path, parameters):
    start_time = time.perf_counter()

    with audio_path.open("rb") as audio_file:
        try:
            response = requests.post(
                api_url,
                files={"file": (audio_path.name, audio_file, "audio/wav")},
                data={
                    "model": model,
                    **parameters
                },
                timeout=(30, 600),
            )
        except requests.exceptions.RequestException as e:
            return None, str(e), elapsed

    elapsed = time.perf_counter() - start_time
    return response, elapsed


def run_benchmark(model, ip_address, dataset, manifest, endpoint, parameters, runs=5):
    api_url = f"http://{ip_address}/{endpoint}"
    audio_dir = Path(dataset)

    normalizer = Compose([
        RemovePunctuation(),
        ToLowerCase(),
        RemoveMultipleSpaces(),
        Strip()
    ])

    manifest = load_manifest(manifest)
    audio_files = sorted(audio_dir.rglob("*.wav"))

    results = []

    for audio_path in audio_files:
        audio_name = audio_path.name
        meta = manifest.get(audio_name, {})

        sample_id = meta.get("sample_id", "")
        reference_text = meta.get("reference_text", "")
        audio_duration = meta.get("audio_duration", "")

        print(f"\nTesting {audio_name}")

        latencies = []
        wers = []
        last_transcript = ""
        error = ""

        for run_index in range(1, runs + 1):
            response, elapsed = transcribe(api_url, model, audio_path, parameters)
            latencies.append(elapsed)

            if response.status_code != 200:
                error = response.text
                print(f" Run {run_index}: ERROR ({elapsed:.2f}s)")
                continue

            transcript = response.json().get("text", "")
            last_transcript = transcript

            norm_reference = normalizer(reference_text)
            norm_transcript = normalizer(transcript)

            run_wer = wer(norm_reference, norm_transcript) if reference_text else None

            if run_wer is not None:
                wers.append(run_wer)

            print(f" Run {run_index}: {elapsed:.2f}s | WER={run_wer:.4f}")

        latency_min, latency_med, latency_max = stats(latencies)
        wer_min, wer_med, wer_max = stats(wers)

        results.append({
            "sample_id": sample_id,
            "audio_path": str(audio_path),
            "reference_text": reference_text,
            "audio_duration": audio_duration,
            "prediction_text": last_transcript,
            "latency_min": latency_min,
            "latency_median": latency_med,
            "latency_max": latency_max,
            "wer_min": wer_min,
            "wer_median": wer_med,
            "wer_max": wer_max,
            "error": error,
            "model": model,
        })
    if not results:
        print("No results generated")
        return
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path(RESULTS_DIR) / f"{model}_{timestamp}.csv"

    with output_file.open("w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\nSaved results to {output_file}")