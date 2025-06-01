# Models/GPT4o.py

import logging
from openai import OpenAI

logging.basicConfig(level=logging.ERROR)

# 환경변수 OPENAI_API_KEY를 자동으로 가져옴
client = OpenAI()

def call_model(prompt: str) -> str:
    """
    GPT-4o API를 호출하여 사용자 메시지에 대한 응답을 반환합니다.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1024,
            top_p=0.95
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"[GPT-4o 호출 오류] {e}")
        return "[API ERROR] Request failed"
