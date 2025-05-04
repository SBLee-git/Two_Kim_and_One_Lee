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

# 7. 모델 로드 및 GPU로 이동
model = GPT2LMHeadModel.from_pretrained(model_name)
model.resize_token_embeddings(len(tokenizer))
model.to("cuda")
model.train()

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

    # 2. 테스트 데이터에서 일부 샘플 가져오기
    num_samples = 10
    test_samples = val_texts.sample(num_samples).tolist()

    # BLEU 및 ROUGE 평가
    references = []
    predictions = []

    for sample in test_samples:
        input_ids = tokenizer(sample, return_tensors="pt", truncation=True, max_length=512).input_ids.to("cuda")
        
        with torch.no_grad():
            output = model.generate(input_ids=input_ids, max_new_tokens=100, do_sample=True)
        
        generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
        
        references.append([sample])  # BLEU 평가는 다중 참조 가능하므로 리스트로 감싸기
        predictions.append(generated_text)

    # 4. BLEU 점수 계산
    bleu_score = bleu.compute(predictions=predictions, references=references)
    print(f"BLEU Score: {bleu_score['bleu']:.4f}")

    # 5. ROUGE 점수 계산
    rouge_score = rouge.compute(predictions=predictions, references=references)
    print(f"ROUGE Score: {rouge_score}")

    # 6. Perplexity(혼란도) 계산
    def compute_perplexity(model, text):
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        inputs = {key: value.to("cuda") for key, value in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs, labels=inputs["input_ids"])  # 🔥 labels 추가
        
        if outputs.loss is None:
            print("Warning: Model did not return a loss value.")
            return np.nan  # 오류 방지를 위해 NaN 반환
        
        loss = outputs.loss.item()
        return np.exp(loss)

    perplexities = [compute_perplexity(model, text) for text in test_samples]
    avg_perplexity = np.nanmean(perplexities)  # NaN 값 제외하고 평균 계산
    print(f"Perplexity: {avg_perplexity:.4f}")


    # BLEU 점수 반올림 처리
    rounded_bleu = {k: round(v, 4) if isinstance(v, (int, float)) else v for k, v in bleu_score.items()}

    # ROUGE 점수 반올림 처리
    rounded_rouge = {k: round(v, 4) if isinstance(v, (int, float)) else v for k, v in rouge_score.items()}

    # 결과 반환
    return {
        "bleu": rounded_bleu,
        "rouge": rounded_rouge,
        "perplexity": round(avg_perplexity, 4)
    }


    