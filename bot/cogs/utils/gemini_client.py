import requests
import os
import time

from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self, model_id):
        # API key
        self.api_key = os.getenv('GOOGLE_API_KEY')
        # Main URL for the Gemini API
        self.api_url = self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={self.api_key}"
        # Headers for the API request
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def fetch(self, prompt):
        payload = {
            "contents" : [{"parts" : [{"text": prompt}]}],
        }

        for attempt in range(3): 
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text']
            
            if response.status_code == 429:
                wait_time = 10 if attempt == 0 else 20
                print(f"Quota exceeded. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                continue

            return f"Error: {response.status_code} - {response.text}"
        
        return "Error: Quota exceeded. Please try again later."
    