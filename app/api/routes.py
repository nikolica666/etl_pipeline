from fastapi import APIRouter
from app.models.query_models import QueryRequest
from app.services.qdrant_service import search_vectors

router = APIRouter()

@router.post("/search")
async def search(request: QueryRequest):
    results = await search_vectors(request.query, request.top_k)
    return {"matches": results}