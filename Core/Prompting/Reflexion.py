from typing import Callable, Dict

def run_reflexion(problem: Dict, model_func: Callable) -> str:
    """
    Reflexion method:
    1. Generate an initial response to the given problem,
    2. Then prompt the model to reflect on that answer and provide a revised response if needed.
    """

    # Step 1: Generate initial answer
    initial_prompt = (
        f"Problem Number: {problem.get('problem_number', '')}\n"
        f"Problem: {problem.get('problem', '')}\n"
        f"Please provide your detailed reasoning and final answer.\n"
    )
    first_response = model_func(initial_prompt).strip()

    # Step 2: Prompt for self-reflection and revision
    reflexion_prompt = (
        f"Here is your initial answer:\n{first_response}\n\n"
        f"Reflect on this answer. Are there any mistakes or improvements needed?\n"
        f"Please revise your reasoning and final answer if necessary."
    )
    final_response = model_func(reflexion_prompt).strip()

    return final_response
