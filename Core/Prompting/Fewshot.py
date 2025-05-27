from typing import Callable, Dict

def run_fewshot(problem: Dict, model_func: Callable) -> str:

    with open("prompt/fewshot.txt", "r", encoding="utf-8") as f:
        fewshot_prompt = f.read().strip()
    
    prompt = (
        f"Problem Number: {problem.get('problem_number', '')}\n\n" +
        fewshot_prompt + "\n\n" +
        f"Problem: {problem.get('problem', '')}\n"
    )
    
    solution = model_func(prompt)
    return solution.strip()
