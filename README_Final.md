## LLM 기반 작사 자동화 알고리즘 모델 개발

### 프로젝트 개요

- 본 프로젝트는 대중적인 음악 작사 과정을 자동화하기 위한 LLM(대규모 언어 모델) 기반 작사 알고리즘을 개발하는 것을 목표로 합니다. 
프로젝트는 자연어 처리(NLP) 및 생성형 AI를 활용하여 이를 기반으로 새로운 가사를 생성하며, 문장 구조 및 감성 적합성을 검증하는 과정을 포함합니다.
- 기간: 2025.1.3 ~ 2025.2.3

◆ 팀원 및 역할

김형섭: 음원 사이트 데이터 수집, 형태소 분석, 모델 개발 등..
김지민: 음원 사이트 데이터 수집, 형태소 분석, 모델 개발 등..
이성복: 음원 사이트 데이터 수집, 형태소 분석, 가사 생성 여러 모델 테스트 등..

### 주요 절차

1. 데이터 수집

- 음악 차트에서 가사 데이터를 수집하여 학습 데이터로 활용합니다.

크롤링 방식 -  동적 크롤링: Selenium, 정적 크롤링: BeautifulSoup4

수집 데이터 - 곡 제목, 아티스트, 좋아요 수, 가사, 발매일

2. 데이터 전처리

- 수집한 데이터를 정리하고 모델 학습에 적합한 형태로 변환합니다.

정규화 - 특수기호 제거, 불필요한 공백 처리 (re.sub 활용)

형태소 분석 및 N-gram 변환 - KoNLPy (Komoran), NLTK 활용

3. 가사 생성 알고리즘 구현

: Transformers 기반 KoGPT-2 모델을 활용하여 새로운 가사를 생성합니다.

모델 학습 - 학습 데이터로 기존 가사 데이터를 활용

KoGPT-2를 Fine-Tuning하여 새로운 문장을 생성

텍스트 생성 코드 예시:
```
from transformers import GPT2LMHeadModel, GPT2Tokenizer

model_name = "gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

def generate_lyrics(prompt, max_length=50, temperature=1.0):
    inputs = tokenizer.encode(prompt, return_tensors="pt")
    outputs = model.generate(inputs, max_length=max_length, temperature=temperature, num_return_sequences=1)
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return generated_text
```
4. 문장 구조 완성도 분석

생성된 가사의 품질을 평가하고 기존 가사와의 유사도를 검증합니다.

유사도 분석 도구 - 코사인 유사도 (Cosine Similarity)

SVM 기반 검증 모델:

- BERT 임베딩을 활용하여 가사 문장 구조를 벡터화

- SVM 모델로 문장 구조의 적합성을 학습 및 평가

문장 구조 유사도 기준 - 유사도 점수 0.76 이상인 문장만 선별

5. 감성 분류

KOTE(Korean Open Translation Emotion)를 활용하여 가사를 테마별로 감성 분류합니다.

분류 대상 테마:

1. 테마 1번 : 쓸쓸함 → R&B/Soul → 안타까움/실망, 아껴주는, 편안/쾌적, 힘듦/지침, 한심함
2. 테마 2번 : 소확행 → 인디장르 → 기대감, 편안/쾌적, 신기함/관심, 아껴주는, 안심/신뢰 
3. 테마 3번 : 인내 → 랩/힙합 → 불평/불만, 화남/분노, 불안/걱정, 패배/자기혐오, 힘듦/지침

6. 가사 데이터 완성

- 최종적으로 16마디 길이의 완성된 가사 데이터를 생성합니다.

### 기술 스택 및 사용 도구

- 주요 라이브러리

크롤링: Selenium, BeautifulSoup4

형태소 분석 및 N-gram 생성: KoNLPy (Komoran), NLTK

Transformers 모델: Hugging Face Transformers (KoGPT-2, BERT)

머신러닝: Scikit-learn (SVM)

임베딩 및 유사도 계산: BERT, Cosine Similarity

- 설치 명령어 예시

``` pip install numpy pandas selenium konlpy nltk transformers scikit-learn matplotlib seaborn scipy ```

### 결과물

생성된 가사:

KoGPT-2 기반으로 창작된 고품질 가사

문장 구조 검증 보고서:

기존 가사와의 유사도 분석 결과

감성 분류 레이블:

테마에 적합한 감성 레이블 부여된 최종 가사 데이터

시각화 결과:

PCA 기반 임베딩 클러스터링 및 가사 감성 분포 시각화

### ☞ 참고 자료

KoGPT2 GitHub Repository

한국어 문장의 법칙

### 프로젝트 절차 요약 (Rev. 1)

데이터 수집 및 병합 (웹 크롤링)

데이터 정규화 및 NLP 전처리

KoGPT-2 모델로 새로운 가사 생성

문장 구조 유사도 검증 (SVM, Cosine Similarity)

감성 분류를 통한 테마 적합성 분석

최종 16마디 가사 데이터 완성 및 보고
