from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import get_db
from app.models.merchant import Merchant
from app.schemas.simulation import SimulationRunRequest, SimulationRunResponse
from app.services.simulation_service import simulation_service

router = APIRouter(prefix="/simulation", tags=["Simulation"])


@router.post("/run", response_model=SimulationRunResponse)
async def run_simulation(
    req: SimulationRunRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Executes a deterministic simulation generating 1,000+ realistic transaction
    and recovery records across 16 scenarios, persisting full state progression.
    """
    try:
        stmt = select(Merchant)
        merchant = (await db.execute(stmt)).scalars().first()
        merchant_id = merchant.id if merchant else "merchant_default"

        res = await simulation_service.run_simulation(
            db=db,
            merchant_id=merchant_id,
            transaction_count=req.transaction_count,
            random_seed=req.random_seed,
            scenario_preset=req.scenario_preset
        )
        return SimulationRunResponse.model_validate(res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {e}")
