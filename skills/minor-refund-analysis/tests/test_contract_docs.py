"""契约测试：确保 skill 文档和适配器只引用 API 返回的日历增强字段。"""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class MinorRefundAnalysisContractTests(unittest.TestCase):
    def test_docs_reference_api_calendar_fields_only(self):
        files = [
            ROOT / "SKILL.md",
            ROOT / "references" / "api.md",
            ROOT / "references" / "analysis-rules.md",
            ROOT / "platforms" / "codex" / "SKILL.md",
            ROOT / "platforms" / "claude-code" / "SKILL.md",
            ROOT / "platforms" / "cursor" / "SKILL.md",
            ROOT / "platforms" / "cursor" / ".cursorrules",
            ROOT / "platforms" / "gemini-code" / "SKILL.md",
        ]
        text = "\n".join(
            path.read_text(encoding="utf-8") for path in files if path.exists()
        )

        self.assertIn("weekdayCn", text)
        self.assertIn("isHoliday", text)
        self.assertIn("holidayName", text)
        self.assertIn("isAdjustedWorkday", text)
        self.assertNotIn("weekday_info.py", text)
        self.assertNotIn("isWeekend", text)

        # analysisMetrics 契约
        self.assertIn("analysisMetrics", text)
        self.assertIn("loginRecordCount", text)
        self.assertIn("keyWindowBuckets", text)
        self.assertNotIn("skill 自行聚合", text)
        self.assertNotIn("本地脚本计算登录高频", text)


if __name__ == "__main__":
    unittest.main()
