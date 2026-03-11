from PIL import Image, ImageDraw, ImageFont
import math

W, H = 800, 420
img = Image.new("RGB", (W, H), "#0d1117")
draw = ImageDraw.Draw(img)

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def gradient_rect(draw, x1, y1, x2, y2, colors, radius=0):
    """水平グラデーション矩形"""
    stops = [hex_to_rgb(c) for c in colors]
    n = len(stops) - 1
    for x in range(x1, x2):
        t_total = (x - x1) / max(x2 - x1 - 1, 1)
        seg = min(int(t_total * n), n - 1)
        t_local = t_total * n - seg
        color = lerp_color(stops[seg], stops[seg + 1], t_local)
        draw.line([(x, y1), (x, y2)], fill=color)

# ── カードの背景 ──
card_x1, card_y1, card_x2, card_y2 = 50, 30, 750, 160
draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=14,
                        fill="#161b22", outline="#30363d", width=1)

# ── タイトル文字（グラデーション）──
title = "Market Dashboard"
try:
    fnt = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 36)
except:
    fnt = ImageFont.load_default()

# グラデーション帯を描いてタイトルでマスク
tx, ty = 80, 70
bbox = draw.textbbox((tx, ty), title, font=fnt)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
grad_img = Image.new("RGB", (tw + 4, th + 4), "#0d1117")
gd = ImageDraw.Draw(grad_img)
gradient_rect(gd, 0, 0, tw + 4, th + 4, ["#58a6ff", "#b388ff", "#f0c040"])
mask = Image.new("L", (tw + 4, th + 4), 0)
md = ImageDraw.Draw(mask)
md.text((0, 0), title, font=fnt, fill=255)
img.paste(grad_img, (tx, ty), mask)

# ── 更新時刻テキスト ──
try:
    sm = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 14)
except:
    sm = ImageFont.load_default()
draw.text((510, 88), "最終更新: 2026/3/11 10:00 (JST)", font=sm, fill="#8b949e")

# ── 新ボタン ──
bx1, by1, bx2, by2 = 610, 77, 720, 107
# グラデーション背景
gradient_rect(draw, bx1, by1, bx2, by2, ["#58a6ff", "#b388ff", "#f0c040"])
# 角丸マスク
btn_mask = Image.new("L", (bx2-bx1, by2-by1), 0)
ImageDraw.Draw(btn_mask).rounded_rectangle([0, 0, bx2-bx1-1, by2-by1-1], radius=15, fill=255)
# グロー
glow = Image.new("RGBA", (W, H), (0,0,0,0))
gd2 = ImageDraw.Draw(glow)
for r in range(18, 0, -2):
    alpha = int(60 * (1 - r/18))
    gd2.ellipse([bx1+(bx2-bx1)//2-r*3, by1+(by2-by1)//2-r,
                 bx1+(bx2-bx1)//2+r*3, by1+(by2-by1)//2+r], fill=(88,166,255,alpha))
img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
draw = ImageDraw.Draw(img)
gradient_rect(draw, bx1, by1, bx2, by2, ["#58a6ff", "#b388ff", "#f0c040"])
# 光沢レイヤー
for y in range(by1, by1 + (by2-by1)//2):
    alpha = int(30 * (1 - (y-by1)/((by2-by1)//2)))
    draw.line([(bx1, y), (bx2, y)], fill=tuple(min(255, c+alpha) for c in (255,255,255)))
try:
    btn_fnt = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 14)
except:
    btn_fnt = ImageFont.load_default()
draw.text((bx1 + 18, by1 + 8), "更新", font=btn_fnt, fill="white")

# ── セクション: 新旧比較 ──
try:
    label_fnt = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 12)
except:
    label_fnt = ImageFont.load_default()
draw.text((240, 200), "変更前", font=label_fnt, fill="#8b949e")
draw.text((480, 200), "変更後", font=label_fnt, fill="#8b949e")

# 旧ボタン
ox1, oy1, ox2, oy2 = 200, 220, 330, 255
draw.rounded_rectangle([ox1, oy1, ox2, oy2], radius=8, fill="#2ea043")
draw.text((ox1 + 18, oy1 + 9), "🔄 更新", font=btn_fnt, fill="white")

# 新ボタン（比較用）
nx1, ny1, nx2, ny2 = 440, 220, 560, 255
for x in range(nx1, nx2):
    t = (x - nx1) / (nx2 - nx1)
    stops = [hex_to_rgb(c) for c in ["#58a6ff", "#b388ff", "#f0c040"]]
    seg = min(int(t * 2), 1)
    t2 = t * 2 - seg
    color = lerp_color(stops[seg], stops[seg+1], t2)
    draw.line([(x, ny1), (x, ny2)], fill=color)
# 角丸クリップ近似
draw.rounded_rectangle([nx1, ny1, nx2, ny2], radius=15, outline="#0d1117", width=0)
for y in range(ny1, ny1 + (ny2-ny1)//2):
    alpha = int(25 * (1 - (y-ny1)/((ny2-ny1)//2)))
    for x in range(nx1, nx2):
        px = img.getpixel((x, y))
        img.putpixel((x, y), tuple(min(255, c+alpha) for c in px))
draw = ImageDraw.Draw(img)
draw.text((nx1 + 18, ny1 + 9), "更新", font=btn_fnt, fill="white")

# グロー（新ボタン比較用）
cx = (nx1 + nx2) // 2
cy = (ny1 + ny2) // 2
for r in range(40, 0, -4):
    alpha = int(15 * (1 - r/40))
    draw.ellipse([cx-r*2, cy-r//2, cx+r*2, cy+r//2], outline=(88,166,255,alpha))

# 矢印
draw.text((370, 228), "→", font=btn_fnt, fill="#8b949e")

# ── 説明テキスト ──
try:
    desc = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 13)
except:
    desc = ImageFont.load_default()
draw.text((200, 270), "緑の角ボタン", font=desc, fill="#8b949e")
draw.text((440, 270), "グラデーション ピル型 グロー", font=desc, fill="#58a6ff")

img.save("preview-button.png")
print("saved: preview-button.png")
