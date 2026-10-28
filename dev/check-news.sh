#!/usr/bin/env bash
# Prints the latest posts from the sources the daily update needs, as plain text.
# Web pages for X and Berriz don't render for bots (X returns 402, Berriz is empty),
# so this reads their data endpoints directly.
#   bash dev/check-news.sh
set -u
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36'

fetch() { # url -> stdout, retries because fxtwitter sometimes answers empty
  local out=""
  for i in 1 2 3 4; do
    out=$(curl -s -m 40 -A "$UA" "$1")
    [ -n "$out" ] && break
    sleep 4
  done
  printf '%s' "$out"
}

x_profile() { # $1 = X handle
  echo "== X @$1 (최근 글, 사진 원본 주소 포함)"
  fetch "https://api.fxtwitter.com/2/profile/$1/statuses" | python3 -I -c '
import json, sys
try:
    rows = json.load(sys.stdin).get("results") or []
except Exception as e:
    print("  (읽기 실패:", e, ")"); rows = []
if not rows:
    print("  (비어 있음: 잠시 뒤 다시 실행하거나, 다른 계정 결과에 같이 나온 글을 본다)")
for r in rows[:10]:
    m = r.get("media") or {}
    print(r.get("created_at"), r.get("url"))
    print("   ", (r.get("text") or "")[:220].replace("\n", " | "))
    for p in m.get("photos") or []:
        print("    photo", p.get("url"), p.get("width"), "x", p.get("height"))
    for v in m.get("videos") or []:
        print("    video", v.get("url"))
'
}

x_profile isegyeidol_ofcl
x_profile isegyechart

echo "== Berriz 공지 (공지 주소: https://berriz.in/ko/isegyeidol/notice/<번호>)"
fetch "https://svc-api.berriz.in/service/v1/community/40/notices?pageSize=8&languageCode=ko" | python3 -I -c '
import json, re, sys
s = sys.stdin.read()
for m in re.finditer(r"\"communityNoticeId\":(\d+).*?\"title\":\"(.*?)\"", s):
    print(m.group(1), m.group(2))
'
echo "   본문 읽기: curl -s \"https://svc-api.berriz.in/service/v1/community/40/notices/<번호>?languageCode=ko\""

echo "== Berriz에 미러된 공식 X 글"
fetch "https://svc-api.berriz.in/service/v1/community/main/sns/40?languageCode=ko" | python3 -I -c '
import json, sys
try:
    rows = json.load(sys.stdin)["data"]["communitySnsContents"]
except Exception:
    rows = []
for c in rows[:6]:
    print(c.get("snsPublishedAt"), c.get("snsOutLinkUrl"), (c.get("snsText") or "")[:120].replace("\n", " "))
'

echo "== 공식 유튜브"
fetch "https://www.youtube.com/feeds/videos.xml?channel_id=UCmblbE_WxTaFWcMEGFJ_97w" | python3 -I -c '
import re, sys
s = sys.stdin.read()
for vid, title, pub in re.findall(r"<yt:videoId>([^<]+)</yt:videoId>.*?<title>([^<]+)</title>.*?<published>([^<]+)</published>", s, re.S)[:5]:
    print(pub[:10], "https://www.youtube.com/watch?v=" + vid, title)
'

echo "== KBS 가요심의 (매주 수요일 오전, 이세계아이돌 곡이 있으면 표시)"
fetch "https://cfpbbsapi.kbs.co.kr/board/v1/list?bbs_id=X2017-0031-04-699231&page=1&page_size=30&kbs_board_auth=0" | python3 -I -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    d = {}
posts = []
def walk(o):
    if isinstance(o, dict):
        if o.get("post_header") == "가요심의" and o.get("id"):
            posts.append((o["id"], o.get("post_title")))
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
walk(d)
for pid, title in posts[:2]:
    print(pid, title)
' | while read -r pid title; do
  echo "  $pid $title"
  fetch "https://cfpbbsapi.kbs.co.kr/board/v1/read_post?bbs_id=X2017-0031-04-699231&id=$pid&post_no=$pid&kbs_board_auth=0" | python3 -I -c '
import json, sys, subprocess, tempfile, os
d = json.load(sys.stdin)
pf = d.get("post_file") or []
pf = json.loads(pf) if isinstance(pf, str) else pf
for f in pf:
    url = (f.get("stored_file_path") or "") + (f.get("file_name") or "")
    if not url.endswith(".xlsx"):
        continue
    path = os.path.join(tempfile.mkdtemp(), "review.xlsx")
    subprocess.run(["curl", "-s", "-m", "60", "-o", path, url])
    try:
        import openpyxl
    except ImportError:
        print("    (openpyxl 없음) 엑셀:", url); continue
    ws = openpyxl.load_workbook(path, read_only=True).worksheets[0]
    hit = False
    for row in ws.iter_rows(values_only=True):
        cells = ["" if c is None else str(c).replace("﻿", "").strip() for c in row[:6]]
        if "이세계아이돌" in cells:
            hit = True
            print("    ", " | ".join(cells))
    if not hit:
        print("    이세계아이돌 곡 없음")
'
done
