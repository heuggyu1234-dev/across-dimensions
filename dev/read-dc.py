#!/usr/bin/env python3
"""Read the dcinside 이세계아이돌 mini gallery for leads (spoilers, leaks, schedules, unions).

  python3 -I dev/read-dc.py --scan            # last 2 days: newest pages + 개념글 + keyword searches, filtered by a wide keyword list
  python3 -I dev/read-dc.py --search 스포 유출  # title/body search for the given words, last 2 days
  python3 -I dev/read-dc.py 5347545 5347622   # print posts with their comments (--no-comments to skip)

Community posts are leads only: find the original source before using anything,
and never put a community URL on the site.
"""
import datetime, html, json, os, re, subprocess, sys, tempfile, time, urllib.parse

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
BASE = "https://gall.dcinside.com/mini/board"

# What counts as a lead. Grouped only to keep the list readable.
KEYWORDS = {
    "스포·유출": ["스포", "유출", "떴다", "떳다", "떴음", "떳음", "뜸", "공개됨", "미리", "선공개", "찌라시", "카더라", "썰", "확정", "단독"],
    "곡·앨범": ["트랙", "트랙리스트", "타이틀", "수록곡", "곡명", "제목", "가사", "작곡", "작사", "편곡", "크레딧", "심의", "kbs", "저작권",
               "음저협", "komca", "멜론", "지니", "벅스", "플로", "바이브", "애플뮤직", "스포티파이", "음원", "음반", "앨범", "cd", "러닝타임",
               "dream", "residue", "꿈잔여물", "anti", "안티히어로", "back 2", "백투", "백2", "rebels", "레벨스", "반란군", "연애세포",
               "smile for you", "스포유", "across", "어크로스", "차원"],
    "영상·공개": ["티저", "뮤비", "mv", "m/v", "하이라이트", "메들리", "스포일러", "컨셉", "콘셉", "포토", "자켓", "재킷", "트레일러", "필름",
                "릴스", "쇼츠", "챌린지", "안무", "퍼포먼스", "직캠"],
    "일정·활동": ["컴백", "발매", "쇼케이스", "음방", "음악방송", "뮤뱅", "뮤직뱅크", "엠카", "쇼챔", "인기가요", "음중", "음악중심", "더쇼", "사녹",
                "라디오", "콘서트", "팬미팅", "팝업", "오프라인", "행사", "일정", "스케줄", "공지", "베리즈", "berriz", "패러블", "팬클럽"],
    "판매·차트": ["예판", "예약", "판매처", "특전", "포카", "셀카", "미공포", "굿즈", "재고", "품절", "배송", "초동", "한터", "써클", "차트",
                "1위", "판매량", "star", "스타버전", "race", "레이스", "러브레터", "love letter", "stayg", "스테이지"],
    "연합·투표": ["연합", "투표", "총공", "스밍", "뮤직웨이브", "mama", "마마", "mma", "aaa", "인기상", "엠넷", "아이돌챔프", "해시태그", "인증"],
}
SEARCH_WORDS = ["스포", "유출", "심의", "트랙", "타이틀", "수록곡", "제목", "가사", "작곡", "티저", "뮤비", "하이라이트", "쇼케이스",
                "음방", "컴백", "발매", "특전", "굿즈", "팝업", "연합", "투표", "공지"]
ALL = sorted({w for ws in KEYWORDS.values() for w in ws}, key=len, reverse=True)


JAR = os.path.join(tempfile.gettempdir(), "dc-cookies.txt")


def get(url):
    return subprocess.run(["curl", "-s", "-m", "25", "-A", UA, "-c", JAR, "-b", JAR, url], capture_output=True, text=True).stdout


def comments(no, page_html, limit=40):
    """Comments come from a separate POST that needs the page's e_s_n_o token and cookies."""
    tok = re.search(r'id="e_s_n_o"[^>]*value="([^"]+)"', page_html)
    if not tok:
        return []
    ref = f"{BASE}/view/?id=isekaidol&no={no}"
    out = []
    for page in (1, 2):
        data = (f"id=isekaidol&no={no}&cmt_id=isekaidol&cmt_no={no}&focus_cno=&focus_pno=&e_s_n_o={tok.group(1)}"
                f"&comment_page={page}&sort=&prevCnt=&board_type=&_GALLTYPE_=MI")
        r = subprocess.run(["curl", "-s", "-m", "25", "-A", UA, "-c", JAR, "-b", JAR, "-X", "POST",
                            "-H", "X-Requested-With: XMLHttpRequest", "-H", f"Referer: {ref}", "-H", "Origin: https://gall.dcinside.com",
                            "--data", data, "https://gall.dcinside.com/board/comment/"], capture_output=True, text=True).stdout
        try:
            d = json.loads(r)
        except ValueError:
            break
        rows = d.get("comments") or []
        for c in rows:
            memo = html.unescape(re.sub(r"<[^>]+>", " ", c.get("memo") or "")).strip()
            memo = re.sub(r"\s+", " ", memo)
            if not c.get("reg_date") or not memo or c.get("del_yn") == "Y":
                continue  # ads and deleted comments
            out.append(f"   - {c.get('reg_date')} {memo[:160]}")
        if len(out) >= limit or len(rows) < 50:
            break
        time.sleep(0.4)
    return out[:limit]


def since():
    return (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9) - datetime.timedelta(days=2)).strftime("%Y-%m-%d")


def rows_of(page_html):
    out = []
    for r in re.findall(r'<tr class="ub-content us-post".*?</tr>', page_html, re.S):
        no = re.search(r'data-no="(\d+)"', r)
        ti = re.search(r'<a[^>]*href="/mini/board/view/[^"]*"[^>]*>(.*?)</a>', r, re.S)
        d = re.search(r'gall_date" title="([^"]+)', r)
        rec = re.search(r'gall_recommend">(\d+)', r)
        rep = re.search(r'reply_num">\[(\d+)', r)
        if no and ti and d:
            out.append({"no": int(no.group(1)), "date": d.group(1), "title": html.unescape(re.sub(r"<[^>]+>", "", ti.group(1))).strip(),
                        "rec": int(rec.group(1)) if rec else 0, "rep": int(rep.group(1)) if rep else 0})
    return out


def groups_for(title):
    t = title.lower()
    return [g for g, ws in KEYWORDS.items() if any(w in t for w in ws)]


def scan():
    cut = since()
    seen = {}
    sources = [f"{BASE}/lists/?id=isekaidol&page={p}" for p in range(1, 9)]
    sources += [f"{BASE}/lists/?id=isekaidol&exception_mode=recommend&page={p}" for p in (1, 2)]
    sources += [f"{BASE}/lists/?id=isekaidol&s_type=search_subject_memo&s_keyword={urllib.parse.quote(w)}" for w in SEARCH_WORDS]
    for url in sources:
        for r in rows_of(get(url)):
            if r["date"][:10] >= cut:
                seen[r["no"]] = r
        time.sleep(0.4)
    hits = [r for r in seen.values() if groups_for(r["title"]) and not r["title"].startswith("[SOOP 알림]")]
    hits.sort(key=lambda r: (r["rec"] * 3 + r["rep"], r["no"]), reverse=True)
    print(f" 최근 2일 글 {len(seen)}개 중 단서 키워드가 있는 글 {len(hits)}개 (추천·댓글 많은 순, 최대 60개)")
    for r in hits[:60]:
        print(f"  {r['no']} {r['date'][5:16]} 추천{r['rec']} 댓글{r['rep']} [{'·'.join(groups_for(r['title']))}] {r['title'][:70]}")


def search(words):
    cut = since()
    for kw in words:
        rows = [r for r in rows_of(get(f"{BASE}/lists/?id=isekaidol&s_type=search_subject_memo&s_keyword={urllib.parse.quote(kw)}")) if r["date"][:10] >= cut]
        print(f" [{kw}] {len(rows)}건")
        for r in rows[:8]:
            print(f"  {r['no']} {r['date']} {r['title'][:80]}")
        time.sleep(0.4)


def read(nos, with_comments=True):
    for no in nos:
        t = get(f"{BASE}/view/?id=isekaidol&no={no}")
        ti = re.search(r'<span class="title_subject">(.*?)</span>', t, re.S)
        d = re.search(r'<span class="gall_date" title="([^"]+)', t)
        b = re.search(r'<div class="write_div"[^>]*>(.*?)if\(window.OutLink', t, re.S)
        x = b.group(1) if b else ""
        links = re.findall(r'href="(https?://[^"]+)"', x)
        imgs = re.findall(r'<img[^>]+src="(https?://[^"]+)"', x)
        x = re.sub(r"<br\s*/?>|</p>|</div>", "\n", x)
        x = re.sub(r"<[^>]+>", "", x)
        x = re.sub(r"\n\s*\n+", "\n", html.unescape(x)).strip()
        print(f"===== {no} {d.group(1) if d else ''} {html.unescape(ti.group(1)) if ti else ''}")
        print(x[:2000])
        if links:
            print("links:", " ".join(links[:8]))
        if imgs:
            print("images:", len(imgs))
        if with_comments:
            cs = comments(no, t)
            print(f"댓글 {len(cs)}개" + (":" if cs else ""))
            print("\n".join(cs))
        time.sleep(0.4)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["--scan"]:
        scan()
    elif a[:1] == ["--search"]:
        search(a[1:])
    else:
        read([x for x in a if x != "--no-comments"], "--no-comments" not in a)
