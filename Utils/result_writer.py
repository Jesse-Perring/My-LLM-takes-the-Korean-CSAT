import os

# RESULT_BASE_DIR를 절대경로로 지정 (항상 프로젝트 루트의 Result_llm_by_llm에 저장)
RESULT_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Result_llm_by_llm"))

def get_result_path(model_name: str, prompting_method: str, data_filename: str) -> str:
    """
    모델명/프롬프팅기법별 폴더에 prompting_method_data_filename.txt 파일 경로 반환
    """
    # dir_path는 RESULT_BASE_DIR(상대경로) + model_name
    dir_path = os.path.join(RESULT_BASE_DIR, model_name)
    os.makedirs(dir_path, exist_ok=True)
    filename = f"{prompting_method}_{data_filename}_result.txt"
    return os.path.join(dir_path, filename)

def write_text_lines_to_file(text_lines, result_path):
    """
    텍스트 라인 리스트를 지정한 파일(result_path)에 저장
    """
    with open(result_path, "w", encoding="utf-8") as f:
        for line in text_lines:
            f.write(line + "\n")

def stats_tuple_to_text(stats_tuple):
    """
    stats_tuple을 사람이 읽기 좋은 통계 문자열로 변환
    """
    if not stats_tuple:
        return ""
    correct_count, total_count, total_score, percent, max_score = stats_tuple
    stats_text = (
        f"정답 개수: {correct_count}/{total_count}\n"
        f"총점: {total_score} / {max_score}\n"
        f"정답률: {percent:.2f}%"
    )
    return stats_text

def save_results(text_lines, model_name, prompting_method, data_filename, stats_tuple=None):
    """
    전체 결과 저장 함수: 텍스트 라인 저장 + 통계 문자열 추가
    """
    result_path = get_result_path(model_name, prompting_method, data_filename)
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, "w", encoding="utf-8") as f:
        for line in text_lines:
            f.write(line + "\n")
        # stats_tuple이 있으면 통계도 추가
        if stats_tuple:
            stats_text = stats_tuple_to_text(stats_tuple)
            f.write('\n\n')
            f.write(stats_text)

def append_result(results, per_problem_results, problem, is_correct):
    """
    문제별 채점 결과를 results, per_problem_results에 추가
    """
    results.append({
        'is_correct': is_correct,
        'score': problem['score'],
        'category': problem.get('category', '')
    })
    per_problem_results.append((
        problem.get('problem_number', ''),
        is_correct,
        problem['score'],
        problem.get('category', '')
    ))

def write_result_lines(per_problem_results, results, problems, model_outputs):
    """
    결과 파일용 text_lines 생성
    """
    import Utils.scoring as scoring  # 순환 import 방지용
    text_lines = []
    # 0. 모델 답변 누적
    text_lines.append("[모델 답변]")
    for idx, model_output in enumerate(model_outputs):
        text_lines.append(f"문제 {per_problem_results[idx][0]}:\n{model_output}\n")
    # 1. 문제별 결과
    text_lines.append("문제번호\t정오\t배점\t과목")
    for num, correct, score, category in per_problem_results:
        text_lines.append(f"{num}\t{correct}\t{score}\t{category}")
    # 2. 전체 통계
    max_score = sum(p['score'] for p in problems)
    stats_tuple = scoring.calc_score_stats(results, max_score)
    stats_text = stats_tuple_to_text(stats_tuple)
    text_lines.append("\n[전체 통계]")
    text_lines.append(stats_text)
    # 3. 과목별 통계
    category_dict = {}
    for idx, r in enumerate(results):
        category = problems[idx].get('category', '')
        if category not in category_dict:
            category_dict[category] = []
        category_dict[category].append(r)
    text_lines.append("\n[과목별 통계]")
    for category, rlist in category_dict.items():
        cat_max_score = sum(r['score'] for r in rlist)
        cat_stats = scoring.calc_score_stats(rlist, cat_max_score)
        cat_stats_text = stats_tuple_to_text(cat_stats)
        text_lines.append(f"({category})")
        text_lines.append(cat_stats_text)
    return text_lines

