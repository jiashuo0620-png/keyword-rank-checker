"""数据结构定义。"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CheckResult:
    """单个「关键词 + 域名」的检查结果。"""

    keyword: str
    domain: str
    found: bool = False
    rank: Optional[int] = None
    matched_url: Optional[str] = None
    status: str = "ok"          # ok | error
    error: Optional[str] = None
    elapsed_ms: int = 0
