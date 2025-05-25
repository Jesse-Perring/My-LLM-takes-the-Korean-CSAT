import json
from openai import OpenAI 

# OpenAI 클라이언트 초기화 
client = OpenAI(api_key="")  #api key 입력

# LLM API 호출
def call_llm(system_prompt, user_prompt, model_name="gpt-3.5-turbo"):
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"LLM 호출 중 오류 발생: {e}")
        return None

# 데이터셋 로드
def load_math_problems(file_path="math_problems.json"):
    """JSON 파일에서 수학 문제 데이터를 로드합니다."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"JSON 파일 형식이 올바르지 않습니다: {file_path}")
        return []

# 데이터셋 로드
math_problems_data = load_math_problems()

if not math_problems_data:
    print("데이터셋을 로드할 수 없습니다.")
    exit()

# 프롬프트 체이닝 적용
results = []

for problem_data in math_problems_data:
    problem_number = problem_data["problem_number"]
    problem_text = problem_data["problem"]
    score = problem_data["score"]
    category = problem_data["category"]

    print(f"\n--- {problem_number}번 문제 처리 중 ({category}) ---")

    # 1단계: 문제 분석
    system_prompt_step1 = """주어진 수학 문제를 분석하여 문제 유형과 필요한 수학 개념을 파악해 주세요.

응답 형식:
- 문제 유형: [구체적인 문제 유형]
- 핵심 개념: [필요한 수학 개념들]
- 접근 전략: [단계별 접근 방법]"""
    
    user_prompt_step1 = f"문제 분류: {category}\n문제: {problem_text}"
    analysis_output = call_llm(system_prompt_step1, user_prompt_step1)

    if not analysis_output:
        print("1단계에서 문제 분석 실패.")
        continue

    print(f"1단계 분석 결과:\n{analysis_output}")

    # 2단계: 풀이 과정 생성
    system_prompt_step2 = """이전 단계에서 분석된 내용을 바탕으로 수학 문제의 상세한 풀이 과정을 작성해 주세요. 
각 단계마다 사용된 개념, 공식, 계산 과정을 명확히 보여주세요."""
    
    user_prompt_step2 = f"""문제: {problem_text}
문제 분류: {category}

이전 단계 분석 결과:
{analysis_output}

위 분석을 바탕으로 단계별 상세 풀이 과정을 작성해 주세요."""
    
    solution_steps_output = call_llm(system_prompt_step2, user_prompt_step2)

    if not solution_steps_output:
        print("2단계에서 풀이 과정 생성 실패.")
        continue

    print(f"2단계 풀이 과정:\n{solution_steps_output}")

    # 3단계: 답안지 형식화
    system_prompt_step3 = """주어진 문제 정보와 상세 풀이 과정을 바탕으로, 정확히 다음 답안지 양식에 맞춰 정리해 주세요.

답안지 양식:
{문제번호}번 문제 :
풀이 과정 : (여기에 풀이 과정을 자세히 작성)
정답 : (최종 정답만 간단히 작성)
배점 : (문제의 배점 입력)

위 양식을 정확히 따라 작성해 주세요."""
    
    user_prompt_step3 = f"""문제 번호: {problem_number}
문제: {problem_text}
배점: {score}점

풀이 과정:
{solution_steps_output}

위 정보를 바탕으로 다음 답안지 양식에 정확히 맞춰 작성해 주세요:
{problem_number}번 문제 :
풀이 과정 : (여기에 풀이 과정을 자세히 작성)
정답 : (최종 정답만 간단히 작성)
배점 : (문제의 배점 입력)"""
    
    final_answer_sheet = call_llm(system_prompt_step3, user_prompt_step3)

    if not final_answer_sheet:
        print("3단계에서 답안지 생성 실패.")
        continue

    print(f"3단계 최종 답안지:\n{final_answer_sheet}")

    # 4단계: 풀이 검토
    system_prompt_step4 = """주어진 문제, 풀이 과정, 최종 답을 검토하여 논리적 오류, 계산 실수 또는 풀이 과정의 누락된 부분이 없는지 확인해 주세요. 
오류가 있다면 구체적으로 설명하고, 풀이가 완벽하면 '검토 완료: 오류 없음'이라고 응답해 주세요."""
    
    user_prompt_step4 = f"""문제: {problem_text}
정답 참조: {problem_data['answer']}

풀이 과정:
{solution_steps_output}

최종 답안지:
{final_answer_sheet}

위 풀이 과정을 검토해 주세요."""
    
    review_output = call_llm(system_prompt_step4, user_prompt_step4)
    
    if review_output:
        print(f"4단계 검토 결과:\n{review_output}")
        
        # 최종 결과 저장
        result = {
            "problem_number": problem_number,
            "category": category,
            "analysis": analysis_output,
            "solution": solution_steps_output,
            "final_answer": final_answer_sheet,
            "review": review_output
        }
        results.append(result)
    else:
        print("4단계 검토 실패.")

print(f"\n--- 총 {len(results)}개 문제 처리 완료 ---")

# 결과를 JSON 파일로 저장 
with open('math_solutions.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
