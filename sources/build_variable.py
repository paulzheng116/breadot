#!/usr/bin/env python3
"""Breadot 可变字体：Regular(400) 与 Bold(700) 合并为一个文件，wght 轴连续可调。

字形、度量全部复用 build_font.py；两个母版只差圆点半径（38 → 46），
中间字重 = 圆点按比例放大。轮廓用 TrueType 二次曲线：每个点 8 个控制点的
全离线圆，两母版点序一致，可直接插值。
用法: python sources/build_variable.py   → fonts/variable/Breadot.ttf + fonts/webfonts/Breadot.woff2
"""
import math
from pathlib import Path

from fontTools import varLib
from fontTools.designspaceLib import (AxisDescriptor, DesignSpaceDocument,
                                      InstanceDescriptor, SourceDescriptor)
from fontTools.fontBuilder import FontBuilder
from fontTools.otlLib.builder import buildStatTable
from fontTools.pens.ttGlyphPen import TTGlyphPen

from build_font import (ASCENT, CAP_ROWS, DESCENT, FAMILY, FEATURES, GLYPHS,
                        META, PITCH, ROOT, VERSION, WEIGHTS, cells, glyph_name)

PS_FAMILY = FAMILY.replace(" ", "")


def draw_tt(pen, on, r):
    """二次曲线圆：8 个离线控制点（半径 r/cos22.5°），隐含在线点正好落在半径 r 上。顺时针 = TT 外轮廓方向。"""
    R = r / math.cos(math.pi / 8)
    for col, row in sorted(on):
        cx = (col + 1) * PITCH
        cy = row * PITCH + PITCH / 2
        pts = [(cx + R * math.cos(a), cy + R * math.sin(a))
               for a in (math.pi / 8 - k * math.pi / 4 for k in range(8))]
        pen.qCurveTo(*pts, None)
        pen.closePath()


def master(style, weight, radius):
    specs = {".notdef": "##### #...# #...# #...# #...# #...# #####"}
    cmap = {}
    for ch, spec in GLYPHS.items():
        name = glyph_name(ch)
        specs[name] = spec
        cmap[ord(ch)] = name
    cmap[0x00A0] = "space"

    glyphs, metrics = {}, {}
    for name, spec in specs.items():
        width, on = cells(spec)
        pen = TTGlyphPen(None)
        draw_tt(pen, on, radius)
        g = pen.glyph()
        glyphs[name] = g
        lsb = min((x for x, _ in g.coordinates), default=0)
        metrics[name] = ((width + 1) * PITCH, lsb)

    ps_name = f"{PS_FAMILY}-{style}"
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(list(specs))
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
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
        fsSelection=0x80 | (0x20 if style == "Bold" else 0x40),
        sTypoAscender=ASCENT, sTypoDescender=DESCENT, sTypoLineGap=0,
        usWinAscent=ASCENT, usWinDescent=-DESCENT,
        sxHeight=5 * PITCH, sCapHeight=CAP_ROWS * PITCH,
        xAvgCharWidth=6 * PITCH, achVendID="NONE",
    )
    fb.updateHead(macStyle=1 if style == "Bold" else 0)
    fb.setupPost(underlinePosition=-150, underlineThickness=PITCH // 2)
    fb.addOpenTypeFeatures(FEATURES)
    return fb.font


def build(out_dir, web_dir=None):
    lo, hi = WEIGHTS[0][1], WEIGHTS[-1][1]
    doc = DesignSpaceDocument()
    doc.addAxis(AxisDescriptor(tag="wght", name="Weight", minimum=lo, default=lo, maximum=hi))
    for style, weight, radius in WEIGHTS:
        doc.addSource(SourceDescriptor(font=master(style, weight, radius), name=style,
                                       familyName=FAMILY, styleName=style,
                                       location={"Weight": weight}))
        doc.addInstance(InstanceDescriptor(familyName=FAMILY, styleName=style,
                                           postScriptFontName=f"{PS_FAMILY}-{style}",
                                           location={"Weight": weight}))
    vf = varLib.build(doc)[0]

    # STAT：Regular 可省略且链接到 Bold，系统/设计软件据此识别字重
    buildStatTable(vf, [dict(tag="wght", name="Weight", values=[
        dict(value=lo, name="Regular", flags=0x2, linkedValue=hi),
        dict(value=hi, name="Bold"),
    ])], elidedFallbackName=2)
    vf["name"].setName(PS_FAMILY, 25, 3, 1, 0x409)   # 可变字体 PostScript 名前缀

    out = Path(out_dir) / f"{PS_FAMILY}.ttf"
    vf.save(out)
    if web_dir:                                       # 网页用 WOFF2（需 brotli）
        vf.flavor = "woff2"
        vf.save(Path(web_dir) / f"{PS_FAMILY}.woff2")
    return out


if __name__ == "__main__":
    dirs = [ROOT / "fonts" / "variable", ROOT / "fonts" / "webfonts"]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    print(build(*dirs))
