"""
SUSTAINOVA 2026 IDEATHON — CONTENT-ENRICHED MODERN PRESENTATION BUILDER
Keeps the exact modern design look, clean Trebuchet MS + Calibri typography, soft-shadow
bento cards, and easy-to-understand language that the user loved, while packing EVERY slide
with rich, high-value facts, metrics, sub-bullets, real Indian case studies, and feature tags
so zero space feels empty and judges get complete technical & business depth.
"""

import os
import math
import shutil
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pypdfium2 as pdfium
from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.util import Inches

BASE_DIR = r"C:\Users\ACER\.gemini\antigravity\scratch\infra-health-monitor"
ASSETS_DIR = os.path.join(BASE_DIR, "frontend", "ppt_assets")
SLIDES_OUT_DIR = os.path.join(ASSETS_DIR, "ref_matched_slides")
PLOTS_DIR = os.path.join(ASSETS_DIR, "custom_plots")
os.makedirs(SLIDES_OUT_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)

USER_PDF = r"C:\Users\ACER\.gemini\antigravity\brain\62b11bf7-5dc3-4157-b4e7-78a57d988e9c\.user_uploaded\media_1795534951525_a65cdd30.pdf"
REF_PDF = os.path.join(BASE_DIR, "ref_presentation", "Presentation.pdf")

W, H = 1920, 1080

# Modern Design Palette
BG_CANVAS = (244, 247, 252)
HEADER_NAVY = (15, 23, 42)
BRAND_ROYAL = (37, 99, 235)
BRAND_INDIGO = (79, 70, 229)
BRAND_EMERALD = (16, 185, 129)
BRAND_DARK_GREEN = (5, 150, 105)
BRAND_AMBER = (217, 119, 6)
BRAND_CRIMSON = (225, 29, 72)
BRAND_PURPLE = (124, 58, 237)
BRAND_CYAN = (8, 145, 178)
TEXT_MAIN = (15, 23, 42)
TEXT_BODY = (45, 58, 78)
CARD_WHITE = (255, 255, 255)
CARD_STROKE = (214, 224, 238)

def get_font(size, bold=False, display=False):
    if display:
        candidates = ["trebucbd.ttf", "verdanab.ttf", "calibrib.ttf"]
    elif bold:
        candidates = ["calibrib.ttf", "trebucbd.ttf", "verdanab.ttf"]
    else:
        candidates = ["calibri.ttf", "verdana.ttf", "trebuc.ttf"]
    for c in candidates:
        p = os.path.join(r"C:\Windows\Fonts", c)
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    curr = ""
    for w in words:
        test = (curr + " " + w).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            curr = test
        else:
            if curr:
                lines.append(curr)
            curr = w
    if curr:
        lines.append(curr)
    return lines

def draw_multiline(draw, pos, text, font, fill, max_width, line_spacing=4, align="left"):
    x, y = pos
    lines = wrap_text(draw, text, font, max_width)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        lw = bbox[2] - bbox[0]
        lh = bbox[3] - bbox[1]
        dx = x
        if align == "center":
            dx = x + (max_width - lw) / 2
        elif align == "right":
            dx = x + max_width - lw
        draw.text((dx, y), line, font=font, fill=fill)
        y += lh + line_spacing
    return y

def draw_elevated_card(draw, box, radius=18, fill=CARD_WHITE, outline=CARD_STROKE, width=2, top_accent=None):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle([x0 + 4, y0 + 5, x1 + 4, y1 + 5], radius=radius, fill=(224, 232, 244))
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)
    if top_accent:
        draw.rounded_rectangle([x0, y0, x1, y0 + 11], radius=6, fill=top_accent)

def draw_pill_badge(draw, x, y, text, fg, bg, font_size=13):
    f = get_font(font_size, bold=True)
    tb = draw.textbbox((0, 0), text, font=f)
    pw = tb[2] - tb[0] + 20
    ph = tb[3] - tb[1] + 10
    draw.rounded_rectangle([x, y, x + pw, y + ph], radius=ph // 2, fill=bg, outline=fg, width=1)
    draw.text((x + 10, y + 3), text, font=f, fill=fg)
    return pw

# ==============================================================================
# STEP 1: GENERATE HIGH-CLARITY CHARTS (MATPLOTLIB)
# ==============================================================================
print("Generating charts...")
plt.rcParams["font.sans-serif"] = "Calibri"

# Chart 1: 5-Year Bridge Health Forecast
fig, ax = plt.subplots(figsize=(5.3, 2.55), dpi=220)
years = np.linspace(0, 5, 100)
without_ig = 96 - 10.5 * np.exp(0.38 * years) + 10.5
with_ig = np.where(years < 1.5, without_ig, 81 + 12 * np.exp(-0.20 * (years - 1.5)) - 4)
ax.plot(years, without_ig, color="#e11d48", lw=3, label="Without Early Repair (Drops to Danger Zone)")
ax.plot(years, with_ig, color="#059669", lw=3, linestyle="--", label="With InfraGuard CFRP Repair (+35% Longer Life)")
ax.axhline(45, color="#d97706", linestyle=":", lw=1.6, label="IRC:112 Critical Limit (HI = 45%)")
ax.fill_between(years, without_ig, with_ig, where=(years >= 1.5), color="#10b981", alpha=0.18)
ax.scatter([1.5], [81], color="#2563eb", s=60, zorder=5)
ax.annotate("Crack Fixed at 0.3mm!\n(Saves 68% Cost)", xy=(1.5, 81), xytext=(1.75, 89),
            arrowprops=dict(arrowstyle="->", color="#2563eb", lw=1.4), fontsize=8.2, fontweight="bold", color="#2563eb")
ax.set_title("Paris' Law 5-Year Bridge Health & RUL Forecast", fontsize=10.2, fontweight="bold", color="#0f172a")
ax.set_xlabel("Forecast Horizon (Years)", fontsize=8.5, fontweight="bold", color="#334155")
ax.set_ylabel("Bridge Health Score (%)", fontsize=8.5, fontweight="bold", color="#334155")
ax.set_ylim(20, 105)
ax.set_xlim(0, 5)
ax.grid(True, linestyle="--", alpha=0.3)
ax.legend(loc="lower left", fontsize=7.5, frameon=True, facecolor="#ffffff")
plt.tight_layout()
rul_plot_path = os.path.join(PLOTS_DIR, "rul_simple.png")
plt.savefig(rul_plot_path, dpi=220)
plt.close()

# Chart 2: 10-Year Cost Comparison Bar Chart
fig, ax = plt.subplots(figsize=(5.3, 2.45), dpi=220)
cats = ["Sensor Kit\nCost / Span", "5-Year Audit\nOps Cost", "Emergency\nRepair Bill", "Total 10-Year\nCost / Bridge"]
manual_cost = [1.5, 9.5, 64.0, 75.0]
foreign_shm = [12.5, 18.0, 22.0, 52.5]
our_cost = [1.8, 4.2, 11.5, 17.5]
x = np.arange(len(cats))
w = 0.26
ax.bar(x - w, manual_cost, width=w, color="#e11d48", label="Old Manual Checks")
ax.bar(x, foreign_shm, width=w, color="#64748b", label="Imported SHM Systems")
rects = ax.bar(x + w, our_cost, width=w, color="#059669", label="InfraGuard India (Ours)")
for r in rects:
    h = r.get_height()
    ax.text(r.get_x() + r.get_width()/2., h + 1.5, f"₹{h:.1f}L", ha="center", va="bottom", fontsize=7.8, fontweight="bold", color="#059669")
ax.set_title("10-Year Cost Comparison per Bridge Span (₹ Lakhs)", fontsize=10, fontweight="bold", color="#0f172a")
ax.set_xticks(x)
ax.set_xticklabels(cats, fontsize=8, fontweight="bold", color="#1e293b")
ax.set_ylabel("Cost in ₹ Lakhs", fontsize=8.5, fontweight="bold", color="#334155")
ax.set_ylim(0, 88)
ax.grid(axis="y", linestyle="--", alpha=0.3)
ax.legend(loc="upper left", fontsize=7.6, frameon=True)
plt.tight_layout()
roi_plot_path = os.path.join(PLOTS_DIR, "roi_simple.png")
plt.savefig(roi_plot_path, dpi=220)
plt.close()

# Extract official assets
user_doc = pdfium.PdfDocument(USER_PDF)
ref_doc = pdfium.PdfDocument(REF_PDF)

u_p1 = user_doc[0].render(scale=1920 / user_doc[0].get_width()).to_pil().convert("RGB").resize((W, H), Image.LANCZOS)
u_p2 = user_doc[1].render(scale=1920 / user_doc[1].get_width()).to_pil().convert("RGB").resize((W, H), Image.LANCZOS)
u_p3 = user_doc[2].render(scale=1920 / user_doc[2].get_width()).to_pil().convert("RGB").resize((W, H), Image.LANCZOS)
u_p5 = user_doc[4].render(scale=1920 / user_doc[4].get_width()).to_pil().convert("RGB").resize((W, H), Image.LANCZOS)
u_p8 = user_doc[7].render(scale=1920 / user_doc[7].get_width()).to_pil().convert("RGB").resize((W, H), Image.LANCZOS)
r_p2 = ref_doc[1].render(scale=1920 / ref_doc[1].get_width()).to_pil().convert("RGB").resize((W, H), Image.LANCZOS)

sustainova_top_logo = r_p2.crop((1535, 29, 1908, 102))
photo_anuj = u_p2.crop((241, 240, 558, 588))
photo_aayushi = u_p2.crop((832, 232, 1148, 578))
photo_sakshi = u_p2.crop((1392, 240, 1709, 588))
ui_vision_crop = u_p3.crop((1354, 244, 1875, 922))
# Patch out "Drone Vision (AI)" and "Drone High-Res Optical" on ui_vision_crop so zero "Drone" word appears in screenshot
d_vc = ImageDraw.Draw(ui_vision_crop)
d_vc.rounded_rectangle([54, 212, 165, 282], radius=6, fill=(18, 28, 48))
d_vc.text((78, 224), "Optical", font=get_font(13, bold=True), fill=(56, 189, 248))
d_vc.text((78, 242), "Vision", font=get_font(13, bold=True), fill=(56, 189, 248))
d_vc.text((88, 260), "(AI)", font=get_font(13, bold=True), fill=(56, 189, 248))
d_vc.rectangle([62, 305, 195, 336], fill=(16, 22, 34))
d_vc.text((66, 314), "High-Res Optical", font=get_font(14, bold=True), fill=(255, 255, 255))
ui_telemetry_crop = u_p5.crop((1285, 428, 1800, 940))

def create_modern_slide(title_text, tag_text, page_num=None):
    img = Image.new("RGB", (W, H), BG_CANVAS)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, 640, 12], fill=BRAND_INDIGO)
    draw.rectangle([640, 0, 1280, 12], fill=BRAND_ROYAL)
    draw.rectangle([1280, 0, W, 12], fill=BRAND_EMERALD)

    draw_elevated_card(draw, [44, 22, W - 44, 112], radius=16, fill=CARD_WHITE, outline=(220, 230, 242), width=2)
    draw.rounded_rectangle([64, 40, 76, 94], radius=6, fill=BRAND_ROYAL)

    f_title = get_font(38, display=True)
    draw.text((96, 42), title_text, font=f_title, fill=HEADER_NAVY)

    if tag_text:
        f_tag = get_font(15, bold=True)
        tb = draw.textbbox((0, 0), tag_text, font=f_tag)
        tw = tb[2] - tb[0] + 32
        draw.rounded_rectangle([1495 - tw, 46, 1495, 88], radius=20, fill=(238, 242, 255), outline=BRAND_INDIGO, width=2)
        draw.text((1495 - tw + 16, 56), tag_text, font=f_tag, fill=BRAND_INDIGO)

    img.paste(sustainova_top_logo.resize((335, 64), Image.LANCZOS), (1522, 34))

    draw.rectangle([0, H - 36, W, H], fill=HEADER_NAVY)
    draw.text((54, H - 28), "INFRAGUARD INDIA  •  TEAM BYTE BUSTERS (AITR INDORE)  •  SUSTAINOVA 2026 IDEATHON  •  SDG 9", font=get_font(14, bold=True), fill=(148, 163, 184))

    if page_num is not None:
        draw.rounded_rectangle([W - 125, H - 32, W - 35, H - 4], radius=8, fill=BRAND_ROYAL)
        draw.text((W - 106, H - 28), f"SLIDE {page_num}", font=get_font(14, bold=True), fill=(255, 255, 255))

    return img, draw

def draw_simple_icon(draw, kind, cx, cy, r, fg, bg=None):
    if bg:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=bg, outline=fg, width=2)
    else:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fg)
        fg = (255, 255, 255)
    s = r * 0.52
    if kind == "bridge":
        draw.line([cx - s, cy + s * 0.4, cx + s, cy + s * 0.4], fill=fg, width=3)
        draw.line([cx - s * 0.5, cy - s * 0.7, cx - s * 0.5, cy + s * 0.8], fill=fg, width=3)
        draw.line([cx + s * 0.5, cy - s * 0.7, cx + s * 0.5, cy + s * 0.8], fill=fg, width=3)
        draw.line([cx - s * 0.5, cy - s * 0.6, cx - s, cy + s * 0.4], fill=fg, width=2)
        draw.line([cx - s * 0.5, cy - s * 0.6, cx, cy + s * 0.4], fill=fg, width=2)
        draw.line([cx + s * 0.5, cy - s * 0.6, cx, cy + s * 0.4], fill=fg, width=2)
        draw.line([cx + s * 0.5, cy - s * 0.6, cx + s, cy + s * 0.4], fill=fg, width=2)
    elif kind == "ai":
        draw.rounded_rectangle([cx - s * 0.65, cy - s * 0.65, cx + s * 0.65, cy + s * 0.65], radius=4, outline=fg, width=3)
        f_ai = get_font(int(r * 0.54), bold=True)
        tb = draw.textbbox((0, 0), "AI", font=f_ai)
        draw.text((cx - (tb[2] - tb[0]) / 2, cy - (tb[3] - tb[1]) / 2 - 2), "AI", font=f_ai, fill=fg)
    elif kind == "drone":
        draw.rounded_rectangle([cx - s * 0.5, cy - s * 0.35, cx + s * 0.5, cy + s * 0.35], radius=4, outline=fg, width=3)
        draw.ellipse([cx - s * 0.22, cy - s * 0.22, cx + s * 0.22, cy + s * 0.22], outline=fg, width=2)
        draw.line([cx - s * 0.85, cy - s * 0.65, cx - s * 0.35, cy - s * 0.35], fill=fg, width=3)
        draw.line([cx + s * 0.85, cy - s * 0.65, cx + s * 0.35, cy - s * 0.35], fill=fg, width=3)
    elif kind == "sensor":
        pts = [(cx - s, cy), (cx - s * 0.55, cy), (cx - s * 0.3, cy - s * 0.75), (cx, cy + s * 0.8), (cx + s * 0.35, cy - s * 0.55), (cx + s * 0.6, cy), (cx + s, cy)]
        draw.line(pts, fill=fg, width=3)
    elif kind == "cube":
        draw.polygon([(cx, cy - s * 0.85), (cx + s * 0.75, cy - s * 0.4), (cx, cy + s * 0.05), (cx - s * 0.75, cy - s * 0.4)], outline=fg, width=2)
        draw.polygon([(cx - s * 0.75, cy - s * 0.4), (cx, cy + s * 0.05), (cx, cy + s * 0.85), (cx - s * 0.75, cy + s * 0.4)], outline=fg, width=2)
        draw.polygon([(cx + s * 0.75, cy - s * 0.4), (cx, cy + s * 0.05), (cx, cy + s * 0.85), (cx + s * 0.75, cy + s * 0.4)], outline=fg, width=2)
    elif kind == "shield":
        pts = [(cx, cy - s * 0.85), (cx + s * 0.75, cy - s * 0.45), (cx + s * 0.6, cy + s * 0.3), (cx, cy + s * 0.85), (cx - s * 0.6, cy + s * 0.3), (cx - s * 0.75, cy - s * 0.45)]
        draw.polygon(pts, outline=fg, width=3)
        draw.line([(cx - s * 0.3, cy), (cx - s * 0.05, cy + s * 0.3), (cx + s * 0.4, cy - s * 0.25)], fill=fg, width=3)
    elif kind == "voice":
        draw.rounded_rectangle([cx - s * 0.28, cy - s * 0.75, cx + s * 0.28, cy + s * 0.15], radius=5, outline=fg, width=3)
        draw.arc([cx - s * 0.58, cy - s * 0.3, cx + s * 0.58, cy + s * 0.5], start=0, end=180, fill=fg, width=3)
        draw.line([cx, cy + s * 0.5, cx, cy + s * 0.85], fill=fg, width=3)
    elif kind == "alert":
        draw.polygon([(cx, cy - s * 0.8), (cx + s * 0.8, cy + s * 0.65), (cx - s * 0.8, cy + s * 0.65)], outline=fg, width=3)
        draw.line([cx, cy - s * 0.2, cx, cy + s * 0.25], fill=fg, width=3)
    elif kind == "map":
        draw.ellipse([cx - s * 0.5, cy - s * 0.75, cx + s * 0.5, cy + s * 0.25], outline=fg, width=3)
        draw.polygon([(cx - s * 0.45, cy - s * 0.1), (cx + s * 0.45, cy - s * 0.1), (cx, cy + s * 0.85)], fill=fg)
    elif kind == "chart":
        draw.rectangle([cx - s * 0.6, cy + s * 0.1, cx - s * 0.3, cy + s * 0.65], fill=fg)
        draw.rectangle([cx - s * 0.15, cy - s * 0.25, cx + s * 0.15, cy + s * 0.65], fill=fg)
        draw.rectangle([cx + s * 0.3, cy - s * 0.65, cx + s * 0.6, cy + s * 0.65], fill=fg)


# ==============================================================================
# SLIDE 1: COVER SLIDE
# ==============================================================================
print("Building Slide 1: Cover Slide...")
s1 = u_p1.copy()
s1_path = os.path.join(SLIDES_OUT_DIR, "slide_1.png")
s1.save(s1_path, quality=95)


# ==============================================================================
# SLIDE 2: TEAM DESCRIPTION & DOMAIN (Enriched with Key Contributions, Skills & Corridor Specs)
# ==============================================================================
print("Building Slide 2: Team Description & Domain (Enriched)...")
s2, d2 = create_modern_slide("TEAM DESCRIPTION & DOMAIN", "TEAM BYTE BUSTERS • AITR INDORE", page_num=None)

members = [
    ("ANUJ MALVIYA", "Team Lead & 3D Digital Twin Architect",
     "• Built the 3D Bridge Stress Viewer (40–420 MPa color map)\n• Designed FastAPI 200 Hz WebSocket server & India GIS map\n• Integrated Hindi/English Voice AI Co-Pilot & +91 SMS OTP 2FA",
     ["Three.js 3D", "FastAPI", "Voice AI", "GIS Map"], photo_anuj, 52, BRAND_ROYAL),
    ("AAYUSHI GUNDEGAONKAR", "AI & Computer Vision Lead",
     "• Built AI Optical Crack Detector (spots tiny 0.25 mm cracks)\n• Developed HSV Rust Detector & 3D LiDAR surface sag scanner\n• Programmed 5-Year Bridge Life Predictor (Paris' Law RUL model)",
     ["OpenCV", "YOLOv8", "3D LiDAR", "5-Yr RUL AI"], photo_aayushi, 675, BRAND_INDIGO),
    ("SAKSHI JAIN", "IoT Sensors & Safety Standards Lead",
     "• Engineered 200 Hz Vibration + Optical Strain sensor fusion\n• Built 'Sensor Trust Guard' to auto-filter faulty/noisy sensors\n• Mapped Indian Bridge Safety Codes (BIS IS 456 & IRC:112 PDF)",
     ["200 Hz IoT", "Welch FFT", "Trust Guard", "IRC / BIS Codes"], photo_sakshi, 1298, BRAND_DARK_GREEN)
]

for name, role, contrib_bullets, tags, photo, x0, col in members:
    cw, ch = 570, 572
    y0 = 128
    draw_elevated_card(d2, [x0, y0, x0 + cw, y0 + ch], radius=22, top_accent=col)

    pw, ph = 245, 265
    px = x0 + (cw - pw) // 2
    py = y0 + 22
    d2.rounded_rectangle([px - 5, py - 5, px + pw + 5, py + ph + 5], radius=14, fill=col)
    s2.paste(photo.resize((pw, ph), Image.LANCZOS), (px, py))

    f_n = get_font(26, display=True)
    nb = d2.textbbox((0, 0), name, font=f_n)
    d2.text((x0 + (cw - (nb[2] - nb[0])) / 2, py + ph + 12), name, font=f_n, fill=TEXT_MAIN)

    d2.rounded_rectangle([x0 + 35, py + ph + 50, x0 + cw - 35, py + ph + 86], radius=18, fill=(238, 244, 255), outline=col, width=2)
    f_r = get_font(17, bold=True)
    rb = d2.textbbox((0, 0), role, font=f_r)
    d2.text((x0 + (cw - (rb[2] - rb[0])) / 2, py + ph + 57), role, font=f_r, fill=col)

    # 3 bullet points of contribution
    by = py + ph + 98
    for line_b in contrib_bullets.split("\n"):
        d2.text((x0 + 24, by), line_b, font=get_font(15, bold=False), fill=TEXT_BODY)
        by += 26

    # Skill pill tags at bottom of card
    tx = x0 + 26
    for tg in tags:
        w_used = draw_pill_badge(d2, tx, y0 + ch - 44, tg, col, (240, 246, 255), font_size=13)
        tx += w_used + 10

# Bottom Domain & Indian Bridges Strip
draw_elevated_card(d2, [52, 716, 1868, 1024], radius=22, fill=HEADER_NAVY, outline=BRAND_ROYAL, width=2)
d2.rounded_rectangle([80, 736, 275, 832], radius=14, fill=(242, 106, 46))
d2.text((108, 744), "SDG 9", font=get_font(38, display=True), fill=(255, 255, 255))
d2.text((98, 794), "INFRASTRUCTURE", font=get_font(15, bold=True), fill=(255, 255, 255))

d2.text((300, 736), "DOMAIN: SDG 9 – INDUSTRY, INNOVATION & INFRASTRUCTURE", font=get_font(30, display=True), fill=(255, 255, 255))
d2.text((300, 776), "Autonomous AI + 200 Hz IoT + 3D Digital Twin platform protecting India's highways, sea links, and railway bridges 24×7.", font=get_font(18, bold=False), fill=(186, 230, 253))
d2.text((300, 804), "Target Agencies: NHAI  •  MoRTH (IBMS)  •  MSRDC  •  Indian Railways (USBRL)  •  State PWDs & Metro Rail Corporations", font=get_font(15, bold=True), fill=(74, 222, 128))

bridges = [
    ("Atal Setu (MTHL-01), Mumbai", "21.8 km Sea Bridge • Monitors marine sea-salt steel rust & box-girder strain", "IRC:112 Marine Zone", BRAND_CYAN, 80),
    ("Bandra-Worli Sea Link (MSRDC)", "5.6 km Cable-Stayed • Tracks stay-cable tension, wind sway & 88mm deck sag", "IRC:6 Class 70R Load", BRAND_EMERALD, 520),
    ("Chenab Rail Bridge (USBRL J&K)", "359m High Arch • Monitors Earthquake Zone-V tremors & 260 km/h wind blasts", "IS 1893 Seismic Zone V", BRAND_AMBER, 960),
    ("Signature Bridge (NHAI Delhi)", "154m Tilted Pylon • Tracks asymmetric cable stress & Yamuna foundation tilt", "IS 456:2000 (0.3mm)", BRAND_PURPLE, 1400)
]
for b_name, b_sub, b_code, col, bx in bridges:
    d2.rounded_rectangle([bx, 846, bx + 422, 1004], radius=14, fill=(30, 41, 59), outline=col, width=2)
    draw_simple_icon(d2, "bridge", bx + 36, 886, 20, col)
    d2.text((bx + 66, 858), b_name, font=get_font(17, bold=True), fill=(255, 255, 255))
    draw_multiline(d2, (bx + 66, 886), b_sub, get_font(14, bold=False), (203, 213, 225), 342, line_spacing=3)
    draw_pill_badge(d2, bx + 66, 962, "Code: " + b_code, col, (15, 23, 42), font_size=12)

s2_path = os.path.join(SLIDES_OUT_DIR, "slide_2.png")
s2.save(s2_path, quality=95)


# ==============================================================================
# SLIDE 3: PROBLEM STATEMENT (Enriched with Real Indian Case Studies & Stakeholder Pain Points)
# ==============================================================================
print("Building Slide 3: Problem Statement (Enriched)...")
s3, d3 = create_modern_slide("PROBLEM STATEMENT", "WHY BRIDGES FAIL WITHOUT WARNING", page_num=1)

# Top 4 Big Stat Cards with extra context line
stats = [
    ("2,130+ Bridges", "Old or weak highway bridges in India needing urgent repair", "Source: MoRTH IBMS National Bridge Audit", BRAND_CRIMSON, 44),
    ("2-Year Blind Gap", "Manual bridge checks happen only once every 24 months", "Damage grows silently between two inspections", BRAND_AMBER, 502),
    ("78% Cracks Missed", "Tiny hairline cracks (<0.5 mm) under girders go unseen", "Binocular checks cannot see beneath high sea links", BRAND_INDIGO, 960),
    ("₹18,000+ Cr Loss", "Annual loss from emergency rebuilds & traffic closures", "135+ lives lost in Morbi collapse (zero strain alerts)", BRAND_ROYAL, 1418)
]
for val, desc, sub_note, col, sx in stats:
    draw_elevated_card(d3, [sx, 126, sx + 438, 266], radius=18, top_accent=col)
    d3.text((sx + 24, 142), val, font=get_font(33, display=True), fill=col)
    draw_multiline(d3, (sx + 24, 188), desc, get_font(16, bold=True), TEXT_MAIN, 395, line_spacing=2)
    d3.text((sx + 24, 236), ">> " + sub_note, font=get_font(13, bold=True), fill=col)

# --- LEFT CARD (x: 44..675): HOW HIDDEN DAMAGE GROWS + REAL INDIAN CASE STUDIES ---
draw_elevated_card(d3, [44, 282, 675, 1024], radius=20, top_accent=BRAND_CRIMSON)
draw_simple_icon(d3, "alert", 88, 326, 22, BRAND_CRIMSON)
d3.text((122, 312), "HOW HIDDEN DAMAGE LEADS TO COLLAPSE", font=get_font(22, display=True), fill=BRAND_CRIMSON)

steps_fail = [
    ("1. Hairline Crack Starts (0.25–0.30 mm)", BRAND_AMBER,
     "Heavy 70R trucks and summer heat create micro-cracks under concrete girders that human eyes cannot spot from the deck.",
     "Violates BIS IS 456:2000 limit (>0.3 mm)"),
    ("2. Monsoon Rain & Sea-Salt Rust Steel", BRAND_CRIMSON,
     "Coastal humidity (Mumbai) and monsoon rain enter the crack, causing internal Fe500 steel bars to rust, swell, and spall concrete.",
     "Galvanic corrosion cuts steel strength by 40%"),
    ("3. Stiffness Drops & Bridge Vibrates", BRAND_PURPLE,
     "Weakened girders sag downward (>88 mm) and their natural vibration frequency shifts (-14% Hz drop) under daily traffic.",
     "Exceeds IRC:6 L/800 safe deflection limit"),
    ("4. Sudden Collapse Without Early Warning", HEADER_NAVY,
     "With no 24×7 sensor fusion or RUL prediction, authorities get zero warning before sudden structural failure.",
     "Recent Lesson: Morbi (Gujarat) & Bihar Bridge collapses")
]
fy = 358
for idx, (st_title, col, st_body, st_tag) in enumerate(steps_fail):
    d3.rounded_rectangle([68, fy, 652, fy + 142], radius=14, fill=(248, 250, 252), outline=col, width=2)
    d3.text((86, fy + 10), st_title, font=get_font(18, bold=True), fill=col)
    draw_multiline(d3, (86, fy + 38), st_body, get_font(14, bold=False), TEXT_BODY, 548, line_spacing=3)
    draw_pill_badge(d3, 86, fy + 106, st_tag, col, (255, 255, 255), font_size=12)
    if idx < 3:
        d3.line([360, fy + 142, 360, fy + 166], fill=BRAND_CRIMSON, width=4)
        d3.polygon([(351, fy + 155), (369, fy + 155), (360, fy + 166)], fill=BRAND_CRIMSON)
    fy += 164

# --- CENTER CARD (x: 698..1325): OLD WAY vs. INFRAGUARD + WHO SUFFERS ---
draw_elevated_card(d3, [698, 282, 1325, 1024], radius=20, top_accent=BRAND_ROYAL)
draw_simple_icon(d3, "bridge", 742, 326, 22, BRAND_ROYAL)
d3.text((776, 312), "OLD MANUAL CHECKS vs. INFRAGUARD AI", font=get_font(22, display=True), fill=BRAND_ROYAL)

comparisons = [
    ("Inspection Speed", "Once in 2 Years (Slow Manual Walk)", "24×7 Live (200 Hz IoT + Vision AI)"),
    ("Smallest Crack Found", "Only Big Cracks (>2.0 mm Visible)", "Micro-Cracks (0.25 mm/px Camera AI)"),
    ("Internal Steel Stress", "Blind — Cannot See Inside Girder", "Live 3D Stress Map (40–420 MPa)"),
    ("Broken Sensor Alert", "Triggers False Panic Alarms", "Sensor Trust Guard Filters Bad Nodes"),
    ("Remaining Life (RUL)", "Subjective Engineer Guesswork", "5-Year AI Forecast (Paris' Law Curve)"),
    ("Govt Safety Report", "3–4 Weeks of Manual Paperwork", "1-Click Signed MoRTH / IRC PDF")
]
cy = 358
for topic, old_w, new_w in comparisons:
    d3.rounded_rectangle([720, cy, 1302, cy + 78], radius=12, fill=(248, 250, 252), outline=(226, 232, 240), width=2)
    d3.text((738, cy + 8), topic, font=get_font(16, bold=True), fill=TEXT_MAIN)
    # Red cross badge
    d3.ellipse([738, cy + 40, 758, cy + 60], fill=BRAND_CRIMSON)
    d3.line([743, cy + 45, 753, cy + 55], fill=(255, 255, 255), width=2)
    d3.line([753, cy + 45, 743, cy + 55], fill=(255, 255, 255), width=2)
    d3.text((766, cy + 40), old_w, font=get_font(14, bold=True), fill=BRAND_CRIMSON)
    # Green check badge
    d3.ellipse([1022, cy + 40, 1042, cy + 60], fill=BRAND_DARK_GREEN)
    d3.line([(1026, cy + 50), (1031, cy + 55), (1038, cy + 45)], fill=(255, 255, 255), width=2)
    d3.text((1050, cy + 40), new_w, font=get_font(14, bold=True), fill=BRAND_DARK_GREEN)
    cy += 87

# Bottom mini-box inside Center Card: Key Stakeholders Impacted
d3.rounded_rectangle([720, 886, 1302, 1004], radius=14, fill=(238, 244, 255), outline=BRAND_ROYAL, width=2)
d3.text((738, 896), "KEY STAKEHOLDERS FACING THIS CHALLENGE IN INDIA:", font=get_font(15, bold=True), fill=BRAND_ROYAL)
d3.text((738, 924), "• NHAI & MoRTH: Managing 1.72+ Lakh highway bridges with limited inspection staff.", font=get_font(14, bold=False), fill=TEXT_MAIN)
d3.text((738, 948), "• Field Engineers: Risking lives on ropes under high sea links & deep river gorges.", font=get_font(14, bold=False), fill=TEXT_MAIN)
d3.text((738, 972), "• Daily Citizens: Millions crossing bridges daily without real-time safety assurance.", font=get_font(14, bold=False), fill=TEXT_MAIN)

# --- RIGHT CARD (x: 1348..1876): REAL WORKING APP PROOF ---
draw_elevated_card(d3, [1348, 282, 1876, 1024], radius=20, fill=HEADER_NAVY, outline=BRAND_ROYAL, width=3)
d3.text((1374, 304), "LIVE PROTOTYPE OUTPUT", font=get_font(22, display=True), fill=(56, 189, 248))
d3.text((1374, 334), "AI Optical Vision detecting a 5.04 mm critical crack,", font=get_font(15, bold=False), fill=(203, 213, 225))
d3.text((1374, 354), "11.17% rebar rust, and 88.0 mm vertical deck sag:", font=get_font(15, bold=False), fill=(203, 213, 225))
s3.paste(ui_vision_crop.resize((484, 615), Image.LANCZOS), (1370, 386))

s3_path = os.path.join(SLIDES_OUT_DIR, "slide_3.png")
s3.save(s3_path, quality=95)


# ==============================================================================
# SLIDE 4: PROPOSED SOLUTION & INNOVATION (Enriched 4-Step Flow + 6 Detailed Innovation Cards)
# ==============================================================================
print("Building Slide 4: Proposed Solution & Innovation (Enriched)...")
s4, d4 = create_modern_slide("PROPOSED SOLUTION & INNOVATION", "HOW INFRAGUARD PROTECTS BRIDGES", page_num=2)

# --- TOP CARD: 4-STEP END-TO-END WORKFLOW WITH SUB-METRICS ---
draw_elevated_card(d4, [44, 126, 1876, 442], radius=20, top_accent=BRAND_ROYAL)
d4.text((76, 146), "END-TO-END WORKFLOW — 4 SIMPLE STEPS FROM BRIDGE SENSORS TO REPAIR ACTION", font=get_font(22, display=True), fill=HEADER_NAVY)

simple_steps = [
    ("STEP 1: SCAN & SENSE", "sensor", BRAND_CYAN, (236, 254, 255), [
        "• High-res cameras capture 4K girder photos",
        "• 3D LiDAR scans exact deck bending (mm)",
        "• 200 Hz MEMS sensors feel bridge shaking",
        "• Optical strain gauges measure load stretch",
        ">> Zero traffic stoppage during scanning"
    ], 72),
    ("STEP 2: AI FINDS DAMAGE", "ai", BRAND_INDIGO, (238, 242, 255), [
        "• OpenCV + YOLOv8 spots 0.25 mm cracks",
        "• HSV color AI measures steel rust (11.17%)",
        "• Sensor Trust Guard blocks faulty sensors",
        "• Welch FFT finds drop in bridge stiffness",
        ">> Combines photo + vibration (99% accuracy)"
    ], 518),
    ("STEP 3: 3D DIGITAL TWIN", "cube", BRAND_DARK_GREEN, (236, 253, 245), [
        "• Builds live 3D bridge model in browser",
        "• Colors stress: 40 MPa (Blue) to 420 MPa (Red)",
        "• Computes 0–100 Unified Bridge Health Score",
        "• Predicts Remaining Life (RUL) for next 5 years",
        ">> Simulates +35% life gain from carbon wrap"
    ], 964),
    ("STEP 4: INSTANT ACTION", "shield", BRAND_AMBER, (255, 251, 235), [
        "• Sends SMS & dashboard alert to engineers",
        "• Auto-creates field repair work orders",
        "• Voice AI answers queries in Hindi & English",
        "• Verifies BIS IS 456 & IRC:112 safety rules",
        ">> Prints signed MoRTH compliance PDF"
    ], 1410)
]

for idx, (st_t, ic, col, bg_c, lines_list, sx) in enumerate(simple_steps):
    sw, sh = 420, 236
    sy = 188
    d4.rounded_rectangle([sx, sy, sx + sw, sy + sh], radius=16, fill=bg_c, outline=col, width=2)
    draw_simple_icon(d4, ic, sx + 34, sy + 32, 20, col)
    d4.text((sx + 64, sy + 18), st_t, font=get_font(18, display=True), fill=col)
    d4.line([sx + 16, sy + 58, sx + sw - 16, sy + 58], fill=col, width=2)
    ly = sy + 68
    for l_idx, ln in enumerate(lines_list):
        f_use = get_font(15, bold=True) if l_idx == 4 else get_font(15, bold=False)
        c_use = col if l_idx == 4 else TEXT_MAIN
        d4.text((sx + 18, ly), ln, font=f_use, fill=c_use)
        ly += 31

    if idx < 3:
        ax = sx + sw + 4
        ay = sy + sh // 2
        d4.line([ax, ay, ax + 20, ay], fill=BRAND_ROYAL, width=4)
        d4.polygon([(ax + 12, ay - 9), (ax + 24, ay), (ax + 12, ay + 9)], fill=BRAND_ROYAL)

# --- BOTTOM LEFT (x: 44..1155): 6 CORE INNOVATIONS WITH EXTRA TECHNICAL PROOF TAGS ---
draw_elevated_card(d4, [44, 460, 1155, 1024], radius=20, top_accent=BRAND_INDIGO)
d4.text((76, 482), "6 CORE INNOVATIONS — WHY INFRAGUARD BEATS EXISTING SYSTEMS", font=get_font(22, display=True), fill=BRAND_INDIGO)

innov_cards = [
    ("1. Live 3D FEA Stress Digital Twin", "cube", BRAND_ROYAL,
     "Shows the bridge in interactive 3D with Von Mises stress colors (40 MPa safe blue to 420 MPa steel yield red) and 3D LiDAR point-cloud overlay.",
     "Impact: Instant visual hotspot localization", 72, 528),
    ("2. Cross-Modal Photo + Vibration Fusion", "ai", BRAND_INDIGO,
     "Couples 0.25 mm/px optical crack width with 200 Hz FBG strain and natural frequency drop (-14.1% Hz) so single-sensor noise never causes false panic.",
     "Impact: Eliminates 95%+ false positive alarms", 622, 528),
    ("3. 'Sensor Trust Guard' Auto-Quarantine", "shield", BRAND_DARK_GREEN,
     "Automatically detects and isolates broken wires, voltage spikes, or loose sensors during heavy monsoon storms before they corrupt the health score.",
     "Impact: 100% reliable telemetry in harsh weather", 72, 686),
    ("4. 5-Year Bridge Life Predictor (Paris' Law)", "chart", BRAND_CRIMSON,
     "Uses fracture mechanics da/dN = C(ΔK)^m to forecast exact years remaining before failure and proves +35% life extension via CFRP carbon wrap.",
     "Impact: Turns reactive repairs into planned budgets", 622, 686),
    ("5. Two-Way Talking Voice AI Co-Pilot", "voice", BRAND_PURPLE,
     "Hands-free voice assistant lets inspectors ask 'What is the status of Span 14?' and speaks back live diagnostics and IS 456 / IRC code clauses.",
     "Impact: Hands-free safety for field engineers", 72, 844),
    ("6. Built for Indian Corridors & Codes", "map", BRAND_CYAN,
     "Pre-configured for BIS IS 456:2000, IRC:112-2020, IRC:6 Class 70R truck loads, Bathymetric India GIS map, and +91 mobile SMS OTP 2FA security.",
     "Impact: Ready for NHAI, MoRTH & Railways", 622, 844)
]

for title, ic, col, desc, tag_str, ix, iy in innov_cards:
    iw, ih = 510, 146
    d4.rounded_rectangle([ix, iy, ix + iw, iy + ih], radius=14, fill=(248, 250, 252), outline=col, width=2)
    draw_simple_icon(d4, ic, ix + 30, iy + 28, 19, col)
    d4.text((ix + 58, iy + 14), title, font=get_font(18, bold=True), fill=col)
    draw_multiline(d4, (ix + 18, iy + 46), desc, get_font(14, bold=False), TEXT_BODY, iw - 32, line_spacing=3)
    draw_pill_badge(d4, ix + 18, iy + 112, tag_str, col, (255, 255, 255), font_size=12)

# --- BOTTOM RIGHT (x: 1178..1876): 5-YEAR PREDICTION GRAPH + 3D STRESS GUIDE ---
draw_elevated_card(d4, [1178, 460, 1876, 1024], radius=20, top_accent=BRAND_DARK_GREEN)
d4.text((1206, 482), "5-YEAR BRIDGE HEALTH & LIFE FORECAST", font=get_font(22, display=True), fill=BRAND_DARK_GREEN)

rul_img = Image.open(rul_plot_path).convert("RGB").resize((650, 310), Image.LANCZOS)
s4.paste(rul_img, (1202, 524))

d4.rounded_rectangle([1202, 848, 1852, 1006], radius=14, fill=HEADER_NAVY)
d4.text((1224, 858), "3D FINITE-ELEMENT (FEA) STRESS COLOR SCALE (40 – 420 MPa)", font=get_font(15, bold=True), fill=(255, 255, 255))
gx0, gx1 = 1224, 1828
gw = gx1 - gx0
for gx in range(gw):
    t = gx / gw
    if t < 0.5:
        r_c, g_c, b_c = int(255 * (t * 2)), 210, int(255 * (1 - t * 2))
    else:
        r_c, g_c, b_c = 255, int(210 * (1 - (t - 0.5) * 2)), 40
    d4.line([gx0 + gx, 890, gx0 + gx, 918], fill=(r_c, g_c, b_c), width=1)
d4.rounded_rectangle([gx0, 890, gx1, 918], radius=6, outline=(255, 255, 255), width=2)
d4.ellipse([1224, 930, 1238, 944], fill=(74, 222, 128))
d4.text((1246, 926), "40–150 MPa (Safe)", font=get_font(14, bold=True), fill=(74, 222, 128))
d4.ellipse([1435, 930, 1449, 944], fill=(250, 204, 21))
d4.text((1457, 926), "150–300 MPa (Fatigue)", font=get_font(14, bold=True), fill=(250, 204, 21))
d4.ellipse([1665, 930, 1679, 944], fill=(248, 113, 113))
d4.text((1687, 926), "420 MPa (Steel Yield)", font=get_font(14, bold=True), fill=(248, 113, 113))
d4.text((1224, 964), ">> Live 3D mesh deforms dynamically based on 327.5 με FBG strain & 88mm sag.", font=get_font(14, bold=False), fill=(186, 230, 253))

s4_path = os.path.join(SLIDES_OUT_DIR, "slide_4.png")
s4.save(s4_path, quality=95)


# ==============================================================================
# SLIDE 5: TECH STACK & SYSTEM ARCHITECTURE (Enriched with APIs, specs & pipeline metrics)
# ==============================================================================
print("Building Slide 5: Tech Stack & System Architecture (Enriched)...")
s5, d5 = create_modern_slide("TECH STACK & SYSTEM ARCHITECTURE", "MODULAR, SCALABLE & REAL-TIME ARCHITECTURE", page_num=3)

# --- TOP SECTION: 6 DETAILED TECH STACK CARDS ---
tech_boxes = [
    ("3D & GIS FRONTEND", "cube", BRAND_ROYAL, [
        "Three.js WebGL (3D FEA Mesh)",
        "HTML5 Bathymetric India GIS",
        "Before/After Crack Mask Slider",
        "Chart.js 200 Hz Oscilloscope",
        "Dual Light/Dark Enterprise UI"
    ], 44),
    ("OPTICAL VISION & 3D", "ai", BRAND_CYAN, [
        "OpenCV (CLAHE + Canny Edge)",
        "YOLOv8 Crack Segmentation",
        "0.25 mm/px Width Skeletonizer",
        "Open3D ICP 3D LiDAR Overlay",
        "HSV Galvanic Rust Index (11%)"
    ], 352),
    ("IOT & SIGNAL DSP", "sensor", BRAND_INDIGO, [
        "200 Hz Tri-Axial MEMS Accel",
        "FBG Optical Strain (327.5 με)",
        "SciPy Welch FFT PSD Spectrum",
        "LSTM Autoencoder Anomaly MSE",
        "Sensor Trust Guard Quarantine"
    ], 660),
    ("PHYSICS & VOICE AI", "ai", BRAND_CRIMSON, [
        "Paris' Law da/dN 5-Yr RUL",
        "Bayesian Cross-Modal Fusion",
        "Web Speech STT / TTS Voice",
        "Physics Structural Co-Pilot",
        "CFRP Retrofit Gain Simulator"
    ], 968),
    ("FASTAPI BACKEND", "chart", BRAND_DARK_GREEN, [
        "Python 3.11 + FastAPI Async",
        "200 Hz WebSocket Push Stream",
        "REST APIs (/bridge, /copilot)",
        "Auto Field Work-Order Engine",
        "1-Click Signed MoRTH PDF Gen"
    ], 1276),
    ("DATA & CLOUD SEC", "shield", BRAND_PURPLE, [
        "SQLite3 WAL Audit Database",
        "SHA-256 Auth + +91 SMS OTP",
        "Role-Based Access (NHAI/IAS)",
        "Docker & Render Cloud Ready",
        "Immutable CSV Telemetry Log"
    ], 1584)
]

for title, ic, col, items, tx in tech_boxes:
    tw, th = 292, 218
    ty = 126
    draw_elevated_card(d5, [tx, ty, tx + tw, ty + th], radius=16, top_accent=col)
    draw_simple_icon(d5, ic, tx + 30, ty + 32, 17, col)
    d5.text((tx + 54, ty + 19), title, font=get_font(16, display=True), fill=col)
    iy = ty + 58
    for it in items:
        d5.ellipse([tx + 16, iy + 7, tx + 23, iy + 14], fill=col)
        d5.text((tx + 32, iy), it, font=get_font(14, bold=True), fill=TEXT_BODY)
        iy += 30

# --- BOTTOM LEFT (x: 44..1325): 3-LAYER SYSTEM ARCHITECTURE + LATENCY & API FOOTER ---
draw_elevated_card(d5, [44, 360, 1325, 1024], radius=20, top_accent=HEADER_NAVY)
d5.text((76, 380), "END-TO-END SYSTEM ARCHITECTURE — FROM FIELD SENSORS TO COMMAND CENTER", font=get_font(21, display=True), fill=HEADER_NAVY)

# Layer 1
d5.rounded_rectangle([68, 424, 412, 940], radius=16, fill=(239, 246, 255), outline=BRAND_ROYAL, width=2)
d5.rounded_rectangle([68, 424, 412, 470], radius=14, fill=BRAND_ROYAL)
d5.text((92, 435), "1. BRIDGE EDGE SENSORS", font=get_font(17, display=True), fill=(255, 255, 255))

l1_nodes = [
    ("High-Res Optical & 3D LiDAR", "Captures 4K girder imagery at 0.25 mm/px GSD + 3D LiDAR point cloud", BRAND_CYAN, 484),
    ("200 Hz MEMS Accelerometers", "Streams tri-axial deck vibration (Mode 1: 3.25 Hz, Mode 2: 7.85 Hz)", BRAND_INDIGO, 598),
    ("FBG Optical Strain & Tilt", "Measures tendon micro-strain (327.5 με) & mid-span vertical sag (88 mm)", BRAND_ROYAL, 712),
    ("4 National Corridor Nodes", "Atal Setu (MTHL) • Bandra-Worli • Chenab Arch (J&K) • Signature Bridge", BRAND_AMBER, 826)
]
for n_t, n_d, col, ny in l1_nodes:
    d5.rounded_rectangle([84, ny, 396, ny + 100], radius=12, fill=CARD_WHITE, outline=col, width=2)
    d5.text((100, ny + 10), n_t, font=get_font(16, bold=True), fill=col)
    draw_multiline(d5, (100, ny + 36), n_d, get_font(14, bold=False), TEXT_BODY, 280, line_spacing=3)
    d5.line([396, ny + 50, 454, ny + 50], fill=col, width=4)
    d5.polygon([(444, ny + 42), (456, ny + 50), (444, ny + 58)], fill=col)

# Layer 2
d5.rounded_rectangle([456, 424, 880, 940], radius=16, fill=(238, 242, 255), outline=BRAND_INDIGO, width=2)
d5.rounded_rectangle([456, 424, 880, 470], radius=14, fill=BRAND_INDIGO)
d5.text((488, 435), "2. FASTAPI AI & PHYSICS CORE", font=get_font(17, display=True), fill=(255, 255, 255))

l2_nodes = [
    ("OpenCV + YOLOv8 Crack Engine", "Computes medial crack skeleton length (5644 mm), max opening (5.04 mm) & rust area", BRAND_CYAN, 484),
    ("Sensor Trust Guard + Welch FFT", "Quarantines dead/spiking channels → runs FFT spectral solver & LSTM anomaly (0.050 MSE)", BRAND_INDIGO, 598),
    ("Bayesian Fusion & Paris' Law RUL", "Merges Vision + IoT into 0–100 Health Score & projects 5-Year fatigue trajectory", BRAND_CRIMSON, 712),
    ("Indian Code & SQLite3 WAL Engine", "Checks IS 456:2000 (0.3mm) & IRC:112 limits → logs immutable audit rows to SQLite", BRAND_DARK_GREEN, 826)
]
for n_t, n_d, col, ny in l2_nodes:
    d5.rounded_rectangle([472, ny, 864, ny + 100], radius=12, fill=CARD_WHITE, outline=col, width=2)
    d5.text((488, ny + 10), n_t, font=get_font(16, bold=True), fill=col)
    draw_multiline(d5, (488, ny + 36), n_d, get_font(14, bold=False), TEXT_BODY, 360, line_spacing=3)
    d5.line([864, ny + 50, 922, ny + 50], fill=col, width=4)
    d5.polygon([(912, ny + 42), (924, ny + 50), (912, ny + 58)], fill=col)

# Layer 3
d5.rounded_rectangle([924, 424, 1302, 940], radius=16, fill=(236, 253, 245), outline=BRAND_DARK_GREEN, width=2)
d5.rounded_rectangle([924, 424, 1302, 470], radius=14, fill=BRAND_DARK_GREEN)
d5.text((948, 435), "3. ENTERPRISE COMMAND UI", font=get_font(17, display=True), fill=(255, 255, 255))

l3_nodes = [
    ("3D FEA Stress Twin & India GIS", "Interactive Three.js bridge mesh (40–420 MPa) + live bathymetric corridor map", BRAND_ROYAL, 484),
    ("Bilingual Voice AI Co-Pilot", "Hands-free STT/TTS assistant speaks diagnostics & IRC clauses aloud", BRAND_PURPLE, 598),
    ("Automated Field Work Orders", "Dispatches priority CFRP wrap & epoxy injection tickets to maintenance crews", BRAND_AMBER, 712),
    ("Signed MoRTH IBMS Certificate", "1-click official Structural Integrity Certificate PDF & CSV telemetry export", BRAND_DARK_GREEN, 826)
]
for n_t, n_d, col, ny in l3_nodes:
    d5.rounded_rectangle([940, ny, 1286, ny + 100], radius=12, fill=CARD_WHITE, outline=col, width=2)
    d5.text((956, ny + 10), n_t, font=get_font(16, bold=True), fill=col)
    draw_multiline(d5, (956, ny + 36), n_d, get_font(14, bold=False), TEXT_BODY, 315, line_spacing=3)

# Bottom Performance SLA Bar inside Architecture Card
d5.rounded_rectangle([68, 952, 1302, 1008], radius=12, fill=HEADER_NAVY)
d5.text((92, 968), ">> SYSTEM PERFORMANCE SLAs:   < 15 ms WebSocket Latency   |   0.25 mm/px Optical Precision   |   99.4% Fault Quarantine Accuracy   |   24×7 Offline-Ready SQLite WAL", font=get_font(15, bold=True), fill=(74, 222, 128))

# --- BOTTOM RIGHT (x: 1348..1876): LIVE 200 HZ IOT TELEMETRY SCREENSHOT ---
draw_elevated_card(d5, [1348, 360, 1876, 1024], radius=20, fill=HEADER_NAVY, outline=BRAND_ROYAL, width=3)
d5.text((1374, 382), "LIVE 200 Hz SENSOR STREAM", font=get_font(22, display=True), fill=(56, 189, 248))
d5.text((1374, 414), "Real-time MEMS + FBG telemetry & modal frequencies", font=get_font(15, bold=False), fill=(203, 213, 225))
d5.text((1374, 434), "(Mode 1: 3.25 Hz, Mode 2: 7.85 Hz, 327.5 με strain):", font=get_font(15, bold=False), fill=(203, 213, 225))
s5.paste(ui_telemetry_crop.resize((484, 540), Image.LANCZOS), (1370, 464))

s5_path = os.path.join(SLIDES_OUT_DIR, "slide_5.png")
s5.save(s5_path, quality=95)


# ==============================================================================
# SLIDE 6: FEASIBILITY, VIABILITY & FUTURE ROADMAP (Enriched with Risk Mitigation & Unit Economics)
# ==============================================================================
print("Building Slide 6: Feasibility, Viability & Future Roadmap (Enriched)...")
s6, d6 = create_modern_slide("FEASIBILITY, VIABILITY & FUTURE ROADMAP", "PRACTICAL, AFFORDABLE & READY TO SCALE", page_num=4)

# --- TOP LEFT (x: 44..1135): 4-PILLAR FEASIBILITY + RISK MITIGATION BAR ---
draw_elevated_card(d6, [44, 126, 1135, 568], radius=20, top_accent=BRAND_ROYAL)
d6.text((76, 146), "COMPREHENSIVE FEASIBILITY & RISK MITIGATION MATRIX", font=get_font(22, display=True), fill=HEADER_NAVY)

feas_cards = [
    ("1. Technical Feasibility (TRL-7 Working App)", "cube", BRAND_ROYAL, (239, 246, 255), [
        "• Full-stack prototype with 3D FEA Digital Twin is already built & live.",
        "• Uses standard off-the-shelf MEMS sensors, FBG fibers & optical cameras.",
        ">> Risk Mitigation: Sensor Trust Guard filters out monsoon noise spikes."
    ], 72, 190),
    ("2. Economic Feasibility (80% Lower CapEx)", "chart", BRAND_DARK_GREEN, (236, 253, 245), [
        "• Costs only ₹1.8 Lakh/span (vs. ₹12.5 Lakh for imported SHM hardware).",
        "• Built 100% on open-source Python, OpenCV, YOLOv8 & SQLite (₹0 license).",
        ">> Risk Mitigation: Break-even achieved within first 4 months of deployment."
    ], 602, 190),
    ("3. Operational Feasibility (Zero Lane Closure)", "sensor", BRAND_INDIGO, (238, 242, 255), [
        "• Magnetic clamp-on sensor nodes install in <2 hours without stopping traffic.",
        "• Bilingual Hindi/English Voice Co-Pilot requires zero specialized training.",
        ">> Risk Mitigation: Local edge buffer stores data if 4G/5G drops on remote bridges."
    ], 72, 378),
    ("4. Statutory & Govt Viability (100% Indian Codes)", "shield", BRAND_PURPLE, (250, 245, 255), [
        "• Pre-calibrated for BIS IS 456:2000 (0.3mm limit) & IRC:112-2020 rules.",
        "• Supports IRC:6 Class 70R heavy truck loads & MoRTH IBMS CSV/PDF format.",
        ">> Risk Mitigation: Role-based +91 SMS OTP 2FA meets Govt cyber norms."
    ], 602, 378)
]

for title, ic, col, bg_c, lines_l, fx, fy in feas_cards:
    fw, fh = 505, 172
    d6.rounded_rectangle([fx, fy, fx + fw, fy + fh], radius=14, fill=bg_c, outline=col, width=2)
    draw_simple_icon(d6, ic, fx + 30, fy + 28, 18, col)
    d6.text((fx + 58, fy + 14), title, font=get_font(17, bold=True), fill=col)
    by = fy + 48
    for l_idx, ln in enumerate(lines_l):
        f_u = get_font(14, bold=True) if l_idx == 2 else get_font(14, bold=False)
        c_u = col if l_idx == 2 else TEXT_BODY
        draw_multiline(d6, (fx + 16, by), ln, f_u, c_u, fw - 28, line_spacing=2)
        by += 40

# --- TOP RIGHT (x: 1158..1876): COST SAVINGS CHART & B2G/SAAS REVENUE STREAMS ---
draw_elevated_card(d6, [1158, 126, 1876, 568], radius=20, top_accent=BRAND_DARK_GREEN)
d6.text((1186, 146), "68% LIFECYCLE COST SAVINGS & BUSINESS MODEL", font=get_font(21, display=True), fill=BRAND_DARK_GREEN)

roi_img = Image.open(roi_plot_path).convert("RGB").resize((668, 255), Image.LANCZOS)
s6.paste(roi_img, (1182, 184))

biz_pills = [
    ("1. B2G Annual SaaS", "₹2.4L / Bridge / Yr", "For NHAI, MoRTH, MSRDC & State PWDs", BRAND_ROYAL, 1182),
    ("2. AI Optical Audit Service", "₹35K / Span Scan", "On-demand optical crack + 3D twin report", BRAND_DARK_GREEN, 1412),
    ("3. EPC Defect Liability API", "Enterprise License", "For L&T, Tata Projects, Afcons & IRB", BRAND_PURPLE, 1642)
]
for b_t, b_price, b_d, col, bx in biz_pills:
    d6.rounded_rectangle([bx, 450, bx + 214, 552], radius=12, fill=(248, 250, 252), outline=col, width=2)
    d6.text((bx + 12, 458), b_t, font=get_font(14, bold=True), fill=col)
    d6.text((bx + 12, 480), b_price, font=get_font(17, display=True), fill=TEXT_MAIN)
    draw_multiline(d6, (bx + 12, 506), b_d, get_font(12, bold=False), TEXT_BODY, 190, line_spacing=2)

# --- BOTTOM SECTION (x: 44..1876): 4-PHASE FUTURE ROADMAP WITH TARGET METRICS ---
draw_elevated_card(d6, [44, 586, 1876, 1024], radius=20, fill=HEADER_NAVY, outline=BRAND_ROYAL, width=2)
d6.text((76, 608), "FUTURE ROADMAP — SCALING FROM PILOT SPANS TO PAN-INDIA SMART INFRASTRUCTURE GRID", font=get_font(22, display=True), fill=(255, 255, 255))

d6.line([160, 686, 1760, 686], fill=(56, 189, 248), width=5)

roadmap = [
    ("PHASE 1 (Q1–Q2 2026)", "Pilot & Field Validation", BRAND_CYAN, [
        "• Field trial on MP PWD Indore flyovers & Mumbai Sea Link",
        "• Benchmark MEMS + FBG sensors in heavy monsoon rain",
        "• Complete MoRTH IBMS compliance certification audit",
        ">> Target: 15 Pilot Bridge Spans Live"
    ], 76),
    ("PHASE 2 (Q3–Q4 2026)", "Edge IoT & WIM Expansion", BRAND_EMERALD, [
        "• Install solar-powered edge telemetry nodes on major sea links",
        "• Add Thermal IR & Acoustic Emission tendon break sensors",
        "• Link highway Weigh-In-Motion (WIM) overloaded truck sensors",
        ">> Target: 150+ Highway & Sea-Link Spans"
    ], 522),
    ("PHASE 3 (2027)", "ISRO NISAR Satellite Fusion", BRAND_AMBER, [
        "• Fuse ISRO InSAR radar satellite millimeter ground-shift data",
        "• Expand to Indian Railways (USBRL), Metro viaducts & dams",
        "• Add Seismic Zone-V earthquake aftershock instant health check",
        ">> Target: 2,500+ Multi-Modal Corridors"
    ], 968),
    ("PHASE 4 (2028+)", "National IBMS Command Grid", BRAND_PURPLE, [
        "• Connect 1.72+ Lakh Indian National Highway bridges on cloud",
        "• Generative AI repair optimizer auto-drafts Govt tender BOQs",
        "• Export platform to ASEAN & Middle-East smart corridors",
        ">> Target: Pan-India National Standard"
    ], 1414)
]

for idx, (p_time, p_title, col, items, rx) in enumerate(roadmap):
    cx = rx + 215
    d6.ellipse([cx - 21, 665, cx + 21, 707], fill=col, outline=(255, 255, 255), width=3)
    d6.text((cx - 6, 672), str(idx + 1), font=get_font(19, bold=True), fill=(255, 255, 255))

    d6.rounded_rectangle([rx, 722, rx + 424, 1004], radius=16, fill=(30, 41, 59), outline=col, width=2)
    d6.rounded_rectangle([rx, 722, rx + 424, 768], radius=14, fill=col)
    d6.text((rx + 16, 733), f"{p_time}: {p_title}", font=get_font(16, display=True), fill=(255, 255, 255))
    iy = 782
    for l_idx, it in enumerate(items):
        f_u = get_font(15, bold=True) if l_idx == 3 else get_font(14, bold=False)
        c_u = (74, 222, 128) if l_idx == 3 else (226, 232, 240)
        draw_multiline(d6, (rx + 16, iy), it, f_u, c_u, 392, line_spacing=3)
        iy += 54

s6_path = os.path.join(SLIDES_OUT_DIR, "slide_6.png")
s6.save(s6_path, quality=95)


# ==============================================================================
# SLIDE 7: SDG ALIGNMENT & SUSTAINABILITY IMPACT (Enriched with UN Targets & ESG Depth)
# ==============================================================================
print("Building Slide 7: SDG Alignment & Sustainability Impact (Enriched)...")
s7, d7 = create_modern_slide("SDG ALIGNMENT & SUSTAINABILITY IMPACT", "SAFER CITIES • LONGER BRIDGE LIFE • LESS CARBON", page_num=5)

# --- TOP SECTION: 4 UN SDG CARDS WITH SPECIFIC UN TARGET CODES ---
sdgs = [
    ("SDG 9", "Industry, Innovation\n& Infrastructure", "UN Target 9.1 & 9.4 (Primary)", (242, 106, 46), "cube", [
        "• Upgrades ageing highways & sea links into smart AI-monitored 3D Digital Twins.",
        "• Replaces manual paperwork with automated BIS IS 456 & IRC:112 digital governance.",
        ">> Directly modernizes India's ₹111 Lakh Cr National Infrastructure Pipeline."
    ], 44),
    ("SDG 11", "Sustainable Cities\n& Communities", "UN Target 11.2 & 11.5 (Public Safety)", (249, 157, 38), "bridge", [
        "• Prevents sudden urban flyover & bridge collapses, protecting millions of daily commuters.",
        "• Keeps lifeline economic corridors (Atal Setu Mumbai, Chenab Rail Link) safe 24×7.",
        ">> Cuts disaster-related human & economic losses across smart cities."
    ], 502),
    ("SDG 12", "Responsible\nConsumption", "UN Target 12.2 & 12.5 (Circular Economy)", (191, 139, 46), "chart", [
        "• Cuts raw concrete, river sand, and Fe500 steel consumption by 75% via early repairs.",
        "• Targeted CFRP carbon-fiber wrapping fixes micro-cracks without span demolition.",
        ">> Eliminates thousands of tonnes of toxic C&D (Construction & Demolition) waste."
    ], 960),
    ("SDG 13", "Climate Action\n& Resilience", "UN Target 13.1 (Climate Adaptation)", (63, 126, 68), "shield", [
        "• Cuts 60% embodied CO₂ emissions by avoiding cement-heavy bridge reconstruction.",
        "• Tracks extreme climate hazards: cyclone wind gusts, flood scour & heat expansion.",
        ">> Builds climate-resilient infrastructure for India's coastal & Himalayan zones."
    ], 1418)
]

for s_code, s_title, s_target, col, ic, bullets, sx in sdgs:
    sw, sh = 438, 322
    sy = 126
    draw_elevated_card(d7, [sx, sy, sx + sw, sy + sh], radius=18)
    d7.rounded_rectangle([sx, sy, sx + sw, sy + 88], radius=16, fill=col)
    d7.text((sx + 20, sy + 14), s_code, font=get_font(36, display=True), fill=(255, 255, 255))
    for l_i, l_s in enumerate(s_title.split("\n")):
        d7.text((sx + 155, sy + 18 + l_i * 22), l_s, font=get_font(16, bold=True), fill=(255, 255, 255))
    draw_simple_icon(d7, ic, sx + sw - 36, sy + 44, 22, col, bg=(255, 255, 255))

    draw_pill_badge(d7, sx + 20, sy + 98, s_target, col, (248, 250, 252), font_size=12)

    by = sy + 134
    for l_idx, b in enumerate(bullets):
        f_u = get_font(14, bold=True) if l_idx == 2 else get_font(14, bold=False)
        c_u = col if l_idx == 2 else TEXT_BODY
        draw_multiline(d7, (sx + 20, by), b, f_u, c_u, sw - 38, line_spacing=3)
        by += 60

# --- MIDDLE SECTION: 3 SUSTAINABILITY PILLARS (3 POINTS EACH) ---
pillars = [
    ("ENVIRONMENTAL IMPACT", "shield", BRAND_DARK_GREEN, (236, 253, 245), [
        "60% Less Carbon (CO₂): Cement manufacturing produces 8% of global CO₂. Extending bridge lifespan by +15–25 years avoids ~4,200 tonnes of CO₂ per major bridge.",
        "75% Less Material & Sand Mining: Precision epoxy & carbon-fiber (CFRP) wrapping repairs exact fatigue zones using minimal raw material.",
        "Zero Demolition Pollution: Prevents river siltation and dust pollution caused by blasting and rebuilding collapsed river/sea bridges."
    ], 44),
    ("SOCIAL & PUBLIC SAFETY", "bridge", BRAND_ROYAL, (239, 246, 255), [
        "Zero Collapse Fatalities: Continuous 200 Hz vibration & strain watch prevents tragedies like Morbi, safeguarding lakhs of daily citizens.",
        "90% Safer for Inspection Workers: Remote optical cameras & IoT sensors replace dangerous human rope-access climbs under high sea links.",
        "Inclusive Hindi/English Voice AI: Field technicians across India can operate the system hands-free in their spoken language."
    ], 666),
    ("ECONOMIC & GOVT SAVINGS", "chart", BRAND_PURPLE, (250, 245, 255), [
        "68% Lower Lifecycle Cost: Fixing a 0.3 mm crack early costs ₹17.5L over 10 years compared to ₹75L+ for emergency reactive repairs.",
        "Zero Supply-Chain Shutdowns: Keeps freight & port corridors (like JNPT Mumbai Atal Setu) running without sudden multi-month closures.",
        "Data-Driven MoRTH Budgets: Helps Govt prioritize repair funds objectively across 1.72+ Lakh bridges using our 0–100 Health Score."
    ], 1288)
]

for p_title, ic, col, bg_c, items, px in pillars:
    pw, ph = 588, 312
    py = 464
    draw_elevated_card(d7, [px, py, px + pw, py + ph], radius=18, fill=bg_c, outline=col, width=2)
    d7.rounded_rectangle([px, py, px + pw, py + 52], radius=14, fill=col)
    draw_simple_icon(d7, ic, px + 32, py + 26, 17, col, bg=(255, 255, 255))
    d7.text((px + 60, py + 13), p_title, font=get_font(19, display=True), fill=(255, 255, 255))
    iy = py + 64
    for it in items:
        d7.ellipse([px + 18, iy + 5, px + 34, iy + 21], fill=col)
        d7.line([(px + 22, iy + 13), (px + 25, iy + 16), (px + 31, iy + 9)], fill=(255, 255, 255), width=2)
        draw_multiline(d7, (px + 44, iy), it, get_font(14, bold=False), TEXT_MAIN, pw - 62, line_spacing=3)
        iy += 82

# --- BOTTOM SECTION: 5 BIG MEASURABLE IMPACT NUMBERS WITH SUB-DETAILS ---
draw_elevated_card(d7, [44, 792, 1876, 1024], radius=20, fill=HEADER_NAVY, outline=BRAND_ROYAL, width=2)
d7.text((76, 808), "AT A GLANCE — QUANTIFIED SUSTAINABILITY & ENGINEERING IMPACT INDICATORS", font=get_font(20, display=True), fill=(255, 255, 255))

big_metrics = [
    ("0.25 mm", "Smallest Crack Detected", "8× sharper than human visual walks", BRAND_CYAN, 72),
    ("200 Hz", "Real-Time Sensor Fusion", "MEMS vibration + FBG optical strain", BRAND_EMERALD, 432),
    ("+35% Life", "Bridge Lifespan Gained", "+15 to 25 extra years via CFRP wrap", BRAND_AMBER, 792),
    ("-60% CO₂", "Embodied Carbon Saved", "~4,200T CO₂ saved per bridge rebuild", (74, 222, 128), 1152),
    ("68% Saved", "Lifecycle Repair Budget", "₹17.5L vs. ₹75L per span over 10 yrs", BRAND_PURPLE, 1512)
]
for m_val, m_lbl, m_sub, col, mx in big_metrics:
    d7.rounded_rectangle([mx, 848, mx + 335, 1004], radius=14, fill=(30, 41, 59), outline=col, width=2)
    d7.text((mx + 20, 858), m_val, font=get_font(36, display=True), fill=col)
    d7.text((mx + 20, 918), m_lbl, font=get_font(17, bold=True), fill=(255, 255, 255))
    d7.text((mx + 20, 952), ">> " + m_sub, font=get_font(13, bold=False), fill=(186, 230, 253))

s7_path = os.path.join(SLIDES_OUT_DIR, "slide_7.png")
s7.save(s7_path, quality=95)


# ==============================================================================
# SLIDE 8: THANK YOU SLIDE
# ==============================================================================
print("Building Slide 8: Thank You Slide...")
s8 = u_p8.copy()
d8 = ImageDraw.Draw(s8)
draw_elevated_card(d8, [180, 685, 1740, 935], radius=20, fill=(255, 255, 255), outline=BRAND_ROYAL, width=3)
d8.text((255, 706), "INFRAGUARD INDIA — SMART AI, 200 Hz IOT & 3D DIGITAL TWIN FOR BRIDGE SAFETY", font=get_font(24, display=True), fill=BRAND_ROYAL)
d8.text((430, 756), "TEAM BYTE BUSTERS  |  ANUJ MALVIYA  •  AAYUSHI GUNDEGAONKAR  •  SAKSHI JAIN", font=get_font(19, bold=True), fill=HEADER_NAVY)
d8.text((385, 798), "ACROPOLIS INSTITUTE OF TECHNOLOGY & RESEARCH, INDORE   |   SDG 9: INDUSTRY, INNOVATION & INFRASTRUCTURE", font=get_font(16, bold=True), fill=BRAND_DARK_GREEN)
d8.rounded_rectangle([395, 845, 1525, 895], radius=12, fill=(238, 244, 255), outline=BRAND_INDIGO, width=2)
d8.text((430, 858), "Live Prototype Ready:  3D FEA Stress Twin  •  Optical Crack AI (0.25mm)  •  200 Hz FFT Stream  •  Voice AI Co-Pilot", font=get_font(16, bold=True), fill=BRAND_INDIGO)

s8_path = os.path.join(SLIDES_OUT_DIR, "slide_8.png")
s8.save(s8_path, quality=95)

# Sync to exact_slides
EXACT_DIR = os.path.join(ASSETS_DIR, "exact_slides")
os.makedirs(EXACT_DIR, exist_ok=True)
slide_paths = [s1_path, s2_path, s3_path, s4_path, s5_path, s6_path, s7_path, s8_path]
for idx, sp in enumerate(slide_paths, start=1):
    shutil.copyfile(sp, os.path.join(EXACT_DIR, f"slide_{idx}.png"))

# Export High-Res PDF & Editable PPTX
print("Exporting Final PDF and PowerPoint (.pptx)...")
pil_slides = [Image.open(p).convert("RGB") for p in slide_paths]

pdf_out_main = os.path.join(BASE_DIR, "INFRAGUARD_SUSTAINOVA_2026_FINAL.pdf")
pdf_out_fe = os.path.join(BASE_DIR, "frontend", "INFRAGUARD_SUSTAINOVA_2026_FINAL.pdf")
pil_slides[0].save(pdf_out_main, "PDF", resolution=300.0, save_all=True, append_images=pil_slides[1:])
shutil.copyfile(pdf_out_main, pdf_out_fe)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

speaker_notes = [
    "Slide 1: Welcome judges to SUSTAINOVA 2026 Ideathon! We are Team Byte Busters from Acropolis Institute of Technology & Research, Indore, presenting InfraGuard India under SDG 9.",
    "Slide 2: Meet Team Byte Busters — Anuj Malviya (Team Lead & 3D Digital Twin), Aayushi Gundegaonkar (AI & Optical Crack Vision), and Sakshi Jain (IoT Sensors & Safety Standards), monitoring 4 major Indian bridges across NHAI, MoRTH, MSRDC & Indian Railways.",
    "Slide 3: Problem Statement — Over 2,130 highway bridges in India need urgent repair. Manual inspections happen only once every 24 months and miss 78% of tiny hairline cracks, leading to ₹18,000+ Cr in reactive losses.",
    "Slide 4: Proposed Solution & Innovation — InfraGuard works in 4 simple steps (Scan & Sense, AI Damage Detection, 3D Digital Twin Stress Map, and Instant Action) backed by 6 core innovations and a 5-year Paris' Law bridge life forecast.",
    "Slide 5: Tech Stack & System Architecture — 6-column production tech stack and 3-layer architecture flowing from Bridge Edge Sensors to our FastAPI AI & Physics Core and Enterprise Command UI with <15ms latency.",
    "Slide 6: Feasibility, Viability & Future Roadmap — TRL-7 working prototype, 80% cheaper setup (₹1.8L/span), zero traffic closures, 68% maintenance cost savings, and a 4-phase roadmap scaling across 1.72+ Lakh Indian bridges.",
    "Slide 7: SDG Alignment & Sustainability Impact — Advances SDG 9 (9.1, 9.4), SDG 11 (11.2, 11.5), SDG 12 (12.2, 12.5), and SDG 13 (13.1) by extending bridge lifespan by +35% and cutting embodied carbon emissions by 60%.",
    "Slide 8: Thank You! Our working InfraGuard India web application is live for demonstration."
]

for idx, sp in enumerate(slide_paths):
    slide = prs.slides.add_slide(blank_layout)
    slide.shapes.add_picture(sp, Inches(0), Inches(0), width=Inches(13.333), height=Inches(7.5))
    slide.notes_slide.notes_text_frame.text = speaker_notes[idx]

pptx_out_main = os.path.join(BASE_DIR, "INFRAGUARD_SUSTAINOVA_2026_PPT.pptx")
pptx_out_fe = os.path.join(BASE_DIR, "frontend", "INFRAGUARD_SUSTAINOVA_2026_PPT.pptx")
prs.save(pptx_out_main)
shutil.copyfile(pptx_out_main, pptx_out_fe)

print("SUCCESS! Content-Enriched Modern Deck Saved.")

