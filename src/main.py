import os
import asyncio
import logging
from contextlib import asynccontextmanager

import fastapi
import uvicorn

from src.container import Container
from src.presentation import api


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    container = app.container
    infrastructure_container = container.infrastructure
    db = infrastructure_container.db()
    await db.create_database()
    kafka_producer = infrastructure_container.kafka_producer()
    await kafka_producer.start()
    logging.info("Kafka Producer started")
    outbox_worker = container.application.process_outbox()
    outbox_task = asyncio.create_task(outbox_worker.run())
    logging.info("Outbox Worker background task started")
    kafka_consumer = container.kafka_consumer()
    consumer_task = asyncio.create_task(kafka_consumer.run())
    logging.info("Kafka Consumer background task started")

    try:
        yield
    finally:
        logging.info("Shutting down services...")

        outbox_worker.stop()

        await kafka_consumer.stop()

        await asyncio.gather(outbox_task, consumer_task, return_exceptions=True)

        await kafka_producer.stop()
        await db.engine.dispose()
        logging.info("All services stopped")


def create_app() -> fastapi.FastAPI:
    container = Container()
    container.config.from_dict(os.environ)
    container.wire(packages=["src.presentation"], modules=[__name__])
    app = fastapi.FastAPI(lifespan=lifespan)
    # app = fastapi.FastAPI()
    app.container = container
    container.wire(packages=["src.presentation"])
    app.include_router(api.router)
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
