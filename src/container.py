import os
from dependency_injector import containers, providers


from src.application.container import ApplicationContainer
from src.infrastructure.container import InfrastructureContainer
from src.infrastructure.message_broker.kafka_consumer import KafkaConsumerService


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    config.from_dict(os.environ)

    infrastructure = providers.Container(
        InfrastructureContainer,
        config=config,
    )

    application = providers.Container(
        ApplicationContainer,
        uow=infrastructure.uow,
        config=config,
        kafka_producer=infrastructure.kafka_producer,
        catalog_api=infrastructure.catalog_api,
        payment_api=infrastructure.payment_api,
    )
    kafka_consumer = providers.Singleton(
        KafkaConsumerService,
        use_case=application.process_inbox,
        topic=config.KAFKA_CONSUMER_TOPIC,
        bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
        group_id=config.KAFKA_CONSUMER_GROUP_ID,
    )
