from dependency_injector import containers, providers

from .use_cases.create_order import CreateOrder
from .use_cases.payment_callback import PaymentCallback


class ApplicationContainer(containers.DeclarativeContainer):
    uow: providers.Dependency = providers.Dependency()
    catalog_api = providers.Dependency()
    payment_api = providers.Dependency()

    create_order = providers.Factory(
        CreateOrder,
        uow=uow,
        catalog=catalog_api,
        payment=payment_api,
    )
    payment_callback = providers.Factory(
        PaymentCallback,
        uow=uow,
    )
