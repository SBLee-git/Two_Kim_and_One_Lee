from fastapi import APIRouter
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline
import torch
import pandas as pd

router = APIRouter()

# 모델 불러오기
tokenizer = AutoTokenizer.from_pretrained("searle-j/kote_for_easygoing_people")
model = AutoModelForSequenceClassification.from_pretrained("searle-j/kote_for_easygoing_people")

# 감성 분석 파이프라인
pipe = TextClassificationPipeline(
    model=model,
    tokenizer=tokenizer,
    device=0 if torch.cuda.is_available() else -1,
    return_all_scores=True,
    function_to_apply='sigmoid'
)

# 요청 데이터 모델
class LyricsRequest(BaseModel):
    text: str  # 전체 가사 전달

# 감성 분석 API (문장별)
@router.post("/kote/")
async def kote_lyrics(request: LyricsRequest):
    text = request.text

    # 문장 단위로 분리 (줄바꿈)
    sentences = [sentence.strip() for sentence in text.split("\n") if sentence.strip()]

    results = []
    for sentence in sentences:
        # 문장별 감성 분석 수행
        analysis = pipe(sentence)[0]

        # 감정 점수 중 가장 높은 감정 선택
        top_emotion = max(analysis, key=lambda x: x["score"])

        results.append({
            "text": sentence,
            "label": top_emotion["label"],
            "score": round(top_emotion["score"], 4)
        })

    return {"results": results}
