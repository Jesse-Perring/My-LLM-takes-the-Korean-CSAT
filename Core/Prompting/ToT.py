from typing import Callable, List, Dict, Any

def generate_thoughts(problem: dict, path_so_far: List[str], model_func: Callable, B: int) -> List[str]:
    """
    현재까지의 사고 경로(path_so_far)를 바탕으로, 다음 단계의 B개 사고 후보를 LLM으로부터 생성
    """
    prompt = (
        f"Problem Number: {problem.get('problem_number', '')}\n"
        f"Problem: {problem.get('problem', '')}\n"
        f"Current reasoning path: {path_so_far}\n"
        f"Think of {B} possible next steps to solve this problem."
    )
    response = model_func(prompt)
    # LLM이 numbered list 또는 줄바꿈으로 사고를 반환한다고 가정
    thoughts = [line.strip('- ').strip() for line in response.strip().split('\n') if line.strip()]
    return thoughts[:B]

def evaluate_thought(problem: dict, thought: str, model_func: Callable) -> bool:
    """
    LLM을 이용해 해당 사고(thought)가 좋은 다음 단계인지 평가 (Yes/No)
    """
    prompt = (
        f"Problem Number: {problem.get('problem_number', '')}\n"
        f"Problem: {problem.get('problem', '')}\n"
        f"Thought: {thought}\n"
        "Is this a good next step? Answer Yes or No and explain briefly. Answer only with 'Yes' or 'No'.\n"
        "If you think this thought is relevant and useful for solving the problem, answer 'Yes'. Otherwise, answer 'No'."
    )
    response = model_func(prompt)
    # 'Yes'가 포함되어 있으면 True, 아니면 False (간단한 파싱)
    return response.strip().lower().startswith('yes')

def run_tot(problem: dict, model_func: Callable, B=3, D=3) -> str:
    """
    ToT 방식으로 문제 해결 경로 탐색 → 최종 풀이 및 정답만 반환 (템플릿 없이)
    problem: 문제 정보를 담은 dict (예: {'problem': '문제 내용', ...})
    """
    # 초기 상태: 빈 사고 경로
    frontier = [ [] ]  # 각 원소는 사고 경로(list of thoughts)
    for depth in range(D):
        next_frontier = []
        for path in frontier:
            thoughts = generate_thoughts(problem, path, model_func, B)
            for thought in thoughts:
                if evaluate_thought(problem, thought, model_func):
                    next_frontier.append(path + [thought])
        # (옵션) pruning/정렬 등은 여기서 추가 가능
        frontier = next_frontier
        if not frontier:
            break  # 더 이상 확장 불가
    # 가장 유망한 사고 흐름 선택 (여기서는 첫 번째, 추후 scoring/pruning 가능)
    best_path = frontier[0] if frontier else []
    # LLM에게 문제 번호와 문제 내용만 전달
    solution_prompt = (
        f"Problem Number: {problem.get('problem_number', '')}\n"
        f"Problem: {problem.get('problem', '')}\n"
        f"Reasoning path: {best_path}\n"
        "Based on the above reasoning path, write a detailed and natural solution in English. On the last line, clearly state the final answer in the format 'Answer: ...'."
    )
    solution = model_func(solution_prompt)
    return solution.strip()
