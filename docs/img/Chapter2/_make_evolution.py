"""Sơ đồ 4 giai đoạn (Hình 2.1): xuất file .excalidraw và PNG cùng bố cục.
Chạy: python docs/img/Chapter2/_make_evolution.py
"""
import json, os, math
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
# Latin Modern (font có chân, giống font chữ của khóa luận), lấy từ MiKTeX
_LM = os.path.expandvars(r"%LOCALAPPDATA%\Programs\MiKTeX\fonts\opentype\public\lm")
FONT = os.path.join(_LM, "lmroman10-regular.otf")
FONT_B = os.path.join(_LM, "lmroman10-bold.otf")

STROKE = "#4d5560"
TEXT = "#202124"
WHITE = "#ffffff"
FILLS = ["#f1f3f4", "#e8f0fe", "#e6f4ea", "#fef7e0"]

STAGES = [
    ("(1) Hệ chuyên gia\ndựa trên luật",
     "Minh bạch, suy diễn xác định.",
     "Cứng nhắc, không đọc được văn bản tự do."),
    ("(2) LLM y khoa\ndùng độc lập",
     "Hiểu và trả lời bằng ngôn ngữ tự nhiên.",
     "Ảo giác, tri thức cố định, không có trích dẫn."),
    ("(3) RAG cơ bản",
     "Cập nhật được tri thức, có trích dẫn nguồn.",
     "Dễ lấy đoạn nhiễu, bỏ qua quan hệ giải phẫu."),
    ("(4) RAG + đồ thị tri thức\n+ độ bất định",
     "Kiểm chứng bằng chứng, biết hỏi thêm hoặc từ chối.",
     "Nhiều thành phần, hệ thống phức tạp hơn."),
]

# layout (pixels)
M = 30            # outer margin
BW = 400          # block width
GAP = 70          # gap between blocks (arrow space)
HH = 110          # header height
PAD = 22          # inner padding of body
FS_H, FS_L, FS_B = 27, 23, 23
LH = 1.3


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


def wrap(draw, text, f, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=f) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def body_lines(draw, pro, con):
    inner = BW - 2 * PAD
    fb = font(FS_B)
    return [("Ưu điểm:", True)] + [(l, False) for l in wrap(draw, pro, fb, inner)] + \
           [("", False)] + \
           [("Nhược điểm:", True)] + [(l, False) for l in wrap(draw, con, fb, inner)]


# measure body height so all four blocks are identical
probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
max_lines = max(len(body_lines(probe, p, c)) for _, p, c in STAGES)
BH = HH + 2 * PAD + int(max_lines * FS_B * LH) - int(FS_B * LH * 0.5)
W = 2 * M + 4 * BW + 3 * GAP
H = 2 * M + BH

im = Image.new("RGB", (W, H), WHITE)
d = ImageDraw.Draw(im)
els, seed = [], 1


def rect_el(x, y, w, h, fill, rounded=True):
    global seed
    seed += 1
    return {"id": f"r{seed}", "type": "rectangle", "x": x, "y": y, "width": w, "height": h, "angle": 0,
            "strokeColor": STROKE, "backgroundColor": fill, "fillStyle": "solid", "strokeWidth": 2,
            "strokeStyle": "solid", "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None,
            "roundness": {"type": 3} if rounded else None, "seed": seed, "version": 1,
            "versionNonce": seed * 17 + 3, "isDeleted": False, "boundElements": [], "updated": 1, "link": None,
            "locked": False}


def text_el(x, y, w, h, text, size, align="left"):
    global seed
    seed += 1
    return {"id": f"t{seed}", "type": "text", "x": x, "y": y, "width": w, "height": h, "angle": 0,
            "strokeColor": TEXT, "backgroundColor": "transparent", "fillStyle": "solid", "strokeWidth": 1,
            "strokeStyle": "solid", "roughness": 0, "opacity": 100, "groupIds": [], "frameId": None,
            "roundness": None, "seed": seed, "version": 1, "versionNonce": seed * 19 + 7, "isDeleted": False,
            "boundElements": [], "updated": 1, "link": None, "locked": False, "fontSize": size, "fontFamily": 2,
            "text": text, "textAlign": align, "verticalAlign": "top", "containerId": None, "originalText": text,
            "autoResize": False, "lineHeight": LH}


def line_el(x1, y1, x2, y2, arrow=False):
    global seed
    seed += 1
    return {"id": f"l{seed}", "type": "arrow" if arrow else "line", "x": x1, "y": y1, "width": x2 - x1,
            "height": y2 - y1, "angle": 0, "strokeColor": STROKE, "backgroundColor": "transparent",
            "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid", "roughness": 1, "opacity": 100,
            "groupIds": [], "frameId": None, "roundness": None, "seed": seed, "version": 1,
            "versionNonce": seed * 23 + 11, "isDeleted": False, "boundElements": [], "updated": 1, "link": None,
            "locked": False, "points": [[0, 0], [x2 - x1, y2 - y1]], "startBinding": None, "endBinding": None,
            "startArrowhead": None, "endArrowhead": "arrow" if arrow else None, "lastCommittedPoint": None}


for i, (title, pro, con) in enumerate(STAGES):
    x = M + i * (BW + GAP)
    y = M
    fill = FILLS[i]
    # block outline + header band
    d.rounded_rectangle((x, y, x + BW, y + BH), radius=18, fill=WHITE, outline=STROKE, width=3)
    d.rounded_rectangle((x, y, x + BW, y + HH), radius=18, fill=fill, outline=STROKE, width=3)
    d.rectangle((x + 2, y + HH - 20, x + BW - 2, y + HH - 1), fill=fill)
    d.line((x, y + HH, x + BW, y + HH), fill=STROKE, width=3)
    els += [rect_el(x, y, BW, BH, WHITE), rect_el(x, y, BW, HH, fill), line_el(x, y + HH, x + BW, y + HH)]
    # title
    fh = font(FS_H, True)
    tl = title.split("\n")
    th = len(tl) * FS_H * LH
    ty = y + (HH - th) / 2
    for l in tl:
        tw = d.textlength(l, font=fh)
        d.text((x + (BW - tw) / 2, ty), l, font=fh, fill=TEXT)
        ty += FS_H * LH
    els.append(text_el(x + PAD, y + (HH - th) / 2, BW - 2 * PAD, th, title, FS_H, "center"))
    # body
    by = y + HH + PAD
    lines = body_lines(d, pro, con)
    for txt, bold in lines:
        if txt:
            d.text((x + PAD, by), txt, font=font(FS_L if bold else FS_B, bold), fill=TEXT)
        by += (FS_B * LH) if txt else FS_B * LH * 0.5
    body_txt = "Ưu điểm:\n" + pro + "\n\nNhược điểm:\n" + con
    els.append(text_el(x + PAD, y + HH + PAD, BW - 2 * PAD, BH - HH - 2 * PAD, body_txt, FS_B))
    # arrow to next block, at header mid-height
    if i < 3:
        ax1, ax2, ay = x + BW + 8, x + BW + GAP - 8, y + HH / 2
        d.line((ax1, ay, ax2 - 4, ay), fill=STROKE, width=4)
        L = 16
        d.polygon([(ax2, ay), (ax2 - L, ay - 8), (ax2 - L, ay + 8)], fill=STROKE)
        els.append(line_el(ax1, ay, ax2, ay, arrow=True))

png = os.path.join(OUT, "evolution_4_stages.png")
im.save(png)
doc = {"type": "excalidraw", "version": 2, "source": "https://excalidraw.com", "elements": els,
       "appState": {"gridSize": None, "viewBackgroundColor": "#ffffff"}, "files": {}}
with open(os.path.join(OUT, "evolution_4_stages.excalidraw"), "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)
print(png, im.size)
