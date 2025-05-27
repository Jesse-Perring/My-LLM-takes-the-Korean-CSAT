from typing import Callable, Dict

def run_cot(problem: Dict, model_func: Callable) -> str:

    with open("prompt/chain-of-thought.txt", "r", encoding="utf-8") as f:
        cot_prompt = f.read().strip()
    
    prompt = (
        f"Problem Number: {problem.get('problem_number', '')}\n\n" +
        cot_prompt + "\n\n" +
        f"Problem: {problem.get('problem', '')}\n"
    )
    
    solution = model_func(prompt)
    return solution.strip()
