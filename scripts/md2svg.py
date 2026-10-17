import re, sys, html, textwrap, os

FS, LH, PAD = 15, 22, 24
LAYOUT = "side"   # "side" = art left, text right | "stacked" = art on top, text below

def render_text(md, x0, width, y0):
    chars = int(width / (FS * 0.55))
    y, out = y0, []
    for block in md.strip().split("\n\n"):
        block = block.strip()
        if block.startswith("#"):
            level = len(block) - len(block.lstrip("#"))
            size = {1: 26, 2: 21, 3: 17}.get(level, 16)
            y += size
            out.append(f'<text x="{x0}" y="{y}" class="h" font-size="{size}">'
                       f'{html.escape(block.lstrip("# ").strip())}</text>')
            y += 14
            continue
        for line in block.split("\n"):
            bullet = line.lstrip().startswith(("- ", "* "))
            text = re.sub(r"[*_`]", "", line.lstrip().lstrip("-* ").strip())
            x = x0 + (16 if bullet else 0)
            for i, chunk in enumerate(textwrap.wrap(text, chars - (3 if bullet else 0))):
                y += LH
                if bullet and i == 0:
                    out.append(f'<text x="{x0}" y="{y}" class="t">•</text>')
                out.append(f'<text x="{x}" y="{y}" class="t">{html.escape(chunk)}</text>')
        y += 10
    return out, y

def render_art(art, x0, y0, fs):
    lh = fs * 1.2
    lines = textwrap.dedent(art).rstrip().split("\n")
    out = [f'<text class="a" font-size="{fs}" xml:space="preserve">']
    for i, l in enumerate(lines):
        out.append(f'<tspan x="{x0:.1f}" y="{y0 + (i + 1) * lh:.1f}">{html.escape(l)}</tspan>')
    out.append("</text>")
    return out, y0 + len(lines) * lh, max(len(l) for l in lines)

def render(md, art=None):
    out = []
    if art and LAYOUT == "side":
        W, afs = 800, 7
        art_w = max(len(l) for l in textwrap.dedent(art).split("\n")) * afs * 0.6
        a, a_end, _ = render_art(art, PAD, PAD, afs)
        tx = PAD + art_w + 32
        t, t_end = render_text(md, tx, W - PAD - tx, PAD + 10)
        out += a + t
        H = max(a_end, t_end) + PAD
    elif art:
        W, afs = 600, 9
        cols = max(len(l) for l in textwrap.dedent(art).split("\n"))
        art_w = cols * afs * 0.6
        a, a_end, _ = render_art(art, (W - art_w) / 2, PAD, afs)
        t, t_end = render_text(md, PAD, W - 2 * PAD, a_end + 16)
        out += a + t
        H = t_end + PAD
    else:
        W = 600
        t, t_end = render_text(md, PAD, W - 2 * PAD, PAD)
        out += t
        H = t_end + PAD

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H:.0f}" role="img">
<style>
  text {{ font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; }}
  .t {{ font-size: {FS}px; fill: #1f2328; }}
  .h {{ font-weight: 600; fill: #1f2328; }}
  .a {{ font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace; fill: #1f2328; white-space: pre; }}
  @media (prefers-color-scheme: dark) {{ .t, .h, .a {{ fill: #e6edf3; }} }}
</style>
{chr(10).join(out)}
</svg>'''

if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    art_path = os.path.splitext(src)[0] + ".txt"
    art = open(art_path).read() if os.path.exists(art_path) else None
    open(dst, "w").write(render(open(src).read(), art))