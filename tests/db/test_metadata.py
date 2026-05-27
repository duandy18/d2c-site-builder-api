from app.core.db import Base


def test_metadata_loads() -> None:
    assert Base.metadata is not None
