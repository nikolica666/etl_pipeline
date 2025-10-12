from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=512)
    top_k: int = Field(3, ge=1, le=30)