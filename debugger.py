from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def auto_debug(code, error):
    prompt = f"""
                You are a Python debugger.

                Fix the following code based on the error.

                Code:
                {code}

                Error:
                {error}

                Return ONLY fixed Python code.
                """

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()