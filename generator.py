from openai import OpenAI


def generate_code(openai_api_key: str, user_input: str, model: str = "gpt-5-mini", max_tokens: int = 512, temperature: float = 0.2) -> str:
    if not openai_api_key:
        raise ValueError("OpenAI API key is required")

    client = OpenAI(api_key=openai_api_key)
    prompt = f"""
                Convert this natural language instruction to Python code. 
                Instruction:
                {user_input}
                Return ONLY Python code.
                """
    # Some models use max_completion_tokens instead of max_tokens (OpenAI recently changed API naming for gpt-5 family)
    kwargs = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }

    if model.startswith("gpt-5") or model.startswith("gpt-4"):
        kwargs["max_completion_tokens"] = max_tokens
        # Newer models may only support default temperature=1
        kwargs["temperature"] = 1.0
    else:
        kwargs["max_tokens"] = max_tokens
        kwargs["temperature"] = temperature

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content.strip()