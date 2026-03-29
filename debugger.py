from openai import OpenAI

def auto_debug(openai_api_key: str, code: str, error: str) -> str:
    if not openai_api_key:
        raise ValueError("OpenAI API key is required")
    client = OpenAI(api_key=openai_api_key)
    
    prompt = f"Debug this code:\n{code}\nError: {error}\nReturn fixed code."
    
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=512,
        temperature=0.2
    )
    
    return response.choices[0].message.content.strip()