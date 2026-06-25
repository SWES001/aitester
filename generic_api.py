import requests

def generate_response(prompt_input, config):
    # 1. Grab host address
    target_host = config.get("ipAddress", "").strip()
    
    # 2. Defensive check for endpoint keys (handles both 'endpoint' and 'endpointPath')
    route = config.get("endpoint", "")
    if not route:
        route = config.get("endpointPath", "/v1/chat/completions")
    route = route.strip()
    
    # Ensure there is exactly one clean routing slash separating host and path
    if not route.startswith("/"):
        route = "/" + route
        
    url = f"http://{target_host}{route}"
    
    # 3. Pull the prompt instructions from your standalone key
    system_prompt = config.get("prompt", "").strip()
    
    # Add a clean trailing space if it isn't there so words don't mash together
    if system_prompt and not system_prompt.endswith(" "):
        system_prompt += " "
        
    final_prompt = f"{system_prompt}{prompt_input}"

    # 🕵️‍♂️ LIVE TERMINAL AUDIT LINES
    print(f"\n   [DEBUG LOG] Connecting to: {url}")
    print(f"   [DEBUG LOG] System Instruction: '{system_prompt}'")
    print(f"   [DEBUG LOG] Sent Text: '{prompt_input}'")
    print(f"   [DEBUG LOG] Full Compiled String: '{final_prompt}'\n")

    # 4. Extract parameters string
    param_dict = {}
    raw_params = config.get("parameters", "")
    if raw_params:
        for item in raw_params.split(','):
            if '=' in item:
                k, v = item.split('=', 1)
                param_dict[k.strip().lower()] = v.strip()

    # 5. Type cast fallback values safely
    try: temp = float(param_dict.get("temperature", 0.7))
    except ValueError: temp = 0.7

    try: top_p = float(param_dict.get("top_p", 0.6))
    except ValueError: top_p = 0.6

    try: max_tokens = int(param_dict.get("max_tokens", 4096))
    except ValueError: max_tokens = 4096

    # 6. Assemble complete JSON structure
    # Inside models/generic_api.py:
    payload = {
        "messages": [{"role": "user", "content": prompt_input}], # Just pass it right through
        "temperature": temp,
        "top_p": top_p,
        "max_tokens": max_tokens
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=45)
        if response.status_code == 200:
            res_data = response.json()
            # Standard path extraction for chat completion arrays
            return res_data['choices'][0]['message']['content'].strip()
        else:
            return f"❌ Container API Error: HTTP {response.status_code} - {response.text}"
    except Exception as e:
        return f"❌ Failed to reach model container at {url}: {e}"