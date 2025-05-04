# from fastapi import APIRouter
# import requests

# router = APIRouter()

# # FastAPI 서버 주소 확인
# FASTAPI_URL = "http://127.0.0.1:8000/api"

# @router.get("/use_generated_lyrics", include_in_schema=False)
# async def use_generated_lyrics():
#     """
#     app1.py에서 생성된 최신 가사를 가져와 반환
#     """
#     # `app1.py`의 `/get_latest_lyrics/` 엔드포인트 호출
#     response = requests.get(f"{FASTAPI_URL}/get_latest_lyrics", allow_redirects=False)  # Redirect 방지
    
#     if response.status_code == 200:
#         latest_lyrics = response.json().get("latest_lyrics", "")
#         return {"message": "Success", "latest_lyrics": latest_lyrics}
#     else:
#         return {"message": "Failed to retrieve lyrics"}
from fastapi import APIRouter
import os
import glob
from transformers import BertTokenizer, BertForSequenceClassification
import torch


router = APIRouter()

# 저장된 가사 파일이 위치한 디렉토리 (경로 수정 필요)
LYRICS_DIR = "../../1.데이터모음/generated_lyrics/"

def get_latest_file(directory, prefix="generated_lyrics_"):
    """
    주어진 디렉토리에서 가장 최근에 생성된 파일 찾기
    """
    files = glob.glob(os.path.join(directory, f"{prefix}*.txt"))  # 파일 리스트 가져오기
    if not files:
        return None  # 파일이 없으면 None 반환
    
    latest_file = max(files, key=os.path.getctime)  # 가장 최근에 생성된 파일 찾기
    return latest_file

@router.get("/get_latest_saved_lyrics/")
async def get_latest_saved_lyrics():
    """
    최근 저장된 가사 파일에서 마지막 줄을 읽어 반환
    """
    latest_file = get_latest_file(LYRICS_DIR)
    if not latest_file:
        return {"message": "No saved lyrics found"}
    
    # 가장 최근 파일에서 마지막 줄 읽기
    with open(latest_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        last_line = lines[-1].strip() if lines else "No lyrics available"

        
        # KoBERT 모델 로드
        model_name = "monologg/kobert"
        tokenizer = BertTokenizer.from_pretrained(model_name)
        model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2)  # 0: 부적합, 1: 적합

        def evaluate_sentence(sentence):
            inputs = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True)
            with torch.no_grad():
                logits = model(**inputs).logits
            score = torch.softmax(logits, dim=1).tolist()[0]
            return {"부적합 확률": score[0], "적합 확률": score[1]}

            # 문장 결과 
            print(evaluate_sentence(lines))


    return {"latest_saved_lyrics": evaluate_sentence(lines)}
