from openai import OpenAI
from collections import Counter
import json

# OpenAI 클라이언트 초기화
client = OpenAI(api_key="")

# # LLM API 호출, Self-Consistency로 다양한 풀이 생성
def generate_solutions(problem, n=2):    # n을 5에서 2로 줄임 (API 호출 횟수 감소)
    responses = []
    for i in range(n):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # 또는 "gpt-4o-mini", "gpt-4o" 사용 가능
                temperature=0.7,
                messages=[
                    # CoT 적용(필수) - self-consistency는 CoT 위에서 작용하는 기법
                    # zero-shot을 적용함(few-shot 적용 시 정밀도 증가)
                    {"role": "user", "content": f"문제: {problem}\n풀이 과정을 자세히 작성해주세요."}

                    # 앙상블 적용(선택)
                    # role-based prompting 적용 예시
                    # {"role": "system", "content": "당신은 수능 수학 선생님입니다. 문제를 다양한 풀이 방법으로 풉니다."},
                ]
            )
            responses.append(response.choices[0].message.content)
        except Exception as e:
            print(f"풀이 {i+1} 실패: {str(e)}")
            continue
    return responses

# 정답 추출 (단순 숫자 또는 수식 중심)
def extract_answer(solution):
    lines = solution.splitlines()
    for line in reversed(lines):
        if "정답" in line or "답은" in line or "=" in line:
            return line.strip().split()[-1]
    return "정답 없음"

# 해설 생성 (Prompt Chaining)
def generate_explanation(problem, solution):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # 모델 선택
            temperature=0.5,
            messages=[
                # CoT 적용(필수)
                # zero-shot을 적용함
                {"role": "user", "content": f"문제: {problem}\n아래의 풀이를 바탕으로 해설을 작성하세요:\n{solution}"}

                # 앙상블 적용(선택)
                # role-based prompting 적용 예시
                # {"role": "system", "content": "당신은 수능 수학 해설 전문가입니다. 명확하고 자세한 해설을 작성합니다."},
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"해설 생성 실패: {str(e)}")
        return solution  # 실패시 원래 풀이를 반환

# 출력 포맷 함수
def format_solution(problem_number, solution_text, final_answer, score):
    return f"""Problem {problem_number}:
Solution:
{solution_text.strip()}

Answer: {final_answer.strip()}
Score: {score}
"""

# 데이터셋 로드
def load_math_problems(file_path="math_problems.json"):
    """JSON 파일에서 수학 문제 데이터를 로드합니다."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"JSON 파일 형식이 올바르지 않습니다: {file_path}")
        return []

# 데이터셋 로드
math_problems_data = load_math_problems()

if not math_problems_data:
    print("데이터셋을 로드할 수 없습니다.")
    exit()

# 전체 문제 실행
results = []

for problem_data in math_problems_data:
    problem_number = problem_data["problem_number"]
    problem_text = problem_data["problem"]
    score = problem_data["score"]

    print(f"\n{problem_number}번 문제를 풀이 중...")

    # Self-Consistency 적용 (API 호출 횟수 줄임)
    solutions = generate_solutions(problem_text, n=2)  # 5에서 2로 줄임

    if not solutions:
        print(f"{problem_number}번 문제 풀이 실패 - API 호출 실패")
        continue

    answers = [extract_answer(sol) for sol in solutions]
    most_common_answer = Counter(answers).most_common(1)[0][0]

    # 가장 관련 있는 풀이 선택
    selected_solution = next((sol for sol in solutions if most_common_answer in sol), solutions[0])

    # 해설 생성 (optional)
    explanation = generate_explanation(problem_text, selected_solution)

    # 답안지 출력
    result = format_solution(problem_number, explanation, most_common_answer, score)
    print(result)
    results.append(result)

# 결과를 JSON 파일로 저장 
with open('math_solutions.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
    
