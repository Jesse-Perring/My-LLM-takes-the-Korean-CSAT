import os

RESULT_BASE_DIR = os.path.join("Result_llm_by_llm")  # 상대경로로 통일

def get_result_path(model_name: str, prompting_method: str, data_filename: str) -> str:
    """
    모델명/프롬프팅기법별 폴더에 prompting_method_data_filename.txt 파일 경로 반환
    """
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