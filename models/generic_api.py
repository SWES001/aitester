import requests

def generate_response(prompt, config):
    """
    Universal connection script that handles all containerized model requests
    dynamically by reading the endpoints and target parameters.
    """
    target_host = config.get("ipAddress", "").strip()
    route = config.get("endpoint", "v1/chat/completions").strip()
    
    # Standard complete network URL construction
    url = f"http://{target_host}/{route}"
    
    # Helper to parse parameter string ("temperature=0.5,top_p=0.9") into a clean dictionary
    param_dict = {}
    raw_params = config.get("parameters", "")
    if raw_params:
        for item in raw_params.split(','):
            if '=' in item:
                k, v = item.split('=')
                try: param_dict[k.strip()] = float(v.strip())
                except ValueError: param_dict[k.strip()] = v.strip()

    # Generic OpenAI-compatible container payload layout
    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "temperature": param_dict.get("temperature", 0.7),
        "top_p": param_dict.get("top_p", 0.9),
        "max_tokens": int(param_dict.get("max_tokens", 2048))
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=45)
        if response.status_code == 200:
            res_data = response.json()
            # Standard parsing out for standard completion servers
            return res_data['choices'][0]['message']['content'].strip()
        else:
            return f"❌ Container API Error: HTTP {response.status_code} - {response.text}"
    except Exception as e:
        return f"❌ Failed to reach model container at {url}: {e}"