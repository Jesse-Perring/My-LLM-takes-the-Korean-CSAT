import os
import logging
import sys
from google import genai
from google.genai import types

logging.basicConfig(
    stream=sys.stderr,
    level=logging.ERROR,
    format="%(levelname)s:%(name)s:%(message)s",
    encoding="utf-8"
)

def _log_error(msg):
    logging.error(f"[Gemini API] {msg}")

def call_model(prompt: str) -> str:
    """
    Gemini API를 호출하여 답변을 받아오는 함수.
    파라미터는 prompt(텍스트)만 받음.
    """
    api_key = os.environ.get("API_KEY")
    if not api_key:
        _log_error("API key not found in environment variables.")
        return "[API ERROR] No API key"
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-1.5-pro-latest",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=1024,
                top_p=0.95,
            )

        )
        # Gemini API 응답 구조: choices[0].message.content
        if hasattr(response, "candidates") and response.candidates:
            parts = response.candidates[0].content.parts
            # parts의 원소가 2개 이상일 때(여러 텍스트 블록으로 쪼개진 답변일 때) 합쳐서 리턴
            return "".join(part.text for part in parts)
        # dict 형태 응답을 받았을 때
        elif isinstance(response, dict) and "candidates" in response and response.candidates:
            return "".join(part.text for part in parts)
        else:
            _log_error(f"No result in response: {response}")
            return ""
    except Exception as e:
        _log_error(f"Request failed: {e}")
        return "[API ERROR] Request failed"
