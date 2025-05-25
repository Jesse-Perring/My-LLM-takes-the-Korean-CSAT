import os
import logging
import sys
from together import Together

logging.basicConfig(
    stream=sys.stderr,
    level=logging.ERROR,
    format="%(levelname)s:%(name)s:%(message)s",
    encoding="utf-8"
)

def _log_error(msg):
    logging.error(f"[Mixtral API] {msg}")

def call_model(prompt):
    """
    Mixtral 8x22B API를 together SDK의 chat.completions로 호출하여 답변을 받아오는 함수.
    파라미터는 prompt(텍스트)만 받음.
    """
    api_key = os.environ.get("API_KEY")
    if not api_key:
        _log_error("API key not found in environment variables.")
        return "[API ERROR] No API key"
    try:
        client = Together(api_key=api_key)
        # chat.completions.create는 반드시 messages 파라미터만 허용
        # top_k, repetition_penalty 등은 지원하지 않을 수 있음 (공식 문서 확인 필요)
        response = client.chat.completions.create(
            model="JessePerring/nim/mistralai/mixtral-8x22b-instruct-v01-79b0ece7",  # 서버리스 모델명, 필요시 엔드포인트명으로 교체,  # 서버리스 모델명
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=512,
            temperature=0.2,
            top_p=0.95,
            stop=["</s>", "[/INST]"],
            n=1
        )
        # together SDK chat 응답 구조: choices[0].message.content
        if hasattr(response, "choices") and response.choices:
            return response.choices[0].message.content
        elif isinstance(response, dict) and "choices" in response and response["choices"]:
            return response["choices"][0]["message"]["content"]
        else:
            _log_error(f"No result in response: {response}")
            return ""
    except Exception as e:
        _log_error(f"Request failed: {e}")
        return "[API ERROR] Request failed"
