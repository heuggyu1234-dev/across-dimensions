const fs = require("fs");
const [src, out] = process.argv.slice(2);
const html = fs.readFileSync(src, "utf8");
const cut = html.indexOf("</style>") + "</style>".length;
const head = html.slice(0, cut).replace(/<meta name="claude:viewport-fit-sides"[^>]*>\n?/, "");
const body = html.slice(cut);
const doc = `<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="이세계아이돌 미니 2집 Across Dimensions의 버전 구성, 공개 일정, 굿즈 올클 가이드, 최신 소식을 모은 비공식 팬 페이지.">
<meta property="og:title" content="Across Dimensions 팬 트래커">
<meta property="og:description" content="이세계아이돌 미니 2집 버전, 일정, 굿즈 가이드, 최신 소식">
<meta property="og:image" content="cover.webp">
<meta property="og:type" content="website">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>
${head}
</head>
<body>${body}
</body>
</html>
`;
fs.writeFileSync(out, doc);
console.log("built", out, doc.length, "bytes");
