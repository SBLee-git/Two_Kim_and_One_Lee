from fastapi import APIRouter
from pydantic import BaseModel
import pandas as pd
import random

router = APIRouter()

# 기존 가사 데이터 로드
df = pd.read_csv("../../1.데이터모음/'music_data(Merge)'.csv").dropna()
df['sentences'] = df['lyrics'].apply(lambda x: [s.strip() for s in x.split("\n") if s.strip()])
lyrics_sentences = [sent for sublist in df['sentences'] for sent in sublist]

# 비문 변형 함수
def shuffle_words(sentence):
    words = sentence.split()
    random.shuffle(words)
    return " ".join(words)

def remove_random_word(sentence):
    words = sentence.split()
    if len(words) > 1:
        words.pop(random.randint(0, len(words)-1))
    return " ".join(words)

# 랜덤 비문 생성
num_samples = 50
bad_sentences = []

for _ in range(num_samples):
    original = random.choice(lyrics_sentences)
    method = random.choice([shuffle_words, remove_random_word])
    generated = method(original).strip()
    if generated:
        bad_sentences.append({"original": original, "generated": generated})

# 비문 데이터 반환 API
@router.get("/get_sentences")
def get_sentences():
    return {"sentences": bad_sentences}

# 요청 데이터 모델
class LabelInput(BaseModel):
    original: str
    generated: str
    score: int

labeled_data = []

# 라벨 저장 API
@router.post("/submit_label")
def submit_label(label: LabelInput):
    labeled_data.append({"original": label.original, "generated": label.generated, "score": label.score})
    return {"message": "라벨링 완료!"}

# 라벨링된 데이터 확인 API
@router.get("/get_labeled_data")
def get_labeled_data():
    return {"labeled_data": labeled_data}
