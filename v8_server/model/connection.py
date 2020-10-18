from __future__ import annotations

from pathlib import Path
from types import TracebackType
from typing import Optional, Type

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import Session as AlchemySession


Base: DeclarativeMeta = declarative_base()


class Database(object):
    def __init__(self, echo: bool = False) -> None:
        self.uri = f"sqlite+pysqlite:///{Path(__file__).parent / 'v8.db'}"
        self.engine = create_engine(self.uri, echo=echo)
        self.session = AlchemySession(bind=self.engine)

    def __enter__(self) -> Database:
        return self

    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> bool:
        self.session.close()
        return exception_type is None

    def __del__(self) -> None:
        self.engine.dispose()
