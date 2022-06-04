"""Tests for the get request hook.

Author: Dmitry Sergeev <realnexusway@gmail.com>
"""

from datetime import datetime
from unittest.mock import AsyncMock

import articles
from articles import ArticleEntry
from articles.api.schema import ReplyOne
from articles.dal.repository import RepositoryException

from httpx import AsyncClient

import pytest


@pytest.mark.asyncio()
async def test_get_success() -> None:
    """Tests that the repository is calls properly and the response."""
    article = ArticleEntry(
        article_id=123,
        topic="expected topic",
        text="expected text",
        updated=None,
        created=datetime.now(),
    )

    articles.api.Repository.get = AsyncMock(return_value=article)

    async with AsyncClient(
        app=articles.api.app,
        base_url="http://localhost"
    ) as ac:
        response = await ac.get("/articles/v1/get/123")

    articles.api.Repository.get.assert_called_with(123)
    assert response.status_code == 200

    expected = ReplyOne(success=True, article=article).dict()
    expected["article"]["created"] = expected["article"]["created"].isoformat()
    assert response.json() == expected


@pytest.mark.asyncio()
async def test_get_failed() -> None:
    """Tests the response if the reposithory raises an exception."""
    articles.api.Repository.get = AsyncMock(
        side_effect=RepositoryException("expected message")
    )

    async with AsyncClient(
        app=articles.api.app,
        base_url="http://localhost"
    ) as ac:
        response = await ac.get("/articles/v1/get/123")

    assert response.status_code == 418

    assert response.json() == {
        "success": False,
        "error": "expected message"
    }