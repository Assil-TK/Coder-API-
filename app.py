from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import re

# Load .env variables
load_dotenv()

app = Flask(__name__)
CORS(app)

class LLMInterface:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.system_message = """
 You are an AI that generates a high-quality frontend code in React.js with MUI.
 Follow these strict rules:
- Styling and Design:
    - Use these design constants:
        - Primary color: #1B374C
        - Accent color: #F39325
        - Background: #F5F5F6
        - Font family: 'Fira Sans' (use sx where needed)

- Strict Rules:
    - return only comple code without extra text or characters 
    - do not start with ```jsx, start directly with the code 
"""
        self.model = "Qwen/Qwen2.5-Coder-7B-Instruct-fast"

    def query(self, prompt: str) -> str:
        payload = {
            "messages": [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,
            "model": self.model
        }
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code}, {response.text}"

@app.route('/')
def home():
    return "Welcome to the SECOND AI Code Generator API (PORT 5001)!"

@app.route('/generate', methods=['POST'])
def generate_code():
    data = request.get_json()
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    api_url = "https://router.huggingface.co/nebius/v1/chat/completions"
    api_key = os.getenv("HF_API_KEY")

    if not api_key:
        return jsonify({"error": "API key is missing. Set it in the .env file."}), 500

    llm = LLMInterface(api_url, api_key)
    response = llm.query(prompt)

    # Clean markdown code block formatting
    cleaned_code = re.sub(r'^```[a-z]*\n([\s\S]*?)\n```$', r'\1', response.strip(), flags=re.MULTILINE)

    return jsonify({"code": cleaned_code})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
