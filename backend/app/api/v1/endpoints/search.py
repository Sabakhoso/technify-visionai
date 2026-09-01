from fastapi import APIRouter, Query


router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


@router.get("/")
async def search(
    q: str = Query(..., min_length=1),
):
    """
    Basic search endpoint.

    AI-powered semantic search can be connected later
    through the existing AI search service.
    """

    return {
        "query": q,
        "results": [],
        "message": "Search endpoint is ready.",
    }