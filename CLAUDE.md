# Across Dimensions 팬 트래커

이세계아이돌(ISEGYE IDOL) 미니 2집 [Across Dimensions]의 비공식 팬 사이트. 사용자와는 한국어로 대화한다.

## 주소
- 공개 사이트: https://mini2isegye.hehezone.com (Cloudflare Pages 프로젝트 `mini2isegye`가 이 저장소 `main`을 자동 배포, 1~2분. 예전 주소 https://mini2isegye.pages.dev 도 같은 사이트)
- 도메인 `hehezone.com`은 사용자의 Cloudflare 계정에 있다. 다른 사이트(예: 짭난투)도 서브도메인으로 붙일 수 있다.
- claude.ai 페이지(같은 내용, 로그인 사용자는 실시간 소식 DB를 봄): https://claude.ai/artifact/GqUmUotJNZrRRVMBw8cttR
- GitHub Pages는 꺼 둠. 다시 켜지 않는다.

## 파일 구조
- `dev/across-dimensions.html`: **원본**. 여기만 고친다. claude.ai 아티팩트 형식(문서 뼈대 없이 `<title>`·`<style>`부터 시작).
- `dev/build-site.js`: 원본을 완전한 HTML 문서로 감싸 `index.html`을 만든다.
  `node dev/build-site.js dev/across-dimensions.html index.html`
- `dev/serve.js`: 로컬 미리보기 서버. `node dev/serve.js 4173` 후 http://localhost:4173
- `index.html`: 빌드 결과물. 직접 고치지 않는다.
- `cover.webp`(앨범 표지), `ver-star.jpg`·`ver-race.jpg`·`ver-letter.jpg`·`ver-stayg.jpg`(공식 버전 상세 이미지, ⓒ 패러블엔터테인먼트)
- `_redirects`: `dev/`와 이 파일이 공개 사이트에서 보이지 않게 막음.

## 고치고 올리는 순서
1. `dev/across-dimensions.html` 수정
2. 스크립트 문법 확인: `awk '/<script>/{f=1;next}/<\/script>/{f=0}f' dev/across-dimensions.html > /tmp/c.js && node --check /tmp/c.js`
3. `node dev/build-site.js dev/across-dimensions.html index.html`
4. 커밋 후 `git push origin main` → mini2isegye.hehezone.com에 자동 반영
5. claude.ai 페이지도 맞추려면 Artifact 도구 publish, `url`은 위 아티팩트 주소, `file_path`는 `dev/across-dimensions.html` (capabilities·icon은 넘기지 않음). **새로 생긴 이미지(concept/·news/·union-*.jpg 등)가 있으면 꼭 `files`에 {"concept/파일.webp": "concept/파일.webp"}처럼 전부 넣는다.** 안 넣으면 claude.ai 페이지에서 사진이 깨진다. 아티팩트 도구가 없는 환경이면 건너뛰고 사용자에게 알린다.

## 소식 데이터
- 소식(news)과 바로가기(links)는 claude.ai 아티팩트의 공유 DB(`news`, `links` 컬렉션)에 있다.
- 로그인하지 않은 방문자와 공개 사이트는 DB를 못 읽으므로, 원본 안 `<script type="application/json" id="snapshot">` 의 JSON 스냅샷을 보여 준다. 소식을 바꾸면 이 JSON도 같이 바꾸고(updated 날짜 포함) 빌드·푸시한다.
- 소식 필드: id, title, source, url, date(YYYY-MM-DD), kind(official|press|fan), status(confirmed|unverified), summary, addedAt
- 링크 필드: label, url, group(store|media|official), note, order

## 지켜야 할 것
- 이번 앨범 전용 정보와 주소만 넣는다. 나무위키 등 위키, 아티스트 일반 페이지, 이전 앨범 소식은 넣지 않는다.
- 실존 인물에 대한 확인되지 않은 루머는 넣지 않는다.
- 디자인은 깔끔하게, 글은 짧게. 사용자는 정보 나열보다 보기 쉬운 화면을 원한다. 휴대폰(375px)에서도 꼭 확인한다.
- 공식 이미지에는 출처(ⓒ 패러블엔터테인먼트)를 단다.

## 앨범 기본 정보
- 예약 판매 2026-10-19(월) 15:00 KST, 발매 2026-11-09(월) 18:00 KST, 유통 KT지니뮤직
- 버전: STAR, RACE, LOVE LETTER(6색), STAYG(NFC)
- 공식 스케줄러: 10/20~23 STAR 컨셉 포토(단체·유닛·개인1·개인2), 10/26~29 RACE 컨셉 포토, 10/30 트랙리스트, 11/02 하이라이트 메들리, 11/04 MV 티저, 11/06 발매 전 스포일러, 11/09 MV와 앨범 발매

## 자동 업데이트
- **매일 소식 작업을 하는 에이전트는 예약 작업 지침의 WebSearch 단계보다 먼저 `bash dev/check-news.sh`를 실행하고 그 결과를 주된 근거로 쓴다.** 최신 지침 전체는 `dev/cloud-daily-news.md`에 있다. 예약 작업에 저장된 지침이 이 파일과 다르면 이 파일을 따른다.
- claude.ai 클라우드 예약 작업 "이세돌 Across Dimensions 매일 소식"(https://claude.ai/code/routines/trig_01Pnr4rHjsaZezNR5iAG5MWT)이 매일 10:07·18:07·21:07 KST에 돈다(공식 사진·공지는 보통 18:00, 연합 발표는 저녁 8시 전후). 사용자 대화에서 도는 커뮤 단서 확인은 09:37·15:37·20:37. PC가 꺼져 있어도 된다. 지침 원본은 `dev/cloud-daily-news.md`. 이 저장소를 받아 스냅샷을 고치고 빌드한 뒤 `main`에 푸시한다.
- `bash dev/check-news.sh`의 출력은 grep·head로 자르지 말고 `bash dev/check-news.sh > /tmp/news.txt 2>&1` 로 저장한 뒤 파일 전체를 Read로 읽는다(Berriz·유튜브·KBS 부분을 놓치지 않게).
- 소식 확인은 `bash dev/check-news.sh`(공식 X·Berriz·유튜브·KBS 가요심의를 데이터 주소로 직접 읽음). 공식 X와 Berriz 웹페이지는 봇에게 막히거나 비어 보여서 WebFetch로는 못 읽는다.
- 커뮤니티(디시 이세계아이돌 갤러리) 스포·유출 단서는 `python3 -I dev/read-dc.py --scan`(최근 2일 최신 8쪽·개념글·키워드 검색을 넓은 키워드 목록으로 걸러 추천·댓글 순으로 보여 줌, check-news.sh에 포함), 글 읽기는 `python3 -I dev/read-dc.py <글번호>`(본문과 댓글 최대 40개). 단서만 쓰고 원본을 찾아 확인한다. 커뮤니티 주소는 사이트에 넣지 않는다.
- **커뮤니티발 정보(디시·왁물원·펨코·X 팬 계정)는 사이트에 바로 넣지 않는다.** 사용자와의 대화에 먼저 올리고(묻지 않아도 먼저 알린다) 사용자가 허락한 것만 넣는다. 이미 보고한 단서와 허락 여부는 `dev/community-leads.md`에 적어 둔다. 커뮤 글이 가리킨 공식 원본(KBS 심의, Berriz·공식 X, 음원 사이트, 기사)을 직접 확인했다면 그 원본은 공식 소식으로 넣어도 된다.
- **연합(이세계차트 발표)은 묻지 않고 바로 넣는다.**
- 왁물원(네이버 카페 steamindiegame, cafeId 27842958) 단서는 `python3 -I dev/read-cafe.py --scan`, 글 읽기는 `python3 -I dev/read-cafe.py <글번호>`. 펨코는 봇 차단이라 WebSearch(allowed_domains fmkorea.com)로만 찾는다. X는 검색이 막혀 check-news.sh에 적어 둔 계정 글만 읽는다.
- 연합(이세계차트 @isegyechart 발표)은 `U_TASKS`·`U_RETURN`·`PARTNERS`(dev/across-dimensions.html) 를 고쳐 반영한다. 자세한 방법은 `dev/cloud-daily-news.md` 2-2.
- 공식 컨셉 포토 넣기는 `python3 -I dev/add-photos.py` (유닛·개인은 소식 페이지 사진 칸, 단체는 `--group`으로 홈).
- 예전 PC 예약 작업(`across-dimensions-daily-news`)은 겹치지 않게 꺼 두었다.
- 클라우드에서는 claude.ai 아티팩트 DB·publish 도구가 없을 수 있다. 그때는 공개 사이트(스냅샷)만 갱신하고, claude.ai 페이지는 PC에서 다음에 작업할 때 맞춘다.
- 어느 기기에서 작업하든 시작할 때 `git pull origin main`, 끝에 꼭 `git push origin main`.

## 남은 일 (2026-10-18 기준)
- 예약 판매가 열리면(10/19 15:00 KST) 판매처 링크와 특전 정보를 찾는다. 공식 Berriz 공지 https://berriz.in/ko/isegyeidol/notice/2596 에 판매처 주소가 추가될 예정. 찾은 내용은 **사이트에 넣기 전에 사용자에게 먼저 보여 주고**, 허락받으면 links(group "store")와 스냅샷에 넣는다.
