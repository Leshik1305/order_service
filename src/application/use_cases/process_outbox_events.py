from src.infrastructure.message_broker.kafka_producer import KafkaProducerService
from src.infrastructure.uow import UnitOfWork


class ProcessOutboxEventsUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        kafka_producer: KafkaProducerService,
        topic: str,
        batch_size: int = 100,
    ):
        self._uow = uow
        self._kafka_producer = kafka_producer
        self._topic = topic
        self._batch_size = batch_size

    async def run(self) -> None:
        async with self._uow() as uow:
            events = await uow.outbox.get_pending_events(limit=self._batch_size)

        if not events:
            return

        for event in events:
            try:
                await self._kafka_producer.publish_event(topic=self._topic, event=event)

                async with self._uow() as uow:
                    await uow.outbox.mark_as_sent(event.id)
                    await uow.commit()

            except Exception as e:

                continue
