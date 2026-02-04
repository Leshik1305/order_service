from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from src.application.dtos.order import OrderCreateDTO, OrderReadDTO
from src.application.dtos.payment import PaymentCallbackDTO
from src.application.exceptions import IsAvailableQtyError, ItemNotFoundError
from src.application.use_cases.create_order import CreateOrder
from src.application.use_cases.get_order_by_id import GetOrderByIdUseCase
from src.application.use_cases.payment_callback import PaymentCallback
from src.container import Container

router = APIRouter()


@router.post(
    "/orders", status_code=status.HTTP_201_CREATED, response_model=OrderReadDTO
)
@inject
async def create_order(
    order: OrderCreateDTO,
    uc: CreateOrder = Depends(Provide[Container.application.create_order]),
):
    try:
        return await uc.execute(order)
    except (IsAvailableQtyError, ItemNotFoundError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/orders/{order_id}", status_code=status.HTTP_200_OK, response_model=OrderReadDTO
)
@inject
async def get_order_by_id(
    order_id: UUID,
    uc: GetOrderByIdUseCase = Depends(Provide[Container.application.get_order_by_id]),
):
    return await uc.get_order(order_id)


@router.post("/orders/payment-callback", status_code=status.HTTP_200_OK)
@inject
async def payment_callback(
    data: PaymentCallbackDTO,
    use_case: PaymentCallback = Depends(
        Provide[Container.application.payment_callback]
    ),
):
    await use_case.execute(data)
    return {"status": "ok"}
