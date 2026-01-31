from dependency_injector import containers, providers

from .db import Database
from .http.catalog_service import CatalogServiceAPI
from .http.payments_service import PaymentsServiceAPI
from .message_broker.kafka_producer import KafkaProducerService
from .uow import UnitOfWork


class InfrastructureContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    db = providers.Singleton(
        Database,
        db_url=config.POSTGRES_CONNECTION_STRING,
    )

    uow = providers.Factory(
        UnitOfWork,
        session_factory=db.provided.session_factory,
    )

    catalog_api = providers.Singleton(
        CatalogServiceAPI,
        base_url=config.BASE_URL,
        api_key=config.API_KEY,
    )

    payment_api = providers.Singleton(
        PaymentsServiceAPI,
        base_url=config.BASE_URL,
        api_key=config.API_KEY,
        callback_url=config.CALLBACK_URL,
    )

    kafka_producer = providers.Singleton(
        KafkaProducerService,
        bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
    )
