import json
import sys
from typing import List, Dict, Tuple

def judge_by_llm(model_func, problem: dict, model_output: str) -> bool:
    """
    LLM에게 풀이와 정답만 보내 True/False로 채점하게 함.
    """
    judge_prompt = (
        f"Model's solution:\n{model_output}\n"
        f"Ground truth answer: {problem['answer']}\n"
        "Is the model's final answer exactly the same as the ground truth answer? Reply only with True or False."
    )
    judge_result = model_func(judge_prompt)
    return str(judge_result).strip().lower().startswith("true")

def calc_score_stats(results: List[Dict], max_score: int) -> Tuple[int, int, int, float, int]:
    """
    점수 통계 계산 함수.
    Args:
        results (List[Dict]): [{'is_correct': bool, 'score': int}, ...] 형태의 리스트
        max_score (int): 전체 문제의 최고점수 합계
    Returns:
        Tuple: (정답 개수, 전체 개수, 맞힌 문제의 총점, 정답률, max_score)
    """
    total_count = len(results)
    correct_count = sum(1 for r in results if r['is_correct'])
    total_score = sum(r['score'] for r in results if r['is_correct'])
    percent = (total_score / max_score * 100) if max_score else 0
    return correct_count, total_count, total_score, percent, max_score

