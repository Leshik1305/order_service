import json

from aiokafka import AIOKafkaProducer

from src.application.dtos.outbox import OutboxEventDTO
from ..utils.serializer_for_json import default_serializer


class KafkaProducerService:
    def __init__(self, bootstrap_servers: str):
        self._bootstrap_servers = bootstrap_servers
        self._producer: AIOKafkaProducer | None = None

    async def start(self):
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self._bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, default=default_serializer).encode(
                "utf-8"
            ),
            acks="all",
        )
        await self._producer.start()

    async def stop(self):
        if self._producer:
            await self._producer.stop()

    async def publish_event(self, topic: str, event: OutboxEventDTO):
        if not self._producer:
            raise RuntimeError("KafkaProducerService is not started.")

        await self._producer.send_and_wait(
            topic,
            value=event.payload,
            key=str(event.id).encode("utf-8"),
        )
