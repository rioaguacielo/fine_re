#!/usr/bin/env python3
"""기존 사이트의 로고(투명 PNG)를 images/logo.png 로 한 번 가져옵니다. 이미 있으면 아무것도 하지 않습니다."""
import urllib.request
from pathlib import Path

DEST = Path(__file__).resolve().parent.parent / "images" / "logo.png"
URL = "http://www.finegarden.net/wp-content/uploads/2015/02/logo.png"

if DEST.exists():
    print("logo exists")
else:
    try:
        req = urllib.request.Request(URL, headers={"User-Agent": "finegarden-migrate"})
        data = urllib.request.urlopen(req, timeout=30).read()
        if data[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError("not a png")
        DEST.parent.mkdir(exist_ok=True)
        DEST.write_bytes(data)
        print(f"logo saved ({len(data)} bytes)")
    except Exception as e:
        print(f"logo skip: {e}")
