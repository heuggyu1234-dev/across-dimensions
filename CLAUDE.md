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
5. claude.ai 페이지도 맞추려면 Artifact 도구 publish, `url`은 위 아티팩트 주소, `file_path`는 `dev/across-dimensions.html` (files·capabilities·icon은 넘기지 않음). 아티팩트 도구가 없는 환경이면 건너뛰고 사용자에게 알린다.

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
- claude.ai 클라우드 예약 작업 "이세돌 Across Dimensions 매일 소식"(https://claude.ai/code/routines/trig_01Pnr4rHjsaZezNR5iAG5MWT)이 매일 08:10 KST에 돈다. PC가 꺼져 있어도 된다. 지침 원본은 `dev/cloud-daily-news.md`. 이 저장소를 받아 스냅샷을 고치고 빌드한 뒤 `main`에 푸시한다.
- 예전 PC 예약 작업(`across-dimensions-daily-news`)은 겹치지 않게 꺼 두었다.
- 클라우드에서는 claude.ai 아티팩트 DB·publish 도구가 없을 수 있다. 그때는 공개 사이트(스냅샷)만 갱신하고, claude.ai 페이지는 PC에서 다음에 작업할 때 맞춘다.
- 어느 기기에서 작업하든 시작할 때 `git pull origin main`, 끝에 꼭 `git push origin main`.

## 남은 일 (2026-10-18 기준)
- 예약 판매가 열리면(10/19 15:00 KST) 판매처 링크와 특전 정보를 찾는다. 공식 Berriz 공지 https://berriz.in/ko/isegyeidol/notice/2596 에 판매처 주소가 추가될 예정. 찾은 내용은 **사이트에 넣기 전에 사용자에게 먼저 보여 주고**, 허락받으면 links(group "store")와 스냅샷에 넣는다.
