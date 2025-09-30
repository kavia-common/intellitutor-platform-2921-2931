from fastapi import APIRouter
from typing import List

from src.models.schemas import RetrievalQuery, RetrievalDocument
from src.services.retrieval import retrieval_index

router = APIRouter()


@router.post(
    "/query",
    response_model=List[RetrievalDocument],
    summary="Query knowledge base",
    responses={200: {"description": "Top K documents returned"}},
)
def query_retrieval(payload: RetrievalQuery):
    """
    Query the knowledge base for relevant documents.

    Parameters:
        payload: RetrievalQuery with text query and optional top_k.

    Returns:
        List of RetrievalDocument with similarity scores and metadata.
    """
    docs = retrieval_index.query(payload.query, top_k=payload.top_k or 4)
    return docs
