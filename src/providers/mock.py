"""离线检索源，用固定数据演示流程，不依赖网络。"""

import json
from pathlib import Path

from .base import SearchProvider


class MockProvider(SearchProvider):
    name = "mock"

    def __init__(self, fixture_path):
        self.data = json.loads(Path(fixture_path).read_text(encoding="utf-8"))

    def search(self, keyword: str, limit: int = 10) -> list[str]:
        return list(self.data.get(keyword, []))[:limit]
