#!/usr/bin/env python3
"""Read 왁물원 (Naver cafe steamindiegame) boards that matter for the album.

  python3 -I dev/read-cafe.py --scan          # last 2 days: notice boards in full, free boards filtered by the lead keywords
  python3 -I dev/read-cafe.py 22132926        # print an article with its comments

Cafe posts are leads like any community post: confirm with the original source,
and never put a cafe URL on the site unless it is an official notice board post.
"""
import datetime, html, importlib.util, json, os, re, subprocess, sys, time

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
CAFE = 27842958
KST = datetime.timezone(datetime.timedelta(hours=9))

# menuId: (name, show everything?)  Notice boards are shown whole, busy boards are keyword-filtered.
MENUS = {
    1250: ("소속사 공지사항", True),
    345: ("이세돌의 공지사항", True),
    24: ("카페 공지사항", True),
    347: ("이세돌 NEWS", False),
    1270: ("이세계아이돌 음원 스트리밍", True),
    327: ("이세돌 자유게시판", False),
    367: ("이세돌 반응 모음", False),
    397: ("이세돌 노래 근황", True),
}
PAGES = {327: 6, 367: 2}

# reuse the keyword list from read-dc.py
spec = importlib.util.spec_from_file_location("read_dc", os.path.join(os.path.dirname(os.path.abspath(__file__)), "read-dc.py"))
read_dc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(read_dc)
KEYWORDS = read_dc.KEYWORDS


def get_json(url):
    out = subprocess.run(["curl", "-s", "-m", "25", "-A", UA, "-H", "Referer: https://cafe.naver.com/steamindiegame", url],
                         capture_output=True, text=True).stdout
    try:
        return json.loads(out)
    except ValueError:
        return {}


def groups_for(title):
    t = title.lower()
    return [g for g, ws in KEYWORDS.items() if any(w in t for w in ws)]


def scan():
    cut = datetime.datetime.now(KST) - datetime.timedelta(days=2)
    for mid, (name, whole) in MENUS.items():
        rows = []
        for page in range(1, PAGES.get(mid, 1) + 1):
            d = get_json(f"https://apis.naver.com/cafe-web/cafe2/ArticleListV2dot1.json?search.clubid={CAFE}&search.menuid={mid}"
                         f"&search.queryType=lastArticle&search.page={page}&search.perPage=50")
            arts = ((d.get("message") or {}).get("result") or {}).get("articleList") or []
            for a in arts:
                ts = datetime.datetime.fromtimestamp(a.get("writeDateTimestamp", 0) / 1000, KST)
                if ts < cut:
                    continue
                title = html.unescape(a.get("subject") or "")
                g = groups_for(title)
                if whole or g:
                    rows.append((a.get("commentCount", 0), ts, a.get("articleId"), title, g))
            time.sleep(0.3)
        rows.sort(key=lambda r: (r[0], r[1]), reverse=True)
        print(f" [{name}] {len(rows)}개")
        for c, ts, aid, title, g in rows[:15]:
            print(f"  {aid} {ts:%m-%d %H:%M} 댓글{c} {('[' + '·'.join(g) + '] ') if g else ''}{title[:70]}")


def read(ids):
    for aid in ids:
        d = get_json(f"https://apis.naver.com/cafe-web/cafe-articleapi/v2.1/cafes/{CAFE}/articles/{aid}?useCafeId=true")
        r = d.get("result") or {}
        a = r.get("article") or {}
        if not a:
            print(f"===== {aid} (읽을 수 없음: 회원 전용이거나 삭제)")
            continue
        t = a.get("contentHtml") or ""
        links = sorted(set(re.findall(r'href="(https?://[^"]+)"', t)))
        t = re.sub(r"<(br|/p|/div|/li)[^>]*>", "\n", t)
        t = html.unescape(re.sub(r"<[^>]+>", "", t))
        t = re.sub(r"[ \t​]+", " ", t)
        t = re.sub(r"\n\s*\n+", "\n", t).strip()
        ts = datetime.datetime.fromtimestamp((a.get("writeDate") or 0) / 1000, KST)
        menu = (a.get("menu") or {}).get("name", "")
        print(f"===== {aid} {ts:%Y-%m-%d %H:%M} [{menu}] {a.get('subject')}")
        print(t[:2500])
        if links:
            print("links:", " ".join(links[:10]))
        items = ((r.get("comments") or {}).get("items")) or []
        cs = [f"   - {(c.get('content') or '').strip()[:160]}" for c in items if (c.get("content") or "").strip() and not c.get("isDeleted")]
        print(f"댓글 {len(cs)}개" + (":" if cs else ""))
        print("\n".join(cs[:40]))
        time.sleep(0.3)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["--scan"]:
        scan()
    else:
        read(a)
