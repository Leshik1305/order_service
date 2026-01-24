import fastapi
import uvicorn

from src.container import Container
from src.presentation import api
from src.settings import Settings


def create_container() -> Container:
    container = Container()
    container.config.from_pydantic(Settings())  # type: ignore
    return container


def create_app() -> fastapi.FastAPI:
    app = fastapi.FastAPI()
    app.container = create_container()
    app.container.wire(packages=["src.presentation"])  # type: ignore
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
