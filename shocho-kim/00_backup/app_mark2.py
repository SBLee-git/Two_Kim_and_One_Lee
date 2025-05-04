import streamlit as st
import requests
import pandas as pd

# FastAPI 서버 주소
API_URL = "http://127.0.0.1:8000/api"  # FastAPI의 엔드포인트가 /api로 시작하는지 확인

# **탭 구조 사용 (가사 생성 & 문장 자연스러움 평가)**
tab1, tab2, tab3, tab4 = st.tabs(["🎤 가사 생성기", "📊 가사 라벨링", "☑️ 가사 평가", "🧠 감성 분류"])

# **1️. 가사 생성기 탭**
with tab1:
    st.title("🎶 김둘이하나 : 가사 생성기 🎶")

    # 사용자 입력 받기
    user_input = st.text_input("당신의 가사를 완성할 첫 마디를 입력하세요:")

    if st.button("🎼 생성하기"):
        if user_input:
            with st.spinner("생성 중... 잠시만 기다려 주세요! "):
                # FastAPI 서버에 POST 요청 보내기
                response = requests.post(f"{API_URL}/generate/", json={"text": user_input})

                # 결과 출력
                if response.status_code == 200:
                    st.subheader("✨ 생성된 가사:")
                    st.write(response.json()["response"])
                else:
                    st.error("서버 오류! FastAPI가 실행 중인지 확인하세요.")
        else:
            st.warning("문장을 입력해주세요.")

# **2️. 문장 자연스러움 평가 탭**
with tab2:
    st.title("📊 가사 문장 자연스러움 평가")

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

        # 자연스러움 점수 선택 (0~5)
        score = st.radio("자연스러움 점수 (0=매우 어색, 5=자연스러움)", [0, 1, 2, 3, 4, 5], index=2)

        # 점수 제출 버튼
        if st.button("💾 점수 제출"):
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
                st.error("🚨 라벨링 저장 실패")

    # 현재까지 라벨링된 데이터 확인
    st.header("📊 라벨링된 데이터")
    response = requests.get(f"{API_URL}/get_labeled_data")
    if response.status_code == 200:
        labeled_data = response.json()["labeled_data"]
        if labeled_data:
            df = pd.DataFrame(labeled_data)
            st.dataframe(df)
        else:
            st.write("⚠️ 아직 라벨링된 데이터가 없습니다.")

# **3️. 최근 저장된 가사 탭**
with tab3:
    st.title("📖 최근 저장된 가사")

    # FastAPI 서버에서 최신 저장된 가사 가져오기
    response = requests.get(f"{API_URL}/get_latest_saved_lyrics")

    if response.status_code == 200:
        latest_saved_lyrics = response.json().get("latest_saved_lyrics", "")
        if latest_saved_lyrics:
            # st.subheader("✨ 가장 최근에 저장된 가사:")
            st.write(latest_saved_lyrics)
        else:
            st.write("⚠️ 아직 저장된 가사가 없습니다.")
    else:
        st.error("🚨 FastAPI 서버에서 데이터를 가져오는 데 실패했습니다.")

# **4. 감성분류** 
with tab4:
    st.title("🧠 최근 생성된 가사 감성 분석")

    if st.button("🔍 감성 분석 시작"):
        with st.spinner("감성 분석 중... 🤖"):
            response = requests.get(f"{API_URL}/kote/")

            if response.status_code == 200:
                results = response.json().get("results", [])

                if results:
                    st.subheader("📊 감성 분석 결과")
                    df = pd.DataFrame(results)
                    st.dataframe(df)
                else:
                    st.write("⚠️ 분석할 가사가 없습니다.")
            else:
                st.error("🚨 감성 분석 요청 실패!")