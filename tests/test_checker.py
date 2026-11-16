"""核心逻辑单元测试：python -m unittest discover -s tests"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.checker import check_one, domain_matches, normalize_domain  # noqa: E402
from src.providers.mock import MockProvider  # noqa: E402


class TestDomainMatching(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_domain("https://Example.COM/path?x=1"), "example.com")
        self.assertEqual(normalize_domain("example.com:8080"), "example.com")

    def test_exact_match(self):
        self.assertTrue(domain_matches("https://example.com/page", "example.com"))

    def test_subdomain_match(self):
        self.assertTrue(domain_matches("https://blog.example.com/post", "example.com"))

    def test_non_match(self):
        self.assertFalse(domain_matches("https://notexample.com/", "example.com"))


class TestCheckOne(unittest.TestCase):
    def setUp(self):
        fixture = Path(__file__).resolve().parent.parent / "data" / "fixtures.json"
        self.provider = MockProvider(fixture)

    def test_found_with_rank(self):
        result = check_one(self.provider, "python 爬虫教程", "example.com")
        self.assertTrue(result.found)
        self.assertEqual(result.rank, 2)

    def test_not_found(self):
        result = check_one(self.provider, "seo 关键词工具", "example.com")
        self.assertFalse(result.found)
        self.assertIsNone(result.rank)


if __name__ == "__main__":
    unittest.main()
