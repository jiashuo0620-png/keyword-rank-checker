# Keyword Rank Checker

> 批量查询关键词在搜索结果中的收录与排名情况，自动导出 Excel 报告。

## 背景

做 SEO 或内容运营时，经常需要确认「这个词我们排第几、页面有没有被收录」。手工一个个搜、一个个记，几十个词就要花掉半天，还容易漏。

这个工具把整个流程自动化：读取关键词表格 → 并发检索 → 判断目标域名是否出现 → 输出带排名的 Excel 报告。

## 功能

- **批量处理**：一次读取整张关键词表（CSV）
- **并发 + 限速**：多线程加速，同时控制请求频率，避免触发风控
- **域名匹配**：支持子域名，自动归一化 `http/https`、路径和大小写
- **失败重试**：单个关键词失败自动重试，不影响整体任务
- **Excel 报告**：输出是否收录、排名、命中 URL、耗时、状态
- **可插拔检索源**：内置离线 Mock 与 DuckDuckGo 适配器，方便扩展其他来源

## 技术栈

Python 3.9+ / requests / openpyxl / concurrent.futures

## 快速开始

```bash
pip install -r requirements.txt

# 离线演示（无需联网，使用内置数据）
python main.py --input data/keywords.example.csv --provider mock --output outputs/report.xlsx

# 使用真实检索源
python main.py --input data/keywords.example.csv --provider duckduckgo --output outputs/report.xlsx
```

## 输入格式

`data/keywords.example.csv`：

```csv
keyword,domain
python 爬虫教程,example.com
playwright 自动化,playwright.dev
```

## 输出示例

| 关键词 | 目标域名 | 是否收录 | 排名 | 匹配URL |
|---|---|---|---|---|
| python 爬虫教程 | example.com | 是 | 2 | https://example.com/... |
| seo 关键词工具 | example.com | 否 | | |

## 命令行参数

| 参数 | 说明 | 默认值 |
|---|---|---|
| `--input` | 关键词 CSV 路径 | 必填 |
| `--provider` | 检索源：`mock` / `duckduckgo` | `mock` |
| `--output` | Excel 输出路径 | `outputs/report.xlsx` |
| `--limit` | 每词检查前 N 条结果 | 10 |
| `--concurrency` | 并发线程数 | 4 |
| `--delay` | 每次请求间隔（秒） | 0.5 |

## 设计要点

1. **检索源解耦**：`SearchProvider` 抽象基类，换搜索引擎只需实现一个方法
2. **域名归一化**：统一处理协议、路径、大小写，避免 `www` 与裸域误判
3. **并发与限速并存**：线程池提速度，间隔控制降风险
4. **失败不拖垮任务**：单点异常单独标记为 `error`，其余结果照常输出

## 目录结构

```
.
├── data/
│   ├── keywords.example.csv   # 示例输入
│   └── fixtures.json          # 离线演示数据
├── src/
│   ├── checker.py             # 检索与匹配逻辑
│   ├── export.py              # Excel 导出
│   ├── models.py              # 数据结构
│   └── providers/             # 检索源适配器
├── tests/
│   └── test_checker.py
└── main.py
```

## 说明

- 默认的 `mock` 模式完全离线，克隆即可运行
- 使用真实检索源时请遵守目标站点的 robots 协议与使用条款，控制请求频率
