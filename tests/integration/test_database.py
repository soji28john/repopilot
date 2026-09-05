import pytest
from sqlalchemy import text

from packages.database.connection import engine


@pytest.mark.asyncio
async def test_database_connection():
    async with engine.connect() as connection:
        result = await connection.execute(text("SELECT 1"))

        assert result.scalar_one() == 1