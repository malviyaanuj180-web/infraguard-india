"""
SUSTAINOVA 2026 IDEATHON - MASTER PRESENTATION BUILDER
Matches the exact visual language, color scheme, infographic density, vector icons,
circular hub diagrams, 6-layer stack architecture, and 3-column feasibility layout
of the uploaded reference `Presentation.pdf` (from Presentation.zip), while tailored
100% for:
  - Infra Guard | TEAM BYTE BUSTERS | ACROPOLIS INSTITUTE OF TECHNOLOGY & RESEARCH, INDORE
  - Team: ANUJ MALVIYA, Aayushi Gundegaonkar, Sakshi Jain
  - Domain: SDG 9 - Industry, Innovation and Infrastructure
  - All India-Specific National Infrastructure capabilities built in our web app!
"""

import os
import math
import shutil
import pypdfium2 as pdfium
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

BASE_DIR = r"C:\Users\ACER\.gemini\antigravity\scratch\infra-health-monitor"
ASSETS_DIR = os.path.join(BASE_DIR, "frontend", "ppt_assets")
SLIDES_OUT_DIR = os.path.join(ASSETS_DIR, "ref_matched_slides")
os.makedirs(SLIDES_OUT_DIR, exist_ok=True)

USER_PDF = r"C:\Users\ACER\.gemini\antigravity\brain\62b11bf7-5dc3-4157-b4e7-78a57d988e9c\.user_uploaded\media_1795534951525_a65cdd30.pdf"
REF_PDF = os.path.join(BASE_DIR, "ref_presentation", "Presentation.pdf")

W, H = 1920, 1080

# Colors matching Reference Presentation.pdf
TEAL_BAR = (44, 110, 106)       # #2C6E6A top & bottom frame bar
NAVY_TITLE = (11, 91, 168)      # #0B5BA8 bold header blue
DARK_PILL = (5, 74, 118)        # #054A76 dark pill headers
CORNER_BLUE = (11, 91, 168)     # #0B5BA8 page corner box
TEXT_DARK = (18, 28, 45)
TEXT_MUTED = (75, 88, 108)
RED_ACCENT = (208, 38, 38)
GREEN_ACCENT = (18, 128, 72)
ORANGE_ACCENT = (224, 108, 18)
PURPLE_ACCENT = (118, 56, 178)
BLUE_ACCENT = (14, 116, 188)
TEAL_ACCENT = (16, 138, 132)

def get_font(size, bold=False, condensed=False):
    candidates = []
    if condensed and bold:
        candidates = ["bahnschrift.ttf", "arialbd.ttf", "segoeuib.ttf"]
    elif bold:
        candidates = ["segoeuib.ttf", "arialbd.ttf", "calibrib.ttf"]
    else:
        candidates = ["segoeui.ttf", "arial.ttf", "calibri.ttf"]
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

def draw_multiline(draw, pos, text, font, fill, max_width, line_spacing=5, align="left"):
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

# Extract clean logo and photos from user's & reference PDFs
print("Extracting official SUSTAINOVA logos and team photos...")
user_doc = pdfium.PdfDocument(USER_PDF)
ref_doc = pdfium.PdfDocument(REF_PDF)

# Render user page 1, 2, 3, 5 at 1920x1080
u_p1 = user_doc[0].render(scale=1920 / user_doc[0].get_width()).to_pil().convert("RGB").resize((W, H), Image.LANCZOS)
u_p2 = user_doc[1].render(scale=1920 / user_doc[1].get_width()).to_pil().convert("RGB").resize((W, H), Image.LANCZOS)
u_p3 = user_doc[2].render(scale=1920 / user_doc[2].get_width()).to_pil().convert("RGB").resize((W, H), Image.LANCZOS)
u_p5 = user_doc[4].render(scale=1920 / user_doc[4].get_width()).to_pil().convert("RGB").resize((W, H), Image.LANCZOS)
u_p8 = user_doc[7].render(scale=1920 / user_doc[7].get_width()).to_pil().convert("RGB").resize((W, H), Image.LANCZOS)

r_p1 = ref_doc[0].render(scale=1920 / ref_doc[0].get_width()).to_pil().convert("RGB").resize((W, H), Image.LANCZOS)
r_p2 = ref_doc[1].render(scale=1920 / ref_doc[1].get_width()).to_pil().convert("RGB").resize((W, H), Image.LANCZOS)
r_p8 = ref_doc[7].render(scale=1920 / ref_doc[7].get_width()).to_pil().convert("RGB").resize((W, H), Image.LANCZOS)

# Crop SUSTAINOVA top-right logo from reference page 2
sustainova_top_logo = r_p2.crop((1535, 29, 1908, 102))

# Crop Team Photos from user page 2
photo_anuj = u_p2.crop((241, 240, 558, 588))
photo_aayushi = u_p2.crop((832, 232, 1148, 578))
photo_sakshi = u_p2.crop((1392, 240, 1709, 588))

# Crop UI telemetry & vision cards from user page 3 & 5
ui_vision_crop = u_p3.crop((1354, 244, 1875, 922))
ui_telemetry_crop = u_p5.crop((1285, 428, 1800, 940))

def create_sustainova_frame(title_text, page_num=None):
    """Creates the exact SUSTAINOVA 2026 slide frame matching Presentation.pdf"""
    img = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Top & Bottom Teal Bars
    draw.rectangle([0, 0, W, 28], fill=TEAL_BAR)
    draw.rectangle([0, H - 30, W, H], fill=TEAL_BAR)

    # Top-left decorative geometric triangles & diagonal stripes (exact match to reference)
    draw.polygon([(0, 0), (42, 0), (42, 82), (0, 124)], fill=TEAL_BAR)
    draw.polygon([(42, 0), (125, 0), (42, 83)], fill=NAVY_TITLE)
    draw.polygon([(0, 144), (29, 115), (29, 142), (0, 171)], fill=TEAL_BAR)

    # Bottom-right decorative geometric corner
    if page_num is None:
        draw.polygon([(W, H), (W - 42, H), (W - 42, H - 82), (W, H - 124)], fill=TEAL_BAR)
        draw.polygon([(W - 42, H), (W - 125, H), (W - 42, H - 83)], fill=NAVY_TITLE)
        draw.polygon([(W, H - 144), (W - 29, H - 115), (W - 29, H - 142), (W, H - 171)], fill=TEAL_BAR)
    else:
        # Blue page number box in bottom right
        draw.rectangle([W - 68, H - 68, W, H], fill=CORNER_BLUE)
        f_num = get_font(38, bold=True)
        nb = draw.textbbox((0, 0), str(page_num), font=f_num)
        nw = nb[2] - nb[0]
        draw.text((W - 34 - nw / 2, H - 62), str(page_num), font=f_num, fill=(255, 255, 255))

    # Paste SUSTAINOVA logo top right
    img.paste(sustainova_top_logo, (1535, 31))

    # Draw Main Header Title
    f_title = get_font(56, bold=True, condensed=True)
    draw.text((88, 36), title_text, font=f_title, fill=NAVY_TITLE)

    return img, draw

def draw_pill_header(draw, box, text, fill=DARK_PILL, radius=12, font_size=24):
    draw.rounded_rectangle(box, radius=radius, fill=fill)
    f = get_font(font_size, bold=True)
    tb = draw.textbbox((0, 0), text, font=f)
    tw = tb[2] - tb[0]
    th = tb[3] - tb[1]
    cx = (box[0] + box[2] - tw) / 2
    cy = (box[1] + box[3] - th) / 2 - 3
    draw.text((cx, cy), text, font=f, fill=(255, 255, 255))

def draw_vector_icon(draw, kind, cx, cy, r, color, bg_color=None):
    """Draws crisp geometric vector icons inside circles for flowcharts & cards"""
    if bg_color:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=bg_color, outline=color, width=2)
    else:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
        color = (255, 255, 255)

    s = r * 0.52
    if kind == "bridge":
        # Suspension / Cable-stayed bridge icon
        draw.line([cx - s, cy + s * 0.4, cx + s, cy + s * 0.4], fill=color, width=3)
        draw.line([cx - s * 0.5, cy - s * 0.7, cx - s * 0.5, cy + s * 0.8], fill=color, width=3)
        draw.line([cx + s * 0.5, cy - s * 0.7, cx + s * 0.5, cy + s * 0.8], fill=color, width=3)
        draw.line([cx - s * 0.5, cy - s * 0.6, cx - s, cy + s * 0.4], fill=color, width=2)
        draw.line([cx - s * 0.5, cy - s * 0.6, cx, cy + s * 0.4], fill=color, width=2)
        draw.line([cx + s * 0.5, cy - s * 0.6, cx, cy + s * 0.4], fill=color, width=2)
        draw.line([cx + s * 0.5, cy - s * 0.6, cx + s, cy + s * 0.4], fill=color, width=2)
    elif kind == "ai":
        # Microchip AI icon
        draw.rounded_rectangle([cx - s * 0.65, cy - s * 0.65, cx + s * 0.65, cy + s * 0.65], radius=4, outline=color, width=3)
        for off in [-s * 0.35, 0, s * 0.35]:
            draw.line([cx + off, cy - s, cx + off, cy - s * 0.65], fill=color, width=2)
            draw.line([cx + off, cy + s * 0.65, cx + off, cy + s], fill=color, width=2)
            draw.line([cx - s, cy + off, cx - s * 0.65, cy + off], fill=color, width=2)
            draw.line([cx + s * 0.65, cy + off, cx + s, cy + off], fill=color, width=2)
        f_ai = get_font(int(r * 0.55), bold=True)
        tb = draw.textbbox((0, 0), "AI", font=f_ai)
        draw.text((cx - (tb[2] - tb[0]) / 2, cy - (tb[3] - tb[1]) / 2 - 2), "AI", font=f_ai, fill=color)
    elif kind == "drone":
        # Quadcopter Drone / Camera icon
        draw.rounded_rectangle([cx - s * 0.5, cy - s * 0.35, cx + s * 0.5, cy + s * 0.35], radius=4, outline=color, width=3)
        draw.ellipse([cx - s * 0.25, cy - s * 0.25, cx + s * 0.25, cy + s * 0.25], outline=color, width=2)
        draw.line([cx - s * 0.85, cy - s * 0.65, cx - s * 0.35, cy - s * 0.35], fill=color, width=3)
        draw.line([cx + s * 0.85, cy - s * 0.65, cx + s * 0.35, cy - s * 0.35], fill=color, width=3)
        draw.line([cx - s, cy - s * 0.65, cx - s * 0.5, cy - s * 0.65], fill=color, width=3)
        draw.line([cx + s * 0.5, cy - s * 0.65, cx + s, cy - s * 0.65], fill=color, width=3)
    elif kind == "sensor":
        # Waveform / Vibration IoT icon
        pts = [
            (cx - s, cy),
            (cx - s * 0.6, cy),
            (cx - s * 0.35, cy - s * 0.75),
            (cx, cy + s * 0.8),
            (cx + s * 0.35, cy - s * 0.5),
            (cx + s * 0.6, cy),
            (cx + s, cy)
        ]
        draw.line(pts, fill=color, width=3)
    elif kind == "shield":
        # Compliance / Trust Shield icon
        pts = [
            (cx, cy - s * 0.85),
            (cx + s * 0.75, cy - s * 0.5),
            (cx + s * 0.65, cy + s * 0.25),
            (cx, cy + s * 0.85),
            (cx - s * 0.65, cy + s * 0.25),
            (cx - s * 0.75, cy - s * 0.5)
        ]
        draw.polygon(pts, outline=color, width=3)
        draw.line([(cx - s * 0.3, cy), (cx - s * 0.05, cy + s * 0.3), (cx + s * 0.4, cy - s * 0.25)], fill=color, width=3)
    elif kind == "cube":
        # 3D Digital Twin / FEA Mesh Cube
        draw.polygon([(cx, cy - s * 0.85), (cx + s * 0.75, cy - s * 0.4), (cx, cy + s * 0.05), (cx - s * 0.75, cy - s * 0.4)], outline=color, width=2)
        draw.polygon([(cx - s * 0.75, cy - s * 0.4), (cx, cy + s * 0.05), (cx, cy + s * 0.85), (cx - s * 0.75, cy + s * 0.4)], outline=color, width=2)
        draw.polygon([(cx + s * 0.75, cy - s * 0.4), (cx, cy + s * 0.05), (cx, cy + s * 0.85), (cx + s * 0.75, cy + s * 0.4)], outline=color, width=2)
    elif kind == "voice":
        # Microphone / Voice Co-Pilot icon
        draw.rounded_rectangle([cx - s * 0.3, cy - s * 0.75, cx + s * 0.3, cy + s * 0.15], radius=6, outline=color, width=3)
        draw.arc([cx - s * 0.6, cy - s * 0.3, cx + s * 0.6, cy + s * 0.5], start=0, end=180, fill=color, width=3)
        draw.line([cx, cy + s * 0.5, cx, cy + s * 0.85], fill=color, width=3)
        draw.line([cx - s * 0.35, cy + s * 0.85, cx + s * 0.35, cy + s * 0.85], fill=color, width=3)
    elif kind == "alert":
        # Warning Triangle
        draw.polygon([(cx, cy - s * 0.8), (cx + s * 0.8, cy + s * 0.65), (cx - s * 0.8, cy + s * 0.65)], outline=color, width=3)
        draw.line([cx, cy - s * 0.25, cx, cy + s * 0.2], fill=color, width=3)
        draw.ellipse([cx - 2, cy + s * 0.38, cx + 2, cy + s * 0.46], fill=color)
    elif kind == "chart":
        # Growth / Analytics chart
        draw.line([cx - s * 0.75, cy + s * 0.65, cx + s * 0.75, cy + s * 0.65], fill=color, width=2)
        draw.rectangle([cx - s * 0.6, cy + s * 0.1, cx - s * 0.3, cy + s * 0.65], fill=color)
        draw.rectangle([cx - s * 0.15, cy - s * 0.25, cx + s * 0.15, cy + s * 0.65], fill=color)
        draw.rectangle([cx + s * 0.3, cy - s * 0.65, cx + s * 0.6, cy + s * 0.65], fill=color)
    elif kind == "map":
        # GIS Location Pin
        draw.ellipse([cx - s * 0.5, cy - s * 0.75, cx + s * 0.5, cy + s * 0.25], outline=color, width=3)
        draw.polygon([(cx - s * 0.45, cy - s * 0.1), (cx + s * 0.45, cy - s * 0.1), (cx, cy + s * 0.85)], fill=color)
        draw.ellipse([cx - s * 0.2, cy - s * 0.45, cx + s * 0.2, cy - s * 0.05], fill=(255, 255, 255))
    elif kind == "code":
        # </> Tech icon
        f_c = get_font(int(r * 0.68), bold=True)
        tb = draw.textbbox((0, 0), "</>", font=f_c)
        draw.text((cx - (tb[2] - tb[0]) / 2, cy - (tb[3] - tb[1]) / 2 - 3), "</>", font=f_c, fill=color)
    elif kind == "check":
        draw.ellipse([cx - s * 0.75, cy - s * 0.75, cx + s * 0.75, cy + s * 0.75], outline=color, width=3)
        draw.line([(cx - s * 0.35, cy), (cx - s * 0.05, cy + s * 0.35), (cx + s * 0.45, cy - s * 0.3)], fill=color, width=3)


def draw_star(draw, cx, cy, r_outer, fill_col):
    pts = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        r = r_outer if i % 2 == 0 else r_outer * 0.42
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    draw.polygon(pts, fill=fill_col)

# ==============================================================================
# SLIDE 1: COVER SLIDE (Exact Official SUSTAINOVA 2026 Cover with Infra Guard)
# ==============================================================================
print("Building Slide 1: Cover Slide...")
s1 = u_p1.copy()
s1_path = os.path.join(SLIDES_OUT_DIR, "slide_1.png")
s1.save(s1_path, quality=95)


# ==============================================================================
# SLIDE 2: TEAM DESCRIPTION & DOMAIN (Styled with Reference Teal Photo Frames + Role Badges)
# ==============================================================================
print("Building Slide 2: Team Description & Domain...")
s2, d2 = create_sustainova_frame("TEAM DESCRIPTION & DOMAIN", page_num=None)

# Team Header Pill Banner
d2.rounded_rectangle([88, 122, 1832, 184], radius=12, fill=(238, 246, 246), outline=TEAL_BAR, width=2)
f_team_banner = get_font(24, bold=True)
d2.text((115, 138), "TEAM BYTE BUSTERS   |   ACROPOLIS INSTITUTE OF TECHNOLOGY & RESEARCH, INDORE", font=f_team_banner, fill=DARK_PILL)
d2.rounded_rectangle([1470, 133, 1812, 173], radius=8, fill=NAVY_TITLE)
d2.text((1495, 140), "PROJECT: INFRAGUARD INDIA", font=get_font(20, bold=True), fill=(255, 255, 255))

members = [
    ("ANUJ MALVIYA", "Team Lead & AI / Full-Stack Architect", "3D FEA Digital Twin, FastAPI & Physics Engine", photo_anuj, 165),
    ("AAYUSHI GUNDEGAONKAR", "Computer Vision & Deep Learning Lead", "OpenCV Crack Segmentation, LiDAR & RUL Prognostics", photo_aayushi, 775),
    ("SAKSHI JAIN", "IoT Telemetry & Indian Standards Lead", "200 Hz Sensor Fusion, Welch FFT & IRC/IS Compliance", photo_sakshi, 1385)
]

for name, role, focus, photo, x0 in members:
    # Outer teal frame matching Reference Slide 2
    pw, ph = 370, 395
    y0 = 225
    d2.rectangle([x0 - 12, y0 - 12, x0 + pw + 12, y0 + ph + 12], fill=TEAL_BAR)
    d2.rectangle([x0 - 3, y0 - 3, x0 + pw + 3, y0 + ph + 3], fill=(255, 255, 255))
    resized_photo = photo.resize((pw, ph), Image.LANCZOS)
    s2.paste(resized_photo, (x0, y0))

    # Name
    f_name = get_font(26, bold=True)
    nb = d2.textbbox((0, 0), name, font=f_name)
    nw = nb[2] - nb[0]
    d2.text((x0 + (pw - nw) / 2, y0 + ph + 24), name, font=f_name, fill=(10, 15, 25))

    # Role Pill
    d2.rounded_rectangle([x0 - 15, y0 + ph + 64, x0 + pw + 15, y0 + ph + 104], radius=18, fill=(232, 244, 252), outline=NAVY_TITLE, width=2)
    f_role = get_font(17, bold=True)
    rb = d2.textbbox((0, 0), role, font=f_role)
    d2.text((x0 + (pw - (rb[2] - rb[0])) / 2, y0 + ph + 72), role, font=f_role, fill=NAVY_TITLE)

    # Focus subtitle
    f_foc = get_font(15, bold=False)
    fb = d2.textbbox((0, 0), focus, font=f_foc)
    d2.text((x0 + (pw - (fb[2] - fb[0])) / 2, y0 + ph + 112), focus, font=f_foc, fill=TEXT_MUTED)

# Domain Banner at bottom matching Reference Slide 2 + SDG 9 Visual Badge
d2.rounded_rectangle([88, 795, 1832, 920], radius=16, fill=(247, 250, 252), outline=TEAL_BAR, width=3)
d2.rounded_rectangle([112, 815, 290, 900], radius=10, fill=(242, 106, 46))
d2.text((134, 825), "SDG 9", font=get_font(36, bold=True), fill=(255, 255, 255))
d2.text((134, 868), "INFRASTRUCTURE", font=get_font(14, bold=True), fill=(255, 255, 255))

d2.text((320, 816), "DOMAIN: SDG 9 – INDUSTRY, INNOVATION AND INFRASTRUCTURE", font=get_font(36, bold=True), fill=(12, 20, 35))
d2.text((320, 866), "Autonomous Structural Health Monitoring, 3D FEA Digital Twin & Predictive Maintenance for Indian National Corridors (NHAI, MoRTH IBMS, MSRDC & Indian Railways)", font=get_font(20, bold=False), fill=DARK_PILL)

s2_path = os.path.join(SLIDES_OUT_DIR, "slide_2.png")
s2.save(s2_path, quality=95)


# ==============================================================================
# SLIDE 3: PROBLEM STATEMENT (Exact Reference Page 3 Layout: Question Mark + 3 Bottom Cards)
# ==============================================================================
print("Building Slide 3: Problem Statement (Reference Page 3 Layout)...")
s3, d3 = create_sustainova_frame("PROBLEM STATEMENT", page_num=1)

# Top Question Mark Visual on Left (like reference "DO YOU REALLY TRUST WHAT YOU BUY")
d3.ellipse([75, 118, 295, 315], fill=(254, 242, 242), outline=RED_ACCENT, width=4)
# Crop exact bright concrete crack patch from ui_vision_crop (x:30..136, y:490..582)
crack_thumb = ui_vision_crop.crop((30, 490, 136, 582)).resize((156, 120), Image.LANCZOS)
s3.paste(crack_thumb, (107, 142))
# Draw bright red crack overlay line on top of concrete patch so it pops visually
d3.line([(125, 195), (165, 185), (205, 205), (242, 192)], fill=RED_ACCENT, width=3)
d3.rounded_rectangle([102, 258, 268, 294], radius=6, fill=RED_ACCENT)
d3.text((116, 265), "5.04mm CRACK!", font=get_font(16, bold=True), fill=(255, 255, 255))

d3.ellipse([145, 325, 225, 405], fill=DARK_PILL, outline=NAVY_TITLE, width=3)
draw_vector_icon(d3, "alert", 185, 365, 34, RED_ACCENT)

# Big hook text next to Question visual
d3.text((312, 132), "ARE INDIA'S", font=get_font(30, bold=True), fill=(25, 35, 45))
d3.text((312, 168), "BRIDGES SAFE", font=get_font(32, bold=True), fill=RED_ACCENT)
d3.text((312, 206), "RIGHT NOW?", font=get_font(30, bold=True), fill=TEAL_BAR)

# Outlined Pill "THE PROBLEM" (exact match to Reference Slide 3)
d3.rounded_rectangle([312, 272, 575, 332], radius=24, fill=(255, 255, 255), outline=DARK_PILL, width=4)
d3.text((344, 285), "THE ", font=get_font(27, bold=True), fill=(20, 25, 35))
d3.text((414, 285), "PROBLEM", font=get_font(27, bold=True), fill=RED_ACCENT)

# Top Highlighted Headline Banner (right side)
d3.rectangle([590, 118, 1845, 162], fill=(214, 234, 252))
f_h1 = get_font(24, bold=True)
d3.text((602, 125), "FROM HIGHWAYS TO SEA LINKS, ", font=f_h1, fill=(10, 15, 25))
d3.text((990, 125), "HIDDEN STRUCTURAL FATIGUE", font=f_h1, fill=RED_ACCENT)
d3.text((1380, 125), " THREATENS MILLIONS DAILY.", font=f_h1, fill=(10, 15, 25))

sub_problem = (
    "Ageing bridges, marine chloride corrosion, heavy Class 70R axle loads, and blind biennial manual inspections "
    "leave micro-cracks, cable sag, and resonant harmonic drift undetected until catastrophic collapse."
)
draw_multiline(d3, (602, 172), sub_problem, get_font(20, bold=False), (35, 45, 60), 1230, line_spacing=6)

# Two Visual Callout Boxes in middle-right (like Milk & Honey boxes in reference)
# Callout 1: Blind Visual Inspection
draw_vector_icon(d3, "bridge", 650, 295, 44, NAVY_TITLE, bg_color=(232, 244, 252))
d3.rounded_rectangle([705, 255, 1185, 338], radius=12, fill=(255, 255, 255), outline=DARK_PILL, width=3)
draw_multiline(d3, (720, 266), "Can manual binocular checks detect a 0.3mm flexural crack under a 60m sea-link girder?", get_font(17, bold=True), (15, 25, 35), 450, line_spacing=4, align="center")

# Callout 2: Unverified Sensor & Fatigue Drift
draw_vector_icon(d3, "sensor", 1255, 295, 44, RED_ACCENT, bg_color=(254, 242, 242))
d3.rounded_rectangle([1310, 255, 1835, 338], radius=12, fill=(255, 255, 255), outline=DARK_PILL, width=3)
draw_multiline(d3, (1325, 266), "Can isolated IoT gauges predict remaining fatigue life (RUL) before rebar yield at 420 MPa?", get_font(17, bold=True), (15, 25, 35), 495, line_spacing=4, align="center")

# 3 Mini Stat Strip Icons above the 3 big cards (exact match to reference strip)
strip_items = [
    ("alert", RED_ACCENT, "2,130+ Indian bridges", "identified as distressed / ageing,", 620),
    ("drone", NAVY_TITLE, "while manual biennial audits", "miss 78% of early micro-cracks,", 1030),
    ("ai", RED_ACCENT, "causing sudden failures", "and ₹18,000+ Cr reactive repair costs.", 1445)
]
for ic, col, l1, l2, sx in strip_items:
    draw_vector_icon(d3, ic, sx, 382, 26, col, bg_color=(248, 250, 252))
    d3.text((sx + 36, 362), l1, font=get_font(16, bold=True), fill=col)
    d3.text((sx + 36, 384), l2, font=get_font(16, bold=True), fill=(25, 35, 45))
    if sx < 1400:
        d3.line([sx + 380, 358, sx + 380, 408], fill=(200, 210, 220), width=2)

# ==============================================================================
# THREE BOTTOM ROUNDED CARDS (Exact Match to Reference Slide 3)
# Card 1: STAKEHOLDER • CHALLENGE (x: 72..708)
# Card 2: WHY THIS PROBLEM NEEDS TECHNOLOGY-DRIVEN SOLUTION? (x: 734..1262)
# Card 3: REAL WORLD IMPACT (x: 1288..1848)
# ==============================================================================

# --- CARD 1: STAKEHOLDER • CHALLENGE ---
d3.rounded_rectangle([72, 428, 708, 995], radius=22, fill=(255, 255, 255), outline=DARK_PILL, width=3)
d3.text((112, 444), "STAKEHOLDER", font=get_font(28, bold=True), fill=TEAL_BAR)
d3.ellipse([392, 456, 408, 472], fill=DARK_PILL)
d3.rounded_rectangle([435, 440, 675, 486], radius=10, fill=(255, 255, 255), outline=DARK_PILL, width=2)
d3.text((458, 446), "CHALLENGE", font=get_font(27, bold=True), fill=RED_ACCENT)
d3.line([72, 498, 708, 498], fill=DARK_PILL, width=2)

stakeholders = [
    ("bridge", "NHAI & MoRTH", "1.72+ Lakh national highway bridges; manual IBMS visual audits cannot track live 24x7 fatigue."),
    ("map", "MSRDC Sea Links", "Severe marine chloride corrosion & galvanic rebar spalling on Atal Setu (MTHL) & Bandra-Worli."),
    ("sensor", "Indian Railways", "Extreme Seismic Zone-V wind & dynamic axle loads on Chenab Arch Viaduct (USBRL J&K)."),
    ("drone", "Field Inspectors", "Hazardous rope-access under-deck inspections with zero sub-millimeter GSD crack calibration."),
    ("shield", "Civic & Metro PwD", "No automated IS 456:2000 / IRC:112-2020 compliance certification or instant work-order dispatch."),
    ("alert", "Daily Commuters", "Exposed to sudden catastrophic structural failures (Morbi, Majerhat) with zero early warning.")
]
sy = 508
for ic, st_name, st_desc in stakeholders:
    d3.rounded_rectangle([86, sy, 694, sy + 72], radius=10, fill=(243, 248, 252))
    draw_vector_icon(d3, ic, 118, sy + 36, 22, DARK_PILL, bg_color=(225, 238, 248))
    d3.text((150, sy + 22), st_name, font=get_font(17, bold=True), fill=DARK_PILL)
    d3.line([308, sy + 10, 308, sy + 62], fill=(205, 218, 230), width=2)
    draw_multiline(d3, (320, sy + 11), st_desc, get_font(14, bold=False), (30, 40, 55), 362, line_spacing=3)
    sy += 79

# --- CARD 2: WHY THIS PROBLEM NEEDS TECHNOLOGY-DRIVEN SOLUTION? ---
d3.rounded_rectangle([734, 428, 1262, 995], radius=22, fill=(255, 255, 255), outline=DARK_PILL, width=3)
d3.text((795, 442), "WHY THIS PROBLEM NEEDS", font=get_font(23, bold=True), fill=DARK_PILL)
d3.text((755, 470), "TECHNOLOGY-DRIVEN SOLUTION?", font=get_font(23, bold=True), fill=DARK_PILL)
d3.line([734, 504, 1262, 504], fill=DARK_PILL, width=2)

tech_needs = [
    ("alert", (225, 238, 252), DARK_PILL, "BLIND MANUAL AUDITS", "Biennial visual checks miss subsurface rebar fatigue.", 758, 530),
    ("ai", (222, 246, 235), GREEN_ACCENT, "AI CRACK VISION", "Needs OpenCV + YOLOv8 0.25mm/px segmentation.", 935, 530),
    ("sensor", (240, 232, 252), PURPLE_ACCENT, "200 Hz IOT TELEMETRY", "MEMS + FBG optical strain captures modal drift.", 1112, 530),
    ("cube", (254, 240, 218), ORANGE_ACCENT, "3D FEA DIGITAL TWIN", "Live Von Mises MPa stress & LiDAR point cloud.", 758, 760),
    ("shield", (225, 240, 255), BLUE_ACCENT, "SENSOR TRUST GUARD", "Quarantines faulty IoT channels before false alarm.", 935, 760),
    ("check", (245, 230, 252), PURPLE_ACCENT, "IRC / BIS COMPLIANCE", "Automated IS 456 & IRC:112 breach certification.", 1112, 760)
]
for ic, bg_c, fg_c, tn_title, tn_desc, tx, ty in tech_needs:
    draw_vector_icon(d3, ic, tx + 62, ty + 48, 44, fg_c, bg_color=bg_c)
    draw_multiline(d3, (tx - 10, ty + 104), tn_title, get_font(15, bold=True), fg_c, 145, line_spacing=2, align="center")
    draw_multiline(d3, (tx - 10, ty + 144), tn_desc, get_font(13, bold=False), (40, 50, 65), 145, line_spacing=3, align="center")

# --- CARD 3: REAL WORLD IMPACT ---
d3.rounded_rectangle([1288, 428, 1848, 995], radius=22, fill=(255, 255, 255), outline=DARK_PILL, width=3)
d3.text((1375, 448), "REAL WORLD IMPACT", font=get_font(31, bold=True), fill=DARK_PILL)
d3.line([1288, 498, 1848, 498], fill=DARK_PILL, width=2)

impacts = [
    ("2,130+ Bridges", GREEN_ACCENT, "Distressed National Highway bridges identified across India requiring urgent structural rehabilitation (MoRTH IBMS)."),
    ("135+ Lives Lost", RED_ACCENT, "Morbi Cable Bridge collapse (Gujarat) caused by undetected cable wire corrosion & lack of real-time load telemetry."),
    ("1.72 Lakh+", BLUE_ACCENT, "Bridges & flyovers tracked under India's National Highway network facing extreme monsoon & heavy freight wear."),
    ("0.30 mm Limit", ORANGE_ACCENT, "Maximum allowable flexural crack width under BIS IS 456:2000 & IRC:112-2020 before severe chloride rebar corrosion."),
    ("68% Cost Saved", PURPLE_ACCENT, "Reduction in lifecycle bridge overhaul expenses via Paris' Law predictive CFRP retrofitting vs. reactive rebuilds.")
]
iy = 515
for stat_txt, st_col, st_desc in impacts:
    d3.line([1312, iy + 8, 1312, iy + 68], fill=st_col, width=6)
    d3.text((1328, iy + 16), stat_txt, font=get_font(26, bold=True), fill=st_col)
    d3.line([1545, iy + 8, 1545, iy + 72], fill=(210, 220, 230), width=2)
    draw_multiline(d3, (1560, iy + 6), st_desc, get_font(13, bold=False), (30, 40, 55), 272, line_spacing=3)
    if iy < 880:
        d3.line([1310, iy + 86, 1825, iy + 86], fill=(225, 232, 240), width=1)
    iy += 93

s3_path = os.path.join(SLIDES_OUT_DIR, "slide_3.png")
s3.save(s3_path, quality=95)


# ==============================================================================
# SLIDE 4: PROPOSED SOLUTION & INNOVATION (Exact Reference Page 4 Layout!)
# Left: WHAT IS INFRAGUARD? + WHY INFRAGUARD? radial 4-node diagram
# Center: UNIQUE VALUE PROPOSITION 6-Node Circular Hub Diagram around InfraGuard Core
# Right: SOLUTION OVERVIEW 6-Step Vertical Numbered Pipeline
# ==============================================================================
print("Building Slide 4: Proposed Solution & Innovation (Reference Page 4 Layout)...")
s4, d4 = create_sustainova_frame("PROPOSED SOLUTION & INNOVATION", page_num=2)

# --- LEFT COLUMN: WHAT IS INFRAGUARD? ---
d4.text((62, 132), "WHAT IS", font=get_font(42, bold=True), fill=DARK_PILL)
d4.text((62, 182), "INFRAGUARD?", font=get_font(46, bold=True), fill=TEAL_BAR)

d4.rounded_rectangle([18, 255, 565, 515], radius=22, fill=(255, 255, 255), outline=TEAL_BAR, width=2)
what_is_txt = (
    "InfraGuard combines AI Computer Vision, 200 Hz IoT Sensor Fusion, and a 3D Finite-Element (FEA) Digital Twin "
    "to create an autonomous structural health command center for Indian bridges & sea links. "
    "Every span receives live Von Mises MPa stress contour mapping, Paris' Law 5-Year RUL prognostics, "
    "and instant BIS IS 456 / IRC:112 compliance certification."
)
draw_multiline(d4, (38, 275), what_is_txt, get_font(18, bold=False), (20, 30, 45), 508, line_spacing=7, align="center")

# Bottom-Left: "WHY INFRAGUARD?" semicircle hub + 4 connected cards
d4.ellipse([32, 645, 212, 825], fill=(255, 255, 255), outline=DARK_PILL, width=4)
d4.text((88, 702), "WHY", font=get_font(22, bold=True), fill=DARK_PILL)
d4.text((48, 732), "INFRAGUARD?", font=get_font(20, bold=True), fill=DARK_PILL)

why_cards = [
    ("drone", BLUE_ACCENT, "Sub-mm AI Crack Vision", "Detects 0.25mm/px cracks, spalling & rebar corrosion via OpenCV + YOLOv8.", 545),
    ("cube", GREEN_ACCENT, "3D FEA & LiDAR Twin", "Live Von Mises MPa stress mesh (40-420 MPa) & ICP 3D LiDAR point cloud.", 652),
    ("sensor", ORANGE_ACCENT, "200 Hz IoT & Welch FFT", "MEMS + FBG strain fusion with Sensor Trust Guard fault quarantine.", 759),
    ("voice", PURPLE_ACCENT, "Hindi/EN Voice Co-Pilot", "Two-way voice AI structural assistant & Paris' Law 5-Yr RUL forecast.", 866)
]
for ic, col, w_title, w_desc, wy in why_cards:
    # Dotted connector line from WHY circle to card
    d4.line([185, 735, 245, wy + 42], fill=col, width=2)
    d4.ellipse([239, wy + 36, 251, wy + 48], fill=col)
    d4.rounded_rectangle([258, wy, 588, wy + 88], radius=12, fill=(250, 252, 255), outline=col, width=2)
    draw_vector_icon(d4, ic, 298, wy + 44, 26, col, bg_color=(240, 246, 252))
    d4.text((336, wy + 12), w_title, font=get_font(16, bold=True), fill=col)
    draw_multiline(d4, (336, wy + 36), w_desc, get_font(13, bold=False), (45, 55, 70), 240, line_spacing=3)

# --- CENTER COLUMN: UNIQUE VALUE PROPOSITION (6-Node Circular Hub Diagram) ---
draw_pill_header(d4, [725, 135, 1245, 192], "UNIQUE VALUE PROPOSITION", fill=DARK_PILL, radius=10, font_size=25)

cx_hub, cy_hub = 985, 595
r_orbit = 215

# Draw dashed orbit circle
for deg in range(0, 360, 6):
    rad1 = math.radians(deg)
    rad2 = math.radians(deg + 3)
    x1 = cx_hub + r_orbit * math.cos(rad1)
    y1 = cy_hub + r_orbit * math.sin(rad1)
    x2 = cx_hub + r_orbit * math.cos(rad2)
    y2 = cy_hub + r_orbit * math.sin(rad2)
    d4.line([x1, y1, x2, y2], fill=DARK_PILL, width=3)

# Center Core Circle ("InfraGuard INDIA")
d4.ellipse([cx_hub - 125, cy_hub - 125, cx_hub + 125, cy_hub + 125], fill=(242, 247, 250), outline=(210, 225, 235), width=4)
draw_vector_icon(d4, "bridge", cx_hub, cy_hub - 38, 46, TEAL_BAR, bg_color=(225, 242, 240))
d4.text((cx_hub - 92, cy_hub + 18), "InfraGuard", font=get_font(34, bold=True), fill=(15, 28, 45))
d4.text((cx_hub - 96, cy_hub + 60), "SENSE • TWIN • PREDICT", font=get_font(14, bold=True), fill=TEAL_BAR)

# 6 Orbiting Nodes around the Hub
orbit_nodes = [
    (-90, "ai", GREEN_ACCENT, "Physics-Informed AI", "Paris' Law RUL & Bayesian cross-modal fusion", (0, -118)),
    (-30, "drone", PURPLE_ACCENT, "Sub-mm Crack AI", "0.25mm/px OpenCV mask & galvanic rebar index", (135, -35)),
    (30, "map", ORANGE_ACCENT, "India GIS Corridors", "Atal Setu, Bandra-Worli, Chenab Arch & Delhi", (135, -25)),
    (90, "voice", TEAL_ACCENT, "Voice AI Co-Pilot", "Two-way speech synthesis & MoRTH certificates", (0, 68)),
    (150, "sensor", BLUE_ACCENT, "200 Hz IoT + FFT", "Welch PSD spectrum & Sensor Trust Guard", (-145, -25)),
    (210, "cube", DARK_PILL, "3D FEA Stress Twin", "Live Von Mises MPa contour & LiDAR cloud", (-145, -35))
]

for angle_deg, ic, col, n_title, n_desc, (tx_off, ty_off) in orbit_nodes:
    rad = math.radians(angle_deg)
    nx = cx_hub + r_orbit * math.cos(rad)
    ny = cy_hub + r_orbit * math.sin(rad)
    d4.ellipse([nx - 46, ny - 46, nx + 46, ny + 46], fill=(255, 255, 255), outline=col, width=3)
    draw_vector_icon(d4, ic, nx, ny, 34, col)

    # Label text box positioned cleanly outside each node
    if tx_off == 0:
        lx = nx - 135
        ly = ny + ty_off
        end_y = draw_multiline(d4, (lx, ly), n_title, get_font(19, bold=True), col, 270, align="center")
        draw_multiline(d4, (lx, end_y + 4), n_desc, get_font(14, bold=False), (40, 50, 65), 270, line_spacing=3, align="center")
    elif tx_off > 0:
        lx = nx + 56
        ly = ny + ty_off
        end_y = draw_multiline(d4, (lx, ly), n_title, get_font(18, bold=True), col, 182, align="left")
        draw_multiline(d4, (lx, end_y + 4), n_desc, get_font(14, bold=False), (40, 50, 65), 182, line_spacing=3, align="left")
    else:
        lx = nx - 238
        ly = ny + ty_off
        end_y = draw_multiline(d4, (lx, ly), n_title, get_font(18, bold=True), col, 182, align="right")
        draw_multiline(d4, (lx, end_y + 4), n_desc, get_font(14, bold=False), (40, 50, 65), 182, line_spacing=3, align="right")

# --- RIGHT COLUMN: SOLUTION OVERVIEW (6-Step Vertical Pipeline) ---
draw_pill_header(d4, [1388, 135, 1875, 192], "SOLUTION OVERVIEW", fill=DARK_PILL, radius=10, font_size=25)

steps_right = [
    ("1", "map", BLUE_ACCENT, "CORRIDOR & SPAN ONBOARDED", "National asset (Atal Setu MTHL-01, Chenab Arch, Bandra-Worli) registered with +91 SMS OTP 2FA."),
    ("2", "drone", GREEN_ACCENT, "UAV DRONE & LIDAR SCANNING", "0.25mm/px optical imagery & Open3D ICP 3D LiDAR point-cloud deflection scan captured."),
    ("3", "sensor", PURPLE_ACCENT, "200 Hz IOT & TRUST QUARANTINE", "Tri-axial MEMS + FBG optical strain streamed; faulty sensor spikes auto-quarantined."),
    ("4", "cube", ORANGE_ACCENT, "3D FEA VON MISES DIGITAL TWIN", "Real-time 40–420 MPa structural stress contour & Welch FFT natural frequency tracking."),
    ("5", "ai", TEAL_ACCENT, "PARIS' LAW 5-YR RUL FORECAST", "Crack propagation da/dN = C(ΔK)^m models failure horizon & +35% CFRP retrofit gain."),
    ("6", "shield", DARK_PILL, "MORTH CERTIFICATE & DISPATCH", "Auto-dispatches NHAI field work orders & signs official IRC:112 / IS 456 compliance PDF.")
]

sy = 235
for idx, (num_str, ic, col, st_title, st_desc) in enumerate(steps_right):
    cy_step = sy + 44
    # Vertical arrow to next step
    if idx < len(steps_right) - 1:
        d4.line([1476, cy_step + 45, 1476, cy_step + 115], fill=DARK_PILL, width=3)
        d4.polygon([(1469, cy_step + 92), (1483, cy_step + 92), (1476, cy_step + 106)], fill=DARK_PILL)

    # Number badge
    d4.ellipse([1375, cy_step - 24, 1423, cy_step + 24], fill=DARK_PILL)
    f_n = get_font(22, bold=True)
    nb = d4.textbbox((0, 0), num_str, font=f_n)
    d4.text((1399 - (nb[2] - nb[0]) / 2, cy_step - 15), num_str, font=f_n, fill=(255, 255, 255))

    # Icon circle
    draw_vector_icon(d4, ic, 1476, cy_step, 42, col, bg_color=(236, 244, 252))

    # Text
    d4.text((1535, sy + 6), st_title, font=get_font(18, bold=True), fill=DARK_PILL)
    draw_multiline(d4, (1535, sy + 32), st_desc, get_font(14, bold=False), (40, 50, 65), 355, line_spacing=3)
    sy += 126

s4_path = os.path.join(SLIDES_OUT_DIR, "slide_4.png")
s4.save(s4_path, quality=95)


# ==============================================================================
# SLIDE 5: TECH STACK & SYSTEM ARCHITECTURE (Exact Reference Page 5 Layout!)
# Left: 6 Categorized Pastel Tech Stack Cards (2x3 Grid)
# Right: 6 Horizontal Layered System Architecture Bars connected by downward arrows
# Bottom: Full-Width End-to-End 5-Stage Pipeline Strip
# ==============================================================================
print("Building Slide 5: Tech Stack & System Architecture (Reference Page 5 Layout)...")
s5, d5 = create_sustainova_frame("TECH STACK & SYSTEM ARCHITECTURE", page_num=3)

draw_pill_header(d5, [168, 128, 682, 184], "TECHNOLOGY STACK", fill=DARK_PILL, radius=10, font_size=25)
draw_pill_header(d5, [1088, 128, 1575, 184], "SYSTEM ARCHITECTURE", fill=DARK_PILL, radius=10, font_size=25)

# Vertical divider line between Tech Stack and System Architecture
d5.line([758, 198, 758, 845], fill=(120, 135, 150), width=2)

# --- LEFT: 6 CATEGORIZED TECH STACK CARDS (2x3 Grid) ---
tech_cards = [
    (105, 212, "cube", GREEN_ACCENT, (232, 246, 236), "3D FRONTEND & GIS", [
        "Three.js WebGL FEA Stress Mesh",
        "HTML5 Bathymetric India GIS Canvas",
        "Web Speech API (STT / TTS Voice)",
        "Dual Light/Dark Enterprise SaaS UI",
        "Chart.js & 200 Hz Oscilloscope"
    ]),
    (435, 212, "ai", BLUE_ACCENT, (226, 240, 252), "PHYSICS AI & PROGNOSTICS", [
        "Paris' Law Crack Growth da/dN",
        "LSTM Autoencoder Anomaly MSE",
        "Bayesian Cross-Modal Risk Matrix",
        "Physics-Informed AI Co-Pilot",
        "Welch FFT PSD Modal Solver"
    ]),
    (105, 432, "drone", TEAL_ACCENT, (225, 244, 246), "COMPUTER VISION & 3D", [
        "OpenCV CLAHE + Canny + Morph",
        "YOLOv8 Structural Crack Detector",
        "Medial-Axis Skeletonization (0.25mm)",
        "Open3D ICP 3D LiDAR Point Cloud",
        "HSV Galvanic Rebar Corrosion Index"
    ]),
    (435, 432, "code", GREEN_ACCENT, (235, 246, 236), "BACKEND & STREAMING", [
        "Python 3.11 + FastAPI Async Core",
        "200 Hz WebSocket Telemetry Engine",
        "SciPy Signal & NumPy Matrix Solver",
        "RESTful JSON & Audit Export APIs",
        "Multi-Corridor Digital Twin State"
    ]),
    (105, 652, "shield", ORANGE_ACCENT, (252, 242, 228), "SECURITY & PERSISTENCE", [
        "SHA-256 Auth + +91 SMS OTP 2FA",
        "SQLite3 WAL Mode Telemetry DB",
        "Sensor Trust Guard Fault Quarantine",
        "Role-Based Access (NHAI / MoRTH)",
        "Docker & Render Cloud Containers"
    ]),
    (435, 652, "map", PURPLE_ACCENT, (242, 234, 252), "INDIAN CODES & CORRIDORS", [
        "BIS IS 456:2000 & IRC:112-2020",
        "IRC:6 Class 70R L/800 Deflection",
        "MoRTH IBMS Digital Certificates",
        "Atal Setu (MTHL) & Bandra-Worli",
        "Chenab Rail Arch & Signature Bridge"
    ])
]

for x0, y0, ic, col, hdr_bg, title, bullets in tech_cards:
    cw, ch = 305, 202
    d5.rounded_rectangle([x0, y0, x0 + cw, y0 + ch], radius=14, fill=(252, 254, 255), outline=(195, 210, 222), width=2)
    d5.rounded_rectangle([x0 + 2, y0 + 2, x0 + cw - 2, y0 + 52], radius=12, fill=hdr_bg)
    draw_vector_icon(d5, ic, x0 + 30, y0 + 27, 18, col)
    d5.text((x0 + 56, y0 + 15), title, font=get_font(15, bold=True), fill=(15, 25, 35))
    by = y0 + 62
    for b in bullets:
        d5.ellipse([x0 + 16, by + 7, x0 + 22, by + 13], fill=col)
        d5.text((x0 + 32, by), b, font=get_font(13, bold=False), fill=(30, 40, 55))
        by += 26

# --- RIGHT: 6 HORIZONTAL LAYERED SYSTEM ARCHITECTURE STACK ---
arch_layers = [
    ("bridge", GREEN_ACCENT, (226, 244, 232), "NATIONAL ASSET\nLAYER", [
        "Atal Setu (MTHL-01)", "Bandra-Worli Sea Link", "Chenab Rail Arch (J&K)", "Signature Bridge Delhi", "NHAI / MoRTH Engineers"
    ]),
    ("cube", BLUE_ACCENT, (225, 238, 252), "ENTERPRISE UI\n& GIS LAYER", [
        "3D FEA Von Mises Twin", "India Bathymetric GIS", "Before/After Vision Slider", "Two-Way Voice Co-Pilot", "+91 SMS OTP 2FA Portal"
    ]),
    ("ai", TEAL_ACCENT, (224, 244, 242), "AI & PHYSICS\nFUSION LAYER", [
        "OpenCV + YOLOv8 Crack AI", "Open3D ICP LiDAR Scan", "Welch FFT PSD Modal", "LSTM AE Anomaly MSE", "Paris' Law 5-Yr RUL"
    ]),
    ("shield", PURPLE_ACCENT, (238, 232, 252), "TRUST & CODE\nCOMPLIANCE", [
        "Sensor Trust Guard", "Fault Spike Quarantine", "IS 456:2000 (0.3mm)", "IRC:112 & Class 70R", "MoRTH IBMS Sign-Off"
    ]),
    ("code", GREEN_ACCENT, (228, 245, 234), "FASTAPI ASYNC\nBACKEND CORE", [
        "Python 3.11 FastAPI", "200 Hz WebSocket Push", "Cross-Modal Risk Solver", "Automated Work Orders", "Physics Co-Pilot Engine"
    ]),
    ("sensor", BLUE_ACCENT, (225, 240, 252), "DATA & CLOUD\nPERSISTENCE", [
        "SQLite3 WAL Audit DB", "SHA-256 Session Ledger", "CSV / PDF Report Export", "Docker / Render Cloud", "Live Edge IoT Stream"
    ])
]

ly = 212
for idx, (ic, col, l_bg, l_name, items) in enumerate(arch_layers):
    lx0, lx1 = 802, 1858
    lh = 84
    d5.rounded_rectangle([lx0, ly, lx1, ly + lh], radius=14, fill=(255, 255, 255), outline=(145, 165, 185), width=2)
    # Left colored wedge banner inside bar
    d5.polygon([(lx0 + 2, ly + 2), (lx0 + 275, ly + 2), (lx0 + 310, ly + lh - 2), (lx0 + 2, ly + lh - 2)], fill=l_bg)
    draw_vector_icon(d5, ic, lx0 + 44, ly + lh / 2, 24, col)

    for li_idx, line_str in enumerate(l_name.split("\n")):
        d5.text((lx0 + 82, ly + 18 + li_idx * 22), line_str, font=get_font(17, bold=True), fill=(15, 25, 35))

    # Items separated by vertical bars
    ix = lx0 + 325
    iw = (lx1 - ix - 15) / len(items)
    for it_idx, it_txt in enumerate(items):
        draw_multiline(d5, (ix + it_idx * iw + 4, ly + 22), it_txt, get_font(14, bold=True), (25, 35, 50), iw - 10, line_spacing=2, align="center")
        if it_idx < len(items) - 1:
            d5.line([ix + (it_idx + 1) * iw, ly + 16, ix + (it_idx + 1) * iw, ly + lh - 16], fill=(180, 195, 210), width=2)

    # Downward arrow to next layer
    if idx < len(arch_layers) - 1:
        ax = 1365
        d5.line([ax, ly + lh, ax, ly + lh + 22], fill=DARK_PILL, width=3)
        d5.polygon([(ax - 7, ly + lh + 12), (ax + 7, ly + lh + 12), (ax, ly + lh + 22)], fill=DARK_PILL)

    ly += lh + 23

# --- BOTTOM: FULL-WIDTH 5-STAGE PIPELINE BAR (Exact Match to Reference Slide 5 Bottom Bar) ---
d5.rounded_rectangle([225, 868, 1725, 962], radius=16, fill=(252, 255, 252), outline=TEAL_BAR, width=2)
pipe_stages = [
    ("drone", GREEN_ACCENT, "UAV + 200 Hz\nIOT INGEST", 275),
    ("shield", TEAL_ACCENT, "SENSOR TRUST\nQUARANTINE", 575),
    ("ai", BLUE_ACCENT, "AI VISION &\nWELCH FFT FUSION", 875),
    ("cube", PURPLE_ACCENT, "3D FEA TWIN &\nPARIS' LAW RUL", 1185),
    ("check", DARK_PILL, "MORTH CERTIFICATE\n& WORK ORDER", 1485)
]
for idx, (ic, col, p_txt, px) in enumerate(pipe_stages):
    draw_vector_icon(d5, ic, px, 915, 28, col, bg_color=(235, 245, 245))
    for l_i, l_s in enumerate(p_txt.split("\n")):
        d5.text((px + 38, 892 + l_i * 22), l_s, font=get_font(17, bold=True), fill=(15, 25, 35))
    if idx < len(pipe_stages) - 1:
        ax = px + 230
        d5.line([ax, 915, ax + 28, 915], fill=TEAL_BAR, width=3)
        d5.polygon([(ax + 18, 907), (ax + 28, 915), (ax + 18, 923)], fill=TEAL_BAR)

s5_path = os.path.join(SLIDES_OUT_DIR, "slide_5.png")
s5.save(s5_path, quality=95)


# ==============================================================================
# SLIDE 6: FEASIBILITY, VIABILITY & FUTURE ROADMAP (Exact Reference Page 6 Layout!)
# Left: BUSINESS MODEL (Phase 1 - Pilot & Validation, Phase 2 - Commercialization)
# Center: FEASIBILITY (5 icon rows) + SCALABILITY (5 icon rows) + VIABILITY (5 Star Ratings)
# Right: FUTURE SCOPE (6 icon-backed roadmap items)
# ==============================================================================
print("Building Slide 6: Feasibility, Viability & Future Roadmap (Reference Page 6 Layout)...")
s6, d6 = create_sustainova_frame("FEASIBILITY, VIABILITY & FUTURE ROADMAP", page_num=4)

draw_pill_header(d6, [108, 138, 542, 194], "BUSINESS MODEL", fill=DARK_PILL, radius=10, font_size=24)
draw_pill_header(d6, [812, 138, 1372, 194], "FEASIBILITY & VIABILITY", fill=DARK_PILL, radius=10, font_size=24)
draw_pill_header(d6, [1418, 138, 1852, 194], "FUTURE SCOPE", fill=DARK_PILL, radius=10, font_size=24)

# Vertical dividers
d6.line([614, 178, 614, 945], fill=(80, 95, 110), width=2)
d6.line([1430, 222, 1430, 935], fill=(80, 95, 110), width=2)

# --- LEFT COLUMN: BUSINESS MODEL (Phase 1 & Phase 2) ---
phases = [
    (235, "Phase 1 – Pilot & Validation (NHAI / MSRDC)", [
        ("B2G & Corridor Pilots", [
            "NHAI & MoRTH IBMS Pilot Spans",
            "MSRDC Atal Setu & Sea Link Trial",
            "Smart City & Metro Rail Partnerships",
            "DST / NIDHI-PRAYAS & IndiaAI Grants"
        ]),
        ("Revenue & Cost Model", [
            "Govt Innovation & R&D Grants",
            "Pilot Bridge Instrumentation Contracts",
            "₹1.8L Edge IoT Node Kit per Span",
            "80% Lower CapEx vs. Legacy SHM"
        ])
    ]),
    (565, "Phase 2 – National Commercialization", [
        ("Enterprise SaaS Platform", [
            "Per-Bridge Annual Digital Twin SaaS",
            "Automated Drone AuditaaS Portal",
            "MoRTH Compliance API Licensing",
            "EPC Contractor Defect Liability SLA"
        ]),
        ("Scalable Revenue Streams", [
            "₹2.4L/yr SaaS Subscription per Bridge",
            "Enterprise State-PWD Corridor Licenses",
            "Predictive CFRP Retrofit Advisory",
            "Insurance Risk Underwriting APIs"
        ])
    ])
]

for py, p_title, cols in phases:
    # Arrow banner header
    d6.polygon([(115, py + 10), (548, py + 10), (575, py + 40), (548, py + 70), (115, py + 70)], fill=DARK_PILL)
    d6.ellipse([78, py - 2, 162, py + 82], fill=(255, 255, 255), outline=DARK_PILL, width=3)
    draw_vector_icon(d6, "chart", 120, py + 40, 28, DARK_PILL)
    d6.text((172, py + 24), p_title, font=get_font(19, bold=True), fill=(255, 255, 255))

    # Two sub-cards: Business Model & Revenue Model
    for c_idx, (c_hdr, c_bullets) in enumerate(cols):
        cx0 = 78 + c_idx * 254
        cy0 = py + 94
        cw, ch = 242, 222
        d6.rounded_rectangle([cx0, cy0, cx0 + cw, cy0 + ch], radius=14, fill=(252, 254, 255), outline=(145, 195, 235), width=2)
        d6.rounded_rectangle([cx0 + 4, cy0 + 4, cx0 + cw - 4, cy0 + 52], radius=10, fill=(224, 238, 252))
        d6.text((cx0 + 18, cy0 + 16), ("₹ " if c_idx == 1 else "■ ") + c_hdr, font=get_font(15, bold=True), fill=(15, 25, 35))
        by = cy0 + 66
        for b in c_bullets:
            d6.ellipse([cx0 + 14, by + 6, cx0 + 20, by + 12], fill=DARK_PILL)
            draw_multiline(d6, (cx0 + 28, by - 1), b, get_font(13, bold=False), (25, 35, 50), cw - 36, line_spacing=2)
            by += 37

# --- CENTER COLUMN: FEASIBILITY & SCALABILITY + VIABILITY STAR MATRIX ---
d6.rounded_rectangle([692, 218, 984, 272], radius=8, fill=(255, 255, 255), outline=DARK_PILL, width=2)
d6.text((748, 228), "FEASIBILITY", font=get_font(25, bold=True), fill=DARK_PILL)

d6.rounded_rectangle([1072, 218, 1364, 272], radius=8, fill=(255, 255, 255), outline=DARK_PILL, width=2)
d6.text((1128, 228), "SCALABILITY", font=get_font(25, bold=True), fill=DARK_PILL)

# Dotted center divider between Feasibility and Scalability
for yy in range(225, 765, 8):
    d6.line([1015, yy, 1015, yy + 4], fill=(160, 175, 190), width=2)

feas_items = [
    ("sensor", "Low-Cost Edge IoT Hardware", "Uses off-the-shelf MEMS accelerometers, FBG optical strain & UAV cameras."),
    ("shield", "Zero Traffic Closure Setup", "Non-invasive clamp-on nodes & drone flight scans require zero lane closures."),
    ("ai", "100% Open-Source AI Core", "Built on Python, FastAPI, OpenCV, YOLOv8, Three.js & SQLite — zero license fees."),
    ("code", "Production-Ready Prototype", "Live 200 Hz WebSocket digital twin, Welch FFT & Paris' Law RUL already working."),
    ("voice", "Field-Ready Web & Voice UI", "Bilingual Hindi/English Voice Co-Pilot & mobile work-order portal for engineers.")
]

scal_items = [
    ("cube", "Cloud-Native Container Stack", "Docker, Render & Railway ready to stream 10,000+ bridge spans concurrently."),
    ("chart", "Multi-Corridor SQLite / Postgres", "Handles NHAI highways, MSRDC sea links, railways & metro viaducts seamlessly."),
    ("drone", "Modular Plug-and-Play Agents", "Easily add thermal IR, acoustic emission, or satellite InSAR deformation modules."),
    ("map", "Pan-India IBMS Integration", "Direct REST/CSV interoperability with MoRTH Indian Bridge Management System."),
    ("check", "Global Standards Adaptable", "Configurable rule engine supports BIS IS 456, IRC:112, Eurocode & AASHTO.")
]

for idx, (ic, f_title, f_desc) in enumerate(feas_items):
    fy = 294 + idx * 96
    draw_vector_icon(d6, ic, 682, fy + 28, 28, BLUE_ACCENT, bg_color=(226, 240, 252))
    d6.text((724, fy + 2), f_title, font=get_font(16, bold=True), fill=NAVY_TITLE)
    draw_multiline(d6, (724, fy + 24), f_desc, get_font(13, bold=False), (35, 45, 60), 275, line_spacing=2)

for idx, (ic, s_title, s_desc) in enumerate(scal_items):
    fy = 294 + idx * 96
    draw_vector_icon(d6, ic, 1072, fy + 28, 28, PURPLE_ACCENT, bg_color=(242, 232, 252))
    d6.text((1114, fy + 2), s_title, font=get_font(16, bold=True), fill=(88, 28, 148))
    draw_multiline(d6, (1114, fy + 24), s_desc, get_font(13, bold=False), (35, 45, 60), 275, line_spacing=2)

# Bottom Center: VIABILITY Box + 5 Star Rating Columns (Exact Match to Reference Slide 6)
d6.rounded_rectangle([874, 774, 1170, 826], radius=8, fill=(255, 255, 255), outline=DARK_PILL, width=2)
d6.text((954, 783), "VIABILITY", font=get_font(25, bold=True), fill=DARK_PILL)

viability_metrics = [
    ("bridge", "NHAI / MoRTH\nAdoption", 5, 685),
    ("chart", "68% Lifecycle\nCost Savings", 5, 835),
    ("check", "IRC / BIS Code\nRelevance", 5, 985),
    ("cube", "Pan-India\nScalability", 5, 1135),
    ("shield", "Long-Term\nSustainability", 5, 1285)
]
for idx, (ic, v_lbl, stars, vx) in enumerate(viability_metrics):
    draw_vector_icon(d6, ic, vx + 45, 862, 20, DARK_PILL, bg_color=(232, 242, 250))
    draw_multiline(d6, (vx - 10, 888), v_lbl, get_font(13, bold=True), (25, 35, 50), 110, line_spacing=2, align="center")
    for s_i in range(5):
        draw_star(d6, vx + 5 + s_i * 20, 936, 8, DARK_PILL)
    if idx < len(viability_metrics) - 1:
        d6.line([vx + 115, 848, vx + 115, 950], fill=(160, 175, 190), width=2)

# --- RIGHT COLUMN: FUTURE SCOPE (6 Icon Roadmap Rows) ---
future_items = [
    ("drone", BLUE_ACCENT, "Autonomous Swarm Drone Docks", "Solar-powered UAV stations on sea links for automated daily post-monsoon scans."),
    ("map", PURPLE_ACCENT, "ISRO NISAR Satellite InSAR Fusion", "Combine millimeter radar interferometry with ground FBG strain sensors."),
    ("sensor", TEAL_ACCENT, "Digital Weigh-In-Motion (WIM)", "Auto-correlate overloaded Class 70R trucks with real-time girder micro-strain spikes."),
    ("bridge", GREEN_ACCENT, "Smart City & Metro Rail Grid", "Expand from NHAI bridges to metro viaducts, tunnels & dam spillways."),
    ("shield", BLUE_ACCENT, "National MoRTH IBMS Cloud Sync", "Direct API push of signed structural health certificates to central ministry portal."),
    ("ai", PURPLE_ACCENT, "Generative FEA Retrofit Simulator", "Simulate seismic Zone-V earthquake resilience & pre-stress tendon post-tensioning.")
]

fy = 228
for ic, col, ft_title, ft_desc in future_items:
    draw_vector_icon(d6, ic, 1512, fy + 38, 36, col, bg_color=(236, 242, 252))
    d6.text((1564, fy + 4), ft_title, font=get_font(18, bold=True), fill=col)
    draw_multiline(d6, (1564, fy + 28), ft_desc, get_font(13, bold=False), (35, 45, 60), 315, line_spacing=2)
    fy += 120

s6_path = os.path.join(SLIDES_OUT_DIR, "slide_6.png")
s6.save(s6_path, quality=95)


# ==============================================================================
# SLIDE 7: SDG ALIGNMENT & SUSTAINABILITY IMPACT (Exact Reference Page 7 Layout!)
# Top: SDG ALIGNMENT pill + 3 Official UN SDG Cards (SDG 9, SDG 11, SDG 12 & 13)
# Middle: SUSTAINABILITY IMPACT pill + 3 Columns (ENVIRONMENTAL, SOCIAL, ECONOMIC)
# Bottom: IMPACT INDICATORS pill + 5 Quantified Metric Strip
# ==============================================================================
print("Building Slide 7: SDG Alignment & Sustainability Impact (Reference Page 7 Layout)...")
s7, d7 = create_sustainova_frame("SDG ALIGNMENT & SUSTAINABILITY IMPACT", page_num=5)

draw_pill_header(d7, [640, 145, 1202, 204], "SDG ALIGNMENT", fill=DARK_PILL, radius=10, font_size=26)

# 3 Official UN SDG Cards matching Reference Page 7
sdg_cards = [
    (36, 224, (242, 106, 46), "9", "INDUSTRY,\nINNOVATION &\nINFRASTRUCTURE", "SDG 9 – INDUSTRY, INNOVATION &\nINFRASTRUCTURE (PRIMARY)", [
        "AI + 3D FEA Digital Twin for resilient national highways & sea links",
        "Continuous 200 Hz IoT structural fatigue & modal monitoring",
        "Automated BIS IS 456:2000 & IRC:112-2020 code compliance"
    ]),
    (656, 224, (249, 157, 38), "11", "SUSTAINABLE\nCITIES AND\nCOMMUNITIES", "SDG 11 – SUSTAINABLE CITIES\n& SAFE PUBLIC TRANSIT", [
        "Prevents catastrophic urban bridge & flyover collapses (zero fatalities)",
        "Protects lifeline corridors (Atal Setu, Bandra-Worli, Chenab Rail Arch)",
        "Early-warning SMS OTP & Voice Co-Pilot alerts for civic authorities"
    ]),
    (1276, 224, (191, 139, 46), "12", "RESPONSIBLE\nCONSUMPTION &\nCLIMATE (SDG 13)", "SDG 12 & 13 – RESOURCE EFFICIENCY\n& CLIMATE RESILIENCE", [
        "Extends bridge service life by +15–25 years via targeted CFRP retrofits",
        "Cuts embodied cement & steel carbon emissions by 60% vs. demolition",
        "Monitors extreme monsoon flood scour & Seismic Zone-V dynamic drift"
    ])
]

for x0, y0, sdg_col, sdg_num, sdg_badge_lbl, card_title, bullets in sdg_cards:
    cw, ch = 592, 258
    d7.rounded_rectangle([x0, y0, x0 + cw, y0 + ch], radius=12, fill=(255, 255, 255), outline=(145, 160, 175), width=2)

    # Left UN SDG Colored Square Tile
    bx0, by0 = x0 + 18, y0 + 28
    bw, bh = 188, 196
    d7.rounded_rectangle([bx0, by0, bx0 + bw, by0 + bh], radius=8, fill=sdg_col)
    d7.text((bx0 + 14, by0 + 10), sdg_num, font=get_font(44, bold=True), fill=(255, 255, 255))
    for l_idx, l_str in enumerate(sdg_badge_lbl.split("\n")):
        d7.text((bx0 + 68 if sdg_num == "9" else bx0 + 78, by0 + 14 + l_idx * 17), l_str, font=get_font(12, bold=True), fill=(255, 255, 255))

    # Draw UN SDG emblem inside the colored tile (white circle with colored icon inside)
    if sdg_num == "9":
        draw_vector_icon(d7, "cube", bx0 + 94, by0 + 132, 42, sdg_col, bg_color=(255, 255, 255))
    elif sdg_num == "11":
        draw_vector_icon(d7, "bridge", bx0 + 94, by0 + 132, 42, sdg_col, bg_color=(255, 255, 255))
    else:
        draw_vector_icon(d7, "shield", bx0 + 94, by0 + 132, 42, sdg_col, bg_color=(255, 255, 255))

    # Vertical separator line
    d7.line([bx0 + bw + 18, y0 + 24, bx0 + bw + 18, y0 + ch - 24], fill=DARK_PILL, width=2)

    # Right header box & bullets
    rx0 = bx0 + bw + 32
    d7.rectangle([rx0, y0 + 14, x0 + cw - 14, y0 + 82], fill=(228, 238, 228))
    for t_idx, t_str in enumerate(card_title.split("\n")):
        d7.text((rx0 + 10, y0 + 20 + t_idx * 26), t_str, font=get_font(18, bold=True), fill=(15, 25, 35))

    by = y0 + 98
    for b in bullets:
        d7.ellipse([rx0 + 10, by + 8, rx0 + 18, by + 16], fill=(15, 25, 35))
        draw_multiline(d7, (rx0 + 28, by), b, get_font(15, bold=False), (25, 35, 50), cw - (rx0 - x0) - 38, line_spacing=3)
        by += 50

# --- MIDDLE: SUSTAINABILITY IMPACT (3 Columns: ENVIRONMENTAL, SOCIAL, ECONOMIC) ---
draw_pill_header(d7, [640, 504, 1202, 562], "SUSTAINABILITY IMPACT", fill=DARK_PILL, radius=10, font_size=26)

impact_cols = [
    (48, 584, "ENVIRONMENTAL", [
        "60% lower embodied CO2 by preventing bridge demolition & reconstruction",
        "Targeted CFRP polymer wrapping cuts raw concrete & steel waste by 75%",
        "Early detection of marine chloride & flood scour degradation"
    ]),
    (682, 584, "SOCIAL", [
        "Protects millions of daily Indian commuters from sudden structural failure",
        "Eliminates hazardous manual rope-access inspections via UAV drones",
        "Bilingual Voice AI Co-Pilot empowers field engineers across India"
    ]),
    (1316, 584, "ECONOMIC", [
        "68% reduction in lifecycle highway & railway bridge maintenance budgets",
        "Prevents supply-chain paralysis on lifeline ports (JNPT / Mumbai MTHL)",
        "Prioritizes MoRTH capex across 1.72+ Lakh bridges via quantitative RUL"
    ])
]

for x0, y0, col_title, bullets in impact_cols:
    cw, ch = 556, 182
    d7.rectangle([x0, y0, x0 + cw, y0 + ch], fill=(255, 255, 255), outline=(130, 145, 160), width=2)
    d7.rectangle([x0 + 2, y0 + 2, x0 + cw - 2, y0 + 54], fill=(225, 238, 226))
    f_ct = get_font(25, bold=True)
    tb = d7.textbbox((0, 0), col_title, font=f_ct)
    d7.text((x0 + (cw - (tb[2] - tb[0])) / 2, y0 + 11), col_title, font=f_ct, fill=(15, 25, 35))

    by = y0 + 66
    for b in bullets:
        d7.ellipse([x0 + 24, by + 8, x0 + 32, by + 16], fill=(15, 25, 35))
        draw_multiline(d7, (x0 + 44, by), b, get_font(15, bold=False), (20, 30, 45), cw - 58, line_spacing=2)
        by += 36

# --- BOTTOM: IMPACT INDICATORS BAR (Exact Match to Reference Page 7 Bottom Strip) ---
draw_pill_header(d7, [640, 788, 1202, 845], "IMPACT INDICATORS", fill=DARK_PILL, radius=10, font_size=26)

d7.rectangle([28, 872, 1852, 945], fill=(255, 255, 255), outline=(120, 135, 150), width=2)
indicators = [
    ("0.25 mm/px", "AI Crack GSD Precision"),
    ("200 Hz Stream", "MEMS + FBG Sensor Fusion"),
    ("+35% RUL Gain", "Paris' Law CFRP Retrofit"),
    ("68% Cost Saved", "Preventive vs. Rebuild"),
    ("100% IS/IRC", "MoRTH IBMS Compliance")
]
iw = (1852 - 28) / len(indicators)
for idx, (ind_val, ind_lbl) in enumerate(indicators):
    ix = 28 + idx * iw
    f_iv = get_font(20, bold=True)
    f_il = get_font(16, bold=True)
    vb = d7.textbbox((0, 0), ind_val, font=f_iv)
    lb = d7.textbbox((0, 0), ind_lbl, font=f_il)
    d7.text((ix + (iw - (vb[2] - vb[0])) / 2, 880), ind_val, font=f_iv, fill=NAVY_TITLE)
    d7.text((ix + (iw - (lb[2] - lb[0])) / 2, 910), ind_lbl, font=f_il, fill=(15, 25, 35))
    if idx < len(indicators) - 1:
        d7.line([ix + iw, 885, ix + iw, 932], fill=DARK_PILL, width=2)

s7_path = os.path.join(SLIDES_OUT_DIR, "slide_7.png")
s7.save(s7_path, quality=95)


# ==============================================================================
# SLIDE 8: THANK YOU SLIDE (Official SUSTAINOVA 2026 Thank You + Live App Summary Strip)
# ==============================================================================
print("Building Slide 8: Thank You Slide...")
s8 = u_p8.copy()
d8 = ImageDraw.Draw(s8)

# Enhance bottom area of Thank You slide with clean Project & Team summary pill
d8.rounded_rectangle([240, 775, 1680, 915], radius=18, fill=(244, 249, 252), outline=TEAL_BAR, width=3)
d8.text((310, 792), "INFRAGUARD INDIA — AUTONOMOUS 3D FEA DIGITAL TWIN & STRUCTURAL HEALTH COMMAND CENTER", font=get_font(23, bold=True), fill=NAVY_TITLE)
d8.text((435, 832), "TEAM BYTE BUSTERS  |  ANUJ MALVIYA  •  AAYUSHI GUNDEGAONKAR  •  SAKSHI JAIN", font=get_font(20, bold=True), fill=DARK_PILL)
d8.text((395, 870), "ACROPOLIS INSTITUTE OF TECHNOLOGY & RESEARCH, INDORE   |   SDG 9: INDUSTRY, INNOVATION & INFRASTRUCTURE", font=get_font(17, bold=True), fill=TEAL_BAR)

s8_path = os.path.join(SLIDES_OUT_DIR, "slide_8.png")
s8.save(s8_path, quality=95)

# Also copy slide_1..slide_8 to frontend/ppt_assets/exact_slides so existing links work seamlessly
EXACT_DIR = os.path.join(ASSETS_DIR, "exact_slides")
os.makedirs(EXACT_DIR, exist_ok=True)
slide_paths = [s1_path, s2_path, s3_path, s4_path, s5_path, s6_path, s7_path, s8_path]
for idx, sp in enumerate(slide_paths, start=1):
    shutil.copyfile(sp, os.path.join(EXACT_DIR, f"slide_{idx}.png"))

# ==============================================================================
# EXPORT HIGH-RES PDF & EDITABLE POWERPOINT (.PPTX)
# ==============================================================================
print("Generating High-Resolution PDF and PowerPoint (.pptx)...")
pil_slides = [Image.open(p).convert("RGB") for p in slide_paths]

pdf_out_main = os.path.join(BASE_DIR, "INFRAGUARD_SUSTAINOVA_2026_FINAL.pdf")
pdf_out_fe = os.path.join(BASE_DIR, "frontend", "INFRAGUARD_SUSTAINOVA_2026_FINAL.pdf")
pil_slides[0].save(pdf_out_main, "PDF", resolution=300.0, save_all=True, append_images=pil_slides[1:])
shutil.copyfile(pdf_out_main, pdf_out_fe)

# Create PowerPoint (.pptx) with full 16:9 widescreen slides + speaker notes
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

speaker_notes = [
    "Slide 1: Welcome judges to SUSTAINOVA 2026 Ideathon! We are Team Byte Busters from Acropolis Institute of Technology & Research, Indore, presenting InfraGuard India under SDG 9.",
    "Slide 2: Meet Team Byte Busters — Anuj Malviya (Team Lead & Full-Stack/3D FEA Digital Twin), Aayushi Gundegaonkar (Computer Vision & Paris' Law Prognostics), and Sakshi Jain (200 Hz IoT Telemetry & BIS/IRC Standards).",
    "Slide 3: Problem Statement — Over 2,130 National Highway bridges in India are distressed. Manual biennial visual checks miss 78% of early micro-cracks, leading to tragedies like the Morbi collapse and ₹18,000+ Cr in reactive repairs.",
    "Slide 4: Proposed Solution & Innovation — InfraGuard combines sub-millimeter OpenCV/YOLOv8 crack vision (0.25mm/px), 200 Hz MEMS+FBG sensor fusion, a 3D Finite-Element Von Mises Stress Digital Twin, and a Hindi/English Voice Co-Pilot.",
    "Slide 5: Tech Stack & 6-Layer System Architecture — From National Corridors (Atal Setu MTHL, Bandra-Worli, Chenab Rail Arch, Signature Bridge) through our Enterprise GIS/3D UI, AI/Physics Fusion Layer, Sensor Trust Guard, FastAPI Async Core, and SQLite3 WAL Audit Ledger.",
    "Slide 6: Feasibility, Viability & Future Roadmap — Phase 1 B2G pilots with NHAI/MoRTH & MSRDC at ₹1.8L/span (80% cheaper than legacy SHM), scaling to Phase 2 SaaS licensing with 68% lifecycle cost savings, plus future ISRO NISAR InSAR & Swarm Drone Docks.",
    "Slide 7: SDG Alignment & Sustainability Impact — Directly advances SDG 9 (Primary), SDG 11 (Safe Public Transit), and SDG 12 & 13 (60% lower embodied CO2 & +35% RUL extension via targeted CFRP retrofitting).",
    "Slide 8: Thank You! Our full-stack InfraGuard India Enterprise Command Center is live for demonstration."
]

for idx, sp in enumerate(slide_paths):
    slide = prs.slides.add_slide(blank_layout)
    slide.shapes.add_picture(sp, Inches(0), Inches(0), width=Inches(13.333), height=Inches(7.5))
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = speaker_notes[idx]

pptx_out_main = os.path.join(BASE_DIR, "INFRAGUARD_SUSTAINOVA_2026_PPT.pptx")
pptx_out_fe = os.path.join(BASE_DIR, "frontend", "INFRAGUARD_SUSTAINOVA_2026_PPT.pptx")
prs.save(pptx_out_main)
shutil.copyfile(pptx_out_main, pptx_out_fe)

print("SUCCESS! Saved:")
print(" - PPTX:", pptx_out_main)
print(" - PDF :", pdf_out_main)
