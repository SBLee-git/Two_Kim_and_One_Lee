from fastapi import FastAPI
import uvicorn
from app1 import router as app1_router
from app2 import router as app2_router
from app3 import router as app3_router
from app4 import router as app4_router 
from app5 import router as app5_router

# FastAPI 인스턴스 생성
app = FastAPI()

# 기본 홈페이지 응답 추가 (404 방지)
@app.get("/")
async def root():
    return {"message": "김둘 이하나의 FastAPI Server 는 건재합니다 🌈"}

# 각 기능 모듈 라우터 등록
app.include_router(app1_router, prefix="/api")
app.include_router(app2_router, prefix="/api")
app.include_router(app3_router, prefix="/api")
app.include_router(app4_router, prefix="/api") 
app.include_router(app5_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)