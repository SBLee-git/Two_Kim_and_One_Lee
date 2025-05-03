import streamlit as st
import requests
import pandas as pd

# FastAPI 서버 주소
API_URL = "http://127.0.0.1:8000/api"

# 세션 상태 초기화
if "generated_lyrics" not in st.session_state:
    st.session_state.generated_lyrics = ""  # 생성된 가사 저장
if "latest_saved_lyrics" not in st.session_state:
    st.session_state.latest_saved_lyrics = ""  # 최근 저장된 가사
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = []  # 감성 분석 결과

# 탭 구조 (가사 생성기, 가사 평가, 감성 분류, 뮤직 비디오)
tab1, tab2, tab3, tab4 = st.tabs(["🎤 가사 생성기", "📊 가사 평가", "🧠 감성 분류", "☑️ 뮤직비디오"])

# 1️⃣ 가사 생성기 탭
with tab1:
    st.title("🎶 김둘이하나 : 가사 생성기 🎶")

    user_input = st.text_input("당신의 가사를 완성할 첫 마디를 입력하세요:")

    if st.button("🎼 생성하기"):
        if user_input:
            with st.spinner("생성 중... 잠시만 기다려 주세요! 🚀"):
                response = requests.post(f"{API_URL}/generate/", json={"text": user_input})

                if response.status_code == 200:
                    st.session_state.generated_lyrics = response.json()["response"]  # 생성된 가사 저장
                else:
                    st.error("🚨 서버 오류! FastAPI가 실행 중인지 확인하세요.")
        else:
            st.warning("⚠️ 문장을 입력해주세요.")

    # 생성된 가사 표시 (탭 전환 후에도 유지)
    if st.session_state.generated_lyrics:
        st.subheader("✨ 생성된 가사:")
        st.write(st.session_state.generated_lyrics)

# 2️⃣ 가사 평가 탭
with tab2:
    st.title("📊 가사 문장 자연스러움 평가")

    if not st.session_state.latest_saved_lyrics:
        response = requests.get(f"{API_URL}/get_latest_saved_lyrics")
        if response.status_code == 200:
            st.session_state.latest_saved_lyrics = response.json().get("latest_saved_lyrics", "")

    # 최근 저장된 가사 표시
    if st.session_state.latest_saved_lyrics:
        st.subheader("✨ 최근 저장된 가사:")
        st.write(st.session_state.latest_saved_lyrics)
    else:
        st.write("⚠️ 아직 저장된 가사가 없습니다.")

# 3️⃣ 감성 분류 탭
with tab3:
    st.title("🧠 생성 가사 감성 분석")

    if st.button("🔍 감성 분석 시작"):
        with st.spinner("감성 분석 중... 🤖"):
            response = requests.get(f"{API_URL}/kote/")

            if response.status_code == 200:
                st.session_state.analysis_results = response.json().get("results", [])  # 감성 분석 결과 저장

    # 감성 분석 결과 표시 (탭 전환 후에도 유지)
    if st.session_state.analysis_results:
        st.subheader("📊 감성 분석 결과")
        df = pd.DataFrame(st.session_state.analysis_results)
        st.dataframe(df)
    else:
        st.write("⚠️ 분석할 가사가 없습니다.")

# 4️⃣ 뮤직 비디오 탭 (추가 기능 확장 가능)
with tab4:
    st.title("🎬 뮤직 비디오 🎵")
    st.write("여기에 뮤직 비디오 기능을 추가하세요.")
