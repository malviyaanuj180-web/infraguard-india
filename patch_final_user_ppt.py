"""
Patches the user's exact final 8-slide PDF (`media_1795577314399_876212bc.pdf`):
1. Slide 3 (Page 3): Replaces "StructSense" with "InfraGuard" in the DETAILED SOLUTION box.
2. Slide 5 (Page 5): Replaces "Camera / drone" with "Optical Camera" in the IOT & EDGE row.
3. Slide 6 (Page 6): Replaces "Drone Vision (AI)" and "Drone High-Res Optical" with "Optical Vision (AI)" and "High-Res Optical" in both PROTOTYPE DESIGN screenshots.
4. Exports the final 8-slide PowerPoint (.pptx) and high-res PDF (.pdf)!
"""

import os
import glob
import shutil
import pypdfium2 as pdfium
from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.util import Inches

UPLOAD_DIR = r"C:\Users\ACER\.gemini\antigravity\brain\62b11bf7-5dc3-4157-b4e7-78a57d988e9c\.user_uploaded"
files = sorted(glob.glob(os.path.join(UPLOAD_DIR, "media_1795577314399_*.pdf")))
LATEST_PDF = files[0]

BASE_DIR = r"C:\Users\ACER\.gemini\antigravity\scratch\infra-health-monitor"
ASSETS_DIR = os.path.join(BASE_DIR, "frontend", "ppt_assets")
SLIDES_OUT_DIR = os.path.join(ASSETS_DIR, "ref_matched_slides")
EXACT_DIR = os.path.join(ASSETS_DIR, "exact_slides")
os.makedirs(SLIDES_OUT_DIR, exist_ok=True)
os.makedirs(EXACT_DIR, exist_ok=True)

W, H = 1920, 1080

doc = pdfium.PdfDocument(LATEST_PDF)
pages = []
for i in range(len(doc)):
    p = doc[i]
    pil_img = p.render(scale=W / p.get_width()).to_pil().convert("RGB").resize((W, H), Image.LANCZOS)
    pages.append(pil_img)

def get_font(size, bold=False):
    candidates = ["calibrib.ttf", "segoeuib.ttf", "arialbd.ttf"] if bold else ["calibri.ttf", "segoeui.ttf", "arial.ttf"]
    for c in candidates:
        p = os.path.join(r"C:\Windows\Fonts", c)
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

# ==============================================================================
# PATCH SLIDE 3 (Page index 2): "StructSense" -> "InfraGuard"
# ==============================================================================
s3 = pages[2].copy()
d3 = ImageDraw.Draw(s3)
# Line 7 of DETAILED SOLUTION: "an early stage. StructSense aims to use"
# Let's check exact y range of that line: y=724..770, x=110..725
bg_s3 = s3.getpixel((115, 740))
d3.rectangle([115, 725, 725, 766], fill=bg_s3)
f_s3 = get_font(34, bold=True)
line_txt = "an early stage. InfraGuard aims to use"
tb = d3.textbbox((0, 0), line_txt, font=f_s3)
tw = tb[2] - tb[0]
# Center inside the left box (x: 96..740 -> center = 418)
d3.text((418 - tw / 2, 724), line_txt, font=f_s3, fill=(24, 34, 48))
pages[2] = s3

# ==============================================================================
# PATCH SLIDE 5 (Page index 4): "Camera / drone" -> "Optical Camera"
# ==============================================================================
s5 = pages[4].copy()
d5 = ImageDraw.Draw(s5)
# In IOT & EDGE bar (bottom right cell around x: 1655..1810, y: 805..872)
bg_s5 = s5.getpixel((1670, 815))
d5.rectangle([1658, 804, 1812, 872], fill=bg_s5)
f_s5 = get_font(23, bold=False)
t1 = "Optical"
t2 = "Camera"
b1 = d5.textbbox((0, 0), t1, font=f_s5)
b2 = d5.textbbox((0, 0), t2, font=f_s5)
cx_s5 = 1734
d5.text((cx_s5 - (b1[2] - b1[0]) / 2, 808), t1, font=f_s5, fill=(24, 34, 48))
d5.text((cx_s5 - (b2[2] - b2[0]) / 2, 838), t2, font=f_s5, fill=(24, 34, 48))
pages[4] = s5

# ==============================================================================
# PATCH SLIDE 6 (Page index 5): Remove "Drone" in both PROTOTYPE DESIGN screenshots
# ==============================================================================
s6 = pages[5].copy()
d6 = ImageDraw.Draw(s6)

# 1. Top-Right Full Screenshot in Slide 6:
# Cover entire text inside tab (x: 1695..1738, y: 295..324)
bg_top_tab = s6.getpixel((1710, 302))
d6.rectangle([1695, 296, 1738, 323], fill=bg_top_tab)
d6.text((1701, 297), "Optical", font=get_font(9, bold=True), fill=(56, 189, 248))
d6.text((1703, 309), "Vision", font=get_font(9, bold=True), fill=(56, 189, 248))

# Cover entire "Drone High-Res Optical" header line (x: 1682..1778, y: 338..354)
bg_top_hdr = s6.getpixel((1698, 344))
d6.rectangle([1684, 339, 1778, 353], fill=bg_top_hdr)
d6.text((1686, 340), "High-Res Optical", font=get_font(9, bold=True), fill=(255, 255, 255))

# 2. Bottom-Right Zoomed Screenshot in Slide 6:
# Cover entire text inside tab (x: 1628..1678, y: 702..742)
bg_bot_tab = s6.getpixel((1642, 720))
d6.rectangle([1630, 704, 1678, 740], fill=bg_bot_tab)
d6.text((1636, 706), "Optical", font=get_font(11, bold=True), fill=(56, 189, 248))
d6.text((1638, 721), "Vision", font=get_font(11, bold=True), fill=(56, 189, 248))

# Cover entire "Drone High-Res Optical" header line (x: 1615..1735, y: 754..772)
bg_bot_hdr = s6.getpixel((1618, 760))
d6.rectangle([1616, 755, 1735, 771], fill=bg_bot_hdr)
d6.text((1620, 756), "High-Res Optical", font=get_font(12, bold=True), fill=(255, 255, 255))

pages[5] = s6

# Save all 8 slides
slide_paths = []
for idx, img in enumerate(pages, start=1):
    sp = os.path.join(SLIDES_OUT_DIR, f"slide_{idx}.png")
    img.save(sp, quality=95)
    shutil.copyfile(sp, os.path.join(EXACT_DIR, f"slide_{idx}.png"))
    slide_paths.append(sp)

# Export High-Res PDF
pdf_out_main = os.path.join(BASE_DIR, "INFRAGUARD_SUSTAINOVA_2026_FINAL.pdf")
pdf_out_fe = os.path.join(BASE_DIR, "frontend", "INFRAGUARD_SUSTAINOVA_2026_FINAL.pdf")
pages[0].save(pdf_out_main, "PDF", resolution=300.0, save_all=True, append_images=pages[1:])
shutil.copyfile(pdf_out_main, pdf_out_fe)

# Export Editable PowerPoint (.pptx)
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

for idx, sp in enumerate(slide_paths):
    slide = prs.slides.add_slide(blank_layout)
    slide.shapes.add_picture(sp, Inches(0), Inches(0), width=Inches(13.333), height=Inches(7.5))

pptx_out_main = os.path.join(BASE_DIR, "INFRAGUARD_SUSTAINOVA_2026_PPT.pptx")
pptx_out_fe = os.path.join(BASE_DIR, "frontend", "INFRAGUARD_SUSTAINOVA_2026_PPT.pptx")
prs.save(pptx_out_main)
shutil.copyfile(pptx_out_main, pptx_out_fe)

print("SUCCESS! Patched Slide 3, Slide 5, and Slide 6 and exported Final PPTX & PDF.")
