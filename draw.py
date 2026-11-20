#!/usr/bin/env python3
"""Draw one day's world news as a newspaper front page (1024x1024 PNG).

Friday 20 November 2026. Self-contained: Pillow plus the DejaVu fonts
shipped with the system. Every line of text is measured before it is
drawn; anything that would overflow its box aborts with an error instead
of being silently clipped.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 36
CONTENT_W = W - 2 * MARGIN
PAPER = (247, 243, 232)
INK = (20, 20, 20)
RED = (176, 30, 36)
GREY = (96, 92, 84)
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def load_font(name, size):
    return ImageFont.truetype(str(FONT_DIR / name), size)


def serif_b(size):
    return load_font("DejaVuSerif-Bold.ttf", size)


def serif(size):
    return load_font("DejaVuSerif.ttf", size)


def sans_b(size):
    return load_font("DejaVuSans-Bold.ttf", size)


def sans(size):
    return load_font("DejaVuSans.ttf", size)


def wrap_lines(draw, text, fnt, max_w):
    """Greedy word wrap; every produced line is guaranteed to fit."""
    lines = []
    current = ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            current = trial
        else:
            if not current:
                raise RuntimeError("single word too wide for box: %r" % word)
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_para(draw, x, y, text, fnt, max_w, leading, fill=INK):
    """Draw a wrapped paragraph; return the y just below its last line."""
    for line in wrap_lines(draw, text, fnt, max_w):
        if draw.textlength(line, font=fnt) > max_w:
            raise RuntimeError("line overflows its box: %r" % line)
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def centred(draw, y, text, fnt, fill=INK):
    """Draw one centred line; fail loudly if it is wider than the page."""
    width = draw.textlength(text, font=fnt)
    if width > CONTENT_W:
        raise RuntimeError("centred line too wide: %r" % text)
    draw.text(((W - width) / 2, y), text, font=fnt, fill=fill)
    return y + fnt.size


def rule(draw, y, weight=2, fill=INK):
    draw.line([(MARGIN, y), (W - MARGIN, y)], fill=fill, width=weight)
    return y + weight


def draw_globe(draw, cx, cy, r):
    """Small line-drawn globe: circle, meridians and parallels."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=3)
    draw.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r],
                 outline=INK, width=2)
    draw.line([(cx - r, cy), (cx + r, cy)], fill=INK, width=2)
    for dy in (-0.55, 0.55):
        half = r * (1 - dy * dy) ** 0.5
        draw.line([(cx - half, cy + dy * r), (cx + half, cy + dy * r)],
                  fill=INK, width=2)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # ---- Masthead -------------------------------------------------------
    y = 22
    y = centred(draw, y, "THE WORLD IN ONE PICTURE", serif_b(46))
    y += 6
    y = rule(draw, y, 3)
    y += 8
    y = centred(draw, y, "ONE DAY'S NEWS  \u00b7  FRIDAY 20 NOVEMBER 2026",
                sans_b(25))
    y += 8
    y = rule(draw, y, 5)

    # ---- Lead story -----------------------------------------------------
    y += 14
    kicker = sans_b(24)
    draw.text((MARGIN, y), "THE HAGUE \u2014 TOP STORY", font=kicker, fill=RED)
    draw_globe(draw, W - MARGIN - 34, y + 22, 32)
    y += 36
    y = draw_para(draw, MARGIN, y, "World Court: Myanmar committed genocide",
                  serif_b(46), CONTENT_W, 54)
    y += 6
    y = draw_para(draw, MARGIN, y,
                  "The ICJ rules 9\u20136 that the 2017 crackdown on the "
                  "Rohingya was genocide \u2014 a first for the World "
                  "Court. Reparations ordered.",
                  serif(25), CONTENT_W, 33)
    y += 12
    y = rule(draw, y, 2)

    # ---- Six more stories, two columns ---------------------------------
    stories = [
        ("TRUMP PUSHES IRAN DECISION TO 2027",
         "Trump says he will decide on new Iran strikes \u2018after the "
         "beginning of the year.\u2019 \u2018I\u2019m not rushing.\u2019"),
        ("CYCLONE AKVAN HITS INDIA\u2019S EAST COAST",
         "300,000 evacuated in Odisha as the storm crosses near Gopalpur "
         "at noon, winds gusting to 110 km/h."),
        ("VOYAGER 1, ONE LIGHT-DAY FROM EARTH",
         "NASA confirms the probe is now a full light-day out, about 16 "
         "billion miles, 49 years after launch."),
        ("COP31 TEXTS DROP FOSSIL-FUEL SHIFT",
         "Near-final drafts in Antalya make no mention of fossil fuels; "
         "campaigners call it \u2018an outrage\u2019."),
        ("GTA VI SALES PASS $1.8 BILLION",
         "A day after launch, sales already pass The Odyssey\u2019s $1.80bn "
         "global run \u2014 a record start."),
        ("HAYABUSA2 DROPS ASTEROID LANDING",
         "Engine trouble forces Japan\u2019s probe to change plans; the "
         "asteroid landing is off."),
    ]
    col_w = (CONTENT_W - 28) // 2
    row_h = 154
    grid_top = y + 14
    for i, (head, body) in enumerate(stories):
        col = i % 2
        row = i // 2
        x = MARGIN + col * (col_w + 28)
        top = grid_top + row * row_h
        if col == 1:
            draw.line([(MARGIN + col_w + 14, top),
                       (MARGIN + col_w + 14, top + row_h - 18)],
                      fill=GREY, width=1)
        bottom = draw_para(draw, x, top, head, sans_b(22), col_w, 27, RED)
        bottom = draw_para(draw, x, bottom + 5, body, serif(21),
                           col_w, 27)
        if bottom > grid_top + (row + 1) * row_h:
            raise RuntimeError("story overflows its grid cell: %r" % head)

    y = grid_top + 3 * row_h + 4

    # ---- Footer ---------------------------------------------------------
    y = rule(draw, y, 2)
    y += 10
    draw.text((MARGIN, y), "ALSO TODAY", font=sans_b(23), fill=RED)
    y += 34
    y = draw_para(draw, MARGIN, y,
                  "Europe open to talks with Russia on ending the Ukraine "
                  "war \u00b7 Dozens missing as a migrant boat sinks off "
                  "Senegal \u00b7 WHO: antibiotics failing against common "
                  "infections",
                  serif(21), CONTENT_W, 27)
    if y > H - 24:
        raise RuntimeError("footer overflows the page")

    out = Path(__file__).resolve().parent / "entry.png"
    img.save(out, optimize=True)
    size = out.stat().st_size
    print("wrote %s (%d bytes)" % (out, size))
    if size > 1048576:
        raise RuntimeError("entry.png exceeds 1 MiB")


if __name__ == "__main__":
    main()
