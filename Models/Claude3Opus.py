import anthropic

API_KEY = "YOUR-ANTHROPIC-API-KEY"  # Anthropic Claude API Key를 여기에 직접 입력
client = anthropic.Anthropic(api_key=API_KEY)

def call_model(prompt: str) -> str:
    try:
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            temperature=0.0,
            system="You are a top Korean high school student preparing for the college entrance exam (수능) with expert-level problem-solving skills. Answer accurately and logically.",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        print(f"Claude call failed: {e}")
        return "[API ERROR]"
