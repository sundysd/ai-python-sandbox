import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise SystemExit("Set OPENAI_API_KEY in .env")

from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)

prompt = "Write a short, friendly message from AI Python Sandbox"
response = client.responses.create(model="gpt-4o-mini", input=prompt)
print(response.output[0].content[0].text)
