from fastapi import FastAPI
from pydantic import BaseModel
import torch
from transformers import GPT2LMHeadModel, AutoTokenizer
import os
import datetime
import random
import pandas as pd

# 현재 시간 가져오기
now = datetime.datetime.now()
# 시간 형식 지정 (예: '2025-01-15_14-30-00')
timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
SAVE_PATH = f"../1.데이터모음/generated_lyrics/generated_lyrics_{timestamp}.txt"  # 저장할 파일 경로

app = FastAPI()

# 1. GPU 사용 여부 확인
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# 2. 저장된 GPT-2 모델 및 토크나이저 로드
# /home/wanted-1/potenup-workspace/Project/project2/team5/2.프로세스/fine_tuned_model
model = GPT2LMHeadModel.from_pretrained("../2.프로세스/fine_tuned_model").to(device)
tokenizer = AutoTokenizer.from_pretrained("../2.프로세스/fine_tuned_model")
model.to("cuda")
model.eval()  # 평가 모드 전환

# 3. 입력 데이터 모델 정의
class InputText(BaseModel):
    text: str

# 4. 텍스트 생성 엔드포인트
@app.post("/generate/")
async def generate_text(data: InputText):
    prompt = data.text
    print(f"prompt >>>> : {prompt}")

    # 입력된 텍스트를 토큰화 및 GPU로 이동
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)

    # 모델을 사용하여 텍스트 생성
    output = model.generate(
        input_ids=input_ids,
        max_length=200,
        temperature=1.0,
        top_k=200,
        top_p=0.9,
        repetition_penalty=1.2,
        do_sample=True
    )

    # 생성된 텍스트 디코딩
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    # generated_text = generated_text[:-1] 

    # 🎵 생성된 가사를 파일에 저장
    with open(SAVE_PATH, "a", encoding="utf-8") as f:
        f.write(generated_text + "\n")

    return {"response": generated_text}

app2 = FastAPI()

### 기존 가사 데이터 로드 (공백 문장 제거)
df = pd.read_csv("../1.데이터모음/'music_data(Merge)'.csv")  # 가사 데이터 가져오기
df = df[['lyrics']].dropna()
df['sentences'] = df['lyrics'].apply(lambda x: [s.strip() for s in x.split("\n") if s.strip()])  # 공백 문장 제거
lyrics_sentences = [sent for sublist in df['sentences'] for sent in sublist]

### 비문 생성 함수
def shuffle_words(sentence):
    words = sentence.split()
    random.shuffle(words)
    return " ".join(words)

def remove_random_word(sentence):
    words = sentence.split()
    if len(words) > 1:
        words.pop(random.randint(0, len(words)-1))
    return " ".join(words)

### 랜덤 비문 데이터 생성 (공백 문장 방지)
num_samples = 50  # 한 번에 생성할 비문 개수
bad_sentences = []

for _ in range(num_samples):
    original = random.choice(lyrics_sentences)
    method = random.choice([shuffle_words, remove_random_word])
    generated = method(original).strip()

    # 완전히 공백인 문장은 저장하지 않음
    if generated:
        bad_sentences.append({"original": original, "generated": generated})

### API 엔드포인트
@app.get("/get_sentences")
def get_sentences():
    """비문 데이터를 반환 (공백 문장 제외)"""
    return {"sentences": bad_sentences}

class LabelInput(BaseModel):
    original: str
    generated: str
    score: int  # 정수 입력

labeled_data = []

@app.post("/submit_label")
def submit_label(label: LabelInput):
    """사용자가 입력한 정수 점수 저장"""
    labeled_data.append({"original": label.original, "generated": label.generated, "score": label.score})
    return {"message": "라벨링 완료!"}

@app.get("/get_labeled_data")
def get_labeled_data():
    """현재까지 라벨링된 데이터 확인"""
    return {"labeled_data": labeled_data}
