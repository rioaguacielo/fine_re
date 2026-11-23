#!/usr/bin/env python3
"""기존 사이트(finegarden.net)의 제품 사진을 한 번만 옮겨 옵니다.

content/products/*.md 중 `old_image:` 가 남아 있는 제품만 처리합니다.
- 기존 사이트에서 사진을 내려받아 uploads/products/ 에 저장하고
- 제품 파일의 `image:` 를 채운 뒤 `old_image:` 줄을 지웁니다.
옮길 것이 없으면 아무것도 하지 않으므로, 배포할 때마다 실행해도 안전합니다.
기존 사이트에 접속하지 못하면 건너뛰고 다음 배포 때 다시 시도합니다.
"""
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OLD_BASE = "http://www.finegarden.net/wp-content/uploads/"
DEST = ROOT / "uploads" / "products"


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    done = failed = 0
    for f in sorted((ROOT / "content" / "products").glob("*.md")):
        text = f.read_text(encoding="utf-8")
        m = re.search(r'^old_image:\s*"?([^"\n]+)"?\s*$', text, re.M)
        if not m:
            continue
        rel = m.group(1).strip()
        ext = Path(rel).suffix.lower() or ".jpg"
        name = f"{f.stem}{ext}"
        url = OLD_BASE + urllib.parse.quote(rel)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "finegarden-migrate"})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            if len(data) < 500:
                raise ValueError("too small")
        except Exception as e:  # 실패한 사진은 다음에 다시 시도
            print(f"skip {f.name}: {url} ({e})")
            failed += 1
            continue
        (DEST / name).write_bytes(data)
        text = re.sub(r'^image:.*$', f'image: "/uploads/products/{name}"', text, count=1, flags=re.M)
        text = re.sub(r'^old_image:.*\n', "", text, count=1, flags=re.M)
        f.write_text(text, encoding="utf-8")
        done += 1
        time.sleep(0.2)
    print(f"migrated {done} image(s), {failed} failed")


if __name__ == "__main__":
    sys.exit(main())
