from typing import Callable
import time
from evaluator import evaluate_answer

def run_reflexion(problem: dict, model_func: Callable[[str], str], max_retries: int = 2) -> str:
    prev_answer = None
    for attempt in range(max_retries):
        if attempt == 0:
            prompt = f"���� ���� ������ �а� Ǯ�� ������ �ۼ��� �� ������ �ٿ� ���丸 ����ϼ���.\n\n���� {problem['problem_number']}: {problem['problem']}\nǮ��:"
        else:
            prompt = f"�ռ� �ۼ��� Ǯ�̰� ������ ���, Ʋ�� ������ �ݿ��� �ٽ� Ǯ�����. ������ �ٿ� ���丸 ����ϼ���.\n\n���� {problem['problem_number']}: {problem['problem']}\n���� �亯: {prev_answer}\n�ٽ� �ۼ��� Ǯ��:"

        output = model_func(prompt)
        if evaluate_answer(output, problem["answer"]):
            return output.strip()
        prev_answer = output
        time.sleep(1.2)

    return output.strip()