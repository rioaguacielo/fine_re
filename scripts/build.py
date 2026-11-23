#!/usr/bin/env python3
"""파인가든 사이트 생성기.

content/products/*.md (제품), content/cases/*.md (납품사례) 와 templates/ 를 읽어
_site/ 에 완성된 HTML을 만듭니다. GitHub Actions(.github/workflows/deploy.yml)가
글이 올라올 때마다 자동으로 실행합니다.

로컬 실행:  python3 scripts/build.py   (필요 패키지: pyyaml, jinja2, markdown)
"""
import datetime as dt
import os
import re
import shutil
import sys
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_site"
KST = dt.timezone(dt.timedelta(hours=9))
STATIC_DIRS = ["css", "images", "uploads"]


def load_site():
    site = yaml.safe_load((ROOT / "site.yml").read_text(encoding="utf-8"))
    base = os.environ.get("BASEURL", site.get("baseurl", "")) or ""
    return site, base.rstrip("/")


def parse_date(v):
    if isinstance(v, dt.datetime):
        d = v
    elif isinstance(v, dt.date):
        d = dt.datetime(v.year, v.month, v.day)
    elif isinstance(v, str) and v.strip():
        s = v.strip().replace(".", "-").replace("T", " ")
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                d = dt.datetime.strptime(s[:19], fmt)
                break
            except ValueError:
                continue
        else:
            d = dt.datetime(1970, 1, 1)
    else:
        d = dt.datetime(1970, 1, 1)
    return d.replace(tzinfo=None)


def read_md(path: Path):
    text = path.read_text(encoding="utf-8")
    meta, body = {}, text
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
    if m:
        meta = yaml.safe_load(m.group(1)) or {}
        body = m.group(2)
    return meta, body


def to_html(body, base):
    body = (body or "").strip()
    if not body:
        return ""
    html = body if body.startswith("<") else markdown.markdown(body, extensions=["extra", "nl2br", "sane_lists"])
    return fix_urls(html, base)


def fix_urls(html, base):
    # CMS가 넣는 /uploads/... 같은 사이트 안 경로에 하위 경로를 붙입니다.
    if not base:
        return html
    return re.sub(r'(src|href)=(["\'])/(?!/)(?!' + re.escape(base.lstrip("/")) + r'/)', rf'\1=\2{base}/', html)


def url_of(path, base):
    if not path:
        return None
    path = str(path)
    return base + path if path.startswith("/") else path


def natural_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def load_products(site, base):
    cats = site["categories"]
    cat_order = {c["name"]: i for i, c in enumerate(cats)}
    sub_order = {(c["name"], s): i for c in cats for i, s in enumerate(c["subs"])}
    items = []
    for f in sorted((ROOT / "content" / "products").glob("*.md")):
        meta, body = read_md(f)
        if meta.get("draft"):
            continue
        cat = str(meta.get("category") or cats[0]["name"])
        sub = str(meta.get("sub") or "기타")
        title = str(meta.get("title") or f.stem)
        items.append({
            "slug": f.stem,
            "title": title,
            "category": cat,
            "sub": sub,
            "size": str(meta.get("size") or "").strip(),
            "material": str(meta.get("material") or "").strip(),
            "image": url_of(meta.get("image"), base),
            "html": to_html(body, base),
            "order": meta.get("order"),
            "url": f"{base}/products/{f.stem}/",
        })
    items.sort(key=lambda p: (
        cat_order.get(p["category"], 99),
        sub_order.get((p["category"], p["sub"]), 99),
        p["order"] if isinstance(p["order"], (int, float)) else 9999,
        natural_key(p["title"]),
    ))
    return items


def load_cases(site, base):
    items = []
    for f in sorted((ROOT / "content" / "cases").glob("*.md")):
        meta, body = read_md(f)
        if meta.get("draft"):
            continue
        html = to_html(body, base)
        image = url_of(meta.get("image"), base)
        if not image:
            m = re.search(r'<img[^>]+src=["\']([^"\']+)', html)
            image = m.group(1) if m else None
        date = parse_date(meta.get("date"))
        items.append({
            "slug": f.stem,
            "title": str(meta.get("title") or f.stem),
            "client_type": str(meta.get("client_type") or ""),
            "products": str(meta.get("products") or ""),
            "date": date,
            "year": date.year if date.year > 1970 else "",
            "image": image,
            "html": html,
            "url": f"{base}/cases/{f.stem}/",
        })
    items.sort(key=lambda p: p["date"], reverse=True)
    return items


def main():
    site, base = load_site()
    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=select_autoescape(["html"]))
    build_id = dt.datetime.now(KST).strftime("%Y%m%d%H%M")
    products = load_products(site, base)
    cases = load_cases(site, base)

    categories = []
    for c in site["categories"]:
        in_cat = [p for p in products if p["category"] == c["name"]]
        subs = [s for s in c["subs"] if any(p["sub"] == s for p in in_cat)]
        cover = next((p["image"] for p in in_cat if p["image"]), None)
        categories.append({**c, "count": len(in_cat), "subs_used": subs, "cover": cover})

    common = {"site": site, "base": base, "build_id": build_id, "categories": categories,
              "products": products, "cases": cases, "year": dt.datetime.now(KST).year}

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for d in STATIC_DIRS:
        if (ROOT / d).exists():
            shutil.copytree(ROOT / d, OUT / d, ignore=shutil.ignore_patterns(".gitkeep"))
    (OUT / ".nojekyll").write_text("")

    def write(rel, html):
        p = OUT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(html, encoding="utf-8")

    # 고정 페이지
    pages = {"home": ("index.html", "home"), "about": ("about.html", "about"), "process": ("process.html", "process"),
             "faq": ("faq.html", "faq"), "contact": ("contact.html", "contact"), "404": ("404.html", "")}
    for name, (out, nav) in pages.items():
        if (ROOT / "templates" / "pages" / f"{name}.html").exists():
            write(out, env.get_template(f"pages/{name}.html").render(nav=nav, **common))

    # 제품
    write("products/index.html", env.get_template("products.html").render(nav="products", **common))
    for i, p in enumerate(products):
        same = [q for q in products if q["sub"] == p["sub"] and q["category"] == p["category"] and q["slug"] != p["slug"]][:4]
        write(f"products/{p['slug']}/index.html",
              env.get_template("product.html").render(nav="products", product=p, related=same, **common))

    # 납품사례
    write("cases/index.html", env.get_template("cases.html").render(nav="cases", **common))
    for c in cases:
        write(f"cases/{c['slug']}/index.html", env.get_template("case.html").render(nav="cases", case=c, **common))

    print(f"built {len(products)} products, {len(cases)} cases -> {OUT}")


if __name__ == "__main__":
    sys.exit(main())
