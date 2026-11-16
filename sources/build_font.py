#!/usr/bin/env python3
"""Breadot —— 5×7 单点点阵字体生成脚本（BreadCrumb Studio，SIL OFL 1.1）。

字形直接写成点阵：每个字形是若干行，"#" 为亮点，"." 为空。
  - 前 7 行 = 大写高度（第 7 行落在基线上），第 8、9 行 = 降部（可省略）
  - 行宽即字形宽度：常规 5 列，窄标点 1~2 列；字宽 = 列数 + 1
  - 标注 REF 的字形取自 Figma「Dot Matrix」组件，其余按同一规则补全
用法: python sources/build_font.py [字体族名]   → fonts/otf/ 输出 Regular / Bold
"""
import sys
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen

FAMILY = sys.argv[1] if len(sys.argv) > 1 else "Breadot"
VERSION = "1.000"
ROOT = Path(__file__).resolve().parent.parent

# 版权与许可（写入 name 表 0/8/9/11/13/14）
REPO_URL = "https://github.com/paulzheng116/breadot"
COPYRIGHT = f"Copyright 2026 BreadCrumb Studio ({REPO_URL})"
META = {
    "copyright": COPYRIGHT,
    "manufacturer": "BreadCrumb Studio",
    "designer": "BreadCrumb Studio",
    "vendorURL": REPO_URL,
    "licenseDescription": "This Font Software is licensed under the SIL Open Font License, "
                          "Version 1.1. This license is available with a FAQ at: "
                          "https://openfontlicense.org",
    "licenseInfoURL": "https://openfontlicense.org",
}

PITCH = 100       # 点间距（1000 UPM 下：大写高 700，常规字宽 600）
CAP_ROWS = 7
# 字重只改圆点半径，字形与字宽完全一致，切换字重不会重排
#   Regular 直径 ≈ 0.76 × 间距（量自 Figma 组件）
#   Bold    直径 ≈ 0.92 × 间距，墨量约 1.5 倍，点之间仍留缝
WEIGHTS = [("Regular", 400, 38), ("Bold", 700, 46)]
# 垂直度量：ASCENT + DESCENT = 大写高 → 行高 = 字号时大写/数字在字框内上下居中
#           ASCENT - DESCENT = 1100 → 默认行高仍是 11 行点，换行后点阵对齐
ASCENT, DESCENT = 900, -200

GLYPHS = {
    # ---------- 数字（REF） ----------
    "0": ".###. #...# #..## #.#.# ##..# #...# .###.",
    "1": "..#.. .##.. ..#.. ..#.. ..#.. ..#.. .###.",
    "2": ".###. #...# ....# ...#. ..#.. .#... #####",
    "3": "##### ...#. ..#.. ...#. ....# #...# .###.",
    "4": "...#. ..##. .#.#. #..#. ##### ...#. ...#.",
    "5": "##### #.... ####. ....# ....# #...# .###.",
    "6": "..##. .#... #.... ####. #...# #...# .###.",
    "7": "##### ....# ...#. ..#.. .#... .#... .#...",
    "8": ".###. #...# #...# .###. #...# #...# .###.",
    "9": ".###. #...# #...# .#### ....# ...#. .##..",
    # ---------- 大写（A C E H L M O S T U Y 为 REF） ----------
    "A": ".###. #...# #...# ##### #...# #...# #...#",
    "B": "####. #...# #...# ####. #...# #...# ####.",
    "C": ".###. #...# #.... #.... #.... #...# .###.",
    "D": "####. #...# #...# #...# #...# #...# ####.",
    "E": "##### #.... #.... ####. #.... #.... #####",
    "F": "##### #.... #.... ####. #.... #.... #....",
    "G": ".###. #...# #.... #.### #...# #...# .###.",
    "H": "#...# #...# #...# ##### #...# #...# #...#",
    "I": ".###. ..#.. ..#.. ..#.. ..#.. ..#.. .###.",
    "J": "..### ...#. ...#. ...#. ...#. #..#. .##..",
    "K": "#...# #..#. #.#.. ##... #.#.. #..#. #...#",
    "L": "#.... #.... #.... #.... #.... #.... #####",
    "M": "#...# ##.## #.#.# #.#.# #...# #...# #...#",
    "N": "#...# #...# ##..# #.#.# #..## #...# #...#",
    "O": ".###. #...# #...# #...# #...# #...# .###.",
    "P": "####. #...# #...# ####. #.... #.... #....",
    "Q": ".###. #...# #...# #...# #.#.# #..#. .##.#",
    "R": "####. #...# #...# ####. #.#.. #..#. #...#",
    "S": ".#### #.... #.... .###. ....# ....# ####.",
    "T": "##### ..#.. ..#.. ..#.. ..#.. ..#.. ..#..",
    "U": "#...# #...# #...# #...# #...# #...# .###.",
    "V": "#...# #...# #...# #...# #...# .#.#. ..#..",
    "W": "#...# #...# #...# #.#.# #.#.# ##.## #...#",
    "X": "#...# #...# .#.#. ..#.. .#.#. #...# #...#",
    "Y": "#...# #...# .#.#. ..#.. ..#.. ..#.. ..#..",
    "Z": "##### ....# ...#. ..#.. .#... #.... #####",
    # ---------- 小写（x 高 5 行，降部 2 行） ----------
    "a": "..... ..... .###. ....# .#### #...# .####",
    "b": "#.... #.... #.##. ##..# #...# #...# ####.",
    "c": "..... ..... .###. #...# #.... #...# .###.",
    "d": "....# ....# .##.# #..## #...# #...# .####",
    "e": "..... ..... .###. #...# ##### #.... .###.",
    "f": "..##. .#..# .#... ###.. .#... .#... .#...",
    "g": "..... ..... .#### #...# #...# #...# .#### ....# .###.",
    "h": "#.... #.... #.##. ##..# #...# #...# #...#",
    "i": "..#.. ..... .##.. ..#.. ..#.. ..#.. .###.",
    "j": "...#. ..... ..##. ...#. ...#. ...#. ...#. #..#. .##..",
    "k": "#.... #.... #..#. #.#.. ##... #.#.. #..#.",
    "l": ".##.. ..#.. ..#.. ..#.. ..#.. ..#.. .###.",
    "m": "..... ..... ##.#. #.#.# #.#.# #.#.# #.#.#",
    "n": "..... ..... #.##. ##..# #...# #...# #...#",
    "o": "..... ..... .###. #...# #...# #...# .###.",
    "p": "..... ..... ####. #...# #...# #...# ####. #.... #....",
    "q": "..... ..... .#### #...# #...# #...# .#### ....# ....#",
    "r": "..... ..... #.##. ##..# #.... #.... #....",
    "s": "..... ..... .#### #.... .###. ....# ####.",
    "t": ".#... .#... ###.. .#... .#... .#..# ..##.",
    "u": "..... ..... #...# #...# #...# #..## .##.#",
    "v": "..... ..... #...# #...# #...# .#.#. ..#..",
    "w": "..... ..... #...# #...# #.#.# #.#.# .#.#.",
    "x": "..... ..... #...# .#.#. ..#.. .#.#. #...#",
    "y": "..... ..... #...# #...# #...# #...# .#### ....# .###.",
    "z": "..... ..... ##### ...#. ..#.. .#... #####",
    # ---------- 窄标点（: 为 REF，1 列宽） ----------
    ":": ". # # . # # .",
    ".": ". . . . . . #",
    ",": ".. .. .. .. .. .# .# #.",
    ";": ".. .# .# .. .. .# .# #.",
    "!": "# # # # # . #",
    "'": "# # . . . . .",
    "|": "# # # # # # #",
    # ---------- 常规标点（% 为 REF） ----------
    " ": "..... ..... ..... ..... ..... ..... .....",
    "%": "##..# ##..# ...#. ..#.. .#... #..## #..##",
    "?": ".###. #...# ....# ...#. ..#.. ..... ..#..",
    '"': ".#.#. .#.#. ..... ..... ..... ..... .....",
    "`": ".#... ..#.. ..... ..... ..... ..... .....",
    "-": "..... ..... ..... ##### ..... ..... .....",
    "_": "..... ..... ..... ..... ..... ..... ..... #####",
    "+": "..... ..#.. ..#.. ##### ..#.. ..#.. .....",
    "=": "..... ..... ##### ..... ##### ..... .....",
    "/": "....# ....# ...#. ..#.. .#... #.... #....",
    "\\": "#.... #.... .#... ..#.. ...#. ....# ....#",
    "(": "...#. ..#.. .#... .#... .#... ..#.. ...#.",
    ")": ".#... ..#.. ...#. ...#. ...#. ..#.. .#...",
    "[": ".###. .#... .#... .#... .#... .#... .###.",
    "]": ".###. ...#. ...#. ...#. ...#. ...#. .###.",
    "{": "...## ..#.. ..#.. .#... ..#.. ..#.. ...##",
    "}": "##... ..#.. ..#.. ...#. ..#.. ..#.. ##...",
    "<": "...#. ..#.. .#... #.... .#... ..#.. ...#.",
    ">": ".#... ..#.. ...#. ....# ...#. ..#.. .#...",
    "@": ".###. #...# ....# .##.# #.#.# #.#.# .###.",
    "#": ".#.#. .#.#. ##### .#.#. ##### .#.#. .#.#.",
    "$": "..#.. .#### #.#.. .###. ..#.# ####. ..#..",
    "&": ".##.. #..#. #.#.. .#... #.#.# #..#. .##.#",
    "*": "..... ..#.. #.#.# .###. #.#.# ..#.. .....",
    "^": "..#.. .#.#. #...# ..... ..... ..... .....",
    "~": "..... ..... .#... #.#.# ...#. ..... .....",
    # ---------- 排版常用补充 ----------
    "°": ".###. .#.#. .###. ..... ..... ..... .....",   # 度
    "×": "..... #...# .#.#. ..#.. .#.#. #...# .....",   # 乘号
    "‘": "#. .# .. .. .. .. ..",                        # 左单引号
    "’": ".# #. .. .. .. .. ..",                        # 右单引号
    "“": "#.#.. .#.#. ..... ..... ..... ..... .....",   # 左双引号
    "”": ".#.#. #.#.. ..... ..... ..... ..... .....",   # 右双引号
    "–": "..... ..... ..... ##### ..... ..... .....",   # 短破折号
    "—": "....... ....... ....... ####### ....... ....... .......",   # 长破折号
    "…": "..... ..... ..... ..... ..... ..... #.#.#",   # 省略号
    "·": ". . . # . . .",                              # 间隔号
    "•": ".. .. ## ## .. .. ..",                        # 项目符号
    # ---------- 底格：5×7 全亮，与数字/字母等宽，叠在文字下方做暗点阵底 ----------
    "█": "##### ##### ##### ##### ##### ##### #####",   # U+2588 FULL BLOCK
    "▌": "## ## ## ## ## ## ##",                        # U+258C 2 列底格（, ; ‘ ’ •）
    "▏": "# # # # # # #",                              # U+258F 1 列底格（: . ! ' | ·）
    # 9 行底格（含 2 行降部，盖住 g j p q y , ; 的下伸）：网点块 ▓▒░ 依次对应 █▌▏ 的宽度
    "▓": " ".join(["#####"] * 9),                       # U+2593 5×9
    "▒": " ".join(["##"] * 9),                          # U+2592 2×9
    "░": " ".join(["#"] * 9),                           # U+2591 1×9
}

# ss01：支持样式集的软件里，把 █▌▏ 一键换成 9 行版（等同直接输入 ▓▒░）
FEATURES = r"""
languagesystem DFLT dflt;
languagesystem latn dflt;
feature ss01 {
    featureNames { name "9-row base"; name 3 1 0x0804 "9\884C\5E95\683C"; };
    sub uni2588 by uni2593;
    sub uni258C by uni2592;
    sub uni258F by uni2591;
} ss01;
"""

NAMES = {
    " ": "space", ".": "period", ",": "comma", ":": "colon", ";": "semicolon",
    "!": "exclam", "?": "question", "'": "quotesingle", '"': "quotedbl",
    "`": "grave", "-": "hyphen", "_": "underscore", "+": "plus", "=": "equal",
    "/": "slash", "\\": "backslash", "|": "bar", "(": "parenleft",
    ")": "parenright", "[": "bracketleft", "]": "bracketright",
    "{": "braceleft", "}": "braceright", "<": "less", ">": "greater",
    "@": "at", "#": "numbersign", "$": "dollar", "%": "percent",
    "&": "ampersand", "*": "asterisk", "^": "asciicircum", "~": "asciitilde",
    "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four",
    "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine",
    "°": "degree", "×": "multiply",
    "‘": "quoteleft", "’": "quoteright", "“": "quotedblleft",
    "”": "quotedblright", "–": "endash", "—": "emdash",
    "…": "ellipsis", "·": "periodcentered", "•": "bullet",
}


def cells(spec):
    """点阵字符串 → (列数, {(col, row)})，row 0 为基线行，向上为正。"""
    rows = spec.split()
    width = len(rows[0])
    assert all(len(r) == width for r in rows), spec
    assert len(rows) >= CAP_ROWS, spec
    on = {(c, CAP_ROWS - 1 - i) for i, r in enumerate(rows) for c, ch in enumerate(r) if ch == "#"}
    return width, on


def draw(pen, on, r):
    k = r * 0.5522847498
    for col, row in sorted(on):
        cx = (col + 1) * PITCH          # 左右各留半列
        cy = row * PITCH + PITCH / 2
        pen.moveTo((cx + r, cy))
        pen.curveTo((cx + r, cy + k), (cx + k, cy + r), (cx, cy + r))
        pen.curveTo((cx - k, cy + r), (cx - r, cy + k), (cx - r, cy))
        pen.curveTo((cx - r, cy - k), (cx - k, cy - r), (cx, cy - r))
        pen.curveTo((cx + k, cy - r), (cx + r, cy - k), (cx + r, cy))
        pen.closePath()


def glyph_name(ch):
    return NAMES.get(ch, ch if ch.isascii() and ch.isalpha() else "uni%04X" % ord(ch))


def build(out_dir, style, weight, radius):
    specs = {".notdef": "##### #...# #...# #...# #...# #...# #####"}
    cmap = {}
    for ch, spec in GLYPHS.items():
        name = glyph_name(ch)
        specs[name] = spec
        cmap[ord(ch)] = name
    cmap[0x00A0] = "space"
    order = list(specs)

    charstrings, metrics = {}, {}
    for name, spec in specs.items():
        width, on = cells(spec)
        advance = (width + 1) * PITCH
        pen = T2CharStringPen(advance, None)
        draw(pen, on, radius)
        charstrings[name] = pen.getCharString()
        lsb = min((c for c, _ in on), default=0) * PITCH + PITCH - radius
        metrics[name] = (advance, lsb)

    bold = style == "Bold"
    ps_name = FAMILY.replace(" ", "") + "-" + style
    fb = FontBuilder(1000, isTTF=False)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupCFF(ps_name, {"FullName": f"{FAMILY} {style}", "Weight": style,
                          "Copyright": COPYRIGHT}, charstrings, {})
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=ASCENT, descent=DESCENT, lineGap=0)
    fb.setupNameTable({
        "familyName": FAMILY, "styleName": style,
        "uniqueFontIdentifier": f"{VERSION};{ps_name}",
        "fullName": f"{FAMILY} {style}", "psName": ps_name,
        "version": f"Version {VERSION}", **META,
    })
    fb.setupOS2(
        version=4, usWeightClass=weight,
        # bit7 USE_TYPO_METRICS；bit5 BOLD / bit6 REGULAR → Regular/Bold 归为同一字族
        fsSelection=0x80 | (0x20 if bold else 0x40),
        sTypoAscender=ASCENT, sTypoDescender=DESCENT, sTypoLineGap=0,
        usWinAscent=ASCENT, usWinDescent=-DESCENT,
        sxHeight=5 * PITCH, sCapHeight=CAP_ROWS * PITCH,
        xAvgCharWidth=6 * PITCH, achVendID="NONE",
    )
    fb.updateHead(macStyle=1 if bold else 0)
    fb.setupPost(underlinePosition=-150, underlineThickness=PITCH // 2)
    fb.addOpenTypeFeatures(FEATURES)
    out = Path(out_dir) / f"{ps_name}.otf"
    fb.save(out)
    return out


if __name__ == "__main__":
    out_dir = ROOT / "fonts" / "otf"
    out_dir.mkdir(parents=True, exist_ok=True)
    for style, weight, radius in WEIGHTS:
        print(build(out_dir, style, weight, radius))
