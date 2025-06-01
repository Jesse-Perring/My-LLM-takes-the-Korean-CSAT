import re
from collections import Counter
from typing import Callable, List, Dict, Any

# n: API 호출 횟수 (Self-Consistency가 생성할 답변의 수)
def self_consistency(problem: dict, model_func: Callable, n: int) -> List[str]:
    """
    Self-Consistency로 다양한 풀이 생성
    - 같은 문제에 대해 n번 LLM(모델)을 호출하여 다양한 풀이를 얻음
    """
    responses = []
    problem_text = problem["problem"] if "problem" in problem else str(problem)
    for i in range(n):
        # 각 호출마다 동일한 CoT 프롬프트로 풀이 요청
        # zero-shot
        with open("Core/Prompting/CoT.py", "r", encoding="utf-8") as f:
            cot_prompt = f.read().strip()
        response = model_func(cot_prompt)
        if response:
            responses.append(response)
        else:
            print(f"풀이 {i+1} 실패")
            continue
    return responses

def extract_answer(solution: str) -> str:
    """
    다양한 답변 패턴에서 정답만 추출하는 함수
    - 여러 정규표현식 패턴을 사용해 '정답'이 포함된 줄에서 실제 값을 뽑아냄
    """
    patterns = [
        r"Answer[:：]?\s*([^\s.,입니다]+)",          # 영어 Answer: 뒤에 나오는 값
        r"정답[:은]\s*([^\s.,입니다]+)",             # 한글 정답: 또는 정답은 뒤의 값
        r"답은\s*([^\s.,입니다]+)",                  # 한글 답은 뒤의 값
        r"= ?([^\s.,입니다]+)",                      # 등호 뒤의 값 (예: a_2 = 19)
        r"\\boxed{([^}]+)}",                         # LaTeX boxed 안의 값
        r"\$([^\$]+)\$",                             # LaTeX $...$ 안의 값
        r"([0-9]+(?:/[0-9]+)?)",                     # 정수 또는 분수 패턴
    ]
    # 풀이의 각 줄을 뒤에서부터(마지막 줄부터) 검사
    for line in reversed(solution.splitlines()):
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                answer = match.group(1)
                # 후처리: 불필요한 문자 제거
                answer = answer.strip().replace("입니다", "").replace(".", "").replace(",", "").replace(" ", "")
                return answer
    # fallback: 마지막 줄에서 숫자/수식만 추출
    for line in reversed(solution.splitlines()):
        nums = re.findall(r"[0-9]+(?:/[0-9]+)?", line)
        if nums:
            return nums[-1]
    return "정답 없음"   # 아무것도 못 찾았을 때 반환

def generate_explanation(problem: str, solution: str, model_func: Callable) -> str:
    """
    해설 생성 (Prompt Chaining)
    - 최빈값이 포함된 풀이(선택된 풀이)에 대해 해설 생성
    """
    with open("Core/Prompting/CoT.py", "r", encoding="utf-8") as f:
        cot_prompt = f.read().strip()
    
    response = model_func(cot_prompt)
    if response:
        return response
    else:
        print("해설 생성 실패")
        return solution  # 실패시 원래 풀이를 반환

# n: API 호출 횟수 (Self-Consistency가 생성할 답변의 수)
def run_selfconsistency(problem: Dict[str, Any], model_func: Callable) -> str:
    """
    Self-Consistency 방식으로 문제 해결
    - 여러 번 풀이를 생성하고, 최빈값(가장 많이 나온 정답)을 선택
    - 선택된 풀이로 해설을 생성하고, 최종 결과를 포맷에 맞춰 출력
    """
    problem_number = problem["problem_number"]
    problem_text = problem["problem"]
    score = problem["score"]
    
    # Self-Consistency 적용: n번 풀이 생성
    solutions = self_consistency(problem_text, model_func, n=3)  
    if not solutions:
        print(f"{problem_number}번 문제 풀이 실패")
        return ""
    
    # 각 풀이에서 정답만 추출
    answers = [extract_answer(sol) for sol in solutions]
    # 가장 많이 등장한 정답(최빈값) 선택
    most_common_answer = Counter(answers).most_common(1)[0][0]
    
    # 최빈값이 포함된 첫 번째 풀이 선택 (관련성 높은 풀이)
    selected_solution = next((sol for sol in solutions if most_common_answer in sol), solutions[0])
    
    # 선택된 풀이로 해설 생성
    explanation = generate_explanation(problem_text, selected_solution, model_func)
    
    # 결과 포맷팅 및 출력
    result = (
        f"[문제 {problem_number}] (배점: {score})\n"
        f"Solution:\n{explanation.strip()}\n"
        f"Answer: {most_common_answer}\n"
    )
    return result
