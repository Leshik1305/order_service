import fastapi

from src.presentation.api import orders

router = fastapi.APIRouter(prefix="/api")
router.include_router(orders.router)
