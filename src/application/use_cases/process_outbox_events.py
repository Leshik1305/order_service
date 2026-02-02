import asyncio
import logging

from src.application.use_cases.send_notification import SendNotificationUseCase
from src.infrastructure.message_broker.kafka_producer import KafkaProducerService
from src.infrastructure.uow import UnitOfWork

logger = logging.getLogger(__name__)


class ProcessOutboxEventsUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        kafka_producer: KafkaProducerService,
        notification_use_case: SendNotificationUseCase,
        topic: str,
        batch_size: int = 100,
    ):
        self._uow = uow
        self._kafka_producer = kafka_producer
        self._notification_use_case = notification_use_case
        self._topic = topic
        self._batch_size = batch_size
        self._is_running = False

    def stop(self):
        self._is_running = False

    async def run(self) -> None:
        self._is_running = True
        while self._is_running:
            events = []
            try:
                async with self._uow() as uow:
                    events = await uow.outbox.get_pending_events(limit=self._batch_size)

                    if events:
                        for event in events:
                            try:
                                await self._kafka_producer.publish_event(
                                    topic=self._topic, event=event
                                )
                                await self._notification_use_case.execute(event.payload)
                                await uow.outbox.mark_as_sent(event.id)

                            except Exception as e:
                                logger.error(f"Failed to process event {event.id}: {e}")

                await asyncio.sleep(1 if events else 5)

            except Exception as e:
                print(f"Error in outbox worker loop: {e}")
                await asyncio.sleep(5)
