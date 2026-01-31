import typing

from .repositories import Repository


class UnitOfWork(typing.Protocol):
    async def __call__(self) -> typing.AsyncContextManager[Repository]: ...
