import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib  
import base64
import streamlit as st
import plotly.graph_objects as go
import requests
import plotly.express as px


# FastAPI 서버 주소
API_URL = "http://127.0.0.1:8025/api"
IMAGE_PATH = "/home/wanted-1/potenup-workspace/Project/project2/team5/3.FastAPI/frontend/memo.png"  # 사용할 이미지 경로


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

# 1️. 가사 생성기 탭
with tab1:
    #     st.title("🎶 김둘이하나 : 가사 생성기 🎶")
    st.markdown("<h1 style='text-align:center;'>🎵 김둘이하나 : 가사 생성기 🎵</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # 입력 칸과 버튼을 한 줄에 배치
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input("", placeholder="당신의 가사를 완성할 첫 마디를 입력하세요:", label_visibility = "collapsed")

    st.markdown("<div style='margin-top: 15px;'>", unsafe_allow_html=True)
    # 버튼을 가운데 정렬
    # col_left, col_center, col_right = st.columns([1, 2, 1])
    # with col_center:
    with col2:
        generate_button = st.button("🎼 생성하기")
        if generate_button:
            if user_input:
                # with st.spinner("생성 중... 잠시만 기다려 주세요! 🚀"):
                    # st.markdown("<div class='spinner-container'></div>", unsafe_allow_html=True)
                    response = requests.post(f"{API_URL}/generate/", json={"text": user_input})

                    if response.status_code == 200:
                        generated_text = response.json()["response"]
                        st.session_state.generated_lyrics = generated_text  # 생성된 가사 저장

                        # 생성된 가사를 FastAPI에 저장 요청
                        requests.post(f"{API_URL}/save_lyrics/", json={"text": generated_text})
                    else:
                        st.error("🚨 서버 오류! FastAPI가 실행 중인지 확인하세요.")
            else:
                st.warning("⚠️ 문장을 입력해주세요.")
    st.markdown("</div>", unsafe_allow_html=True)

    # 생성된 가사 표시 (탭 전환 후에도 유지)
    if st.session_state.generated_lyrics:
        st.subheader("✨ 생성된 가사:")
        # st.write(st.session_state.generated_lyrics)

        # 생성 된 가사 줄바꿈 처리
        generated_lyrics = st.session_state.generated_lyrics.replace("\n", "<br>")
        generated_lyrics = generated_lyrics.replace(".", "<br>")
        generated_lyrics = generated_lyrics.replace(",", "<br>")

        st.markdown(
            f"""
            <style>
            .lyrics-container {{
                background-image: url("{background_image}");
                background-size: cover;
                background-position: center;
                padding: 20px;
                border-radius: 10px;
                color: #212b3a;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
                font-size: 20px;
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
        st.write(f"**BLEU Score:** {results['bleu']['bleu']}")
        st.write(f"**Perplexity:** {results['perplexity']}")

        rouge_scores = results['rouge']
        st.write("**ROUGE Scores:**")
        for metric, score in rouge_scores.items():
            st.write(f"- {metric.upper()}: {score}")

        # 📈 Plotly를 활용한 성능 평가 그래프
        st.subheader("📈 성능 평가 그래프")
        metrics = ["BLEU", "ROUGE-1", "ROUGE-2", "ROUGE-L", "Perplexity"]
        scores = [
            results['bleu'].get('bleu', 0),               # BLEU 점수
            rouge_scores.get("rouge1", 0),                # ROUGE-1
            rouge_scores.get("rouge2", 0),                # ROUGE-2
            rouge_scores.get("rougeL", 0),                # ROUGE-L
            results.get('perplexity', 0)                  # Perplexity
        ]

        # Plotly 그래프 생성
        fig = go.Figure()

        # 막대 그래프 추가
        fig.add_trace(go.Bar(
            x=metrics,
            y=scores,
            marker=dict(
                color=scores,
                colorscale='Viridis',  # 컬러 스케일 변경 (깔끔한 색상)
                showscale=True         # 색상 범례 표시
            ),
            text=[f"{s:.4f}" if isinstance(s, float) else s for s in scores],
            textposition='outside',    # 점수 표시 위치
        ))

        # 그래프 레이아웃 설정
        fig.update_layout(
            title="가사 성능 평가 지표",
            xaxis_title="평가지표 (Metrics)",
            yaxis_title="점수 (Score)",
            plot_bgcolor='rgba(0,0,0,0)',   # 배경 투명
            paper_bgcolor='rgba(0,0,0,0)',  # 외부 배경 투명
            font=dict(size=14),
            margin=dict(t=50, b=50, l=50, r=50),
        )

        # Perplexity 스케일 조정 (큰 값 대비)
        if max(scores) > 100:
            fig.update_yaxes(type='log')  # 로그 스케일 적용

        # Plotly 그래프 출력
        st.plotly_chart(fig, use_container_width=True)

# 3️.감성 분류 탭
with tab3:
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
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📊 감성 분석 결과 (문장별)")
        df = pd.DataFrame(st.session_state.analysis_results)
        st.dataframe(df)

        # 감정별 빈도수 계산
        emotion_counts = df['label'].value_counts()

        # 가장 많이 등장한 감정 표시
        most_common_emotion = emotion_counts.idxmax()
        st.markdown("<br>", unsafe_allow_html=True)
        # st.markdown(f"### ⭐ 가장 많이 나타난 감정: **{most_common_emotion}** ⭐")
        st.markdown(f"<h1 style='text-align:center;'>⭐ 가장 많이 나타난 감정 ⭐ <br/> **{most_common_emotion}** ", unsafe_allow_html=True)

        # 📈 감정 빈도수 막대 그래프 (Plotly Bar Chart)
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📈 감정 빈도수 그래프")
        bar_fig = go.Figure()

        bar_fig.add_trace(go.Bar(
            x=emotion_counts.index,
            y=emotion_counts.values,
            marker=dict(
                color=emotion_counts.values,
                colorscale='Blues',
                showscale=True
            ),
            text=emotion_counts.values,
            textposition='outside'
        ))

        bar_fig.update_layout(
            title="감정별 빈도수 분석",
            xaxis_title="감정 (Emotion)",
            yaxis_title="빈도수 (Frequency)",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=14),
            margin=dict(t=50, b=50, l=50, r=50)
        )

        st.plotly_chart(bar_fig, use_container_width=True)

        # 🥧 감정 비율 파이 차트 (Plotly Pie Chart)
        st.subheader("🥧 감정 비율 (Pie Chart)")
        pie_fig = go.Figure(data=[go.Pie(
            labels=emotion_counts.index,
            values=emotion_counts.values,
            hole=0.4,  # 도넛형 차트로 만들기 (옵션)
            marker=dict(colors=px.colors.qualitative.Set2),
            textinfo='percent+label'
        )])

        pie_fig.update_layout(
            title="감정 비율",
            showlegend=True
        )

        st.plotly_chart(pie_fig, use_container_width=True)
    else:
        st.write("")


# 4️.뮤직 비디오 탭
with tab4:
    st.title("🎬 뮤직 비디오 🎵")
    st.write("여기에 뮤직 비디오 기능을 추가하세요.")
