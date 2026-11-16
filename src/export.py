"""导出 Excel 报告。"""

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from .models import CheckResult

HEADERS = ["关键词", "目标域名", "是否收录", "排名", "匹配URL", "耗时(ms)", "状态"]
COLUMN_WIDTHS = [26, 22, 10, 8, 50, 10, 10]


def export_excel(results: list[CheckResult], path: str) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "检索结果"

    sheet.append(HEADERS)
    header_fill = PatternFill("solid", fgColor="2F6FED")
    for cell in sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    for result in results:
        sheet.append(
            [
                result.keyword,
                result.domain,
                "是" if result.found else "否",
                result.rank or "",
                result.matched_url or "",
                result.elapsed_ms,
                result.status,
            ]
        )

    for index, width in enumerate(COLUMN_WIDTHS, start=1):
        sheet.column_dimensions[get_column_letter(index)].width = width

    sheet.freeze_panes = "A2"
    workbook.save(path)
