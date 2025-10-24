import pathlib
import sys

import pytest
from sqlmodel import SQLModel, create_engine, Session

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import models  # noqa: E402


@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
