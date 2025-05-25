import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import dotenv
dotenv.load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

import importlib
import Utils.problem_loader as problem_loader
import Utils.scoring as scoring
import Utils.result_writer as result_writer
import os

# ===== 프롬프트 기법 옵션 (아래 이름을 PROMPTING_METHOD에 사용) =====
# ZeroShot         : 아무 예시 없이 문제만 던짐 (베이스라인 실험용)
# FewShot          : 유사 예제 몇 개 보여주고 문제 던짐 (패턴 학습 유도)
# CoT              : Chain-of-Thought, 단계별 사고 유도 (수능 풀이 과정 구조화)
# SelfConsistency  : CoT 여러 번 생성 후 다수결 (정답률 안정화)
# ReAct            : 추론 중 도구 사용 (계산 문제 등, 도구 API 필요)
# ToT              : Tree of Thoughts, 여러 사고 경로 트리 탐색 (난이도 높은 문제)
# PromptChaining   : 여러 프롬프트 순차 연결 ("개념 설명→풀이" 등)
# Reflexion        : 모델이 스스로 피드백 후 재시도 (실수 잡기)
# ActivePrompt     : 문제 관련 지식 능동 요구 ("어떤 개념이 필요?" 등)
# ============================================================

# ===== 모델 옵션 (아래 이름을 MODEL_NAME에 사용) =====
# OpenAI      : GPT-4o
# Anthropic   : Claude 3 Opus
# Google      : Gemini 1.5 Pro
# Mistral     : Mixtral 8x7B
# Meta        : LLaMA 3 70B
# ===================================================

MODEL_NAME = "Mixtral8x22B"
PROMPTING_METHOD = "ToT"
DATA_FILENAME = "202511.json"

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/json'))
JSON_PATH = os.path.join(DATA_DIR, DATA_FILENAME)

ANSWER_SHEET_TEMPLATE = (
    "Problem {problem_number}:\n"
    "Solution: {solution}\n"
    "Answer: {answer}\n"
)

def dynamic_import(module_path: str, func_name: str):
    module = importlib.import_module(module_path)
    return getattr(module, func_name)

def main() -> None:
    # 1. 데이터셋 로드
    problems = problem_loader.load_problems(JSON_PATH)
    text_lines = []
    results = []

    # 2. 동적으로 모델 함수와 프롬프트 기법 함수 import
    model_func = dynamic_import(f"Models.{MODEL_NAME}", "call_model")
    prompt_func = dynamic_import(f"Core.Prompting.{PROMPTING_METHOD}", f"run_{PROMPTING_METHOD.lower()}")

    # 3. 문제별 처리
    for problem in problem_loader.crop_problems(problems):
        # 템플릿을 프롬프트 기법 함수에 전달
        answer_sheet = prompt_func(problem, model_func, ANSWER_SHEET_TEMPLATE)
        answer_norm = scoring.extract_answer(answer_sheet)
        is_correct = scoring.evaluate_answer(answer_norm, problem['answer'])
        results.append({'is_correct': is_correct, 'score': problem['score']})
        text_lines.append(
            f"{answer_sheet}\n정답: {problem['answer']} | {'O' if is_correct else 'X'}\n"
        )

    # 4. 점수 통계
    max_score = sum(p['score'] for p in problems)
    stats_tuple = scoring.calc_score_stats(results, max_score)
    stats_text = result_writer.stats_tuple_to_text(stats_tuple)
    text_lines.append("\n" + stats_text)

    result_writer.save_results(
        text_lines, MODEL_NAME, PROMPTING_METHOD, DATA_FILENAME
    )

if __name__ == "__main__":
    main()