import json
import sys
from typing import List, Dict, Tuple

def extract_answer(solution: str) -> str:
    """
    답안지(또는 LLM 출력)에서 'Answer:'가 포함된 줄을 찾아 정답을 추출.
    없으면 마지막 줄을 fallback으로 사용하며, 이때 경고 로그를 출력.
    Args:
        solution (str): 답안지 전체 문자열
    Returns:
        str: 정규화된 정답 문자열
    """
    answer_line = ""
    for line in reversed(solution.split('\n')):
        if line.strip().startswith('Answer:'):
            answer_line = line
            break
    if answer_line:
        answer = answer_line.split(':', 1)[1].strip()
    else:
        answer = solution.strip().split('\n')[-1].strip()
        print("[extract_answer 경고] 'Answer:' 줄을 찾지 못해 마지막 줄을 정답으로 사용합니다.", file=sys.stderr)
    return answer

def evaluate_answer(answer_norm: str, answer_gt: str) -> bool:
    """
    정답 비교
    Args:
        answer_norm (str): LLM이 출력한 정답
        answer_gt (str): 실제 정답
    Returns:
        bool: 정답 여부
    """
    return (answer_norm == answer_gt and answer_gt != "")

def get_max_score_from_json(json_path: str) -> int:
    """
    JSON 파일에서 최고점수 합계 계산
    Args:
        json_path (str): 문제 JSON 파일 경로
    Returns:
        int: 전체 문제의 최고점수 합계
    """
    with open(json_path, encoding='utf-8') as f:
        problems = json.load(f)
    return sum(int(p['score']) for p in problems if str(p.get('score', '')).isdigit())

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