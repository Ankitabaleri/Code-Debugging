import dataclasses
from typing import List, Literal, Union
import requests

MessageRole = Literal["system", "user", "assistant"]

@dataclasses.dataclass
class Message:
    role: MessageRole
    content: str


class ModelBase:
    def __init__(self, name: str):
        self.name = name
        self.is_chat = False  # Because we're sending plain prompts

    def generate_chat(self, messages: List[Message], **kwargs) -> str:
        raise NotImplementedError


class StarcoderAPIClient:
    def __init__(self, api_url="http://127.0.0.1:8000/v1/completions"):
        self.api_url = api_url

    def generate_completion(self, prompt, max_tokens=1024, temperature=0.0):
        headers = {"Content-Type": "application/json"}
        data = {
            "model": "bigcode/starcoder",
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
            print(f"[!] StarcoderAPI Error: {e}")
            return ""


class StarCoder(ModelBase):
    def __init__(self, port="8000"):
        super().__init__("bigcode/starcoder")
        self.api = StarcoderAPIClient(api_url=f"http://127.0.0.1:{port}/v1/completions")

    def generate_chat(self, messages: List[Message], temperature=0.0, max_tokens=1024, stop=None) -> str:
        prompt = self.build_prompt(messages)
        completion = self.api.generate_completion(prompt, max_tokens=max_tokens, temperature=temperature)
        return completion
    
    def generate_completion(self, prompt, max_tokens=5, temperature=0.0):
        return self.api.generate_completion(prompt, max_tokens=max_tokens, temperature=temperature)


    def build_prompt(self, messages: List[Message]) -> str:
        return "\n".join([f"{msg.role}: {msg.content}" for msg in messages])
