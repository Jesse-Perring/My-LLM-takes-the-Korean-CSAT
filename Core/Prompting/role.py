from typing import Callable


def run_role(problem: dict, model_func: Callable[[str], str]) -> str:
    prompt = (
        f"Problem Number: {problem.get('problem_number', '')}\n"
        f"Problem: {problem.get('problem', '')}\n"
        "You are a top Korean high school student preparing for the 수능.\n"
        "Solve this problem logically and step-by-step, and provide a clear final answer."
    )
    return model_func(prompt)
