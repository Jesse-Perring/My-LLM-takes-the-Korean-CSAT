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
# Role             : 역할 기반 프롬프트 
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

# ===== 모델 옵션 (아래 이름을 MODEL_NAME에 사용 띄어쓰기 금지**) =====
# OpenAI      : GPT-4o          ---> GPT4o
# Anthropic   : Claude 3 Opus   ---> Claude3Opus
# Google      : Gemini 1.5 Pro  ---> Gemini1_5Pro
# Mistral     : Mixtral 8x22B   ---> Mixtral8x22B
# Meta        : LLaMA 3 70B     ---> LLaMA3_70B
# ===================================================

MODEL_NAME = "Mixtral8x22B"
PROMPTING_METHOD = "Reflexion"
DATA_FILENAME = "202511_en.json"

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/json'))
JSON_PATH = os.path.join(DATA_DIR, DATA_FILENAME)

def dynamic_import(module_path: str, func_name: str):
    module = importlib.import_module(module_path)
    return getattr(module, func_name)

def main() -> None:
    # 문제 리스트 로드
    problems = problem_loader.load_problems(JSON_PATH)

    # per_problem_results: [(문제번호, 정오, 배점, 과목)]
    # results: [{'is_correct': bool, 'score': int, 'category': str}]
    # model_outputs: [str]
    per_problem_results = []
    results = []
    model_outputs = []

    # 모델 함수: call_model(prompt:str) -> str
    model_func = dynamic_import(f"Models.{MODEL_NAME}", "call_model")
    # 프롬프트 기법 함수: run_zeroshot(problem:dict, model_func:Callable) -> str
    prompt_func = dynamic_import(f"Core.Prompting.{PROMPTING_METHOD}", f"run_{PROMPTING_METHOD.lower()}")

    for idx, problem in enumerate(problem_loader.crop_problems(problems), 1):
        # prompt_func: (problem:dict, model_func:Callable) -> str (풀이+정답)
        # 의미: 문제와 모델을 받아 LLM이 실제로 답변을 생성하는  함수
        model_output = prompt_func(problem, model_func)

        # 문제별 채점 결과를 누적
        model_outputs.append(model_output)

        # LLM에게 다시 채점 요청
        is_correct = scoring.judge_by_llm(model_func, problem, model_output)

        # 문제별 채점 결과를 표준화된 구조로 누적
        result_writer.append_result(results, per_problem_results, problem, is_correct)

        # 진행률 로그 출력
        print(f"[{idx}/{len(problems)}] 문제 {problem.get('problem_number', idx)} 처리 완료 (정오: {is_correct})")

    # 모든 결과를 읽기 편한 텍스트 라인으로 변환
    text_lines = result_writer.write_result_lines(per_problem_results, results, problems, model_outputs)
    
    # 결과 텍스트 파일 저장
    result_writer.save_results(
        text_lines, MODEL_NAME, PROMPTING_METHOD, DATA_FILENAME
    )
    # 예시:
    # text_lines =
    # [
    #   "[모델 답변]",
    #   "문제 1:\nTo solve the problem, first recognize that 25^{1/3} is the cube root of 25, ...\nAnswer: 5\n",
    #   "문제 2:\nFirst, compute f(2) = 2^3 - 8*2 + 7 = ...\nAnswer: 4\n",
    #   ...,
    #   "문제번호\t정오\t배점\t과목",
    #   "1\tTrue\t2\t수학1",
    #   "2\tFalse\t2\t수학2",
    #   ...,
    #   "\n[전체 통계]",
    #   "정답 개수: 18/30\n총점: 56 / 90\n정답률: 62.22%",
    #   "\n[과목별 통계]",
    #   "(수학1)",
    #   "정답 개수: 7/12\n총점: 18 / 36\n정답률: 50.00%",
    #   "(수학2)",
    #   "정답 개수: 6/10\n총점: 20 / 30\n정답률: 66.67%",
    #   "(미적분)",
    #   "정답 개수: 5/8\n총점: 18 / 24\n정답률: 75.00%"
    # ]

if __name__ == "__main__":
    main()