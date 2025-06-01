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
    prompt_step1 = f"""Please analyze the following math problem and summarize the problem type, key concepts, and approach strategies.
Problem Category: {category}
Problem: {problem_text}
"""
    analysis_output = model_func(prompt_step1)
    if not analysis_output:
        return {"error": "문제 분석 실패"}

    # 2단계: 풀이 과정 생성
    prompt_step2 = f"""Problem: {problem_text}
Problem Category: {category}

Based on the previous step’s analysis:
{analysis_output}

Please write a detailed step-by-step solution process based on this analysis."""
    solution_steps_output = model_func(prompt_step2)
    if not solution_steps_output:
        return {"error": "풀이 과정 생성 실패"}

    # 3단계: 답안지 형식화
    prompt_step3 = f"""Problem Number: {problem_number}
Problem: {problem_text}
Points: {score}

Solution Process:
{solution_steps_output}

Based on the information above, please write your answer according to the following answer sheet format:
Problem {problem_number}:
Solution Process: (Write the solution process in detail here)
Answer: (Write only the final answer concisely)
Points: (Enter the points for the problem)"""
    final_answer_sheet = model_func(prompt_step3)
    if not final_answer_sheet:
        return {"error": "답안지 생성 실패"}

    # 4단계: 풀이 검토
    prompt_step4 = f"""Problem: {problem_text}
Reference Answer: {problem.get('answer', '')}

Solution Process:
{solution_steps_output}

Final Answer Sheet:
{final_answer_sheet}

Please review the above solution process.
If there are any errors, explain them in detail. If the solution is perfect, respond with "Review complete: No errors found."""
    review_output = model_func(prompt_step4)
    if not review_output:
        review_output = "Review failed"
    
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
    )
    return solution.strip()
