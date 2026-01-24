from dependency_injector import containers, providers

from src.application.container import ApplicationContainer
from src.infrastructure.container import InfrastructureContainer


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    wiring_config = containers.WiringConfiguration(packages=["src.presentation"])

    infrastructure = providers.Container(
        InfrastructureContainer,
        config=config,
    )

    application = providers.Container(
        ApplicationContainer,
        uow=infrastructure.uow,
        catalog_api=infrastructure.catalog_api,
        payment_api=infrastructure.payment_api,
    )
