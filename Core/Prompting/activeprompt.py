def run_activeprompt(problem: dict, model_func: Callable[[str], str]) -> str:
    prompt = (
        f"Problem Number: {problem.get('problem_number', '')}\n"
        f"Problem: {problem.get('problem', '')}\n"
        "Before solving, please reflect on the required concepts and conditions.\n"
        "Then, provide a detailed solution and final answer."
    )
    return model_func(prompt)
