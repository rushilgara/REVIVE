import pytest
import os
import sys
import asyncio

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.session import init_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    asyncio.run(init_db())
    yield
