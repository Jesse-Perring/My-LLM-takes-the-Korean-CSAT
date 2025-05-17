import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

PROMPT_PATH = r'd:\projects\LLM Takes CSAT\standard prompt\prompot-CoT'
PROBLEM_PATH = r'd:\projects\LLM Takes CSAT\data\JSON\202511.json'
RESULT_PATH = r'd:\projects\LLM Takes CSAT\result by llm\Mixtral 8x22B\baseline_sheet.txt'

def load_prompt():
    # 프롬프트 파일 불러오기
    with open(PROMPT_PATH, encoding='utf-8') as f:
        return f.read().strip()

def load_problems():
    # 문제 데이터(JSON) 불러오기
    with open(PROBLEM_PATH, encoding='utf-8') as f:
        return json.load(f)

def normalize_answer(ans):
    # 정답 문자열 정규화(공백, 특수문자 등 제거)
    if ans is None:
        return ""
    return str(ans).replace('$', '').replace('\\', '').replace(' ', '').replace('\n', '').lower()

def mixtral_8x7b_generate(prompt, problem):
    # 프롬프트와 문제를 LLM에 전달
    full_prompt = f"{prompt}\nQuestion: {problem}"
    payload = {
        "model": "mistralai/Mixtral-8x22B-Instruct-v0.1",
        "prompt": full_prompt
    }
    api_key = os.getenv("API_KEY")
    endpoint = "https://api.together.xyz/v1/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
    result = response.json()
    return result["choices"][0]["text"].strip()

def main():
    prompt = load_prompt()
    problems = load_problems()
    text_lines = []
    correct_count = 0
    total_count = 0
    total_score = 0
    max_score = 100  

    for prob in problems:
        problem_number = prob.get("problem_number")
        problem = prob.get("problem", "")
        score = prob.get("score", 0)
        answer_gt = normalize_answer(prob.get("answer", ""))
        total_count += 1

        if not problem.strip():
            # 문제 문자열이 비어 있으면 풀이와 정답을 빈 문자열로 설정
            solution = ""
            answer = ""
        else:
            # LLM에 문제를 전달하여 풀이 텍스트를 받음
            solution = mixtral_8x7b_generate(prompt, problem)
            # LLM 출력에서 정답을 추출하려고 시도
            answer_line = ""
            # 마지막 줄부터 'Answer'가 포함된 줄을 찾음
            for line in reversed(solution.split('\n')):
                if 'Answer' in line:
                    answer_line = line
                    break
            # 'Answer:'가 있으면 ':' 오른쪽을 정답으로 추출
            if ':' in answer_line:
                answer = answer_line.split(':', 1)[1].strip()
            else:
                # 없으면 마지막 줄을 정답으로 사용
                answer = solution.strip().split('\n')[-1].strip()

        answer_norm = normalize_answer(answer)
        is_correct = (answer_norm == answer_gt and answer_gt != "")
        if is_correct:
            correct_count += 1
            total_score += score

        text_lines.append(
            f"Problem {problem_number}:\n"
            f"Solution: {solution}\n"
            f"Answer: {answer}\n"
            f"Score: {score}\n"
            f"Correct: {'O' if is_correct else 'X'} (GT: {prob.get('answer','')})\n"
            "----------------------------"
        )

    percent = (correct_count / total_count * 100) if total_count else 0
    text_lines.append(
        f"\nCorrect count: {correct_count} / {total_count} ({percent:.1f}%)"
        f"\nTotal score: {total_score} / {max_score}"
    )

    os.makedirs(os.path.dirname(RESULT_PATH), exist_ok=True)
    with open(RESULT_PATH, "w", encoding="utf-8") as f:
        f.write('\n'.join(text_lines))

if __name__ == "__main__":
    main()