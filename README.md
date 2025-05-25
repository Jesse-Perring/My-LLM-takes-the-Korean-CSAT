# Together AI 모델 사용 안내

- Together AI에는 **서버리스(즉시 사용 가능) 모델**과 **Dedicated Endpoint(전용 엔드포인트 필요) 모델**이 있습니다.
- 예시:
  - `mistralai/Mixtral-8x22B-Instruct-v0.1` → 서버리스(즉시 사용 가능, 별도 생성 불필요)
  - `nim/mistralai/mixtral-8x22b-instruct-v01` → 전용 엔드포인트 필요

## 서버리스 모델만 쓸 경우

- `mistralai/Mixtral-8x22B-Instruct-v0.1` 등은 별도 엔드포인트 생성 없이 바로 사용 가능합니다.
- **코드에서 model 파라미터를 반드시 서버리스 모델명으로 지정해야 합니다.**
  - 예시:
    ```python
    model="mistralai/Mixtral-8x22B-Instruct-v0.1"
    ```

## 전용 엔드포인트란?

- 특정 모델(특히 `nim/` 등 프리미엄/대형 모델)은 바로 API 호출이 불가하며,
- Together AI 웹사이트에서 **엔드포인트를 직접 생성(Deploy/Create Endpoint)** 해야 사용 가능합니다.
- 전용 엔드포인트는 사용 시간/분당 과금이 발생합니다.

## 엔드포인트 생성 방법

1. [Together AI 모델 페이지](https://api.together.ai/models) 접속
2. 원하는 모델(예: `nim/mistralai/mixtral-8x22b-instruct-v01`) 선택
3. "Create Endpoint" 또는 "Deploy" 버튼 클릭
4. 생성 후 안내되는 엔드포인트 이름/URL을 코드에 사용

---

**정리:**  
- 서버리스 모델명(`mistralai/Mixtral-8x22B-Instruct-v0.1`)을 사용하면 별도 작업 없이 바로 API 호출 가능  
- `nim/` 등 dedicated endpoint 모델은 직접 엔드포인트를 생성(Deploy)해야 사용 가능  
- 404, model_not_available 에러가 발생하면 서버리스 모델명으로 바꾸거나, 엔드포인트를 생성해야 함
