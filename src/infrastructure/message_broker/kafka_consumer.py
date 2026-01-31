import json
import logging

from aiokafka import AIOKafkaConsumer

from src.application.use_cases.process_inbox_events import ProcessInboxEventsUseCase

logger = logging.getLogger(__name__)


class KafkaConsumerService:
    def __init__(
        self,
        topic: str,
        bootstrap_servers: str,
        group_id: str,
        use_case: ProcessInboxEventsUseCase,
    ):
        self._group_id = group_id
        self._topic = topic
        self._bootstrap_servers = bootstrap_servers
        self._consumer: AIOKafkaConsumer | None = None
        self._use_case = use_case

    async def start(self):
        """Инициализация и запуск Kafka Consumer"""
        self._consumer = AIOKafkaConsumer(
            self._topic,
            bootstrap_servers=self._bootstrap_servers,
            group_id=self._group_id,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")) if m else None,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
        )
        await self._consumer.start()

    async def stop(self):
        """Остановка Consumer"""

        if self._consumer:
            await self._consumer.stop()

    async def run(self):
        await self.start()
        logger.info(f"Consumer started on topic {self._topic}")
        try:
            async for message in self._consumer:
                if message.value is None:
                    continue

                try:

                    await self._use_case.execute(message.value)

                    await self._consumer.commit()

                except Exception as e:

                    logger.error(f"Error processing message: {e}", exc_info=True)
                    continue
        finally:
            await self.stop()
