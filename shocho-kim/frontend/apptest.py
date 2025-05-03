import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib  
import base64

# FastAPI 서버 주소
API_URL = "http://127.0.0.1:8000/api"
IMAGE_PATH = "/home/wanted-1/potenup-workspace/Project/project2/team5/3.FastAPI/frontend/note.png"  # 사용할 이미지 경로

# 세션 상태 초기화
if "generated_lyrics" not in st.session_state:
    st.session_state.generated_lyrics = ""  # 생성된 가사 저장
if "latest_saved_lyrics" not in st.session_state:
    st.session_state.latest_saved_lyrics = ""  # 최근 저장된 가사
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = []  # 감성 분석 결과
if "evaluation_results" not in st.session_state:
    st.session_state.evaluation_results = {}

# 페이지 설정
st.set_page_config(page_title="김둘이하나 : 가사 생성기", page_icon="🎵", layout="centered")

st.markdown("""
    <style>
    body { background: #121212; color: #FFF; font-family: Arial; }
    input, button { border-radius: 10px; padding: 10px; }
    input { background: #2C2C2C; color: white; border: 1px solid #FF6B6B; height: 42px; }
    button { background: #FF6B6B; color: white; border: none; font-weight: bold; height: 42px; }
    button:hover { background: #FF4C4C; color: white;} 
    .stButton { text-align: center; }
    </style>
""", unsafe_allow_html=True)

# Base64로 이미지 인코딩하는 함수
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        base64_str = base64.b64encode(img_file.read()).decode()
    return f"data:image/png;base64,{base64_str}"

# 배경 이미지 가져오기
background_image = get_base64_image(IMAGE_PATH)

# 탭 구조 (가사 생성기, 가사 평가, 감성 분류, 뮤직 비디오) #d63333
tab1, tab2, tab3, tab4 = st.tabs(["🎤 가사 생성기", "📊 가사 평가", "🧠 감성 분류", "☑️ 뮤직비디오"])

# 1. 가사 생성기 탭
with tab1:
    st.title("🎶 김둘이하나 : 가사 생성기 🎶")

    # 입력 칸과 버튼을 한 줄에 배치
    col1, col2 = st.columns([4, 1])

    with col1:
        user_input = st.text_input("", placeholder="당신의 가사를 완성할 첫 마디를 입력하세요:", label_visibility="collapsed")  # 라벨 숨김

    with col2:
        generate_button = st.button("🎼 생성하기")

    if generate_button:
        if user_input:
            with st.spinner("생성 중... 잠시만 기다려 주세요! 🚀"):
                response = requests.post(f"{API_URL}/generate/", json={"text": user_input})

                if response.status_code == 200:
                    generated_text = response.json()["response"]
                    st.session_state.generated_lyrics = generated_text  #  생성된 가사 저장
                    requests.post(f"{API_URL}/save_lyrics/", json={"text": generated_text})
                else:
                    st.error("🚨 서버 오류! FastAPI가 실행 중인지 확인하세요.")
        else:
            st.warning("⚠️ 문장을 입력해주세요.")

    # 생성된 가사 표시 (탭 전환 후에도 유지)
    if "generated_lyrics" in st.session_state:
        st.subheader("✨ 생성된 가사:")

        # 생성 된 가사 줄바꿈 처리
        generated_lyrics = st.session_state.generated_lyrics.replace("\n", "<br>")

        st.markdown(
            f"""
            <style>
            .lyrics-container {{
                background-image: url("{background_image}");
                background-size: cover;
                background-position: center;
                padding: 20px;
                border-radius: 10px;
                color: white;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
                font-size: 20px;
                font-weight: bold;
                text-align: center;
                margin-top: 10px;
            }}
            </style>
            <div class="lyrics-container">
                {generated_lyrics}
            </div>
            """,
            unsafe_allow_html=True
        )

# 2️.가사 평가 탭
with tab2:
    # st.title("📊 가사 문장 자연스러움 평가")

    # # 생성된 가사가 있으면 그것을 사용, 없으면 FastAPI에서 가져오기
    # lyrics_to_evaluate = st.session_state.generated_lyrics
    # if not lyrics_to_evaluate:
    #     response = requests.get(f"{API_URL}/get_latest_saved_lyrics")
    #     if response.status_code == 200:
    #         lyrics_to_evaluate = response.json().get("latest_saved_lyrics", "")

    # # 가사 평가 표시
    # if lyrics_to_evaluate:
    #     st.subheader("✨ 평가할 가사:")
    #     st.write(lyrics_to_evaluate)
    # else:
    #     st.write("⚠️ 평가할 가사가 없습니다.")

    # st.title("📈 생성된 가사 성능 평가 (BLEU, ROUGE, Perplexity)")
    st.markdown("<h1 style='text-align:center;'>📈 생성된 가사 성능 평가 </h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>(BLEU, ROUGE, Perplexity) </h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 성능 평가 시작"):
        with st.spinner("성능 평가 중... ⏳"):
            lyrics_to_evaluate = st.session_state.generated_lyrics
            if lyrics_to_evaluate:
                response = requests.post(f"{API_URL}/evaluation/", json={"text": lyrics_to_evaluate})

                if response.status_code == 200:
                    st.session_state.evaluation_results = response.json()
                else:
                    st.error("🚨 성능 평가 요청 실패!")

    # 평가 결과 
    if st.session_state.evaluation_results:
        results = st.session_state.evaluation_results

        st.subheader("📊 평가 지표")
        st.write(f"**BLEU Score:** {results['bleu']}")
        st.write(f"**Perplexity:** {results['perplexity']}")

        rouge_scores = results['rouge']
        st.write("**ROUGE Scores:**")
        for metric, score in rouge_scores.items():
            st.write(f"- {metric}: {score}")

        # 그래프 시각화 (bar chart)
        st.subheader("📈 성능 평가 그래프")
        metrics = ["BLEU", "ROUGE-1", "ROUGE-2", "ROUGE-L", "Perplexity"]
        scores = [
            results['bleu'],
            rouge_scores.get("rouge1", 0),
            rouge_scores.get("rouge2", 0),
            rouge_scores.get("rougeL", 0),
            results['perplexity']
        ]

        plt.figure(figsize=(8, 5))
        sns.barplot(x=metrics, y=scores, palette="Set2")
        plt.xlabel("평가지표 (Metrics)")
        plt.ylabel("점수 (Score)")
        plt.title("가사 성능 평가 지표")
        st.pyplot(plt.gcf())

# 3️.감성 분류 탭
with tab3:
    # st.title("🧠 생성 가사 감성 분석")
    st.markdown("<h1 style='text-align:center;'>🧠 생성 가사 감성 분석</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔍 감성 분석 시작"):
        with st.spinner("감성 분석 중... 🤖"):
            lyrics_to_analyze = st.session_state.generated_lyrics
            if not lyrics_to_analyze:
                response = requests.get(f"{API_URL}/get_latest_saved_lyrics")
                if response.status_code == 200:
                    lyrics_to_analyze = response.json().get("latest_saved_lyrics", "")

            if lyrics_to_analyze:
                response = requests.post(f"{API_URL}/kote/", json={"text": lyrics_to_analyze})

                if response.status_code == 200:
                    st.session_state.analysis_results = response.json().get("results", [])
                else:
                    st.error("🚨 감성 분석 요청 실패!")

    # 감성 분석 결과 표시
    if st.session_state.analysis_results:
        st.subheader("📊 감성 분석 결과 (문장별)")
        df = pd.DataFrame(st.session_state.analysis_results)
        st.dataframe(df)

        # 감정별 빈도수 계산
        emotion_counts = df['label'].value_counts()

        # 가장 많이 등장한 감정 표시
        most_common_emotion = emotion_counts.idxmax()
        st.markdown(f"### ⭐ 가장 많이 나타난 감정: **{most_common_emotion}** ⭐")

        # 감정 빈도수 막대 그래프 (Bar Chart)
        st.subheader("📈 감정 빈도수 그래프")
        plt.figure(figsize=(8, 5))
        sns.barplot(x=emotion_counts.index, y=emotion_counts.values, palette="Set2")
        plt.xlabel("감정 (Emotion)")
        plt.ylabel("빈도수 (Frequency)")
        plt.title("감정별 빈도수 분석")
        st.pyplot(plt.gcf())  # 그래프 출력

        # 감정 비율 파이 차트 (Pie Chart)
        st.subheader("🥧 감정 비율 (Pie Chart)")
        plt.figure(figsize=(6, 6))
        plt.pie(emotion_counts, labels=emotion_counts.index, autopct='%1.1f%%', colors=sns.color_palette("Set2"))
        plt.title("감정 비율")
        st.pyplot(plt.gcf())
    else:
        # st.write(" 분석 고고고 버튼 눌러눌러눌러 👇👇👇")
        st.write("")

# 4️.뮤직 비디오 탭
with tab4:
    st.title("🎬 뮤직 비디오 🎵")
    st.write("여기에 뮤직 비디오 기능을 추가하세요.")
