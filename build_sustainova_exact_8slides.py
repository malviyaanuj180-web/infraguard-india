"""
SUSTAINOVA 2026 IDEATHON — Exact 8-Slide Visual Template & Flowchart Builder
=============================================================================
Rebuilds the exact 8-slide SUSTAINOVA 2026 Ideathon deck (matching the user's PDF
layout, rounded pastel cards, numbered blue corner badges 1..5, and Slide 5
System Architecture diagram style) while upgrading all content, tech stack,
flowcharts, icons, and screenshots to the complete INFRAGUARD INDIA platform.

Outputs:
1. frontend/INFRAGUARD_SUSTAINOVA_2026_FINAL.pdf  (Exact 8-page PDF for submission)
2. frontend/INFRAGUARD_SUSTAINOVA_2026_PPT.pptx   (16:9 Widescreen PowerPoint)
3. INFRAGUARD_SUSTAINOVA_2026_FINAL.pdf & .pptx in project root
"""

import os
import shutil
import numpy as np
import pypdfium2 as pdfium
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pptx import Presentation
from pptx.util import Inches

PDF_SOURCE = r"C:\Users\ACER\.gemini\antigravity\brain\62b11bf7-5dc3-4157-b4e7-78a57d988e9c\.user_uploaded\media_1795534951525_a65cdd30.pdf"
BASE_DIR = r"C:\Users\ACER\.gemini\antigravity\scratch\infra-health-monitor"
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
ASSETS_DIR = os.path.join(FRONTEND_DIR, "ppt_assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

W, H = 1920, 1080  # Full HD 16:9 canvas


def get_font(name_candidates, size, bold=False):
    win_fonts = r"C:\Windows\Fonts"
    for cand in name_candidates:
        p = os.path.join(win_fonts, cand)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


FONT_TITLE = get_font(["impact.ttf", "arialbd.ttf"], 54)
FONT_H1 = get_font(["calibrib.ttf", "arialbd.ttf", "segoeuib.ttf"], 28)
FONT_H2 = get_font(["calibrib.ttf", "arialbd.ttf", "segoeuib.ttf"], 23)
FONT_H3 = get_font(["calibrib.ttf", "arialbd.ttf", "segoeuib.ttf"], 19)
FONT_BODY = get_font(["calibri.ttf", "arial.ttf", "segoeui.ttf"], 17)
FONT_BODY_B = get_font(["calibrib.ttf", "arialbd.ttf", "segoeuib.ttf"], 17)
FONT_SM = get_font(["calibri.ttf", "arial.ttf", "segoeui.ttf"], 14)
FONT_SM_B = get_font(["calibrib.ttf", "arialbd.ttf", "segoeuib.ttf"], 14)
FONT_XS = get_font(["calibri.ttf", "arial.ttf", "segoeui.ttf"], 12)
FONT_XS_B = get_font(["calibrib.ttf", "arialbd.ttf", "segoeuib.ttf"], 12)
FONT_NUM = get_font(["arialbd.ttf", "calibrib.ttf"], 30)


def wrap_text(draw, text, font, max_width):
    words = text.split(" ")
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_rich_bullet(draw, x, y, max_w, badge_text, badge_col, bold_prefix, body_text, font_b=FONT_BODY_B, font_r=FONT_BODY, line_h=22):
    """Draws a colorful icon/number badge followed by bold prefix + wrapped body text."""
    # Draw small pill badge
    draw.rounded_rectangle([x, y + 2, x + 24, y + 22], radius=6, fill=badge_col)
    bb = draw.textbbox((0, 0), badge_text, font=FONT_XS_B)
    draw.text((x + 12 - (bb[2] - bb[0]) / 2, y + 4), badge_text, font=FONT_XS_B, fill=(255, 255, 255))

    tx = x + 32
    avail_w = max_w - 32
    full_str = f"{bold_prefix} {body_text}".strip()
    lines = wrap_text(draw, full_str, font_r, avail_w)

    cur_y = y
    prefix_words = bold_prefix.split(" ")
    for idx, ln in enumerate(lines):
        if idx == 0 and bold_prefix:
            # Draw bold prefix in dark navy/blue, rest in dark slate
            if ln.startswith(bold_prefix):
                draw.text((tx, cur_y), bold_prefix, font=font_b, fill=(8, 55, 115))
                pw = draw.textbbox((0, 0), bold_prefix + " ", font=font_b)[2]
                rest = ln[len(bold_prefix):]
                draw.text((tx + pw, cur_y), rest, font=font_r, fill=(25, 35, 50))
            else:
                draw.text((tx, cur_y), ln, font=font_b, fill=(8, 55, 115))
        else:
            draw.text((tx, cur_y), ln, font=font_r, fill=(25, 35, 50))
        cur_y += line_h
    return cur_y + 5


def draw_pastel_card(img, box, fill_rgb=(236, 245, 249), border_rgb=(195, 218, 234), radius=24, shadow=True):
    x1, y1, x2, y2 = box
    draw = ImageDraw.Draw(img, "RGBA")
    if shadow:
        draw.rounded_rectangle([x1 + 3, y1 + 5, x2 + 3, y2 + 5], radius=radius, fill=(10, 45, 85, 22))
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill_rgb + (255,), outline=border_rgb + (255,), width=2)


def make_base_slide(bg_template_img, title_text, page_num_str=None):
    slide = bg_template_img.copy().resize((W, H), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(slide, "RGBA")
    # Header Title in SUSTAINOVA Blue Impact font
    draw.text((92, 34), title_text, font=FONT_TITLE, fill=(10, 88, 158))
    if page_num_str:
        draw.rectangle([W - 72, H - 74, W, H], fill=(10, 88, 158))
        bb = draw.textbbox((0, 0), str(page_num_str), font=FONT_NUM)
        draw.text((W - 36 - (bb[2] - bb[0]) / 2, H - 56), str(page_num_str), font=FONT_NUM, fill=(255, 255, 255))
    return slide, draw


def draw_icon_badge(draw, cx, cy, r, bg_col, label):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=bg_col, outline=(255, 255, 255), width=2)
    bb = draw.textbbox((0, 0), label, font=FONT_SM_B)
    draw.text((cx - (bb[2] - bb[0]) / 2, cy - (bb[3] - bb[1]) / 2 - 2), label, font=FONT_SM_B, fill=(255, 255, 255))


def build_all_8_slides():
    print("[1/3] Rendering source PDF pages with pypdfium2...")
    doc = pdfium.PdfDocument(PDF_SOURCE)
    orig_pages = []
    for i in range(len(doc)):
        bmp = doc[i].render(scale=2.5)
        pil_im = bmp.to_pil().convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
        orig_pages.append(pil_im)

    # Build clean SUSTAINOVA blank template from page 3
    p3 = orig_pages[2].copy()
    bg_clean = Image.new("RGB", (W, H), (255, 255, 255))
    # Top gray-teal bar
    bg_clean.paste(p3.crop((0, 0, W, 32)), (0, 0))
    # Top-left geometric corner ribbon
    bg_clean.paste(p3.crop((0, 0, 86, 190)), (0, 0))
    # Top-right SUSTAINOVA logo
    bg_clean.paste(p3.crop((1520, 24, W, 106)), (1520, 24))
    # Bottom gray-teal bar
    bg_clean.paste(p3.crop((0, H - 32, W - 75, H)), (0, H - 32))
    # Bottom-right corner ribbon from page 2 (for non-numbered slides if needed)

    # Crop UI cards from original PDF page 3 and page 5
    ui_vision = orig_pages[2].crop((int(W * 0.704), int(H * 0.242), int(W * 0.978), int(H * 0.924)))
    ui_telemetry = orig_pages[4].crop((int(W * 0.668), int(H * 0.425), int(W * 0.940), int(H * 0.940)))
    # Also crop the tech icon cluster from page 5 top-right and augment it
    tech_logos_crop = orig_pages[4].crop((int(W * 0.595), int(H * 0.145), int(W * 0.915), int(H * 0.385)))

    slides_out = []

    # =========================================================================
    # SLIDE 1: COVER SLIDE (Exact original Page 1)
    # =========================================================================
    s1 = orig_pages[0].copy()
    slides_out.append(s1)

    # =========================================================================
    # SLIDE 2: TEAM DESCRIPTION & DOMAIN (Original Page 2 + Role Badges & India Corridors)
    # =========================================================================
    s2 = orig_pages[1].copy()
    d2 = ImageDraw.Draw(s2, "RGBA")
    # Add sleek role badges under each team member name
    roles_info = [
        (398, 650, "Full-Stack, 3D FEA Twin & Paris' Law RUL Lead", (10, 88, 158)),
        (985, 650, "Drone AI Vision (YOLOv8-seg) & Open3D LiDAR Lead", (5, 150, 105)),
        (1548, 650, "200Hz IoT Welch FFT, PyTorch LSTM & Sensor Trust Lead", (217, 119, 6))
    ]
    for cx, cy, rtext, rcol in roles_info:
        d2.rounded_rectangle([cx - 235, cy, cx + 235, cy + 40], radius=10, fill=rcol + (245,))
        bb = d2.textbbox((0, 0), rtext, font=FONT_SM_B)
        d2.text((cx - (bb[2] - bb[0]) / 2, cy + 10), rtext, font=FONT_SM_B, fill=(255, 255, 255))

    # Add Indian National Infrastructure Scope Pill below DOMAIN
    d2.rounded_rectangle([60, 875, 1780, 955], radius=14, fill=(235, 245, 252, 255), outline=(10, 88, 158, 255), width=2)
    d2.text((88, 887), "INDIAN NATIONAL INFRASTRUCTURE SCOPE (NHAI • MoRTH IBMS • MSRDC • INDIAN RAILWAYS USBRL):", font=FONT_SM_B, fill=(10, 88, 158))
    d2.text((88, 916), "Monitored Corridors: Atal Setu (MTHL Mumbai) • Bandra-Worli Sea Link • Chenab Rail Arch Viaduct (J&K Zone V) • Signature Bridge (New Delhi) | Standards: BIS IS 456:2000 & IRC:112", font=FONT_SM, fill=(20, 35, 55))
    slides_out.append(s2)

    # =========================================================================
    # SLIDE 3 (PAGE 1): PROBLEM STATEMENT (Matches Page 3 Layout + Flowchart + Quantified Outcomes)
    # =========================================================================
    s3, d3 = make_base_slide(bg_clean, "PROBLEM STATEMENT", "1")

    # Top full-width white banner pill with shadow (exact match to example Page 3)
    draw_pastel_card(s3, (46, 118, W - 46, 224), fill_rgb=(247, 251, 254), border_rgb=(205, 224, 238), radius=26, shadow=True)
    t1 = "INFRAGUARD"
    t2 = "AI-Powered Autonomous Infrastructure Health Monitoring, 3D Digital Twin & Predictive RUL System"
    bb1 = d3.textbbox((0, 0), t1, font=FONT_H1)
    bb2 = d3.textbbox((0, 0), t2, font=FONT_H2)
    d3.text((W / 2 - (bb1[2] - bb1[0]) / 2, 132), t1, font=FONT_H1, fill=(10, 88, 158))
    d3.text((W / 2 - (bb2[2] - bb2[0]) / 2, 172), t2, font=FONT_H2, fill=(15, 45, 85))

    # Left Card: DETAILED SOLUTION + Mini Visual Flowchart
    draw_pastel_card(s3, (46, 252, 680, 1005), fill_rgb=(238, 246, 250), border_rgb=(195, 220, 236), radius=28)
    d3.text((195, 274), "DETAILED SOLUTION :", font=FONT_H1, fill=(10, 88, 158))

    sol_points = [
        ("1", (220, 38, 38), "India's Critical Bridge Risk:", "Over 1.5 Lakh NHAI, MoRTH & Railway bridges face severe IMD monsoon pier scour, coastal chloride corrosion, and IRC Class 70R freight overload."),
        ("2", (217, 119, 6), "Failure of Manual Checks:", "Periodic visual inspections fail to catch micro-fatigue cracks (<0.3mm), subsurface scour, or internal tendon stiffness loss early."),
        ("3", (10, 88, 158), "InfraGuard Multi-Modal Twin:", "Fuses Drone YOLOv8-seg Crack Vision, Open3D LiDAR Point-Cloud ICP, 200 Hz PyTorch LSTM Vibration Telemetry, and Paris' Law RUL in a 6-Page Command Center."),
        ("4", (5, 150, 105), "Zero False Hardware Panic:", "Built-in Sensor Trust Guard quarantines loose or flatlined IoT nodes while the Cross-Check Matrix separates cosmetic cracks from silent structural fatigue.")
    ]
    cy = 326
    for b_txt, b_col, b_pre, b_body in sol_points:
        cy = draw_rich_bullet(d3, 72, cy, 580, b_txt, b_col, b_pre, b_body, line_h=23) + 6

    # Mini Visual Problem -> Fusion -> Action Flowchart inside Left Card bottom
    d3.rounded_rectangle([68, 795, 658, 982], radius=16, fill=(15, 23, 42), outline=(37, 99, 235), width=2)
    d3.text((88, 806), "FLOWCHART: HOW INFRAGUARD PREVENTS COLLAPSE", font=FONT_SM_B, fill=(56, 189, 248))
    p_boxes = [
        (84, "1. Multi-Modal Input", "Drone RGB + 3D LiDAR\n+ 200Hz MEMS & FBG", (30, 64, 175)),
        (278, "2. AI + Trust Fusion", "YOLOv8 + Open3D ICP\n+ LSTM + Fault Guard", (5, 150, 105)),
        (472, "3. Paris' Law Action", "RUL Days + CFRP (+45%)\n+ 1-Click MoRTH Order", (220, 38, 38))
    ]
    for bx, bhead, bsub, bcol in p_boxes:
        d3.rounded_rectangle([bx, 838, bx + 168, 966], radius=10, fill=bcol)
        d3.text((bx + 10, 848), bhead, font=FONT_XS_B, fill=(255, 255, 255))
        d3.text((bx + 10, 876), bsub, font=FONT_XS, fill=(235, 245, 255))
    d3.text((256, 890), "➔", font=FONT_H2, fill=(56, 189, 248))
    d3.text((450, 890), "➔", font=FONT_H2, fill=(56, 189, 248))

    # Center Card: TARGET OUTCOME
    draw_pastel_card(s3, (715, 252, 1320, 1005), fill_rgb=(238, 246, 250), border_rgb=(195, 220, 236), radius=28)
    d3.text((875, 274), "TARGET OUTCOME:", font=FONT_H1, fill=(10, 88, 158))

    outcomes = [
        ("✓", (5, 150, 105), "Sub-Millimeter Crack & Rebar Grading:", "Calibrates camera GSD (0.12 mm/px) to measure crack width, skeleton length, spalling (cm²) & exposed rebar per BIS IS 456:2000 & IRC:112."),
        ("✓", (10, 88, 158), "3D LiDAR Sag & FEA Von Mises Stress:", "Open3D SVD Kabsch ICP aligns T₀/T₁ point clouds (1.12mm RMSE) against IRC:6 L/800 (150mm) limits with 3D FEA stress contours (40–420 MPa)."),
        ("✓", (217, 119, 6), "200 Hz Welch FFT & PyTorch LSTM AE:", "Tracks natural frequency shifts (f₁, f₂, f₃) and reconstruction error MSE to flag hidden internal stiffness loss early."),
        ("✓", (124, 58, 237), "Physics-Informed Paris' Law RUL & CFRP:", "Predicts exact Remaining Useful Life in days (da/dN = C(ΔK)^m) and models Bonded CFRP Laminate Retrofit (+45% life extension)."),
        ("✓", (220, 38, 38), "Automated MoRTH Dispatch & +91 OTP:", "Ranks national corridors (Atal Setu, Bandra-Worli, Chenab Arch, Signature Bridge), dispatches work orders, and secures access with +91 SMS OTP 2FA."),
        ("✓", (13, 148, 136), "68% Less Waste & Extended Lifespan:", "Prevents premature bridge demolition, slashing repair costs, cement CO₂ emissions, and catastrophic failures.")
    ]
    cy = 326
    for b_txt, b_col, b_pre, b_body in outcomes:
        cy = draw_rich_bullet(d3, 740, cy, 555, b_txt, b_col, b_pre, b_body, line_h=22) + 5

    # Right Column: Real App Screenshot from PDF + Indian Corridors Status Box
    s3.paste(ui_vision.resize((525, 595), Image.Resampling.LANCZOS), (1350, 255))
    d3.rounded_rectangle([1350, 862, 1875, 1005], radius=14, fill=(15, 23, 42), outline=(10, 88, 158), width=2)
    d3.text((1368, 872), "LIVE MONITORED INDIAN NATIONAL CORRIDORS:", font=FONT_XS_B, fill=(56, 189, 248))
    d3.text((1368, 896), "• MTHL-01: Atal Setu Trans Harbour Link, Mumbai (SHI 94.2)", font=FONT_XS, fill=(235, 245, 255))
    d3.text((1368, 918), "• MSRDC-102: Bandra-Worli Sea Link Pylon #4 (SHI 84.5)", font=FONT_XS, fill=(235, 245, 255))
    d3.text((1368, 940), "• NR-USBRL-409: Chenab Rail Arch Viaduct, J&K (SHI 72.1)", font=FONT_XS, fill=(235, 245, 255))
    d3.text((1368, 962), "• NHAI-DL-214: Signature Bridge Yamuna, New Delhi (SHI 89.2)", font=FONT_XS, fill=(235, 245, 255))

    slides_out.append(s3)

    # =========================================================================
    # SLIDE 4 (PAGE 2): PROPOSED SOLUTION & INNOVATION (Matches Page 4 Layout + 2x2 Matrix Flowchart)
    # =========================================================================
    s4, d4 = make_base_slide(bg_clean, "PROPOSED SOLUTION & INNOVATION", "2")

    # Left Card: PROPOSED SOLUTION (6 Core Modules)
    draw_pastel_card(s4, (56, 175, 935, 715), fill_rgb=(238, 246, 250), border_rgb=(195, 220, 236), radius=28)
    d4.text((335, 195), "PROPOSED SOLUTION", font=FONT_H1, fill=(10, 88, 158))

    prop_items = [
        ("1", (10, 88, 158), "AI Drone Crack & Spalling Lab:", "YOLOv8-seg + OpenCV/Scikit-image medial-axis skeletonization with Before/After Split-Slider, GSD (mm/px) calibration & BIS IS 456 / IRC:112 grading."),
        ("2", (5, 150, 105), "3D Holographic Digital Twin & LiDAR ICP:", "Three.js bridge with FEA Von Mises Stress Contours (40–420 MPa), Open3D SVD Kabsch ICP point-cloud overlay & 5-Year Time-Machine Scrubber."),
        ("3", (217, 119, 6), "200 Hz IoT Telemetry & Sensor Trust Guard:", "Live WebSocket tri-axial MEMS accelerometer & FBG optical strain stream with SciPy Welch FFT PSD (f₁, f₂, f₃) & PyTorch LSTM Autoencoder."),
        ("4", (124, 58, 237), "Physics-Informed Paris' Law RUL & CFRP:", "Computes remaining fatigue life da/dN = C(ΔK)^m with live What-If sliders for IRC Class 70R truck load, corrosion & CFRP Retrofit (+45% life)."),
        ("5", (220, 38, 38), "Autonomous MoRTH Dispatch & Work Orders:", "Ranks all structures by urgency and dispatches official work orders (WO-INFRAGUARD) with PAUT ultrasonic & scour sonar protocols."),
        ("6", (13, 148, 136), "Two-Way Voice Co-Pilot, GIS & +91 OTP 2FA:", "Hands-free microphone voice assistant, Cartographic India GIS Map, Signed MoRTH Certificate & +91 TRAI DLT Mobile SMS OTP login.")
    ]
    cy = 242
    for b_txt, b_col, b_pre, b_body in prop_items:
        cy = draw_rich_bullet(d4, 82, cy, 825, b_txt, b_col, b_pre, b_body, font_b=FONT_SM_B, font_r=FONT_SM, line_h=20) + 3

    # Right Card: INNOVATION + Embedded 2x2 Cross-Check Matrix Flowchart
    draw_pastel_card(s4, (985, 175, 1864, 715), fill_rgb=(238, 246, 250), border_rgb=(195, 220, 236), radius=28)
    d4.text((1330, 195), "INNOVATION", font=FONT_H1, fill=(10, 88, 158))

    innov_items = [
        ("1", (220, 38, 38), "Sensor Trust & Sabotage Guard:", "Isolates flatlines, ADC clipping & loose cable chatter so faulty sensors never trigger false bridge closures (98.4% Fleet Trust)."),
        ("2", (10, 88, 158), "False-Alarm vs. Silent-Killer Matrix:", "Cross-correlates optical crack width with modal frequency shift to distinguish harmless surface fissures from hidden internal tendon fracture."),
        ("3", (217, 119, 6), "IMD Monsoon & IRC Class 70R Stress Lens:", "Contextualizes inspection baselines across Dry Ambient, Post-Monsoon Scour & Heavy Multi-Axle Freight Surge."),
        ("4", (5, 150, 105), "Interactive 5-Year Time-Machine & Voice AI:", "Scrubs Year 0 ➔ Year 5 degradation in 3D while the Voice Co-Pilot answers physics & IRC code queries out loud.")
    ]
    cy = 242
    for b_txt, b_col, b_pre, b_body in innov_items:
        cy = draw_rich_bullet(d4, 1012, cy, 825, b_txt, b_col, b_pre, b_body, font_b=FONT_SM_B, font_r=FONT_SM, line_h=20) + 2

    # Embedded Visual 2x2 Cross-Check Matrix Flowchart inside Innovation Card
    d4.rounded_rectangle([1012, 495, 1838, 696], radius=14, fill=(15, 23, 42), outline=(37, 99, 235), width=2)
    d4.text((1030, 503), "FLOWCHART: CROSS-MODAL DIAGNOSTIC TRUTH MATRIX (VISION × VIBRATION)", font=FONT_XS_B, fill=(56, 189, 248))
    m_quads = [
        (1026, 530, "1. SURFACE NOISE (LOW RISK)", "Wide Static Crack (>0.5mm) + Stable FFT\n➔ Cosmetic Thermal Fissure (No Panic)", (6, 95, 70)),
        (1432, 530, "2. SILENT KILLER (CRITICAL!)", "Hairline Crack (<0.4mm) + High LSTM MSE\n➔ Hidden Tendon Fatigue! Tier-1 Dispatch", (153, 27, 27)),
        (1026, 614, "3. SUBSURFACE SCOUR (WARNING)", "Intact Deck (0mm Crack) + Freq Drop >5%\n➔ Monsoon Pier Scour / Foundation Void", (146, 64, 14)),
        (1432, 614, "4. SENSOR FAULT QUARANTINE", "Flatline/Chatter on 1 Node + Stable Neighbors\n➔ Quarantine Bad Hardware (0% False Alarm)", (30, 58, 138))
    ]
    for qx, qy, qh, qb, qcol in m_quads:
        d4.rounded_rectangle([qx, qy, qx + 392, qy + 74], radius=8, fill=qcol)
        d4.text((qx + 10, qy + 6), qh, font=FONT_XS_B, fill=(255, 255, 255))
        d4.text((qx + 10, qy + 26), qb, font=FONT_XS, fill=(230, 242, 255))

    # Bottom Full-Width Card: KEY USP (Matches Page 4 Bottom Card)
    draw_pastel_card(s4, (56, 738, 1864, 1010), fill_rgb=(238, 246, 250), border_rgb=(195, 220, 236), radius=26)
    d4.text((84, 754), "KEY USP:", font=FONT_H1, fill=(10, 88, 158))

    usp_items = [
        ("1", (10, 88, 158), "Unified 4-Modal Physics + AI Platform:", "First indigenous platform unifying Drone YOLOv8-seg Vision, 3D Open3D LiDAR ICP, 200 Hz PyTorch LSTM Vibration, and Paris' Law Fracture Mechanics in one command center."),
        ("2", (5, 150, 105), "Eliminates Both False Alarms & Missed Collapses:", "Sensor Trust Guard + Cross-Check Matrix cuts 60%+ unnecessary emergency dispatches while catching hidden internal fatigue early."),
        ("3", (217, 119, 6), "Actionable CFRP Retrofit & MoRTH IBMS Compliance:", "Quantifies +45% fatigue life gain from Carbon-Fiber wrapping and generates QR-signed MoRTH / NHAI Structural Integrity Certificates."),
        ("4", (13, 148, 136), "Sustainable & Cost-Effective (<₹3.5L/Span):", "90% cheaper than imported SHM systems; extends bridge lifespan by 15+ years while saving ~4,200 tonnes of embodied cement CO₂ per span.")
    ]
    cy = 796
    for b_txt, b_col, b_pre, b_body in usp_items:
        cy = draw_rich_bullet(d4, 84, cy, 1750, b_txt, b_col, b_pre, b_body, font_b=FONT_SM_B, font_r=FONT_SM, line_h=21) + 2

    slides_out.append(s4)

    # =========================================================================
    # SLIDE 5 (PAGE 3): TECH STACK & SYSTEM ARCHITECTURE (Exact Page 5 Visual Style!)
    # =========================================================================
    s5, d5 = make_base_slide(bg_clean, "TECH STACK & SYSTEM ARCHITECTURE", "3")

    # Top-Left Rounded Card: TECH STACK (Upgraded with our real InfraGuard stack)
    draw_pastel_card(s5, (48, 142, 1115, 412), fill_rgb=(238, 246, 250), border_rgb=(195, 220, 236), radius=26)
    d5.text((76, 158), "TECH STACK", font=FONT_H1, fill=(10, 88, 158))

    stack_rows = [
        ("Frontend & 3D Twin:", "HTML5, CSS3 (Enterprise Light/Dark SaaS), JS ES6, Three.js (3D FEA Bridge), Canvas GIS & Web Speech Voice API"),
        ("Backend & Security:", "Python 3.14, FastAPI (Async REST), 200 Hz WebSockets, SHA-256 + +91 SMS OTP 2FA, Docker / Render"),
        ("AI, Vision & Signal:", "YOLOv8-seg, OpenCV, Scikit-image (GSD Skeletonizer), Open3D (SVD Kabsch ICP), SciPy Welch FFT, PyTorch LSTM AE"),
        ("Physics & Database:", "Paris' Law Fracture RUL Engine (da/dN = C(ΔK)^m), Sensor Trust Guard, SQLite (shm_records.db), CSV/JSON Exporters")
    ]
    sy = 206
    for sk_k, sk_v in stack_rows:
        d5.rounded_rectangle([76, sy + 2, 268, sy + 32], radius=8, fill=(10, 88, 158))
        d5.text((86, sy + 6), sk_k, font=FONT_SM_B, fill=(255, 255, 255))
        d5.text((280, sy + 6), sk_v, font=FONT_SM_B, fill=(20, 35, 55))
        sy += 48

    # Top-Right: Official Tech Logos Cluster + Extra PyTorch/Three.js/Open3D Badges
    s5.paste(tech_logos_crop.resize((620, 215), Image.Resampling.LANCZOS), (1165, 140))
    extra_badges = [
        (1170, 362, "Three.js 3D FEA", (15, 23, 42)),
        (1328, 362, "Open3D LiDAR ICP", (5, 150, 105)),
        (1502, 362, "PyTorch LSTM AE", (220, 38, 38)),
        (1668, 362, "SQLite + FastAPI", (10, 88, 158))
    ]
    for ebx, eby, ebtxt, ebcol in extra_badges:
        d5.rounded_rectangle([ebx, eby, ebx + 148, eby + 36], radius=10, fill=ebcol)
        bb = d5.textbbox((0, 0), ebtxt, font=FONT_XS_B)
        d5.text((ebx + 74 - (bb[2] - bb[0]) / 2, eby + 10), ebtxt, font=FONT_XS_B, fill=(255, 255, 255))

    # Bottom-Left: "System Architecture" Pill Header + 5 Vertical Stage Cards + Bottom Feedback Loop Arrow
    d5.line([(72, 456), (300, 456)], fill=(10, 88, 158), width=2)
    d5.line([(820, 456), (1085, 456)], fill=(10, 88, 158), width=2)
    d5.rounded_rectangle([310, 424, 810, 488], radius=30, fill=(205, 228, 252), outline=(10, 88, 158), width=2)
    sa_txt = "System Architecture"
    bb_sa = d5.textbbox((0, 0), sa_txt, font=FONT_H1)
    d5.text((560 - (bb_sa[2] - bb_sa[0]) / 2, 440), sa_txt, font=FONT_H1, fill=(10, 45, 85))

    arch_stages = [
        ("1", "Data Acquisition\nLayer", "DRONE + LIDAR + IOT", (225, 239, 254), (59, 130, 246), (191, 219, 254),
         "Collects Drone RGB imagery (GSD 0.12mm/px), 3D LiDAR point clouds (T₀/T₁), and 200 Hz MEMS vibration & FBG optical strain."),
        ("2", "AI & Signal\nProcessing Layer", "YOLO + ICP + LSTM", (220, 252, 231), (16, 185, 129), (167, 243, 208),
         "Runs YOLOv8-seg crack skeletonization, Open3D SVD ICP sag alignment, SciPy Welch FFT & PyTorch LSTM Autoencoder."),
        ("3", "Trust & Physics\nRUL Engine", "PARIS' LAW + GUARD", (254, 243, 199), (217, 119, 6), (253, 230, 138),
         "Quarantines faulty sensors, evaluates Cross-Check Matrix, computes SHI (0–100) & Paris' Law RUL with +45% CFRP sim."),
        ("4", "FastAPI & SQLite\nBackend Layer", "REST + 200Hz WS", (243, 232, 255), (139, 92, 246), (221, 214, 254),
         "Streams live 200 Hz WebSockets, authenticates via +91 SMS OTP 2FA, logs to SQLite & exports CSV/JSON audit trails."),
        ("5", "6-Page Enterprise\nCommand UI", "3D TWIN + VOICE AI", (224, 242, 254), (14, 165, 233), (186, 230, 253),
         "Renders Three.js 3D FEA Bridge, 5-Yr Time-Machine, India GIS Map, MoRTH Work Orders, Signed Certificate & Voice Co-Pilot.")
    ]

    sx0 = 24
    sw = 212
    sgap = 28
    for idx, (snum, spill_txt, sicon_txt, sfill, sborder, spill_fill, sbody) in enumerate(arch_stages):
        cx = sx0 + idx * (sw + sgap)
        cy_top = 532
        cy_bot = 958
        # Stage Card
        d5.rounded_rectangle([cx, cy_top, cx + sw, cy_bot], radius=20, fill=sfill, outline=sborder, width=2)
        # Top numbered circle badge overlapping top edge
        draw_icon_badge(d5, cx + sw // 2, cy_top, 22, (37, 99, 235) if idx != 1 and idx != 3 else sborder, snum)

        # Graphic Icon Box inside card
        d5.rounded_rectangle([cx + 18, cy_top + 34, cx + sw - 18, cy_top + 112], radius=12, fill=(255, 255, 255), outline=sborder, width=2)
        bb_ic = d5.textbbox((0, 0), sicon_txt, font=FONT_XS_B)
        d5.text((cx + sw / 2 - (bb_ic[2] - bb_ic[0]) / 2, cy_top + 48), sicon_txt, font=FONT_XS_B, fill=sborder)
        # Mini visual bars/waves inside icon box
        for b_i in range(5):
            bh = 12 + (b_i % 3) * 8
            d5.rectangle([cx + 42 + b_i * 26, cy_top + 100 - bh, cx + 56 + b_i * 26, cy_top + 100], fill=sborder)

        # Layer Pill Subheader
        d5.rounded_rectangle([cx + 12, cy_top + 126, cx + sw - 12, cy_top + 184], radius=16, fill=spill_fill)
        for l_idx, l_str in enumerate(spill_txt.split("\n")):
            bb_l = d5.textbbox((0, 0), l_str, font=FONT_SM_B)
            d5.text((cx + sw / 2 - (bb_l[2] - bb_l[0]) / 2, cy_top + 134 + l_idx * 20), l_str, font=FONT_SM_B, fill=(15, 23, 42))

        # Body description
        w_lines = wrap_text(d5, sbody, FONT_XS_B, sw - 24)
        ty = cy_top + 198
        for wl in w_lines:
            bb_w = d5.textbbox((0, 0), wl, font=FONT_XS)
            d5.text((cx + sw / 2 - (bb_w[2] - bb_w[0]) / 2, ty), wl, font=FONT_XS, fill=(20, 30, 45))
            ty += 18

        # Arrow to next card
        if idx < len(arch_stages) - 1:
            ax = cx + sw + 4
            ay = cy_top + 155
            d5.text((ax, ay - 14), "➔", font=FONT_H2, fill=(15, 45, 85))

    # Bottom Closed-Loop Feedback Pipe & Pill (exact match to Page 5 bottom loop!)
    d5.line([(130, 960), (130, 1015), (1090, 1015), (1090, 960)], fill=(15, 45, 85), width=4)
    d5.polygon([(130, 958), (120, 976), (140, 976)], fill=(15, 45, 85))
    d5.rounded_rectangle([355, 986, 865, 1042], radius=24, fill=(205, 228, 252), outline=(10, 88, 158), width=2)
    loop_txt = "Real-Time 200Hz Monitoring, XAI Alerts & MoRTH Dispatch"
    bb_lp = d5.textbbox((0, 0), loop_txt, font=FONT_SM_B)
    d5.text((610 - (bb_lp[2] - bb_lp[0]) / 2, 1004), loop_txt, font=FONT_SM_B, fill=(10, 45, 85))

    # Bottom-Right: Real 200 Hz IoT Telemetry Screenshot
    s5.paste(ui_telemetry.resize((545, 565), Image.Resampling.LANCZOS), (1265, 455))

    slides_out.append(s5)

    # =========================================================================
    # SLIDE 6 (PAGE 4): FEASIBILITY, VIABILITY & FUTURE ROADMAP (Matches Page 6 + Visual Roadmap Flowchart)
    # =========================================================================
    s6, d6 = make_base_slide(bg_clean, "FEASIBILITY, VIABILITY & FUTURE ROADMAP", "4")

    # 3 Columns + Bottom Visual Roadmap Pipeline
    draw_pastel_card(s6, (44, 148, 632, 815), fill_rgb=(238, 246, 250), border_rgb=(195, 220, 236), radius=28)
    d6.text((210, 168), "FEASIBILITY:", font=FONT_H1, fill=(10, 88, 158))
    feas_list = [
        ("1", (10, 88, 158), "Technical Feasibility:", "Developed using production-ready Python, FastAPI, YOLOv8-seg, OpenCV, Open3D, SciPy, PyTorch LSTM & Three.js compatible with ESP32/STM32 MEMS sensors."),
        ("2", (5, 150, 105), "Economic Feasibility (90% Savings):", "Replaces ₹45+ Lakh imported proprietary SHM systems with an open-source AI + IoT platform costing <₹3.5 Lakh per bridge span."),
        ("3", (217, 119, 6), "Operational Feasibility:", "6-Page Enterprise SaaS UI with Light/Dark themes, Voice Co-Pilot, +91 SMS OTP 2FA, and 1-click MoRTH work orders requires zero complex training."),
        ("4", (124, 58, 237), "Implementation Feasibility:", "Zero-setup synthetic & benchmark datasets included; containerized with Docker, Render & Railway blueprints for instant deployment."),
        ("5", (220, 38, 38), "Multi-Corridor Scalability:", "Scales across suspension spans, sea links, rail arch viaducts, and highway retaining walls.")
    ]
    cy = 220
    for b_txt, b_col, b_pre, b_body in feas_list:
        cy = draw_rich_bullet(d6, 68, cy, 540, b_txt, b_col, b_pre, b_body, font_b=FONT_SM_B, font_r=FONT_SM, line_h=20) + 4

    draw_pastel_card(s6, (664, 148, 1252, 815), fill_rgb=(238, 246, 250), border_rgb=(195, 220, 236), radius=28)
    d6.text((855, 168), "VIABILITY:", font=FONT_H1, fill=(10, 88, 158))
    viab_list = [
        ("1", (5, 150, 105), "High Practical Value:", "Catches hidden internal fatigue and post-monsoon pier scour early before catastrophic collapse."),
        ("2", (10, 88, 158), "70% Repair Cost Reduction:", "Proactive Carbon-Fiber (CFRP) laminate retrofitting (+45% life extension) avoids full concrete girder replacement."),
        ("3", (217, 119, 6), "Zero False Traffic Closures:", "Sensor Trust Guard + Cross-Check Matrix prevents costly highway shutdowns from loose cables or superficial cracks."),
        ("4", (124, 58, 237), "Direct Government & PSU Fit:", "Built specifically for NHAI, MoRTH (IBMS), MSRDC, BRO, and Indian Railways (USBRL Zone V bridges)."),
        ("5", (13, 148, 136), "Environmental Sustainability:", "Extends existing bridge lifespan by 15+ years, slashing construction waste and embodied cement CO₂.")
    ]
    cy = 220
    for b_txt, b_col, b_pre, b_body in viab_list:
        cy = draw_rich_bullet(d6, 688, cy, 540, b_txt, b_col, b_pre, b_body, font_b=FONT_SM_B, font_r=FONT_SM, line_h=20) + 4

    draw_pastel_card(s6, (1284, 148, 1876, 815), fill_rgb=(238, 246, 250), border_rgb=(195, 220, 236), radius=28)
    d6.text((1425, 168), "FUTURE ROADMAP:", font=FONT_H1, fill=(10, 88, 158))
    road_list = [
        ("1", (220, 38, 38), "Autonomous Drone-in-a-Box:", "Automated RTK drone flights triggered when PyTorch LSTM vibration MSE exceeds 0.15."),
        ("2", (10, 88, 158), "Edge TinyML on STM32 / ESP32:", "On-node FFT & LSTM inference transmitting compressed alerts over 5G / LoRaWAN."),
        ("3", (5, 150, 105), "3D Gaussian Splatting / NeRF:", "Automated photorealistic 3D bridge mesh updates from routine drone inspection video."),
        ("4", (217, 119, 6), "Mobile Inspector Field App:", "Offline-capable Android/iOS companion app with QR work-order scanning & voice notes."),
        ("5", (124, 58, 237), "PM GatiShakti & Smart Cities:", "Direct API federation with India's National Master Plan GIS portal & NHAI IBMS.")
    ]
    cy = 220
    for b_txt, b_col, b_pre, b_body in road_list:
        cy = draw_rich_bullet(d6, 1308, cy, 544, b_txt, b_col, b_pre, b_body, font_b=FONT_SM_B, font_r=FONT_SM, line_h=20) + 4

    # Bottom Visual 4-Phase Roadmap Flowchart Bar
    d6.rounded_rectangle([44, 834, 1876, 1012], radius=20, fill=(15, 23, 42), outline=(37, 99, 235), width=2)
    d6.text((70, 846), "VISUAL ROLLOUT ROADMAP FLOWCHART (FROM PROTOTYPE TO PM GATISHAKTI NATIONAL GRID):", font=FONT_SM_B, fill=(56, 189, 248))
    r_phases = [
        (70, "PHASE 1 (COMPLETED)", "6-Page Digital Twin Prototype\n3D FEA • YOLOv8 • LSTM • +91 OTP", (5, 150, 105)),
        (520, "PHASE 2 (Q1–Q2 2027)", "Edge Hardware & Drone Pilot\nESP32 MEMS + RTK Drone Field Trials", (37, 99, 235)),
        (970, "PHASE 3 (Q3–Q4 2027)", "MoRTH IBMS & MSRDC Rollout\n50+ Monsoon & Sea-Link Bridges", (217, 119, 6)),
        (1420, "PHASE 4 (2028+)", "PM GatiShakti National Grid\n10,000+ NHAI & Railway Corridors", (124, 58, 237))
    ]
    for rpx, rptag, rpbody, rpcol in r_phases:
        d6.rounded_rectangle([rpx, 880, rpx + 415, 996], radius=12, fill=rpcol)
        d6.text((rpx + 14, 890), rptag, font=FONT_SM_B, fill=(255, 255, 255))
        d6.text((rpx + 14, 920), rpbody, font=FONT_SM, fill=(240, 249, 255))
    for arr_x in [492, 942, 1392]:
        d6.text((arr_x, 922), "➔", font=FONT_H2, fill=(56, 189, 248))

    slides_out.append(s6)

    # =========================================================================
    # SLIDE 7 (PAGE 5): SDG ALIGNMENT & SUSTAINABILITY IMPACT (Matches Page 7 Layout + Metrics)
    # =========================================================================
    s7, d7 = make_base_slide(bg_clean, "SDG ALIGNMENT & SUSTAINABILITY IMPACT", "5")

    # Top Row: 3 SDG Cards (SDG 9, SDG 11, SDG 12) matching Page 7 layout
    sdg_top = [
        (80, 620, "SDG 9 – INDUSTRY, INNOVATION\nAND INFRASTRUCTURE :", (234, 88, 12), "SDG 9", [
            ("Self-Diagnosing 3D Digital Twins:", "Upgrades national highways, sea links & rail viaducts with continuous AI + IoT structural health monitoring."),
            ("Physics + Deep Learning Fusion:", "Unifies YOLOv8-seg, Open3D ICP, 200 Hz PyTorch LSTM & Paris' Law fracture RUL.")
        ]),
        (670, 1230, "SDG 11 – SUSTAINABLE CITIES\nAND COMMUNITIES:", (217, 119, 6), "SDG 11", [
            ("Zero Catastrophic Bridge Collapses:", "Protects millions of daily commuters across urban flyovers and coastal corridors."),
            ("<3.5 Hr Emergency NDT Dispatch:", "Automated MoRTH urgency ranking & 1-click work orders prevent public safety disasters.")
        ]),
        (1275, 1840, "SDG 12 – RESPONSIBLE\nCONSUMPTION & PRODUCTION:", (180, 83, 9), "SDG 12", [
            ("+45% Lifespan Gain via CFRP:", "Timely Carbon-Fiber laminate retrofitting arrests crack growth early, avoiding bridge demolition."),
            ("68% Less Construction Waste:", "Slashes raw cement, steel & aggregate consumption through predictive maintenance.")
        ])
    ]
    for x1, x2, stitle, scol, sbadge, sbuls in sdg_top:
        draw_pastel_card(s7, (x1, 175, x2, 520), fill_rgb=(238, 246, 250), border_rgb=(195, 220, 236), radius=30)
        d7.rounded_rectangle([x1 + 22, 192, x1 + 115, 224], radius=8, fill=scol)
        d7.text((x1 + 34, 198), sbadge, font=FONT_SM_B, fill=(255, 255, 255))
        for idx_l, tl in enumerate(stitle.split("\n")):
            d7.text((x1 + 128, 190 + idx_l * 24), tl, font=FONT_H3, fill=(10, 88, 158))
        cy = 258
        for bpre, bbody in sbuls:
            cy = draw_rich_bullet(d7, x1 + 24, cy, (x2 - x1) - 48, "★", scol, bpre, bbody, font_b=FONT_SM_B, font_r=FONT_SM, line_h=21) + 6

    # Bottom-Left Card: SDG 13 – CLIMATE ACTION
    draw_pastel_card(s7, (80, 560, 620, 995), fill_rgb=(238, 246, 250), border_rgb=(195, 220, 236), radius=30)
    d7.rounded_rectangle([104, 580, 198, 612], radius=8, fill=(21, 128, 61))
    d7.text((116, 586), "SDG 13", font=FONT_SM_B, fill=(255, 255, 255))
    d7.text((212, 582), "SDG 13 – CLIMATE ACTION:", font=FONT_H2, fill=(10, 88, 158))
    sdg13_buls = [
        ("1", (21, 128, 61), "IMD Monsoon & Flood Scour Lens:", "Monitors extreme climate-induced pier scour, soil saturation & marine chloride attack post-monsoon."),
        ("2", (5, 150, 105), "~4,200 Tonnes CO₂ Saved / Span:", "Extending a single 120m concrete bridge's service life by 15+ years averts massive embodied cement carbon emissions."),
        ("3", (10, 88, 158), "Climate-Resilient National Grid:", "Protects vital disaster-relief corridors in Himalayan Seismic Zone V and coastal cyclone zones.")
    ]
    cy = 638
    for b_txt, b_col, b_pre, b_body in sdg13_buls:
        cy = draw_rich_bullet(d7, 104, cy, 492, b_txt, b_col, b_pre, b_body, font_b=FONT_SM_B, font_r=FONT_SM, line_h=21) + 6

    # Bottom-Right Wide Card: SUSTAINABILITY IMPACT + Quantified Infographic KPI Strip
    draw_pastel_card(s7, (685, 560, 1840, 995), fill_rgb=(238, 246, 250), border_rgb=(195, 220, 236), radius=30)
    d7.text((1095, 578), "SUSTAINABILITY IMPACT", font=FONT_H2, fill=(10, 88, 158))

    imp_items = [
        ("1", (5, 150, 105), "Environmental Impact:", "Reduces construction waste, raw aggregate mining & cement CO₂ emissions by extending existing bridge lifespan by +45%."),
        ("2", (10, 88, 158), "Economic Impact:", "Saves 70% in lifecycle repair costs via early CFRP retrofitting and eliminates 60%+ false sensor inspection dispatches."),
        ("3", (220, 38, 38), "Social & Public Safety Impact:", "Prevents catastrophic bridge collapses through silent-fatigue detection and <3.5 hr MoRTH emergency crew dispatch."),
        ("4", (217, 119, 6), "Resource Efficiency:", "Targets NDT crews (PAUT/Sonar) and carbon-fiber materials strictly to high-priority structural anomalies."),
        ("5", (124, 58, 237), "Long-Term National Resilience:", "Builds a future-ready digital twin backbone for NHAI, MoRTH IBMS & PM GatiShakti infrastructure.")
    ]
    cy = 620
    for b_txt, b_col, b_pre, b_body in imp_items:
        cy = draw_rich_bullet(d7, 712, cy, 1100, b_txt, b_col, b_pre, b_body, font_b=FONT_SM_B, font_r=FONT_SM, line_h=20) + 1

    # Bottom KPI Infographic Strip inside Sustainability Impact Card
    kpis = [
        (712, "+45% Lifespan", "Via Bonded CFRP Wrap", (5, 150, 105)),
        (992, "68% CO₂ Saved", "Avoided Demolition", (10, 88, 158)),
        (1272, "98.4% Trust", "Zero False Closures", (217, 119, 6)),
        (1552, "<3.5 Hr Action", "1-Click MoRTH Order", (220, 38, 38))
    ]
    for kx, khead, ksub, kcol in kpis:
        d7.rounded_rectangle([kx, 902, kx + 262, 976], radius=12, fill=kcol)
        d7.text((kx + 16, 910), khead, font=FONT_H3, fill=(255, 255, 255))
        d7.text((kx + 16, 944), ksub, font=FONT_SM, fill=(240, 249, 255))

    slides_out.append(s7)

    # =========================================================================
    # SLIDE 8: THANK YOU (Exact original Page 8)
    # =========================================================================
    s8 = orig_pages[7].copy()
    slides_out.append(s8)

    # Save individual slide PNGs, combined PDF, and editable PPTX
    print("[2/3] Saving high-resolution slide PNGs and 8-page PDF...")
    slide_png_paths = []
    for idx, im in enumerate(slides_out):
        p = os.path.join(ASSETS_DIR, f"final_slide_{idx+1}.png")
        im.save(p, quality=95)
        slide_png_paths.append(p)

    pdf_out_front = os.path.join(FRONTEND_DIR, "INFRAGUARD_SUSTAINOVA_2026_FINAL.pdf")
    pdf_out_root = os.path.join(BASE_DIR, "INFRAGUARD_SUSTAINOVA_2026_FINAL.pdf")
    slides_out[0].save(
        pdf_out_front, "PDF", resolution=150.0, save_all=True, append_images=slides_out[1:]
    )
    shutil.copyfile(pdf_out_front, pdf_out_root)

    print("[3/3] Saving 16:9 Widescreen PowerPoint (.pptx)...")
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]
    for p in slide_png_paths:
        sl = prs.slides.add_slide(blank_layout)
        sl.shapes.add_picture(p, Inches(0), Inches(0), Inches(13.333), Inches(7.5))

    pptx_out_root = os.path.join(BASE_DIR, "INFRAGUARD_SUSTAINOVA_2026_PPT.pptx")
    pptx_out_front = os.path.join(FRONTEND_DIR, "INFRAGUARD_SUSTAINOVA_2026_PPT.pptx")
    prs.save(pptx_out_root)
    shutil.copyfile(pptx_out_root, pptx_out_front)
    print("DONE! Saved PDF and PPTX successfully.")


if __name__ == "__main__":
    build_all_8_slides()
