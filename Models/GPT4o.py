# Models/GPT4o.py

import openai
import os
import logging

logging.basicConfig(level=logging.ERROR)

# ȯ�� �������� API Ű �������� (.env�� ����� ��)
api_key = os.getenv("API_KEY")
if not api_key:
    logging.error("[OpenAI API] API key not found in environment variables.")
openai.api_key = api_key

def call_model(prompt: str) -> str:
    """
    GPT-4o API�� ȣ���Ͽ� �亯�� �޾ƿ��� �Լ�.
    prompt: ������� �Է� ������Ʈ ���ڿ�
    return: ���� ���� ���ڿ�
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1024,
            top_p=0.95,
            n=1
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logging.error(f"[GPT-4o ȣ�� ����] {e}")
        return "[API ERROR] Request failed"
