from fastapi import APIRouter
import os
import glob
import torch
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline
from pydantic import BaseModel

router = APIRouter()

# 1. 토크나이저 및 모델 불러오기
tokenizer = AutoTokenizer.from_pretrained("searle-j/kote_for_easygoing_people")
model = AutoModelForSequenceClassification.from_pretrained("searle-j/kote_for_easygoing_people")

# 2. 감성 분석 파이프라인 설정
pipe = TextClassificationPipeline(
    model=model,
    tokenizer=tokenizer,
    device=0 if torch.cuda.is_available() else -1,  # GPU 사용 여부 자동 설정
    return_all_scores=True,
    function_to_apply='sigmoid'
)

# 저장된 가사 파일이 위치한 디렉토리
LYRICS_DIR = "../../1.데이터모음/generated_lyrics/"

def get_latest_file(directory, prefix="generated_lyrics_"):
    """
    주어진 디렉토리에서 가장 최근에 생성된 파일 찾기
    """
    files = glob.glob(os.path.join(directory, f"{prefix}*.txt"))
    if not files:
        return None
    latest_file = max(files, key=os.path.getctime)
    return latest_file

# 요청 데이터 모델
class LyricsRequest(BaseModel):
    text: str

# 텍스트 감성 분류 API
@router.post("/kote/")
async def kote_lyrics(request: LyricsRequest):
    # """
    # 최근 저장된 가사 파일에서 마지막 줄을 읽어 감성 분석 결과 반환
    # """
    # latest_file = get_latest_file(LYRICS_DIR)
    # if not latest_file:
    #     return {"message": "No saved lyrics found"}

    # # 가장 최근 파일 읽기
    # with open(latest_file, "r", encoding="utf-8") as f:
    #     lines = f.readlines()

    # # 감성 분석 수행
    # pip_text = pipe(lines)

    text = request.text

    # 감성 분석 수행
    results = pipe([text])[0]

    # 감정 점수 중 가장 높은 것 선택
    top_emotion = max(results, key=lambda x: x["score"])

    # results = []  # 결과 저장 리스트
    # for i, t in enumerate(lines):
    #     for output in pip_text[i]:
    #         if output["score"] > 0.4:
    #             results.append({
    #                 "text": t.strip(),
    #                 "label": output["label"],
    #                 "score": round(output["score"], 4)  # 소수점 4자리로 표시
    #             })

    # for i, t in enumerate(lines):
    #     # 각 문장에서 가장 높은 점수의 감정 결과만 선택
    #     top_emotion = max(pip_text[i], key=lambda x: x["score"])
    #     results.append({
    #         "text": t.strip(),
    #         "label": top_emotion["label"],
    #         "score": round(top_emotion["score"], 4)  # 소수점 4자리로 표시
    #     })

    # 결과를 반환
    # return {"results": results}

    return {
        "results": [{
            "text": text,
            "label": top_emotion["label"],
            "score": round(top_emotion["score"], 4)
        }]
    }