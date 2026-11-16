"""DuckDuckGo HTML 检索适配器。

注意：请遵守目标站点的使用条款与 robots 协议，控制请求频率。
"""

from __future__ import annotations

import re
from urllib.parse import parse_qs, unquote, urlparse

import requests

from .base import SearchProvider


class DuckDuckGoProvider(SearchProvider):
    name = "duckduckgo"
    endpoint = "https://html.duckduckgo.com/html/"

    def __init__(self, timeout: int = 15, user_agent: str | None = None):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": user_agent
                or "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            }
        )

    def search(self, keyword: str, limit: int = 10) -> list[str]:
        response = self.session.post(
            self.endpoint, data={"q": keyword}, timeout=self.timeout
        )
        response.raise_for_status()
        return self._extract_urls(response.text, limit)

    @staticmethod
    def _extract_urls(html: str, limit: int) -> list[str]:
        urls: list[str] = []
        for match in re.finditer(r'class="result__a"[^>]*href="([^"]+)"', html):
            href = match.group(1)
            # DuckDuckGo 的跳转链接形如 /l/?uddg=<urlencoded>
            if "uddg=" in href:
                query = parse_qs(urlparse(href).query)
                if "uddg" in query:
                    href = unquote(query["uddg"][0])
            if href.startswith("//"):
                href = "https:" + href
            if href not in urls:
                urls.append(href)
            if len(urls) >= limit:
                break
        return urls
