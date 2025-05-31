# Models/GPT4o.py

import openai
import os
import logging

logging.basicConfig(level=logging.ERROR)

# 환경 변수에서 API 키 가져오기 (.env에 저장된 값)
api_key = os.getenv("API_KEY")
if not api_key:
    logging.error("[OpenAI API] API key not found in environment variables.")
openai.api_key = api_key

def call_model(prompt: str) -> str:
    """
    GPT-4o API를 호출하여 답변을 받아오는 함수.
    prompt: 사용자의 입력 프롬프트 문자열
    return: 모델의 응답 문자열
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
        logging.error(f"[GPT-4o 호출 오류] {e}")
        return "[API ERROR] Request failed"
