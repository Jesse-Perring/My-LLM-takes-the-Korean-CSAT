import re
from typing import Callable

def run_promptchaining(problem: dict, model_func: Callable):
    """
    프롬프트 체이닝
    """
    problem_number = problem["problem_number"]
    problem_text = problem["problem"]
    score = problem["score"]
    category = problem["category"]

    # 1단계: 문제 분석
    prompt_step1 = f"""아래 수학 문제를 분석하여 문제 유형, 핵심 개념, 접근 전략을 정리해 주세요.
문제 분류: {category}
문제: {problem_text}
"""
    analysis_output = model_func(prompt_step1)
    if not analysis_output:
        return {"error": "문제 분석 실패"}

    # 2단계: 풀이 과정 생성
    prompt_step2 = f"""문제: {problem_text}
문제 분류: {category}

이전 단계 분석 결과:
{analysis_output}

위 분석을 바탕으로 단계별 상세 풀이 과정을 작성해 주세요."""
    solution_steps_output = model_func(prompt_step2)
    if not solution_steps_output:
        return {"error": "풀이 과정 생성 실패"}

    # 3단계: 답안지 형식화
    prompt_step3 = f"""문제 번호: {problem_number}
문제: {problem_text}
배점: {score}점

풀이 과정:
{solution_steps_output}

위 정보를 바탕으로 다음 답안지 양식에 맞춰 작성해 주세요:
{problem_number}번 문제 :
풀이 과정 : (여기에 풀이 과정을 자세히 작성)
정답 : (최종 정답만 간단히 작성)
배점 : (문제의 배점 입력)"""
    final_answer_sheet = model_func(prompt_step3)
    if not final_answer_sheet:
        return {"error": "답안지 생성 실패"}

    # 4단계: 풀이 검토
    prompt_step4 = f"""문제: {problem_text}
정답 참조: {problem.get('answer', '')}

풀이 과정:
{solution_steps_output}

최종 답안지:
{final_answer_sheet}

위 풀이 과정을 검토해 주세요.
오류가 있다면 구체적으로 설명하고, 풀이가 완벽하면 '검토 완료: 오류 없음'이라고 응답해 주세요."""
    review_output = model_func(prompt_step4)
    if not review_output:
        review_output = "검토 실패"
    
    solution = (
        f"Problem Number: {problem.get('problem_number', '')}\n"
        f"Problem: {problem.get('problem', '')}\n"
        f"Solution:\n"
        "{\n"
        f"    Analysis(step1): \n{analysis_output}\n"
        f"    Generating solution(step2): {solution_steps_output}\n"
        f"    Formatting as an Answer Sheet(step3): {final_answer_sheet}\n"
        f"    reviewing(step4): {review_output}\n"
        "}\n"
        f"Answer: {extract_answer(final_answer_sheet)}\n"
    )
    return solution.strip()

def extract_answer(text):
    """
    다양한 형식에서 최종 Answer만 추출
    - 'Answer : ...'
    - 'Answer: ...'
    - '정답 : ...'
    - '정답: ...'
    - '\boxed{...}'
    - '= ...'
    - 숫자/분수 등
    """
    patterns = [
        r"Answer\s*[:：]\s*([^\s.,\n]+)",      # Answer : 4
        r"정답\s*[:：]\s*([^\s.,\n]+)",        # 정답 : 4
        r"= ?([^\s.,\n]+)",                   # = 4
        r"\\boxed{([^}]+)}",                  # \boxed{4}
        r"\$([^\$]+)\$",                      # $4$
        r"([0-9]+(?:/[0-9]+)?)",              # 4, 3/4 등
    ]
    # 마지막 줄부터 검사
    for line in reversed(text.splitlines()):
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                answer = match.group(1)
                # 후처리: 불필요한 문자 제거
                answer = answer.strip().replace("입니다", "").replace(".", "").replace(",", "")
                return answer
    return "정답 없음"
