# "BE MY MUSE” GPT-2 기반 KoGPT를 활용한 감성 작사 모델 개발

### **인원 구성**
- 팀장 : 김형섭(hyeongseob)
- 팀원 : 이성복(sblee)
- 팀원 : 김지민(shocho_kim)

---

## 1. 프로젝트 개요
- ‘다이어리(노래 가제)’ 주제 감성 작사가 공모전용 AI 모델 개발  
- 키워드 입력 시 “나만의 진솔한” 맞춤형 가사 자동 생성 목표
- <a href="https://www.canva.com/design/DAGd1CW20wA/MfQJQDQdldA8Qs6XvhyuLg/edit?utm_content=DAGd1CW20wA&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton"> 프로젝트 발표 자료 링크 </a>

---

## 2. 기술 스택
| 구분    | 기술 및 라이브러리          |
|-------|-------------------------|
| 언어    | Python 3.11             |
| 프레임워크 | FastAPI, uvicorn         |
| 모델    | Hugging Face Transformers (KoGPT2) |
| 크롤링   | BeautifulSoup, Selenium    |
| DB     | PostgreSQL / MariaDB      |
| 배포    | Docker, AWS EC2           |

---

## 데이터 수집 및 전처리
- **정적 크롤링**: BeautifulSoup 기반 멜론 차트 수집  
- **동적 크롤링**: Selenium으로 가사·메타데이터 확보  
- 중복 제거 및 정규화로 최종 4,840곡 데이터셋 구축 

---

## 모델 설계 및 검증

### 1. 모델 알고리즘
- GPT-2 기반 KoGPT2 (skt/kogpt2-base-v2) 선택  
- Auto-Regressive 방식으로 토큰별 다음 단어 예측 

### 2. 맞춤 학습(Fine-Tuning)
- 학습/검증 데이터 분리  
- 학습률·스케줄러·배치 크기 설정을 통한 안정적 학습

### 3. 가사 생성 파이프라인
- `max_length=150`, `temperature=0.9` 등 하이퍼파라미터 조정  
- 키워드 감성 반영하여 1개 시퀀스 생성

### 4. 성능 평가 지표
- BLEU, ROUGE, Perplexity 측정  
- 기준 통과 여부 시각화 

### 5. 감성 분류
- KOTE 모델로 43개 한국어 감정 단어 분류  
- MLM 방식 문장 단위 감성 분석 및 비율 시각화  

---

## 서비스 구현
- **백엔드**: FastAPI 기반 REST & WebSocket 서버  
- **프론트엔드**: 키워드 입력 → 실시간 가사 생성 UI  
- **배포**: Docker 컨테이너, AWS/EC2 등  

---

## 데모 & 뮤직 비디오
1. 웹 서비스 QR 코드  
2. 프로토타입 뮤직 비디오 링크 또는 삽입  

---

## 기여 가이드
1. 이슈 등록 & 토론  
2. 브랜치 생성 (`feature/XX`)  
3. PR 작성 및 리뷰 요청  

---

## 라이선스
MIT License

## 문의
- E-MAIL : rukais2294@gmail.com
