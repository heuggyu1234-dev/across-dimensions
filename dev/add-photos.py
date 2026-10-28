#!/usr/bin/env python3
"""Download official concept photos and put them on the site.

Unit/solo photos go to the top of the photo column on the news page,
group photos (one wide shot) go to the end of the home page "단체 컨셉 포토".

  # two photos per member -> a 3-column grid with names
  python3 -I dev/add-photos.py --caption "RACE ver. 개인 1 (10.28)" --prefix race \
      --member "아이네:ine:URL1,URL2" --member "징버거:jing:URL1,URL2" --member "릴파:lilpa:URL1,URL2"
  # one photo per unit -> a row of 2 or 3
  python3 -I dev/add-photos.py --caption "RACE ver. 유닛 (10.27)" --prefix race-unit \
      --member "아이네 · 징버거 · 릴파:ine-jing-lilpa:URL" --member "주르르 · 고세구 · 비챤:jururu-gosegu-viichan:URL"
  # group photo -> home page
  python3 -I dev/add-photos.py --group --caption "RACE ver. 단체" --date "10.26" --prefix race-group --member "RACE 단체:x:URL"

URLs from X: use the ...jpg?name=orig form (dev/check-news.sh prints them).
Run from the repository root, then build with dev/build-site.js.
"""
import argparse, html, os, subprocess, sys, tempfile

from PIL import Image

SRC = "dev/across-dimensions.html"
CREDIT = "ⓒ 패러블엔터테인먼트"


def fetch(url, dest):
    subprocess.run(["curl", "-sL", "-m", "90", "-o", dest, url], check=True)
    Image.open(dest).verify()


def save(src, name, thumb):
    im = Image.open(src).convert("RGB")
    full = f"concept/{name}.webp"
    im.save(full, quality=82)
    small = None
    if thumb:
        t = im.copy()
        t.thumbnail(thumb)
        small = f"concept/{name}-s.webp"
        t.save(small, quality=82)
    return full, small, im.size


def zoom_button(full, small, alt, size):
    w, h = size
    return (f'<button type="button" class="cp-zoom" data-src="{full}" data-alt="{html.escape(alt)}">'
            f'<img src="{small or full}" alt="{html.escape(alt)}" width="{w}" height="{h}" loading="lazy"></button>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--caption", required=True)
    ap.add_argument("--prefix", required=True, help="file name prefix, e.g. race")
    ap.add_argument("--member", action="append", required=True, help="display name:slug:url[,url]")
    ap.add_argument("--group", action="store_true", help="one wide group photo for the home page")
    ap.add_argument("--date", default="", help="for --group: 공개일 like 10.26")
    a = ap.parse_args()

    s = open(SRC, encoding="utf-8").read()
    tmp = tempfile.mkdtemp()
    members = []
    for m in a.member:
        label, slug, urls = m.split(":", 2)
        members.append((label, slug, [u for u in urls.split(",") if u]))
    os.makedirs("concept", exist_ok=True)

    if a.group:
        label, _, urls = members[0]
        p = os.path.join(tmp, "g.jpg"); fetch(urls[0], p)
        full, _, size = save(p, a.prefix + "-4k", None)
        im = Image.open(full); im.thumbnail((1800, 1800)); im.save(f"concept/{a.prefix}.webp", quality=84)
        alt = f"{a.caption} 컨셉 포토"
        btn = (f'<button type="button" class="cp-zoom" data-src="{full}" data-alt="{html.escape(alt)}">'
               f'<img src="{full}" srcset="concept/{a.prefix}.webp 1800w, {full} {size[0]}w" sizes="(max-width: 92rem) 100vw, 92rem" '
               f'alt="{html.escape(alt)}" width="{size[0]}" height="{size[1]}" loading="lazy"></button>')
        fig = (f'      <figure class="cp">\n        {btn}\n        <figcaption><b>{html.escape(a.caption)}</b>'
               f'<span>{html.escape(a.date)} 공개 · {CREDIT}</span></figcaption>\n      </figure>\n')
        anchor = '    <div class="cp-list">\n'
        i = s.index(anchor); j = s.index('    </div>\n  </section>', i)
        s = s[:j] + fig + s[j:]
    else:
        per = {len(u) for _, _, u in members}
        if per == {2}:
            names = "".join(f'<span class="solo-name">{html.escape(l)}</span>' for l, _, _ in members)
            cells = ""
            for k in (0, 1):
                for label, slug, urls in members:
                    p = os.path.join(tmp, f"{slug}{k}.jpg"); fetch(urls[k], p)
                    full, small, _ = save(p, f"{a.prefix}-{slug}-{k + 1}", (420, 620))
                    w, h = Image.open(small).size
                    cells += zoom_button(full, small, f"{a.caption} 컨셉 포토: {label} {k + 1}", (w, h))
            block = f'<div class="solo-grid" style="margin-top:0">{names}{cells}</div>'
        elif per == {1}:
            items = ""
            for label, slug, urls in members:
                p = os.path.join(tmp, f"{slug}.jpg"); fetch(urls[0], p)
                full, small, _ = save(p, f"{a.prefix}-{slug}", (600, 880))
                w, h = Image.open(small).size
                items += f'<div>{zoom_button(full, small, f"{a.caption} 컨셉 포토: {label}", (w, h))}<span>{html.escape(label)}</span></div>'
            cls = "unit-row unit-2" if len(members) == 2 else "unit-row"
            block = f'<div class="{cls}" style="margin-top:0">{items}</div>'
        else:
            sys.exit("every --member needs the same number of photos (1 or 2)")
        anchor = '<figure class="news-fig">\n'
        i = s.index(anchor) + len(anchor)
        s = (s[:i] + f'          {block}\n          <figcaption>{html.escape(a.caption)} · {CREDIT}</figcaption>\n'
             f'          <div class="fig-gap"></div>\n' + s[i:])

    open(SRC, "w", encoding="utf-8").write(s)
    print("added", a.caption)


if __name__ == "__main__":
    main()
