"""检索源抽象基类。新增搜索引擎只需实现 search 方法。"""

from abc import ABC, abstractmethod


class SearchProvider(ABC):
    name = "base"

    @abstractmethod
    def search(self, keyword: str, limit: int = 10) -> list[str]:
        """返回结果 URL 列表，按排名从高到低排列。"""
        raise NotImplementedError
