## FastAPI + Streamlit 기반 svm 모델 학습 및 평가 

# 목표:
# FastAPI 서버에서 문장 자연스러움 평가 모델 실행
# Streamlit 웹 인터페이스에서 사용자가 문장을 입력하면 점수 출력
# API를 호출해서 문장이 자연스러운지 0~1 사이 점수로 평가
# OpenAI API가 아니라, 우리 자체 모델(SVM/TF-IDF or BERT Fine-tuning) 활용 (openAI 에 불지르려다 참고 지성적인 방안 모색함)

import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"  # FastAPI 서버 주소

st.title("가사 문장 자연스러움 평가")

# 비문 데이터 불러오기
st.header("비문 데이터")
response = requests.get(f"{API_URL}/get_sentences")
if response.status_code == 200:
    sentences = response.json()["sentences"]
else:
    st.error("비문 데이터를 불러오지 못했습니다.")
    sentences = []

# 현재 문장 인덱스 저장 (세션 상태 사용)
if "current_index" not in st.session_state:
    st.session_state.current_index = 0

# 현재 문장 표시
if sentences:
    current_sentence = sentences[st.session_state.current_index]
    st.write(f"**원본 문장:** {current_sentence['original']}")
    st.write(f"**비문:** {current_sentence['generated']}")

    # 정수 점수 선택 (0~5)
    score = st.radio("자연스러움 점수 (정수 선택)", [0, 1, 2, 3, 4, 5], index=2)

    # "점수 제출" 버튼
    if st.button("점수 제출"):
        payload = {
            "original": current_sentence["original"],
            "generated": current_sentence["generated"],
            "score": score
        }
        response = requests.post(f"{API_URL}/submit_label", json=payload)
        if response.status_code == 200:
            st.success("라벨링 완료!")

            # 다음 문장으로 이동 (마지막 문장이면 처음부터 반복)
            st.session_state.current_index = (st.session_state.current_index + 1) % len(sentences)

            # 새 문장 즉시 업데이트 (Streamlit UI 갱신)
            st.rerun()
        else:
            st.error("라벨링 저장 실패")

# 현재까지 라벨링된 데이터 확인
st.header("라벨링된 데이터")
response = requests.get(f"{API_URL}/get_labeled_data")
if response.status_code == 200:
    labeled_data = response.json()["labeled_data"]
    if labeled_data:
        df = pd.DataFrame(labeled_data)
        st.dataframe(df)
    else:
        st.write("아직 라벨링된 데이터가 없습니다.")

