import asyncio

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
        self._is_running = False

    def stop(self):
        self._is_running = False

    async def run(self) -> None:
        self._is_running = True
        while self._is_running:
            try:
                async with self._uow() as uow:
                    events = await uow.outbox.get_pending_events(limit=self._batch_size)

                if not events:
                    await asyncio.sleep(5)
                    continue


                for event in events:
                    try:
                        await self._kafka_producer.publish_event(topic=self._topic, event=event)
                        async with self._uow() as uow:
                            await uow.outbox.mark_as_sent(event.id)
                            await uow.commit()
                    except Exception as e:
                        print(f"Failed to publish outbox event {event.id}: {e}")

                        await asyncio.sleep(1)
                        continue

            except Exception as e:
                print(f"Error in outbox worker loop: {e}")
                await asyncio.sleep(5)  # Пауза при ошибке БД
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
