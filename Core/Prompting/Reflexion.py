from typing import Callable
import time
from evaluator import evaluate_answer

def run_reflexion(problem: dict, model_func: Callable[[str], str], max_retries: int = 2) -> str:
    prev_answer = None
    for attempt in range(max_retries):
        if attempt == 0:
            prompt = f"수능 수학 문제를 읽고 풀이 과정을 작성한 후 마지막 줄에 정답만 출력하세요.\n\n문제 {problem['problem_number']}: {problem['problem']}\n풀이:"
        else:
            prompt = f"앞서 작성한 풀이가 오답일 경우, 틀린 이유를 반영해 다시 풀어보세요. 마지막 줄에 정답만 출력하세요.\n\n문제 {problem['problem_number']}: {problem['problem']}\n이전 답변: {prev_answer}\n다시 작성된 풀이:"

        output = model_func(prompt)
        if evaluate_answer(output, problem["answer"]):
            return output.strip()
        prev_answer = output
        time.sleep(1.2)

    return output.strip()