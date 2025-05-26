from typing import Callable, Dict

def run_zeroshot(problem: Dict, model_func: Callable) -> str:
    """
    # ZeroShot 방식: 문제만 LLM에게 전달하여 풀이 및 정답을 받음
    """
    prompt = (
        f"Problem Number: {problem.get('problem_number', '')}\n"
        f"Problem: {problem.get('problem', '')}\n"
    )
    solution = model_func(prompt)
    return solution.strip()
