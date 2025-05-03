from fastapi import APIRouter
import os
import glob
import pytorch_lightning as pl
import torch.nn as nn
from transformers import ElectraModel, AutoTokenizer
import torch
import pandas as pd
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline

# 1. 토크나이저 및 모델 불러오기 
tokenizer = AutoTokenizer.from_pretrained("searle-j/kote_for_easygoing_people")
model = AutoModelForSequenceClassification.from_pretrained("searle-j/kote_for_easygoing_people")

# 2. 감성 분석 분류 기준 설정 
pipe = TextClassificationPipeline(
        model=model,
        tokenizer=tokenizer,
        device=0, # gpu number, -1 if cpu used
        return_all_scores=True,
        function_to_apply='sigmoid'
    )

device = "cuda" if torch.cuda.is_available() else "cpu"

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

# 텍스트 감성분류 
@router.post("/kote/")
async def kote_lyrics ():
    """
    최근 저장된 가사 파일에서 마지막 줄을 읽어 반환
    """
    latest_file = get_latest_file(LYRICS_DIR)
    if not latest_file:
        return {"message": "No saved lyrics found"}
    
    # 가장 최근 파일 읽기
    with open(latest_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    pip_text = pipe(lines)  

    results = [] # 결과 저장을 위한 리스트

    for i, t in enumerate(lines):            # 잘라낸 텍스트와 그에 대한 감성 분석 결과를 반복합니다.
        for output in pip_text[i]:
            if output["score"] > 0.4:
                results.append({
                    "text": t,
                    "label": output["label"],
                    "score": output["score"]
                })

    # 결과를 데이터프레임으로 변환
    results_df = pd.DataFrame(results)
    results_df

    # for line in lines : 
    #     print("*"*80)
    #     print(line)
    #     preds = trained_model(line)[0]
    #     for l, p in zip(LABELS, preds):
    #         if p>0.4:
    #             print(f"{l}: {p}")
