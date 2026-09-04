from fastapi import APIRouter, Query
from app.schemas.evaluation import EvaluationRunResponse
from app.services.evaluation_service import evaluation_service

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


@router.get("", response_model=EvaluationRunResponse)
@router.post("/run", response_model=EvaluationRunResponse)
async def run_evaluation_benchmark(
    dataset_size: int = Query(1000, ge=100, le=5000),
    random_seed: int = Query(101)
):
    """
    Executes a scientifically fair comparative evaluation of REVIVE 
    vs BASELINE (naive blind retry) over an identical cloned dataset.
    """
    return evaluation_service.run_benchmark(
        dataset_size=dataset_size,
        random_seed=random_seed
    )
