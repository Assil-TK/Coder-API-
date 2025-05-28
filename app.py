from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import re
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)
class LLMInterface:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.system_message = """
You are a professional coding assistant. The user will send you a code snippet followed by a request.

Your job:
- Carefully apply ONLY the requested change.
- Return the FULL, updated code — no explanations, no extra text, no markdown formatting.
- Start directly with the first line of code (no ``` or language tags).
"""
        self.model = "Qwen/Qwen2.5-Coder-7B-Instruct"


    def query(self, prompt: str) -> str:
        payload = {
            "messages": [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2000,
            "model": self.model
        }
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code}, {response.text}"

# Root route
@app.route('/')
def home():
    return "Welcome to the AI Code Modifier API!"

# Main route for generating code
@app.route('/generate', methods=['POST'])
def generate_code():
    data = request.get_json()
    full_prompt = data.get("prompt")

    if not full_prompt:
        return jsonify({"error": "No prompt provided"}), 400

    api_url = "https://router.huggingface.co/nebius/v1/chat/completions"

    api_key = os.getenv("HF_API_KEY")

    if not api_key:
        return jsonify({"error": "API key is missing. Set it in the .env file."}), 500

    llm = LLMInterface(api_url, api_key)
    raw_response = llm.query(full_prompt)

    # Clean markdown formatting bch tna77i ay characters zeydin 9bal lcode 
    cleaned_code = re.sub(r'^```[a-z]*\n([\s\S]*?)\n```$', r'\1', raw_response.strip(), flags=re.MULTILINE)

    return jsonify({"code": cleaned_code})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
