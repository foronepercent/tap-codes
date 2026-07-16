import json
import os
import sys
import tempfile
from datetime import datetime

from scanner import extract_code_blocks, _parse_expiry

EXAMPLE_1 = (
    "兑换码：银色约定\n"
    "有效期至：2026-07-16 23:59:00\n"
    "兑换要求：大熔炉等级大于等于9级"
)

EXAMPLE_2 = (
    "兑换码\n"
    "海上平安\n"
    "有效期至：2026-07-13 23:59:00\n"
    "兑换要求：大熔炉等级大于等于9级"
)

NO_CODE_TEXT = (
    "策划面对面 | 小剧场讨论\n"
    "大家好，欢迎参加本次策划面对面活动。\n"
    "请在本帖下留言，我们会精选问题回答。"
)

MULTI_BLOCK = (
    "【内含兑换码】活动一\n"
    "兑换码：码一\n"
    "有效期至：2026-08-01 23:59:00\n"
    "兑换要求：等级大于等于5级\n"
    "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
    "【内含兑换码】活动二\n"
    "兑换码：码二\n"
    "有效期至：2026-08-15 23:59:00\n"
    "兑换要求：等级大于等于10级\n"
)


def test_example_1():
    blocks = extract_code_blocks(EXAMPLE_1)
    assert len(blocks) == 1, f"Expected 1 block, got {len(blocks)}"
    assert blocks[0]["code"] == "银色约定", f"Expected '银色约定', got '{blocks[0]['code']}'"
    assert blocks[0]["expiry"] is not None, "Expected expiry to be parsed"
    assert blocks[0]["expiry"].strftime("%Y-%m-%d %H:%M:%S") == "2026-07-16 23:59:00"
    assert "大熔炉等级大于等于9级" in blocks[0]["requirement"]
    print("[PASS] test_example_1")


def test_example_2():
    blocks = extract_code_blocks(EXAMPLE_2)
    assert len(blocks) == 1, f"Expected 1 block, got {len(blocks)}"
    assert blocks[0]["code"] == "海上平安", f"Expected '海上平安', got '{blocks[0]['code']}'"
    assert blocks[0]["expiry"] is not None
    assert blocks[0]["expiry"].strftime("%Y-%m-%d %H:%M:%S") == "2026-07-13 23:59:00"
    assert "大熔炉等级大于等于9级" in blocks[0]["requirement"]
    print("[PASS] test_example_2")


def test_no_code():
    blocks = extract_code_blocks(NO_CODE_TEXT)
    assert len(blocks) == 0, f"Expected 0 blocks, got {len(blocks)}"
    print("[PASS] test_no_code")


def test_multi_blocks():
    blocks = extract_code_blocks(MULTI_BLOCK)
    assert len(blocks) == 2, f"Expected 2 blocks, got {len(blocks)}"
    codes = [b["code"] for b in blocks]
    assert "码一" in codes
    assert "码二" in codes
    print("[PASS] test_multi_blocks")


def test_expiry_parsing():
    dt = _parse_expiry("2026-07-16 23:59:00")
    assert dt is not None
    assert dt.year == 2026 and dt.month == 7 and dt.day == 16

    dt2 = _parse_expiry("2026-07-13")
    assert dt2 is not None
    assert dt2.hour == 0 and dt2.minute == 0

    dt3 = _parse_expiry("invalid")
    assert dt3 is None

    print("[PASS] test_expiry_parsing")


def test_expired_skip():
    text = (
        "兑换码：已过期\n"
        "有效期至：2020-01-01 00:00:00\n"
        "兑换要求：无"
    )
    blocks = extract_code_blocks(text)
    assert len(blocks) == 1, f"Expected 1 block, got {len(blocks)}"
    assert blocks[0]["expiry"] < datetime.now(), "Expected expiry to be in the past"
    print("[PASS] test_expired_skip - extract does not filter expiry, main() does")


if __name__ == "__main__":
    test_example_1()
    test_example_2()
    test_no_code()
    test_multi_blocks()
    test_expiry_parsing()
    test_expired_skip()
    print("\n=== 全部测试通过 ===")