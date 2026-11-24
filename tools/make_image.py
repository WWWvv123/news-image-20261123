#!/usr/bin/env python3
"""Draw the front page for Monday 23 November 2026.

Everything on the page is drawn by this script with PIL: the masthead,
the headlines, the six verified stories and the market chart. No image
is loaded from disk and no network is used, so two runs produce the
same bytes.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024
MARGIN = 40
RIGHT = W - MARGIN
CONTENT_W = RIGHT - MARGIN

PAPER = (248, 243, 232)
INK = (17, 17, 17)
RED = (155, 28, 28)
BLUE = (31, 78, 121)
LIGHT_BLUE = (205, 222, 238)
GREY = (90, 84, 74)
RULE = (17, 17, 17)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def font(name, size):
    return ImageFont.truetype(str(FONT_DIR / name), size)


SERIF_B = "DejaVuSerif-Bold.ttf"
SERIF = "DejaVuSerif.ttf"
SANS_B = "DejaVuSans-Bold.ttf"
SANS = "DejaVuSans.ttf"


def wrap(draw, text, fnt, max_w):
    """Split text into lines that fit max_w pixels."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=fnt) <= max_w:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def draw_rule(draw, y, x0=MARGIN, x1=RIGHT, width=2):
    draw.line([(x0, y), (x1, y)], fill=RULE, width=width)


def draw_story(draw, x, y, width, max_h, kicker, headline, body,
               head_size=25, body_size=18):
    """Draw one headed story column. Returns the height used."""
    top = y
    kfont = font(SANS_B, 18)
    draw.text((x, y), kicker, font=kfont, fill=RED)
    y += 24
    hfont = font(SERIF_B, head_size)
    hlines = wrap(draw, headline, hfont, width)
    for line in hlines:
        draw.text((x, y), line, font=hfont, fill=INK)
        y += head_size + 6
    y += 5
    bfont = font(SANS, body_size)
    blines = wrap(draw, body, bfont, width)
    for line in blines:
        draw.text((x, y), line, font=bfont, fill=INK)
        y += body_size + 5
    used = y - top
    assert used <= max_h, (
        f"story {kicker!r} needs {used}px, only {max_h}px available")
    return used


def draw_chart(draw, x0, y0, x1, y1):
    """Draw the Nvidia share-price surge chart inside the given box."""
    title = font(SANS_B, 18)
    draw.text((x0, y0), "NVIDIA SHARES", font=title, fill=INK)

    px0, px1 = x0 + 14, x1 - 14
    py0, py1 = y0 + 30, y1 - 18
    # Gridlines.
    for frac in (0.0, 0.5, 1.0):
        gy = py0 + (py1 - py0) * frac
        draw.line([(px0, gy), (px1, gy)], fill=(200, 192, 176), width=1)

    # The line: a flat week, then a steep jump on Monday. Every point
    # stays inside the plot area between py0 and py1.
    pts = [
        (px0, py1 - 6),
        (px0 + 150, py1 - 12),
        (px0 + 300, py1 - 8),
        (px0 + 450, py1 - 20),
        (px0 + 600, py1 - 28),
        (px0 + 700, py1 - 44),
        (px1 - 60, py1 - 54),
        (px1, py1 - 58),
    ]
    # Shaded area under the line.
    area = pts + [(px1, py1), (px0, py1)]
    draw.polygon(area, fill=LIGHT_BLUE)
    draw.line(pts, fill=BLUE, width=4, joint="curve")
    # End dot and the surge label, placed above the line's end.
    ex, ey = pts[-1]
    draw.ellipse([ex - 6, ey - 6, ex + 6, ey + 6], fill=RED)
    label = "+31%"
    lfont = font(SANS_B, 26)
    lx = ex - text_w(draw, label, lfont) - 14
    ly = ey - 40
    draw.text((lx, ly), label, font=lfont, fill=RED)

    axis = font(SANS, 15)
    draw.text((px0, py1 + 5), "LAST WEEK", font=axis, fill=GREY)
    monday = "MONDAY"
    draw.text((px1 - text_w(draw, monday, axis), py1 + 5),
              monday, font=axis, fill=GREY)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # Top double rule.
    draw_rule(draw, 24, width=3)
    draw_rule(draw, 31, width=1)

    # Masthead.
    mfont = font(SERIF_B, 80)
    masthead = "THE DAILY WORLD"
    mw = text_w(draw, masthead, mfont)
    draw.text(((W - mw) / 2, 40), masthead, font=mfont, fill=INK)

    # Dateline.
    draw_rule(draw, 132, width=2)
    dfont = font(SANS_B, 23)
    date = "MONDAY, 23 NOVEMBER 2026"
    draw.text((MARGIN, 142), date, font=dfont, fill=INK)
    right = "WORLD NEWS IN ONE PAGE"
    draw.text((RIGHT - text_w(draw, right, dfont), 142),
              right, font=dfont, fill=INK)

    # Thick rule under the dateline.
    draw_rule(draw, 176, width=5)
    draw_rule(draw, 184, width=1)

    # Kicker above the main headline.
    kfont = font(SANS_B, 21)
    kicker = "MARKETS  \u2022  TECHNOLOGY"
    draw.text(((W - text_w(draw, kicker, kfont)) / 2, 198),
              kicker, font=kfont, fill=RED)

    # Main headline, two lines.
    hfont = font(SERIF_B, 56)
    for i, line in enumerate(["NVIDIA REINSTATES", "HUANG AS CEO"]):
        lw = text_w(draw, line, hfont)
        draw.text(((W - lw) / 2, 226 + i * 62), line,
                  font=hfont, fill=INK)

    # Deck: the facts of the lead story.
    deck = ("Co-founder Jensen Huang returns 11 days after resigning. "
            "Shares surge about 31% as the AI sell-off reverses.")
    dfont2 = font(SANS, 24)
    dlines = wrap(draw, deck, dfont2, 880)
    dy = 358
    for line in dlines:
        lw = text_w(draw, line, dfont2)
        draw.text(((W - lw) / 2, dy), line, font=dfont2, fill=INK)
        dy += 29

    # Market chart.
    draw_chart(draw, MARGIN, 416, RIGHT, 540)

    # Rule above the story grid.
    draw_rule(draw, 548, width=2)

    # Row one: three stories.
    col_w = 298
    gap = 24
    row1_y = 562
    row1_h = 238
    stories_row1 = [
        ("CLIMATE",
         "COP31 ENDS WITH NO DEAL",
         "UN climate talks in Antalya end with no deal on fossil "
         "fuels or finance \u2014 the longest climate conference "
         "in history."),
        ("IRAN \u2013 US",
         "IRAN VOWS TO COUNTER US BLOCKADE",
         "Tehran says it will use all means against the US naval "
         "blockade; a Saturday attack in Bahrain injured two "
         "civilians."),
        ("UKRAINE",
         "KYIV: SEA DRONES HIT SHIPS IN LIBYA",
         "Zelenskyy says Ukrainian sea drones struck two Russian "
         "ships in Benghazi port. A Russian drone strike in Dymer, "
         "near Kyiv, killed at least 11."),
    ]
    for i, (kicker, headline, body) in enumerate(stories_row1):
        x = MARGIN + i * (col_w + gap)
        if i:
            vx = x - gap // 2
            draw.line([(vx, row1_y), (vx, row1_y + row1_h)],
                      fill=(200, 192, 176), width=1)
        draw_story(draw, x, row1_y, col_w, row1_h,
                   kicker, headline, body)

    # Rule between the rows.
    draw_rule(draw, 812, width=1)

    # Row two: two wider stories.
    col2_w = 460
    row2_y = 824
    row2_h = 148
    stories_row2 = [
        ("US POLITICS",
         "DEMOCRATS WIN 258 HOUSE SEATS",
         "Democrats take at least 258 seats \u2014 their largest "
         "majority in the House since 1992."),
        ("BUSINESS",
         "CROWDSTRIKE TO BUY ZSCALER FOR $43.9BN",
         "The all-stock cybersecurity deal, announced Monday, "
         "is worth $43.9 billion."),
    ]
    for i, (kicker, headline, body) in enumerate(stories_row2):
        x = MARGIN + i * (col2_w + gap)
        if i:
            vx = x - gap // 2
            draw.line([(vx, row2_y), (vx, row2_y + row2_h)],
                      fill=(200, 192, 176), width=1)
        draw_story(draw, x, row2_y, col2_w, row2_h,
                   kicker, headline, body,
                   head_size=29, body_size=18)

    # Footer: sources and the date again.
    draw_rule(draw, 982, width=1)
    ffont = font(SANS, 14)
    footer = ("Sources: Reuters \u2022 Just Security \u2022 Algenom "
              "\u2022 OneTurn  \u2014  Monday 23 November 2026")
    fw = text_w(draw, footer, ffont)
    draw.text(((W - fw) / 2, 990), footer, font=ffont, fill=GREY)

    return img


def main():
    out = Path(__file__).resolve().parent.parent / "entry.png"
    img = build()
    img.save(out, format="PNG")
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
