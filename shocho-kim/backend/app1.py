from fastapi import APIRouter
from pydantic import BaseModel
import torch
from transformers import GPT2LMHeadModel, AutoTokenizer
import datetime

router = APIRouter()

# 현재 시간 가져오기
now = datetime.datetime.now()
timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
SAVE_PATH = f"../../1.데이터모음/generated_lyrics/generated_lyrics_{timestamp}.txt"

# GPU 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 모델 및 토크나이저 로드
model = GPT2LMHeadModel.from_pretrained("../../2.프로세스/fine_tuned_new_model").to(device)
tokenizer = AutoTokenizer.from_pretrained("../../2.프로세스/fine_tuned_new_model")
model.eval()  # 평가 모드 전환

# 요청 데이터 모델
class InputText(BaseModel):
    text: str

# 텍스트 생성 API
@router.post("/generate/")
async def generate_text(data: InputText):
    prompt = data.text
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)

    output = model.generate(
        input_ids=input_ids,
        max_length=200,
        temperature=1.0,
        top_k=200,
        top_p=0.9,
        repetition_penalty=1.2,
        do_sample=True
    )

    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)

    # 생성된 텍스트 저장
    with open(SAVE_PATH, "a", encoding="utf-8") as f:
        f.write(generated_text + "\n")

    return {"response": generated_text}

# 가사 저장 API
class SaveLyricsRequest(BaseModel):
    text: str

@router.post("/save_lyrics/")
async def save_lyrics(request: SaveLyricsRequest):
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    save_path = f"{SAVE_PATH}/generated_lyrics_{now}.txt"

    with open(save_path, "w", encoding="utf-8") as f:
        f.write(request.text)

    return {"message": "가사가 저장되었습니다."}