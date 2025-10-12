from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Vector Pipeline API")

app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {"status": "ok"}