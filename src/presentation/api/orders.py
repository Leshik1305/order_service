from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from src.application.dtos.payment import PaymentCallbackDTO
from src.application.use_cases.payment_callback import PaymentCallback
from src.application.use_cases.create_order import CreateOrder
from src.container import Container
from src.application.dtos.order import OrderCreateDTO, OrderReadDTO

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=OrderReadDTO)
@inject
async def create_order(
    order: OrderCreateDTO,
    uc: CreateOrder = Depends(Provide[Container.application.create_order]),
):
    result = await uc.execute(order)
    print(result)
    return result


@router.post("/payment-callback", status_code=status.HTTP_200_OK)
@inject
async def payment_callback(
    data: PaymentCallbackDTO,
    use_case: PaymentCallback = Depends(
        Provide[Container.application.payment_callback]
    ),
):
    await use_case.execute(data)
    return {"status": "ok"}
