"""核心逻辑：域名归一化、匹配、并发检索。"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

from .models import CheckResult
from .providers.base import SearchProvider


def normalize_domain(domain: str) -> str:
    """去掉协议、路径、端口和大小写差异，只保留主机名。"""
    value = domain.strip().lower()
    for prefix in ("https://", "http://"):
        if value.startswith(prefix):
            value = value[len(prefix):]
    value = value.split("/")[0]
    value = value.split(":")[0]
    return value


def domain_matches(url: str, domain: str) -> bool:
    """判断 URL 的主机名是否等于目标域名，或为其子域名。"""
    host = urlparse(url).netloc.lower().split(":")[0]
    target = normalize_domain(domain)
    if not host or not target:
        return False
    return host == target or host.endswith("." + target)


def _elapsed_ms(started: float) -> int:
    return int((time.time() - started) * 1000)


def check_one(
    provider: SearchProvider,
    keyword: str,
    domain: str,
    limit: int = 10,
    retries: int = 2,
) -> CheckResult:
    """检查单个关键词：目标域名是否出现在前 limit 条结果中。"""
    started = time.time()
    last_error = None

    for attempt in range(retries + 1):
        try:
            urls = provider.search(keyword, limit=limit)
            for rank, url in enumerate(urls, start=1):
                if domain_matches(url, domain):
                    return CheckResult(
                        keyword=keyword,
                        domain=domain,
                        found=True,
                        rank=rank,
                        matched_url=url,
                        elapsed_ms=_elapsed_ms(started),
                    )
            return CheckResult(
                keyword=keyword,
                domain=domain,
                found=False,
                elapsed_ms=_elapsed_ms(started),
            )
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
            if attempt < retries:
                time.sleep(1)

    return CheckResult(
        keyword=keyword,
        domain=domain,
        status="error",
        error=last_error,
        elapsed_ms=_elapsed_ms(started),
    )


def check_all(
    provider: SearchProvider,
    pairs: list[tuple[str, str]],
    limit: int = 10,
    concurrency: int = 4,
    delay: float = 0.5,
) -> list[CheckResult]:
    """并发检查一批「关键词 + 域名」，并保持输出顺序稳定。"""
    results: list[CheckResult] = []

    with ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool:
        futures = []
        for keyword, domain in pairs:
            futures.append(pool.submit(check_one, provider, keyword, domain, limit))
            if delay > 0:
                time.sleep(delay)  # 控制提交速率，降低触发风控的概率

        for future in as_completed(futures):
            results.append(future.result())

    results.sort(key=lambda r: (r.keyword, r.domain))
    return results
