#!/usr/bin/env python3
"""Render the demo cards from tools/demos.json into index.html.

Each demo is one VideoOdyssey question answered by the deployed LEAP system
(outputs/eval/block_scan/outline_qcond_anslora/videoodyssey/qcond_final.jsonl in
the research repo) and by the benchmark's official 64-frame recipe on the same
backbone (outputs/eval/vo_official64/full/predictions.jsonl). The clips under
static/videos/ are cut from the retained windows only; nothing else from the
recording is shipped.

Usage: python3 tools/build_demos.py   # rewrites the block between the markers
"""
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEMOS = json.loads((ROOT / "tools" / "demos.json").read_text())
INDEX = ROOT / "index.html"
START = "<!-- demos:start -->"
END = "<!-- demos:end -->"

RED = "#E8645A"
RED_FAINT = "#F8D3CF"
GOLD = "#F2B134"
GRID = "#C9D2DE"


def hms(t):
    t = int(round(t))
    h, m, s = t // 3600, (t % 3600) // 60, t % 60
    return f"{h:d}:{m:02d}:{s:02d}"


def dur_label(t):
    h, m = int(t // 3600), int((t % 3600) // 60)
    return f"{h} h {m:02d} min" if h else f"{m} min"


def timeline_svg(d):
    W, H = 1000.0, 90.0
    x0, x1, y_bar, h_bar = 8.0, 992.0, 30.0, 18.0
    dur = d["duration"]
    sx = lambda t: x0 + (x1 - x0) * t / dur
    parts = [f'<svg class="timeline" viewBox="0 0 {W:g} {H:g}" preserveAspectRatio="none" role="img" '
             f'aria-label="Timeline of the {dur_label(dur)} recording with the retained windows">']
    # whole recording
    parts.append(f'<rect x="{x0}" y="{y_bar}" width="{x1 - x0}" height="{h_bar}" fill="#EEF2F7" stroke="{GRID}" stroke-width="1"/>')
    # retained blocks (faint)
    bl = d["block_len"]
    for b in d["top_blocks"]:
        s, e = b * bl, min((b + 1) * bl, dur)
        parts.append(f'<rect x="{sx(s):.2f}" y="{y_bar}" width="{sx(e) - sx(s):.2f}" height="{h_bar}" fill="{RED_FAINT}"/>')
    # block grid ticks
    for b in range(1, d["n_blocks"]):
        x = sx(b * bl)
        parts.append(f'<line x1="{x:.2f}" y1="{y_bar}" x2="{x:.2f}" y2="{y_bar + h_bar}" stroke="{GRID}" stroke-width="1"/>')
    # retained windows (solid), labelled under the bar at the first retained block
    for s, e in d["windows"]:
        w = max(sx(e) - sx(s), 2.0)
        parts.append(f'<rect x="{sx(s):.2f}" y="{y_bar}" width="{w:.2f}" height="{h_bar}" fill="{RED}"/>')
    fb = min(d["top_blocks"])
    fx = sx(fb * bl) + 2
    fa = "start"
    if fx > W - 200:
        fx, fa = sx(min((fb + 1) * bl, dur)) - 2, "end"
    parts.append(f'<text x="{fx:.2f}" y="{H - 2}" font-size="12" fill="#b4443a" text-anchor="{fa}">windows LEAP retained (red), blocks it kept (tinted)</text>')
    # evidence span (gold, above the bar)
    g0, g1 = d["gt"]
    gw = max(sx(g1) - sx(g0), 3.0)
    parts.append(f'<rect x="{sx(g0):.2f}" y="{y_bar - 9}" width="{gw:.2f}" height="6" fill="{GOLD}" rx="1"/>')
    # hour labels
    hours = int(dur // 3600)
    xe = sx(dur)
    for hh in range(hours + 1):
        x = sx(hh * 3600)
        if hh and xe - x < 70:  # too close to the end label
            continue
        anchor = "start" if hh == 0 else "middle"
        parts.append(f'<line x1="{x:.2f}" y1="{y_bar + h_bar}" x2="{x:.2f}" y2="{y_bar + h_bar + 5}" stroke="#6b7280" stroke-width="1"/>')
        parts.append(f'<text x="{x:.2f}" y="{y_bar + h_bar + 18}" font-size="12" fill="#6b7280" text-anchor="{anchor}">{hh} h</text>')
    parts.append(f'<line x1="{xe:.2f}" y1="{y_bar + h_bar}" x2="{xe:.2f}" y2="{y_bar + h_bar + 5}" stroke="#6b7280" stroke-width="1"/>')
    parts.append(f'<text x="{xe:.2f}" y="{y_bar + h_bar + 18}" font-size="12" fill="#6b7280" text-anchor="end">{hms(dur)}</text>')
    # evidence label above the gold mark
    lx = sx((g0 + g1) / 2)
    la = "middle"
    if lx < 120:
        lx, la = sx(g0), "start"
    elif lx > W - 120:
        lx, la = sx(g1), "end"
    parts.append(f'<text x="{lx:.2f}" y="{y_bar - 13}" font-size="12" fill="#92400e" text-anchor="{la}">ground-truth evidence {hms(g0)}&#8211;{hms(g1)} (benchmark annotation)</text>')
    parts.append("</svg>")
    return "".join(parts)


def video_tile(src, poster, label, sub, big):
    cls = "clip clip-main" if big else "clip"
    return (f'<figure class="{cls}">'
            f'<video controls playsinline preload="none" poster="{poster}"><source src="{src}" type="video/mp4"></video>'
            f'<figcaption><span class="clip-label">{html.escape(label)}</span><span class="clip-sub">{html.escape(sub)}</span></figcaption>'
            f'</figure>')


def card(d):
    k = d["key"]
    opts = []
    for o in d["options"]:
        letter = o[0]
        cls = []
        mark = ""
        if letter == d["answer"]:
            cls.append("opt-leap")
            mark += ' <span class="tag tag-leap">LEAP &#10003;</span>'
        if letter == d["base_pred"]:
            cls.append("opt-base")
            mark += ' <span class="tag tag-base">64-frame recipe &#10007;</span>'
        opts.append(f'<li class="{" ".join(cls)}">{html.escape(o)}{mark}</li>')
    ev0, ev1 = d["ev_clip"]
    ev_block = next(b for b in d["top_blocks"] if b * d["block_len"] <= ev0 < (b + 1) * d["block_len"])
    tiles = [video_tile(f"static/videos/{k}_ev.mp4", f"static/videos/{k}_ev.jpg",
                        f"LEAP retained this window, {hms(ev0)}", f"block {ev_block + 1} of {d['n_blocks']}, covers the ground-truth span", True)]
    for i, (p0, p1) in enumerate(d["peeks"], 1):
        pb = int(p0 // d["block_len"])
        tiles.append(video_tile(f"static/videos/{k}_p{i}.mp4", f"static/videos/{k}_p{i}.jpg",
                                f"LEAP also retained, {hms(p0)}", f"block {pb + 1} of {d['n_blocks']}", False))
    qtype = " / ".join(d["qtype"])
    return f'''
<div class="demo-card">
  <div class="demo-head">
    <span class="demo-dur">{dur_label(d["duration"])}</span>
    <span class="demo-type">{html.escape(qtype)} &middot; {d["n_blocks"]} blocks &middot; {len(d["windows"])} windows retained</span>
  </div>
  <p class="demo-q">{html.escape(d["question"])}</p>
  {timeline_svg(d)}
  <div class="demo-clips">
    {"".join(tiles)}
  </div>
  <ul class="demo-opts">
    {"".join(opts)}
  </ul>
</div>'''


def main():
    body = "\n".join(card(d) for d in DEMOS)
    text = INDEX.read_text()
    a, b = text.index(START) + len(START), text.index(END)
    INDEX.write_text(text[:a] + "\n" + body + "\n" + text[b:])
    print(f"wrote {len(DEMOS)} demo cards into {INDEX.name}")


if __name__ == "__main__":
    main()
