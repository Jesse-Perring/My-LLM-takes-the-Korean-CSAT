from typing import Callable, Dict

def run_fewshot(problem: Dict, model_func: Callable) -> str:
    fewshot_prompt = """
    Q: There are 15 trees in the grove. Grove workers will plant trees in the grove today. After they are done, there will be 21 trees. How many trees did the grove workers plant today?
    A: 6
    
    Q: If there are 3 cars in the parking lot and 2 more cars arrive, how many cars are in the parking lot?
    A: 5
    
    Q: Leah had 32 chocolates and her sister had 42. If they ate 35, how many pieces do they have left in total?
    A: 39
    
    Q: Jason had 20 lollipops. He gave Denny some lollipops. Now Jason has 12 lollipops. How many lollipops did Jason give to Denny?
    A: 8
    
    Q: Shawn has five toys. For Christmas, he got two toys each from his mom and dad. How many toys does he have now?
    A: 9
    
    Q: There were nine computers in the server room. Five more computers were installed each day, from monday to thursday. How many computers are now in the server room?
    A: 29
    
    Q: Michael had 58 golf balls. On tuesday, he lost 23 golf balls. On wednesday, he lost 2 more. How many golf balls did he have at the end of wednesday?
    A: 33
    
    Q: Olivia has $23. She bought five bagels for $3 each. How much money does she have left?
    A: 8
    """
    
    prompt = (
        f"Problem Number: {problem.get('problem_number', '')}\n\n" +
        fewshot_prompt + "\n\n" +
        f"Problem: {problem.get('problem', '')}\n"
    )
    
    solution = model_func(prompt)
    return solution.strip()
