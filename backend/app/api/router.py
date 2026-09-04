from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.recovery import router as recovery_router
from app.api.routes.approvals import router as approvals_router
from app.api.routes.actions import router as actions_router
from app.api.routes.policies import router as policies_router
from app.api.routes.audit import router as audit_router
from app.api.routes.simulation import router as simulation_router
from app.api.routes.evaluation import router as evaluation_router
from app.api.routes.events import router as events_router
from app.api.routes.webhooks import router as webhooks_router
from app.api.routes.demo import router as demo_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router)
api_router.include_router(dashboard_router)
api_router.include_router(recovery_router)
api_router.include_router(approvals_router)
api_router.include_router(actions_router)
api_router.include_router(policies_router)
api_router.include_router(audit_router)
api_router.include_router(simulation_router)
api_router.include_router(evaluation_router)
api_router.include_router(events_router)
api_router.include_router(webhooks_router)
api_router.include_router(demo_router)
