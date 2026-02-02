from dependency_injector import containers, providers

from .use_cases.create_order import CreateOrder
from .use_cases.get_order_by_id import GetOrderByIdUseCase
from .use_cases.payment_callback import PaymentCallback
from .use_cases.process_inbox_events import ProcessInboxEventsUseCase
from .use_cases.process_outbox_events import ProcessOutboxEventsUseCase
from .use_cases.send_notification import SendNotificationUseCase


class ApplicationContainer(containers.DeclarativeContainer):
    uow: providers.Dependency = providers.Dependency()
    catalog_api = providers.Dependency()
    payment_api = providers.Dependency()
    config = providers.Configuration()
    kafka_producer = providers.Dependency()
    notifications_api = providers.Dependency()

    create_order = providers.Factory(
        CreateOrder,
        uow=uow,
        catalog=catalog_api,
        payment=payment_api,
    )
    send_notification = providers.Factory(
        SendNotificationUseCase,
        notifications_api=notifications_api,
    )
    get_order_by_id = providers.Factory(
        GetOrderByIdUseCase,
        uow=uow,
    )
    payment_callback = providers.Factory(
        PaymentCallback,
        uow=uow,
    )

    process_outbox = providers.Factory(
        ProcessOutboxEventsUseCase,
        uow=uow,
        kafka_producer=kafka_producer,
        notification_use_case=send_notification,
        batch_size=config.OUTBOX_BATCH_SIZE.as_int(),
        topic=config.KAFKA_PRODUCER_TOPIC,
    )

    process_inbox = providers.Factory(
        ProcessInboxEventsUseCase,
        uow=uow,
    )
