# 1. 모듈 불러오기
from fastapi import APIRouter
from pydantic import BaseModel
from transformers import BertTokenizer, BertForSequenceClassification, GPT2LMHeadModel, AutoTokenizer
from sklearn.model_selection import train_test_split
import torch
from torch.utils.data import Dataset, DataLoader
from evaluate import load
import numpy as np
import pandas as pd

# 2. 모델 설정하기
model_name = "skt/kogpt2-base-v2"

# 3. 토크나이저 설정하기
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token # 패딩 토큰 설정

# 4. 데이터셋 클래스 정의
class LyricsDataset(Dataset):
    def __init__(self, texts, tokenizer, max_length=128):
        self.texts = texts.reset_index(drop=True)
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts.iloc[idx])
        inputs = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt",
        )
        inputs["labels"] = inputs["input_ids"].clone()
        return {key: val.squeeze(0).to("cuda") for key, val in inputs.items()}
    
# 5. 기존 가사 데이터 로드
df = pd.read_csv("../../1.데이터모음/'music_data(Merge)'.csv").dropna()
df['sentences'] = df['lyrics'].apply(lambda x: [s.strip() for s in x.split("\n") if s.strip()])
lyrics_sentences = [sent for sublist in df['sentences'] for sent in sublist]

lyrics_texts = df["lyrics"]

# 6. 학습, 검증 데이터 분리
train_texts, val_texts = train_test_split(lyrics_texts, test_size=0.2, random_state=42)
train_dataset = LyricsDataset(train_texts, tokenizer)
val_dataset = LyricsDataset(val_texts, tokenizer)

train_dataloader = DataLoader(train_dataset, batch_size=16, shuffle=True)
val_dataloader = DataLoader(val_dataset, batch_size=16, shuffle=True)

# 저장된 모델 및 토크나이저 로드
model = GPT2LMHeadModel.from_pretrained("skt/kogpt2-base-v2")
tokenizer = AutoTokenizer.from_pretrained("skt/kogpt2-base-v2")
model.eval()

router = APIRouter()

# 요청 데이터 모델
class LyricsRequest(BaseModel):
    text: str  # 전체 가사 전달

# 가사 평가 API (BLEU, ROUGE, Perplexity)
@router.post("/evaluation/")
async def evaluate_lyrics(request: LyricsRequest):
    text = request.text

    # 문장 단위로 분리
    sentences = [sentence.strip() for sentence in text.split("\n") if sentence.strip()]

    # 평가 지표 불러오기
    bleu = load("bleu")
    rouge = load("rouge")

    # BLEU 및 ROUGE 평가
    references = [[sentence] for sentence in sentences]  # 참조 데이터 (원본)
    predictions = lyrics_sentences  

    bleu_score = bleu.compute(predictions=predictions, references=references)["bleu"]
    rouge_score = rouge.compute(predictions=predictions, references=references)

    # Perplexity 계산
    def calculate_perplexity(text):
        inputs = tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs, labels=inputs["input_ids"])
            loss = outputs.loss
        return torch.exp(loss).item()

    perplexities = [calculate_perplexity(sentence) for sentence in sentences]
    avg_perplexity = np.mean(perplexities)

    return {
        "bleu": round(bleu_score, 4),
        "rouge": {k: round(v, 4) for k, v in rouge_score.items()},
        "perplexity": round(avg_perplexity, 4)
    }

    