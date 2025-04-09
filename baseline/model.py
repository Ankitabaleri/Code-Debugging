import requests

class StarcoderAPIClient:
    def __init__(self, api_url="http://127.0.0.1:8000/v1/completions"):
        self.api_url = api_url

    def generate_completion(self, prompt, max_tokens=1024, temperature=0.0):
        
        headers = {"Content-Type": "application/json"}
        data = {
            "model": "bigcode/starcoder",  # Model name you are using
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        try:
            response = requests.post(self.api_url, json=data, headers=headers)

            if response.status_code == 200:
                result = response.json()
                return result.get('choices', [{}])[0].get('text', "")
            else:
                raise Exception(f"Request failed with status {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Error: {e}")
            return ""