import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

for attempt in range(5):
    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents="Say Hello. Are you working?"
        )

        print("SUCCESS!")
        print(response.text)
        break

    except Exception as e:
        print(f"Attempt {attempt + 1} failed: {e}")

        if "503" in str(e):
            wait = 2 ** (attempt + 1)
            print(f"Retrying in {wait} seconds...")
            time.sleep(wait)
        else:
            break