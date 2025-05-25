import json
from typing import List, Dict, Generator

def load_problems(problem_path: str) -> List[Dict]:
    """
    문제 JSON 파일을 로드하여 리스트 반환
    Args:
        problem_path (str): 문제 JSON 파일 경로
    Returns:
        List[Dict]: 문제 dict의 리스트
    """
    with open(problem_path, encoding='utf-8') as f:
        return json.load(f)

def crop_problems(problems: List[Dict]) -> Generator[Dict, None, None]:
    """
    문제 리스트에서 문제를 하나씩 yield.
    Args:
        problems (List[Dict]): 문제 dict의 리스트
    Yields:
        Dict: 문제 하나
    """
    for problem in problems:
        yield problem