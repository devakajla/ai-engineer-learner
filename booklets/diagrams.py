#!/usr/bin/env python3
"""Turn small diagram blocks in Markdown into inline SVG.

    @@ flow | Figure 1.1: caption
    Client|phone;browser|blue -request-> Server|your code|green <-> Database|data|yellow
    @@ end

Kinds: flow (horizontal arrows), vflow (vertical arrows), stack (vertical, no arrows),
grid N (N boxes per row). Box = Title|line1;line2|color. Colors: blue green yellow red purple gray.
Arrow: `->` one way, `-label->` one way with a label, `<->` both ways, `<-label->` both ways with a label.
"""
import html
import re
import sys

COL = {
    "blue": ("#e8f1ff", "#3a86ff"), "green": ("#e8f6ee", "#1b9e5a"),
    "yellow": ("#fff7e6", "#fca311"), "red": ("#fdecec", "#d64545"),
    "purple": ("#eef0ff", "#5a5fd6"), "gray": ("#f1f3f6", "#8a93a6"),
}
FONT = 'font-family="Helvetica, Arial, sans-serif"'


def esc(s):
    return html.escape(s, quote=False)


def parse_box(tok):
    p = [x.strip() for x in tok.split("|")]
    sub = [s.strip() for s in p[1].split(";")] if len(p) > 1 and p[1] else []
    return p[0], sub, (p[2] if len(p) > 2 and p[2] in COL else "blue")


def box_h(sub):
    return max(52, 20 + 16 * len(sub) + 22)


def box_w(items, minimum):
    longest = max(max([len(t)] + [len(s) for s in sub]) for t, sub, _ in items)
    return max(minimum, int(longest * 7.6) + 28)


def draw_box(x, y, w, h, title, sub, color):
    fill, stroke = COL[color]
    total = 20 + 16 * len(sub)
    top = y + (h - total) / 2
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{fill}" stroke="{stroke}" stroke-width="2"/>',
           f'<text x="{x + w / 2}" y="{top + 15}" text-anchor="middle" font-size="14" font-weight="bold" fill="#14213d">{esc(title)}</text>']
    for i, s in enumerate(sub):
        out.append(f'<text x="{x + w / 2}" y="{top + 32 + 16 * i}" text-anchor="middle" font-size="12" fill="#4a5468">{esc(s)}</text>')
    return "".join(out)


def parse_items(line):
    parts = re.split(r"\s+(<?)-(.*?)>\s+", line.strip())
    boxes = [parse_box(parts[0])]
    arrows = []
    for i in range(1, len(parts), 3):
        arrows.append((parts[i] == "<", parts[i + 1].rstrip("-").strip()))
        boxes.append(parse_box(parts[i + 2]))
    return boxes, arrows


def arrow_line(x1, y1, x2, y2, both):
    start = ' marker-start="url(#m)"' if both else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#14213d" stroke-width="2" marker-end="url(#m)"{start}/>'


DEFS = ('<defs><marker id="m" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto-start-reverse">'
        '<path d="M0,0 L10,4 L0,8 z" fill="#14213d"/></marker></defs>')


def render(kind, cols, caption, lines):
    body, W, H = [], 0, 0
    if kind in ("flow", "vflow"):
        boxes, arrows = parse_items(" ".join(lines))
        if kind == "flow":
            w = box_w(boxes, 140)
            h = max(box_h(s) for _, s, _ in boxes)
            gap = max(80, max([len(a[1]) for a in arrows] + [0]) * 7 + 24)
            W, H = 20 + len(boxes) * w + (len(boxes) - 1) * gap, h + 20
            for i, (t, s, c) in enumerate(boxes):
                x = 10 + i * (w + gap)
                body.append(draw_box(x, 10, w, h, t, s, c))
                if i < len(arrows):
                    both, label = arrows[i]
                    body.append(arrow_line(x + w + 3, 10 + h / 2, x + w + gap - 3, 10 + h / 2, both))
                    if label:
                        body.append(f'<text x="{x + w + gap / 2}" y="{10 + h / 2 - 7}" text-anchor="middle" font-size="12" fill="#14213d">{esc(label)}</text>')
        else:
            w = box_w(boxes, 300)
            gap = 38
            y = 10
            W = w + 20 + 120
            for i, (t, s, c) in enumerate(boxes):
                h = box_h(s)
                body.append(draw_box(10, y, w, h, t, s, c))
                if i < len(arrows):
                    both, label = arrows[i]
                    body.append(arrow_line(10 + w / 2, y + h + 3, 10 + w / 2, y + h + gap - 3, both))
                    if label:
                        body.append(f'<text x="{10 + w / 2 + 10}" y="{y + h + gap / 2 + 4}" font-size="12" fill="#14213d">{esc(label)}</text>')
                y += h + gap
            H = y - gap + 20
    else:
        boxes = [parse_box(l) for l in lines if l.strip()]
        if kind == "stack":
            w = box_w(boxes, 520)
            y = 10
            for t, s, c in boxes:
                h = box_h(s)
                body.append(draw_box(10, y, w, h, t, s, c))
                y += h + 8
            W, H = w + 20, y + 2
        else:
            w = box_w(boxes, 190)
            gap = 14
            rows = [boxes[i:i + cols] for i in range(0, len(boxes), cols)]
            y = 10
            for row in rows:
                h = max(box_h(s) for _, s, _ in row)
                for j, (t, s, c) in enumerate(row):
                    body.append(draw_box(10 + j * (w + gap), y, w, h, t, s, c))
                y += h + gap
            W, H = 20 + cols * w + (cols - 1) * gap, y - gap + 10
    svg = (f'<svg viewBox="0 0 {W} {H}" width="{min(W, 660)}" xmlns="http://www.w3.org/2000/svg" {FONT}>'
           f'{DEFS}{"".join(body)}</svg>')
    return f'<div class="fig">{svg}<div class="cap">{esc(caption)}</div></div>'


def main():
    lines = sys.stdin.read().split("\n")
    out, i = [], 0
    while i < len(lines):
        m = re.match(r"@@\s+(flow|vflow|stack|grid)\s*(\d*)\s*\|\s*(.*)$", lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue
        j = i + 1
        block = []
        while lines[j].strip() != "@@ end":
            block.append(lines[j])
            j += 1
        out.append(render(m.group(1), int(m.group(2) or 3), m.group(3), block))
        i = j + 1
    sys.stdout.write("\n".join(out))


main()
