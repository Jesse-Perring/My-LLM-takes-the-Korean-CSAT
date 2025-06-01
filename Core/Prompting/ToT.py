from typing import Callable, List, Dict, Any

def generate_thoughts(problem: dict, path_so_far: List[str], model_func: Callable, B: int) -> List[str]:
    """
    현재까지의 사고 경로(path_so_far)를 바탕으로, 다음 단계의 B개 사고 후보를 LLM으로부터 생성
    """
    prompt = (
        f"Problem Number: {problem.get('problem_number', '')}\n"
        f"Problem: {problem.get('problem', '')}\n"
        f"Current reasoning path: {path_so_far}\n"
        f"Think of {B} possible next steps to solve this problem. List each step on a new line."
    )
    response = model_func(prompt)
    thoughts = [line.strip('- ').strip() for line in response.strip().split('\n') if line.strip()]
    return thoughts[:B]

def rank_thoughts(problem: dict, path_so_far: List[str], thoughts: List[str], model_func: Callable) -> List[int]:
    """
    LLM에게 thoughts를 1~3위로 순위 매기게 함. 반환값: [0,1,2] (0=best, 1=2nd, 2=worst)
    """
    thoughts_str = "\n".join([f"{i+1}. {t}" for i, t in enumerate(thoughts)])
    prompt = (
        f"Problem Number: {problem.get('problem_number', '')}\n"
        f"Problem: {problem.get('problem', '')}\n"
        f"Current reasoning path: {path_so_far}\n"
        f"Candidate next steps:\n{thoughts_str}\n"
        "Rank these 3 candidate steps from best (1st) to worst (3rd) for solving the problem. "
        "Reply ONLY with a ranking in the format: 1,2,3 (where 1 is the best, 3 is the worst)."
    )
    response = model_func(prompt)
    # 예: "2,1,3" → [1,0,2]
    ranking = []
    for tok in response.strip().split(','):
        try:
            idx = int(tok.strip()) - 1
            if 0 <= idx < len(thoughts):
                ranking.append(idx)
        except Exception:
            continue
    # ranking: [best_idx, 2nd_idx, worst_idx]
    if len(ranking) != 3:
        # fallback: 그대로 순서
        ranking = [0, 1, 2]
    return ranking

def run_tot(problem: dict, model_func: Callable, max_depth=4) -> str:
    """
    Adaptive Tree of Thoughts: 각 단계에서 3개 후보 생성, LLM이 순위 매김.
    1등 thought는 3개, 2등 thought는 1개, 3등 thought는 확장X. depth=4까지.
    """
    # 각 path는 (사고 경로 list, 현재까지의 순위 score)로 관리
    paths = [([], 0)]  # (path_so_far, score)
    for depth in range(max_depth):
        next_paths = []
        for path_so_far, score in paths:
            # 1. 후보 사고 3개 생성
            thoughts = generate_thoughts(problem, path_so_far, model_func, 3)
            if not thoughts:
                continue
            # 2. LLM에게 순위 매기기
            ranking = rank_thoughts(problem, path_so_far, thoughts, model_func)
            # 3. 분기: 1등은 3개, 2등은 1개, 3등은 확장X
            # 1등 thought 확장 (B=3)
            best_idx = ranking[0]
            for _ in range(3):
                next_paths.append((path_so_far + [thoughts[best_idx]], score + 3))
            # 2등 thought 확장 (B=1)
            second_idx = ranking[1]
            next_paths.append((path_so_far + [thoughts[second_idx]], score + 1))
            # 3등 thought는 확장하지 않음
        # pruning: 너무 많아지지 않게 상위 10개만 유지
        next_paths = sorted(next_paths, key=lambda x: -x[1])[:10]
        if not next_paths:
            break
        paths = next_paths

    # 가장 높은 score의 path 선택
    best_path = paths[0][0] if paths else []
    solution_prompt = (
        f"Problem Number: {problem.get('problem_number', '')}\n"
        f"Problem: {problem.get('problem', '')}\n"
        f"Reasoning path: {best_path}\n"
        "Based on the above reasoning path, write a detailed and natural solution in English. On the last line, clearly state the final answer in the format 'Answer: ...'."
    )
    solution = model_func(solution_prompt)
    return solution.strip()
