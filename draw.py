#!/usr/bin/env python3
"""Draw the 20 November 2026 newspaper front page (1024x1024 PNG).

Renders masthead + date + lead story + six news cards + footer band.
Every text block is measured before it is drawn; if a headline or body
does not fit its allotted box the script raises instead of clipping.
Run:  python3 draw.py   (writes entry.png next to this file)
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 40
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

CREAM = (250, 246, 236)
INK = (26, 26, 26)
NAVY = (27, 58, 95)
RED = (178, 34, 34)
GREY = (96, 96, 96)
MIDGREY = (110, 110, 110)
DARKNAVY = (24, 48, 88)
GOLD = (232, 184, 76)
WHITE = (255, 255, 255)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
            if draw.textlength(cur, font=fnt) > max_w:
                raise ValueError(f"single word too wide: {cur!r}")
    if cur:
        lines.append(cur)
    return lines


def block_height(draw, lines, fnt, leading):
    """Total pixel height of lines drawn with `leading` between baselines."""
    if not lines:
        return 0
    heights = [draw.textbbox((0, 0), ln, font=fnt)[3] for ln in lines]
    return sum(heights) + leading * (len(lines) - 1)


def draw_lines(draw, x, y, lines, fnt, fill, leading):
    """Draw lines top-aligned; returns the y just below the last line."""
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += draw.textbbox((0, 0), ln, font=fnt)[3] + leading
    return y


# ---------------------------------------------------------------- icons
def icon_flag(d, x0, y0, s):
    d.line([x0 + 18, y0 + 12, x0 + 18, y0 + s - 12], fill=WHITE, width=4)
    d.polygon([(x0 + 22, y0 + 14), (x0 + s - 14, y0 + 22),
               (x0 + s - 22, y0 + 32), (x0 + s - 14, y0 + 42),
               (x0 + 22, y0 + 48)], fill=WHITE)


def icon_cyclone(d, x0, y0, s):
    cx, cy = x0 + s // 2, y0 + s // 2
    for r, start in ((26, 20), (19, 140), (12, 260)):
        d.arc([cx - r, cy - r, cx + r, cy + r], start=start, end=start + 260,
              fill=WHITE, width=4)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=WHITE)


def icon_rocket(d, x0, y0, s):
    cx, cy = x0 + s // 2, y0 + s // 2
    d.polygon([(cx, cy - 28), (cx + 15, cy + 10), (cx + 7, cy + 18),
               (cx - 7, cy + 18), (cx - 15, cy + 10)], fill=WHITE)
    d.ellipse([cx - 7, cy - 6, cx + 7, cy + 8], outline=NAVY, width=3)
    d.polygon([(cx - 5, cy + 18), (cx + 5, cy + 18), (cx, cy + 30)],
              fill=WHITE)


def icon_globe(d, x0, y0, s):
    cx, cy = x0 + s // 2, y0 + s // 2
    d.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], outline=WHITE, width=4)
    d.line([cx - 24, cy, cx + 24, cy], fill=WHITE, width=3)
    d.line([cx, cy - 24, cx, cy + 24], fill=WHITE, width=3)
    d.arc([cx - 12, cy - 24, cx + 12, cy + 24], start=270, end=90,
          fill=WHITE, width=3)
    d.arc([cx - 12, cy - 24, cx + 12, cy + 24], start=90, end=270,
          fill=WHITE, width=3)


def icon_gamepad(d, x0, y0, s):
    d.rounded_rectangle([x0 + 12, y0 + 24, x0 + s - 12, y0 + s - 20],
                        radius=12, outline=WHITE, width=4)
    d.line([x0 + 24, y0 + 40, x0 + 36, y0 + 40], fill=WHITE, width=4)
    d.line([x0 + 30, y0 + 34, x0 + 30, y0 + 46], fill=WHITE, width=4)
    for bx, by in ((x0 + s - 34, y0 + 36), (x0 + s - 26, y0 + 44)):
        d.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=WHITE)


def icon_asteroid(d, x0, y0, s):
    cx, cy = x0 + s // 2, y0 + s // 2
    d.ellipse([cx - 20, cy - 18, cx + 20, cy + 18], outline=WHITE, width=4)
    d.ellipse([cx - 12, cy - 8, cx - 4, cy], fill=WHITE)
    d.ellipse([cx + 4, cy + 4, cx + 12, cy + 12], fill=WHITE)
    d.ellipse([cx + 8, cy - 12, cx + 12, cy - 8], fill=WHITE)
    for sx, sy in ((x0 + 10, y0 + 12), (x0 + s - 12, y0 + s - 14)):
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=WHITE)


# ---------------------------------------------------------------- content
LEAD_KICKER = "THE HAGUE \u2014 TOP STORY"
LEAD_HEAD = "World Court: Myanmar committed genocide"
LEAD_DECK = ("The ICJ rules 9\u20136 that the 2017 crackdown on the Rohingya "
             "was genocide \u2014 a first for the World Court. "
             "Reparations ordered.")

CARDS = [
    ("TRUMP PUSHES IRAN DECISION TO 2027",
     "Trump says he will decide on new Iran strikes \u2018after the beginning "
     "of the year.\u2019 \u2018I\u2019m not rushing.\u2019",
     (178, 34, 34), icon_flag),
    ("CYCLONE AKVAN HITS INDIA\u2019S EAST COAST",
     "300,000 evacuated in Odisha as the storm crosses near Gopalpur at "
     "noon, winds gusting to 110 km/h.",
     (14, 120, 110), icon_cyclone),
    ("VOYAGER 1, ONE LIGHT-DAY FROM EARTH",
     "NASA confirms the probe is now a full light-day out, about 16 "
     "billion miles, 49 years after launch.",
     (27, 58, 95), icon_rocket),
    ("COP31 TEXTS DROP FOSSIL-FUEL SHIFT",
     "Near-final drafts in Antalya make no mention of fossil fuels; "
     "campaigners call it \u2018an outrage\u2019.",
     (74, 92, 110), icon_globe),
    ("GTA VI SALES PASS $1.8 BILLION",
     "A day after launch, sales already pass The Odyssey\u2019s $1.80bn "
     "global run \u2014 a record start.",
     (84, 48, 138), icon_gamepad),
    ("HAYABUSA2 DROPS ASTEROID LANDING",
     "Engine trouble forces Japan\u2019s probe to change plans; the "
     "asteroid landing is off.",
     (198, 110, 20), icon_asteroid),
]

FOOTER_BODY = ("Europe open to talks with Russia on ending the Ukraine war "
               "\u00b7 Dozens missing as a migrant boat sinks off Senegal "
               "\u00b7 WHO: antibiotics failing against common infections")


def main():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # ---- masthead strip -------------------------------------------------
    f_top = font(SANS_BOLD, 30)
    d.text((MARGIN, 26), "THE WORLD IN ONE PICTURE", font=f_top, fill=NAVY)
    right = "ONE DAY'S NEWS"
    d.text((W - MARGIN - d.textlength(right, font=f_top), 26), right,
           font=f_top, fill=GREY)
    d.line([(MARGIN, 68), (W - MARGIN, 68)], fill=INK, width=4)

    # ---- date block ------------------------------------------------------
    d.text((MARGIN, 84), "FRIDAY", font=font(SANS_BOLD, 46), fill=RED)
    f_date = font(SERIF, 80)
    date = "20 NOVEMBER 2026"
    assert d.textlength(date, font=f_date) <= W - 2 * MARGIN, "date too wide"
    d.text((MARGIN, 132), date, font=f_date, fill=INK)
    d.line([(MARGIN, 248), (W - MARGIN, 248)], fill=RED, width=5)

    # ---- lead story ------------------------------------------------------
    y = 266
    d.text((MARGIN, y), LEAD_KICKER, font=font(SANS_BOLD, 26), fill=RED)
    f_head = font(SERIF, 54)
    head_lines = wrap(d, LEAD_HEAD, f_head, W - 2 * MARGIN)
    assert len(head_lines) <= 2, f"lead headline wraps to {len(head_lines)}"
    y = draw_lines(d, MARGIN, 300, head_lines, f_head, INK, 6)
    f_deck = font(SANS, 27)
    deck_lines = wrap(d, LEAD_DECK, f_deck, W - 2 * MARGIN)
    assert len(deck_lines) <= 2, f"lead deck wraps to {len(deck_lines)}"
    y = draw_lines(d, MARGIN, y + 6, deck_lines, f_deck, INK, 4)
    # Rule sits below the deck's actual ink (deck ink ends at y - leading).
    rule_y = y + 10
    d.line([(MARGIN, rule_y), (W - MARGIN, rule_y)], fill=INK, width=3)

    # ---- six cards, 2 columns x 3 rows ----------------------------------
    f_card_head = font(SANS_BOLD, 22)
    f_card_body = font(SANS, 19)
    col_w = (W - 2 * MARGIN - 28) // 2
    icon_s = 76
    grid_top = rule_y + 12
    row_h = (926 - grid_top) // 3
    assert row_h >= 128, f"card rows squeezed to {row_h}px"
    for i, (head, body, colour, icon_fn) in enumerate(CARDS):
        col, row = i % 2, i // 2
        x0 = MARGIN + col * (col_w + 28)
        y0 = grid_top + row * row_h
        tx = x0 + icon_s + 14
        tw = col_w - icon_s - 14
        head_lines = wrap(d, head, f_card_head, tw)
        assert len(head_lines) <= 2, f"card {i} headline wraps to {len(head_lines)}"
        body_lines = wrap(d, body, f_card_body, tw)
        assert len(body_lines) <= 3, f"card {i} body wraps to {len(body_lines)}"
        need = (block_height(d, head_lines, f_card_head, 1)
                + 4 + block_height(d, body_lines, f_card_body, 2))
        assert need <= row_h - 8, f"card {i} needs {need}px, row has {row_h - 8}"
        d.rounded_rectangle([x0, y0 + 4, x0 + icon_s, y0 + 4 + icon_s],
                            radius=12, fill=colour)
        icon_fn(d, x0, y0 + 4, icon_s)
        yy = draw_lines(d, tx, y0 + 2, head_lines, f_card_head, INK, 1)
        draw_lines(d, tx, yy + 4, body_lines, f_card_body, MIDGREY, 2)

    # ---- footer band ------------------------------------------------------
    band_top = 926
    d.rectangle([0, band_top, W, H], fill=DARKNAVY)
    d.text((MARGIN, band_top + 10), "ALSO TODAY",
           font=font(SANS_BOLD, 24), fill=GOLD)
    f_foot = font(SANS, 20)
    foot_lines = wrap(d, FOOTER_BODY, f_foot, W - 2 * MARGIN)
    assert len(foot_lines) <= 2, f"footer wraps to {len(foot_lines)}"
    foot_h = block_height(d, foot_lines, f_foot, 2)
    assert band_top + 38 + foot_h <= H - 8, "footer overflows page"
    draw_lines(d, MARGIN, band_top + 38, foot_lines, f_foot, WHITE, 2)

    img.save(OUT, "PNG", optimize=True)
    size = os.path.getsize(OUT)
    assert size <= 1048576, f"entry.png is {size} bytes, over 1 MiB"
    print(f"wrote {OUT} {img.size[0]}x{img.size[1]} {size} bytes")


if __name__ == "__main__":
    main()
