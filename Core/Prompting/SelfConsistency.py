import re
from collections import Counter
from typing import Callable, List, Dict, Any

# n: API 호출 횟수 (Self-Consistency가 생성할 답변의 수)
def self_consistency(problem: str, model_func: Callable, n: int) -> List[str]:
    """
    Self-Consistency로 다양한 풀이 생성
    - 같은 문제에 대해 n번 LLM(모델)을 호출하여 다양한 풀이를 얻음
    """
    responses = []
    for i in range(n):
        # 각 호출마다 동일한 CoT 프롬프트로 풀이 요청
        # zero-shot
        cot_prompt = f"문제: {problem}\n풀이 과정을 자세히 작성해주세요. 문제를 풀고 마지막에 Answer: 값 형태로 최종 답을 명시해주세요."
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
       r'Answer:\s*(.+?)(?:\n|$)',                    # Answer: 5
       r'답:\s*(.+?)(?:\n|$)',                        # 답: 5  
       r'∴\s*(.+?)(?:\n|$)',                         # ∴ 5
   ]
   
   # 풀이의 각 줄을 뒤에서부터(마지막 줄부터) 검사
   lines = solution.splitlines()
   for line in reversed(lines):
       line = line.strip()
       if not line:  # 빈 줄 건너뛰기
           continue
           
       for pattern in patterns:
           match = re.search(pattern, line, re.IGNORECASE)
           if match:
               answer = match.group(1).strip()
               # 후처리: 불필요한 문자 제거
               answer = clean_answer(answer)
               if answer:  # 빈 문자열이 아닌 경우만 반환
                   return answer
   
   # fallback 1: 숫자가 포함된 마지막 몇 줄에서 수학적 표현 찾기
   for line in reversed(lines[-5:]):  # 마지막 5줄만 확인
       line = line.strip()
       if not line:
           continue
           
       # 분수, 소수, 정수, 수식 등을 찾기
       math_expressions = re.findall(r'-?\d+(?:\.\d+)?(?:/\d+)?|[a-zA-Z]\s*=\s*-?\d+(?:\.\d+)?', line)
       if math_expressions:
           # 가장 마지막 수학적 표현 반환
           return clean_answer(math_expressions[-1])
   
   # fallback 2: 단순 숫자 찾기
   for line in reversed(lines[-3:]):  # 마지막 3줄만 확인
       line = line.strip()
       numbers = re.findall(r'-?\d+(?:\.\d+)?', line)
       if numbers and len(numbers) <= 3:  # 숫자가 너무 많으면 답이 아닐 가능성
           return numbers[-1]
   
   return "정답 없음"

def clean_answer(answer: str) -> str:
   """답에서 불필요한 문자들을 제거하고 정리"""
   if not answer:
       return ""
   
   # 기본 정리
   answer = answer.strip()
   
   # 한국어 종결어미 제거
   korean_endings = ["입니다", "이다", "다", "임", "이고", "입니다."]
   for ending in korean_endings:
       if answer.endswith(ending):
           answer = answer[:-len(ending)].strip()
   
   # 구두점 제거 (단, 소수점과 분수 구분자는 보존)
   answer = re.sub(r'[,.!?;]$', '', answer)  # 끝에 있는 구두점만 제거
   
   # 공백 정리
   answer = re.sub(r'\s+', ' ', answer).strip()
   
   # 등호나 변수명이 포함된 경우 처리 (예: k = 5 -> 5)
   eq_match = re.search(r'[a-zA-Z]\s*=\s*(.+)', answer)
   if eq_match:
       answer = eq_match.group(1).strip()
   
   # 괄호 안의 내용만 있는 경우 괄호 제거
   paren_match = re.match(r'^\((.+)\)$', answer)
   if paren_match:
       answer = paren_match.group(1).strip()
   
   return answer

def generate_explanation(problem: str, solution: str, model_func: Callable) -> str:
    """
    해설 생성 (Prompt Chaining)
    - 최빈값이 포함된 풀이(선택된 풀이)에 대해 해설 생성
    """
    cot_prompt = f"문제: {problem}\n아래의 풀이를 바탕으로 해설을 작성하세요:\n{solution}"
    
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
    print(problem_text)
    score = problem["score"]
    
    print(f"\n=== {problem_number}번 문제 시작 ===")
    print(problem_text)

    # Self-Consistency 적용: n번 풀이 생성
    solutions = self_consistency(problem_text, model_func, 3)  
    if not solutions:
        print(f"{problem_number}번 문제 풀이 실패")
        return ""
    
    for sol in solutions:
      print(sol);
    
    # 각 풀이에서 정답만 추출
    #answers = [extract_answer(sol) for sol in solutions]
    # 가장 많이 등장한 정답(최빈값) 선택
    answers = []
    print("\n---------- extract_answer 결과 ----------") # 구분선 추가
    for i, sol in enumerate(solutions):  # solutions의 각 solution에 대해 반복
        print(f"Solution {i+1} 해설")
        print(sol);
        extracted_value = extract_answer(sol)  # extract_answer 함수 호출
        print(f"-> 추출된 값: '{extracted_value}'")  # 각 결과를 출력
        answers.append(extracted_value)  # 결과를 answers 리스트에 추가
    print("------------------------------------")
    
    # answers 리스트 최종 내용 확인
    print(f"\n최종 answers 리스트: {answers}")
    answers = [ans for ans in answers if ans != "정답 없음"]
    print(f"\n유효한 답변들: {answers}")

    if not answers:
            print("경고: 유효한 답변이 없습니다.")
            most_common_answer = "정답 없음"

    #most_common_answer = Counter(answers).most_common(1)[0][0]
    if not answers:
        most_common_answer = "추출된 답변 없음"
        print("Warning: answers 리스트가 비어 있어 most_common_answer를 설정할 수 없습니다.")
    else:
        answer_counts = Counter(answers)
        if not answer_counts:
            most_common_answer = "유효한 답변 카운트 없음"
        else:
            common_answers = answer_counts.most_common(1)
            if common_answers:
                most_common_answer = common_answers[0][0] 
            else:
                most_common_answer = "최빈값 찾기 실패"

    # 최빈값이 포함된 첫 번째 풀이 선택 (관련성 높은 풀이)
    selected_solution = solutions[0]
    for sol in solutions:
      if extract_answer(sol) == most_common_answer:
          selected_solution = sol
          break # most_common_answer와 일치하는 첫 번째 풀이를 찾으면 중단

    #selected_solution = next((sol for sol in solutions if most_common_answer in sol), solutions[0])
    
    # 선택된 풀이로 해설 생성
    explanation = generate_explanation(problem_text, selected_solution, model_func)
    
    # 결과 포맷팅 및 출력
    result = (
        f"[문제 {problem_number}] (배점: {score})\n"
        f"Solution:\n{explanation.strip()}\n"
        f"Answer: {most_common_answer}\n"
    )
    print(result)
    print(f"\n=== {problem_number}번 문제 완료 ===")

    return result
