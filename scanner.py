import json
import os
import re
import sys
import time
from datetime import datetime
from typing import Optional

import requests

GROUP_ID = "711102"
TAP_TAP_BASE = "https://www.taptap.cn/webapiv2"
SERVERCHAN_URL = "https://sctapi.ftqq.com"
KEYWORDS = ["兑换码", "有效期", "兑换要求"]
WINDOW_SIZE = 8
CACHE_FILE = "pushed_codes.json"
REQUEST_INTERVAL = 1.5

HEADERS = {
    "X-UA": "V=1&PN=WebApp&LANG=zh_CN&VN_CODE=102&LOC=CN&PLT=PC&DT=PC&UID=abc&OS=Windows",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.taptap.cn/app/521534",
}


def fetch_official_topics() -> list[dict]:
    url = f"{TAP_TAP_BASE}/feed/v7/by-group"
    params = {
        "group_id": GROUP_ID,
        "type": "official",
        "sort": "created",
        "from": 0,
        "limit": 10,
    }
    resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    topics = []
    for item in data.get("data", {}).get("list", []):
        moment = item.get("moment", {})
        topic = moment.get("topic", {})
        tid = topic.get("id_str")
        title = topic.get("title", "")
        if tid:
            topics.append({"id": tid, "title": title})
    return topics


def fetch_topic_body(topic_id: str) -> str:
    url = f"{TAP_TAP_BASE}/topic/v1/detail"
    params = {"id": topic_id}
    resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json().get("data", {})
    topic = data.get("topic", {})
    return topic.get("summary", "")


def extract_code_blocks(text: str) -> list[dict]:
    lines = text.split("\n")
    blocks = []
    seen_codes = set()
    i = 0

    while i < len(lines):
        window = lines[i : i + WINDOW_SIZE]
        has_code = any(KEYWORDS[0] in line for line in window)
        has_expiry = any(KEYWORDS[1] in line for line in window)
        has_require = any(KEYWORDS[2] in line for line in window)

        if has_code and has_expiry and has_require:
            block = _parse_block(window)
            if block and block["code"] and block["code"] not in seen_codes:
                seen_codes.add(block["code"])
                blocks.append(block)
            i += len(window)
        else:
            i += 1

    return blocks


def _parse_block(lines: list[str]) -> Optional[dict]:
    result = {"code": "", "expiry": None, "requirement": "", "raw_lines": lines}

    code_value = ""
    expiry_str = ""
    requirement = ""

    for idx, line in enumerate(lines):
        if "兑换码" in line:
            if "：" in line or ":" in line:
                parts = re.split(r"[：:]\s*", line, maxsplit=1)
                if len(parts) > 1 and parts[1].strip():
                    code_value = parts[1].strip()
                else:
                    if idx + 1 < len(lines):
                        code_value = lines[idx + 1].strip()
            else:
                if idx + 1 < len(lines):
                    code_value = lines[idx + 1].strip()

        if "有效期" in line:
            match = re.search(
                r"(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}(?:[\sT]\d{1,2}[:：]\d{2}(?:[:：]\d{2})?)?)",
                line,
            )
            if match:
                expiry_str = match.group(1)

        if "兑换要求" in line:
            if "：" in line or ":" in line:
                parts = re.split(r"[：:]\s*", line, maxsplit=1)
                if len(parts) > 1:
                    requirement = parts[1].strip()
            else:
                if idx + 1 < len(lines):
                    requirement = lines[idx + 1].strip()

    result["code"] = code_value
    result["expiry"] = _parse_expiry(expiry_str) if expiry_str else None
    result["requirement"] = requirement

    if not code_value:
        return None
    return result


def _parse_expiry(date_str: str) -> Optional[datetime]:
    s = date_str.replace("年", "-").replace("月", "-").replace("日", "").replace("/", "-").replace("：", ":")
    for fmt in [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M",
    ]:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def load_cache() -> dict:
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_cache(codes: dict):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(codes, f, ensure_ascii=False, indent=2)


def push_to_phone(code_info: dict) -> bool:
    send_key = os.environ.get("SERVERCHAN_KEY", "")
    if not send_key:
        print("WARNING: SERVERCHAN_KEY 未设置，跳过推送", file=sys.stderr)
        return False

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    expiry_str = code_info["expiry"].strftime("%Y-%m-%d %H:%M") if code_info["expiry"] else "未知"

    title = f"新兑换码: {code_info['code']}"
    desp = (
        f"**兑换码**：{code_info['code']}\n\n"
        f"**有效期至**：{expiry_str}\n\n"
        f"**兑换要求**：{code_info['requirement']}\n\n"
        f"**扫描时间**：{now}"
    )

    payload = {"title": title, "desp": desp}
    url = f"{SERVERCHAN_URL}/{send_key}.send"

    resp = requests.post(url, data=payload, timeout=10)
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") == 0:
        print(f"  + 推送成功: {code_info['code']}")
        return True
    else:
        print(f"  x 推送失败: {result.get('message', '未知错误')}", file=sys.stderr)
        return False


def main():
    print("=" * 50)
    print(f"TapTap 兑换码扫描 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    print("\n[1/3] 获取官方帖列表...")
    topics = fetch_official_topics()
    print(f"  -> 找到 {len(topics)} 条官方帖")
    if not topics:
        print("  没有官方帖，结束")
        return

    print("\n[2/3] 提取兑换码...")
    all_blocks = []
    for t in topics:
        print(f"  [{t['id']}] {t['title'][:40]}")
        body = fetch_topic_body(t["id"])
        if not body:
            print("    正文为空，跳过")
            continue
        blocks = extract_code_blocks(body)
        if blocks:
            print(f"    发现 {len(blocks)} 个兑换码块")
            all_blocks.extend(blocks)
        time.sleep(REQUEST_INTERVAL)

    if not all_blocks:
        print("  未发现兑换码，结束")
        return

    print(f"\n[3/3] 推送新兑换码...")
    cache = load_cache()
    print(f"  缓存中有 {len(cache)} 个已推送码")

    new_count = 0
    for block in all_blocks:
        code = block["code"]
        if code in cache:
            print(f"  skip {code} 已推送过")
            continue
        if block["expiry"] and block["expiry"] < datetime.now():
            print(f"  skip {code} 已过期 ({block['expiry']})")
            continue

        print(f"  新兑换码: {code}")
        success = push_to_phone(block)
        if success:
            cache[code] = datetime.now().strftime("%Y-%m-%d")
            new_count += 1

    if new_count > 0:
        save_cache(cache)
        print(f"\n  本次新增 {new_count} 个兑换码")

    print("\n" + "=" * 50)
    print("扫描完成")
    print("=" * 50)


if __name__ == "__main__":
    main()