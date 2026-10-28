#!/usr/bin/env python3
"""Read the dcinside 이세계아이돌 mini gallery.
  python3 -I dev/read-dc.py 5347545            # print a post
  python3 -I dev/read-dc.py --search 스포 유출   # titles from the last 2 days matching each word
Community posts are leads only: find the original source before using anything."""
import datetime, html, re, subprocess, sys, urllib.parse

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
def get(url):
    return subprocess.run(["curl", "-s", "-m", "25", "-A", UA, url], capture_output=True, text=True).stdout


if sys.argv[1:2] == ["--search"]:
    since = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9) - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
    for kw in sys.argv[2:]:
        t = get("https://gall.dcinside.com/mini/board/lists/?id=isekaidol&s_type=search_subject_memo&s_keyword=" + urllib.parse.quote(kw))
        rows = []
        for r in re.findall(r'<tr class="ub-content us-post".*?</tr>', t, re.S):
            no = re.search(r'data-no="(\d+)"', r)
            ti = re.search(r'<a[^>]*href="/mini/board/view/[^"]*"[^>]*>(.*?)</a>', r, re.S)
            d = re.search(r'gall_date" title="([^"]+)', r)
            if no and ti and d and d.group(1)[:10] >= since:
                rows.append(f"  {no.group(1)} {d.group(1)} {html.unescape(re.sub(r'<[^>]+>', '', ti.group(1))).strip()[:80]}")
        print(f" [{kw}] {len(rows)}건")
        print("\n".join(rows[:8]))
    sys.exit()

for no in sys.argv[1:]:
    t = get(f"https://gall.dcinside.com/mini/board/view/?id=isekaidol&no={no}")
    ti = re.search(r'<span class="title_subject">(.*?)</span>', t, re.S)
    d = re.search(r'<span class="gall_date" title="([^"]+)', t)
    b = re.search(r'<div class="write_div"[^>]*>(.*?)if\(window.OutLink', t, re.S)
    x = b.group(1) if b else ""
    links = re.findall(r'href="(https?://[^"]+)"', x)
    x = re.sub(r"<br\s*/?>|</p>|</div>", "\n", x)
    x = re.sub(r"<[^>]+>", "", x)
    x = re.sub(r"\n\s*\n+", "\n", html.unescape(x)).strip()
    print(f"===== {no} {d.group(1) if d else ''} {html.unescape(ti.group(1)) if ti else ''}")
    print(x[:2000])
    if links:
        print("links:", " ".join(links[:8]))
