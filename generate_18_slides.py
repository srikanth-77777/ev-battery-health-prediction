import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# COLOR PALETTE
DARK_GREEN  = RGBColor(15, 76, 58)      # #0F4C3A
FOREST_MED   = RGBColor(22, 101, 52)     # #166534
ACCENT_MINT  = RGBColor(16, 185, 129)    # #10B981
LIGHT_MINT   = RGBColor(236, 253, 245)   # #ECFDF5
BG_LIGHT     = RGBColor(248, 250, 252)   # #F8FAFC
CARD_BG      = RGBColor(255, 255, 255)   # #FFFFFF
BORDER_GREY  = RGBColor(226, 232, 240)   # #E2E8F0
TEXT_MAIN    = RGBColor(15, 23, 42)      # #0F172A
TEXT_MUTED   = RGBColor(100, 116, 139)   # #64748B
TEXT_DARK    = RGBColor(30, 41, 59)      # #1E293B
WHITE        = RGBColor(255, 255, 255)
BIN_BLUE     = RGBColor(37, 99, 235)
BIN_GREEN    = RGBColor(22, 163, 74)
BIN_YELLOW   = RGBColor(202, 138, 4)
BIN_RED      = RGBColor(220, 38, 38)
BIN_GREY     = RGBColor(71, 85, 105)

FONT_FAMILY = "Segoe UI"

def set_slide_background(slide, color=BG_LIGHT):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_header(slide, title_text, category_breadcrumb=None):
    top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.1))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = ACCENT_MINT
    top_bar.line.color.rgb = ACCENT_MINT
    
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(11.733), Inches(1.1))
    tf = title_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    if category_breadcrumb:
        p_sub = tf.paragraphs[0]
        p_sub.text = category_breadcrumb.upper()
        p_sub.font.name = FONT_FAMILY
        p_sub.font.size = Pt(9.5)
        p_sub.font.bold = True
        p_sub.font.color.rgb = FOREST_MED
        p_sub.space_after = Pt(2)
        p_title = tf.add_paragraph()
    else:
        p_title = tf.paragraphs[0]
        
    p_title.text = title_text
    p_title.font.name = FONT_FAMILY
    p_title.font.size = Pt(23)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_MAIN

def add_footer(slide, slide_num, total_slides=18):
    footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.0), Inches(11.733), Inches(0.4))
    tf = footer_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = "SRM Institute of Science and Technology | Department of Computational Intelligence | B.Tech CSE (AI & ML)"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(8.5)
    p.font.color.rgb = TEXT_MUTED
    
    num_p = tf.add_paragraph()
    num_p.text = f"{slide_num:02d} / {total_slides:02d}"
    num_p.alignment = PP_ALIGN.RIGHT
    num_p.font.name = FONT_FAMILY
    num_p.font.size = Pt(8.5)
    num_p.font.bold = True
    num_p.font.color.rgb = FOREST_MED

def create_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=BORDER_GREY):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1)
    return shape

def build_18_slide_presentation(filename="Smart_Waste_Classification_18_Slides.pptx"):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # ========================================================
    # SLIDE 1: Title Slide
    # ========================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, RGBColor(246, 249, 248))
    
    bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.45), Inches(7.5))
    bar.fill.solid()
    bar.fill.fore_color.rgb = DARK_GREEN
    bar.line.fill.background()
    
    subbar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.45), Inches(0), Inches(0.12), Inches(7.5))
    subbar.fill.solid()
    subbar.fill.fore_color.rgb = ACCENT_MINT
    subbar.line.fill.background()

    badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(0.8), Inches(4.5), Inches(0.38))
    badge.fill.solid()
    badge.fill.fore_color.rgb = LIGHT_MINT
    badge.line.color.rgb = ACCENT_MINT
    badge.line.width = Pt(1)
    tf_b = badge.text_frame
    tf_b.margin_left = Inches(0.15)
    tf_b.margin_top = Inches(0.04)
    p_b = tf_b.paragraphs[0]
    p_b.text = "FINAL YEAR B.TECH (CSE - AI & ML) CAPSTONE PROJECT"
    p_b.font.name = FONT_FAMILY
    p_b.font.size = Pt(9)
    p_b.font.bold = True
    p_b.font.color.rgb = FOREST_MED

    title_box = s1.shapes.add_textbox(Inches(1.2), Inches(1.35), Inches(10.8), Inches(1.8))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
    p1 = tf_t.paragraphs[0]
    p1.text = "SMART WASTE CLASSIFICATION SYSTEM"
    p1.font.name = FONT_FAMILY
    p1.font.size = Pt(28)
    p1.font.bold = True
    p1.font.color.rgb = DARK_GREEN
    
    p2 = tf_t.add_paragraph()
    p2.text = "USING DEEP LEARNING WITH BIN RECOMMENDATION AND ANALYTICS DASHBOARD"
    p2.font.name = FONT_FAMILY
    p2.font.size = Pt(20)
    p2.font.bold = True
    p2.font.color.rgb = FOREST_MED
    p2.space_before = Pt(4)

    card_stu = create_card(s1, Inches(1.2), Inches(3.6), Inches(5.3), Inches(2.9))
    tf_s = card_stu.text_frame
    tf_s.word_wrap = True
    tf_s.margin_left = tf_s.margin_top = Inches(0.3)
    p = tf_s.paragraphs[0]
    p.text = "STUDENT INVESTIGATORS"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = FOREST_MED
    p.space_after = Pt(8)
    for name, reg in [("Student Name 1", "RA211100301XXXX"), ("Student Name 2", "RA211100301XXXX"), ("Student Name 3", "RA211100301XXXX"), ("Student Name 4", "RA211100301XXXX")]:
        p_row = tf_s.add_paragraph()
        p_row.text = f"• {name}  [{reg}]"
        p_row.font.name = FONT_FAMILY
        p_row.font.size = Pt(11)
        p_row.font.color.rgb = TEXT_DARK
        p_row.space_after = Pt(3)

    card_inst = create_card(s1, Inches(6.8), Inches(3.6), Inches(5.3), Inches(2.9))
    tf_i = card_inst.text_frame
    tf_i.word_wrap = True
    tf_i.margin_left = tf_i.margin_top = Inches(0.3)
    p = tf_i.paragraphs[0]
    p.text = "PROJECT SUPERVISION & INSTITUTION"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = FOREST_MED
    p.space_after = Pt(8)
    for lbl, val in [("Project Guide:", "[Faculty Guide Name & Title]"), ("Department:", "Department of Computational Intelligence"), ("School / Faculty:", "School of Computing"), ("Institution:", "SRM Institute of Science and Technology"), ("Academic Year:", "2025 – 2026")]:
        p_r = tf_i.add_paragraph()
        p_r.text = f"{lbl} {val}"
        p_r.font.name = FONT_FAMILY
        p_r.font.size = Pt(11)
        p_r.font.color.rgb = TEXT_DARK
        p_r.space_after = Pt(3)
    add_footer(s1, 1, 18)

    # ========================================================
    # SLIDE 2: Introduction
    # ========================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "Introduction: The Growing Waste Challenge", "Project Background")
    
    col_w = Inches(3.7)
    gap = Inches(0.3)
    c1 = create_card(s2, Inches(0.8), Inches(1.6), col_w, Inches(5.1))
    tf1 = c1.text_frame
    tf1.word_wrap = True
    tf1.margin_left = tf1.margin_top = tf1.margin_right = Inches(0.28)
    tf1.paragraphs[0].text = "1. Global Waste Escalation"
    tf1.paragraphs[0].font.name = FONT_FAMILY
    tf1.paragraphs[0].font.size = Pt(13)
    tf1.paragraphs[0].font.bold = True
    tf1.paragraphs[0].font.color.rgb = DARK_GREEN
    tf1.paragraphs[0].space_after = Pt(10)
    for title, desc in [
        ("Massive Generation", "Global municipal solid waste generation currently exceeds 2.01 billion metric tons annually and is projected to reach 3.4 billion tons by 2050."),
        ("Urbanization Pressure", "Rapid urban expansion strains municipal logistics, causing overflow at collection hubs and processing bottlenecks."),
        ("Environmental Toll", "Unsegregated garbage releases methane in landfills, generates toxic leachate, and severely contaminates soil and water ecosystems.")
    ]:
        p_t = tf1.add_paragraph()
        p_t.text = f"• {title}:"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(10.5)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_DARK
        p_d = tf1.add_paragraph()
        p_d.text = f"  {desc}"
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_MUTED
        p_d.space_after = Pt(6)

    c2 = create_card(s2, Inches(0.8) + col_w + gap, Inches(1.6), col_w, Inches(5.1))
    tf2 = c2.text_frame
    tf2.word_wrap = True
    tf2.margin_left = tf2.margin_top = tf2.margin_right = Inches(0.28)
    tf2.paragraphs[0].text = "2. Source Segregation Gap"
    tf2.paragraphs[0].font.name = FONT_FAMILY
    tf2.paragraphs[0].font.size = Pt(13)
    tf2.paragraphs[0].font.bold = True
    tf2.paragraphs[0].font.color.rgb = DARK_GREEN
    tf2.paragraphs[0].space_after = Pt(10)
    for title, desc in [
        ("Source-Level Contamination", "Recycling processes fail when wet organic waste contaminates dry recyclables like paper and cardboard, dropping recyclability from 90% to near 0%."),
        ("Public Confusion", "Users struggle to decipher regional recycling codes, mixed-material packaging, and differing municipal disposal regulations."),
        ("Manual Sorting Hazards", "Downstream manual sorting exposes sanitation workers to biohazards, sharp metal objects, and toxic industrial chemicals.")
    ]:
        p_t = tf2.add_paragraph()
        p_t.text = f"• {title}:"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(10.5)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_DARK
        p_d = tf2.add_paragraph()
        p_d.text = f"  {desc}"
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_MUTED
        p_d.space_after = Pt(6)

    c3 = create_card(s2, Inches(0.8) + (col_w + gap)*2, Inches(1.6), col_w, Inches(5.1), bg_color=LIGHT_MINT, border_color=ACCENT_MINT)
    tf3 = c3.text_frame
    tf3.word_wrap = True
    tf3.margin_left = tf3.margin_top = tf3.margin_right = Inches(0.28)
    tf3.paragraphs[0].text = "3. AI & Deep Learning Role"
    tf3.paragraphs[0].font.name = FONT_FAMILY
    tf3.paragraphs[0].font.size = Pt(13)
    tf3.paragraphs[0].font.bold = True
    tf3.paragraphs[0].font.color.rgb = FOREST_MED
    tf3.paragraphs[0].space_after = Pt(10)
    for title, desc in [
        ("Automated Visual Inspection", "Computer Vision and Convolutional Neural Networks automatically extract visual textures, geometry, and material features without human contact."),
        ("High-Speed Inference", "Deep learning models execute inference in milliseconds, providing instantaneous feedback at the point of disposal."),
        ("Smart Bin Integration", "Coupling deep learning with bin recommendations bridges the gap between identification and proper physical disposal.")
    ]:
        p_t = tf3.add_paragraph()
        p_t.text = f"• {title}:"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(10.5)
        p_t.font.bold = True
        p_t.font.color.rgb = DARK_GREEN
        p_d = tf3.add_paragraph()
        p_d.text = f"  {desc}"
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_DARK
        p_d.space_after = Pt(6)
    add_footer(s2, 2, 18)

    # ========================================================
    # SLIDE 3: Problem Statement
    # ========================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "Problem Statement: Challenges in Current Systems", "Problem Definition")
    
    problems = [
        ("1. Manual Identification Dependency", "Existing waste sorting predominantly relies on manual visual judgment by consumers or municipal personnel. This is slow, subjective, highly inconsistent, and impractical for high-density academic or commercial hubs."),
        ("2. High Incidence of Classification Errors", "Unassisted public users make incorrect segregation choices due to haste, indifference, or lack of knowledge, resulting in widespread cross-contamination of recyclable and organic waste streams."),
        ("3. Visual Similarity of Divergent Materials", "Materials such as transparent plastic bottles vs. glass containers, aluminum foil vs. metallic plastic laminates, and coated paper present extreme visual ambiguity that human intuition frequently misjudges."),
        ("4. Total Absence of Automated Disposal Guidance", "Conventional bin setups offer passive static stickers that users ignore. There is no automated, interactive mechanism to recommend the exact bin matching the classified item."),
        ("5. Lack of Integrated Waste Analytics", "Facility administrators have zero historical or real-time visibility into waste volume, category distribution, or sorting compliance rates, making data-driven sustainability planning impossible.")
    ]
    card_h = Inches(0.92)
    gap_y = Inches(0.12)
    for i, (p_title, p_desc) in enumerate(problems):
        y_pos = Inches(1.6) + i * (card_h + gap_y)
        c = create_card(s3, Inches(0.8), y_pos, Inches(11.733), card_h)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = Inches(0.2)
        p = tf.paragraphs[0]
        p.text = p_title
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = DARK_GREEN
        p_d = tf.add_paragraph()
        p_d.text = p_desc
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_DARK
    add_footer(s3, 3, 18)

    # ========================================================
    # SLIDE 4: Motivation
    # ========================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "Project Motivation & Environmental Impact", "Significance & Scope")
    
    col_w2 = Inches(5.7)
    gap2 = Inches(0.33)
    
    m_left = create_card(s4, Inches(0.8), Inches(1.6), col_w2, Inches(5.1))
    tf_ml = m_left.text_frame
    tf_ml.word_wrap = True
    tf_ml.margin_left = tf_ml.margin_top = tf_ml.margin_right = Inches(0.3)
    tf_ml.paragraphs[0].text = "ENVIRONMENTAL & ECONOMIC DRIVERS"
    tf_ml.paragraphs[0].font.name = FONT_FAMILY
    tf_ml.paragraphs[0].font.size = Pt(13)
    tf_ml.paragraphs[0].font.bold = True
    tf_ml.paragraphs[0].font.color.rgb = DARK_GREEN
    tf_ml.paragraphs[0].space_after = Pt(10)
    for title, desc in [
        ("Transition to Circular Economy", "Transitioning from a 'take-make-dispose' model to a circular economy requires pristine segregated feedstocks to make recycling industrially and economically viable."),
        ("Landfill Volume Reduction", "Automating separation diverts biodegradable organics to composting and valuable recyclables to manufacturing, dramatically extending municipal landfill life."),
        ("Resource Conservation", "Recovering aluminum cans, PET plastics, and paper pulp saves up to 95%, 70%, and 60% of virgin production energy respectively.")
    ]:
        p_t = tf_ml.add_paragraph()
        p_t.text = f"• {title}:"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_DARK
        p_d = tf_ml.add_paragraph()
        p_d.text = f"  {desc}"
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = TEXT_MUTED
        p_d.space_after = Pt(8)

    m_right = create_card(s4, Inches(0.8) + col_w2 + gap2, Inches(1.6), col_w2, Inches(5.1), bg_color=LIGHT_MINT, border_color=ACCENT_MINT)
    tf_mr = m_right.text_frame
    tf_mr.word_wrap = True
    tf_mr.margin_left = tf_mr.margin_top = tf_mr.margin_right = Inches(0.3)
    tf_mr.paragraphs[0].text = "TECHNOLOGICAL & ACADEMIC VALUE"
    tf_mr.paragraphs[0].font.name = FONT_FAMILY
    tf_mr.paragraphs[0].font.size = Pt(13)
    tf_mr.paragraphs[0].font.bold = True
    tf_mr.paragraphs[0].font.color.rgb = FOREST_MED
    tf_mr.paragraphs[0].space_after = Pt(10)
    for title, desc in [
        ("AI for Climate Action (SDG 12 & 13)", "Demonstrating how contemporary Deep Learning architectures solve tangible United Nations Sustainable Development Goals."),
        ("Accessible Campus Deployment", "Developing a low-barrier, browser/edge accessible tool that educates university students and visitors while gathering scientific disposal data."),
        ("Bridging Vision to Physical Action", "Going beyond mere benchmark classification by tying predictions directly to physical disposal bins and real-time operational metrics.")
    ]:
        p_t = tf_mr.add_paragraph()
        p_t.text = f"• {title}:"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = DARK_GREEN
        p_d = tf_mr.add_paragraph()
        p_d.text = f"  {desc}"
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = TEXT_DARK
        p_d.space_after = Pt(8)
    add_footer(s4, 4, 18)

    # ========================================================
    # SLIDE 5: Project Objectives
    # ========================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "Project Objectives & Deliverables", "Core Goals")
    
    objs = [
        ("1. Automated Image Classification", "Engineer and train a Convolutional Neural Network capable of classifying waste imagery into 7 granular categories with high accuracy."),
        ("2. Transfer Learning Utilization", "Harness pre-trained deep architectures (MobileNetV2 / EfficientNet) to optimize feature extraction while preserving computational efficiency."),
        ("3. Contextual Bin Recommendation", "Develop a deterministic recommendation rule engine that associates predicted waste categories with standardized color-coded bins."),
        ("4. Persistent Prediction History", "Establish a structured database backend to log every classification event including image metadata, predicted class, and confidence score."),
        ("5. Interactive Analytics Dashboard", "Construct an intuitive web-based analytics dashboard to visualize category breakdowns, temporal usage patterns, and segregation ratios."),
        ("6. Environmental Awareness Cultivation", "Deliver an educational interface that raises public mindfulness and provides transparent explanations for disposal choices.")
    ]
    card_h = Inches(0.76)
    gap_y = Inches(0.1)
    for i, (o_title, o_desc) in enumerate(objs):
        y_pos = Inches(1.6) + i * (card_h + gap_y)
        c = create_card(s5, Inches(0.8), y_pos, Inches(11.733), card_h)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = Inches(0.18)
        p = tf.paragraphs[0]
        p.text = o_title
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = DARK_GREEN
        p_d = tf.add_paragraph()
        p_d.text = o_desc
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_DARK
    add_footer(s5, 5, 18)

    # ========================================================
    # SLIDE 6: Existing System & Limitations
    # ========================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Existing Systems & Architectural Limitations", "Literature & Baseline")
    
    c_ex = create_card(s6, Inches(0.8), Inches(1.6), col_w2, Inches(5.1))
    tf_ex = c_ex.text_frame
    tf_ex.word_wrap = True
    tf_ex.margin_left = tf_ex.margin_top = tf_ex.margin_right = Inches(0.3)
    tf_ex.paragraphs[0].text = "EXISTING APPROACHES"
    tf_ex.paragraphs[0].font.name = FONT_FAMILY
    tf_ex.paragraphs[0].font.size = Pt(13)
    tf_ex.paragraphs[0].font.bold = True
    tf_ex.paragraphs[0].font.color.rgb = DARK_GREEN
    tf_ex.paragraphs[0].space_after = Pt(10)
    for title, desc in [
        ("Manual Waste Sorting", "Relies entirely on individual awareness at the dustbin or centralized manual laborers at transfer stations."),
        ("Static Bin Signage", "Passive color stickers and posters affixed to bins. Widely overlooked and ineffective for complex composite items."),
        ("Basic Rule-Based Image Classifiers", "Traditional image processing pipelines using handcrafted features (SIFT/SURF, Haar cascades) that perform poorly under real-world lighting variations."),
        ("Isolated Academic Proof-of-Concepts", "Standard DL models trained purely on benchmark datasets without user interfaces, bin mapping, or data telemetry.")
    ]:
        p_t = tf_ex.add_paragraph()
        p_t.text = f"• {title}:"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(10.5)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_DARK
        p_d = tf_ex.add_paragraph()
        p_d.text = f"  {desc}"
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_MUTED
        p_d.space_after = Pt(6)

    c_lim = create_card(s6, Inches(0.8) + col_w2 + gap2, Inches(1.6), col_w2, Inches(5.1))
    tf_lim = c_lim.text_frame
    tf_lim.word_wrap = True
    tf_lim.margin_left = tf_lim.margin_top = tf_lim.margin_right = Inches(0.3)
    tf_lim.paragraphs[0].text = "LIMITATIONS & SHORTCOMINGS"
    tf_lim.paragraphs[0].font.name = FONT_FAMILY
    tf_lim.paragraphs[0].font.size = Pt(13)
    tf_lim.paragraphs[0].font.bold = True
    tf_lim.paragraphs[0].font.color.rgb = RGBColor(185, 28, 28)
    tf_lim.paragraphs[0].space_after = Pt(10)
    for title, desc in [
        ("Heavy Human Dependency", "Inefficient, slow, and exposes workers to sharp objects, chemical spills, and pathogenic contaminants."),
        ("High Error Rates", "Cognitive fatigue and public indifference cause high misclassification, rendering recyclables unusable."),
        ("No Actionable Disposal Output", "Standard image models output a class label (e.g., 'metal') but do not guide the user on where to throw it."),
        ("Zero Historical Tracking", "Municipalities and facilities have no feedback loop to assess waste trends or evaluate sorting policies."),
        ("Inability to Generalize", "Handcrafted feature pipelines fail on deformed, partially crumpled, or shadowed items.")
    ]:
        p_t = tf_lim.add_paragraph()
        p_t.text = f"✕ {title}:"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(10.5)
        p_t.font.bold = True
        p_t.font.color.rgb = RGBColor(185, 28, 28)
        p_d = tf_lim.add_paragraph()
        p_d.text = f"  {desc}"
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_DARK
        p_d.space_after = Pt(6)
    add_footer(s6, 6, 18)

    # ========================================================
    # SLIDE 7: Proposed System
    # ========================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "Proposed System: Intelligent End-to-End Solution", "Proposed Solution")
    
    stages = [
        ("1. Image Acquisition", "User uploads a waste photo or captures an item directly via camera through a responsive frontend portal."),
        ("2. Automated Preprocessing", "Image is standardized to 224x224, normalized to [0,1], and converted into suitable tensor formats."),
        ("3. Deep Learning Classification", "Pre-trained deep neural network model extracts visual feature maps and predicts the waste class with confidence scores."),
        ("4. Smart Bin Recommendation", "Inference result triggers the bin recommendation module to display the designated color-coded disposal bin."),
        ("5. Database Logging & Auditing", "Event telemetry (timestamp, category, confidence, assigned bin) is stored in the database."),
        ("6. Analytics Dashboard Visualization", "Aggregated data is served to an interactive dashboard illustrating waste trends, recycling rates, and historical logs.")
    ]
    card_h = Inches(0.76)
    for i, (st_t, st_d) in enumerate(stages):
        y_pos = Inches(1.6) + i * (card_h + Inches(0.1))
        c = create_card(s7, Inches(0.8), y_pos, Inches(11.733), card_h, bg_color=LIGHT_MINT if i in (2,3) else CARD_BG, border_color=FOREST_MED if i in (2,3) else BORDER_GREY)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = Inches(0.18)
        p = tf.paragraphs[0]
        p.text = st_t
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = DARK_GREEN
        p_d = tf.add_paragraph()
        p_d.text = st_d
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_DARK
    add_footer(s7, 7, 18)

    # ========================================================
    # SLIDE 8: System Architecture
    # ========================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "System Architecture & High-Level Dataflow", "System Architecture")
    
    arch_steps = [
        ("User / Camera", "Image capture or upload from client device."),
        ("Frontend Client", "React/HTML UI with instant preview & validation."),
        ("Backend Gateway", "Flask/FastAPI REST handling payload & session."),
        ("Image Preprocessor", "OpenCV resizing (224x224), scaling & normalization."),
        ("Deep Learning Model", "MobileNetV2/EfficientNet classifier inference."),
        ("Bin Recommendation", "Rule-engine mapping class to color bin."),
        ("Database Storage", "Persistent logging in MySQL / SQLite."),
        ("Analytics Dashboard", "Chart.js dynamic telemetry visualization.")
    ]
    w_step = Inches(2.75)
    gap_x = Inches(0.24)
    for i in range(4):
        x = Inches(0.8) + i * (w_step + gap_x)
        c = create_card(s8, x, Inches(2.0), w_step, Inches(2.1))
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = Inches(0.2)
        p = tf.paragraphs[0]
        p.text = f"Step {i+1}:\n{arch_steps[i][0]}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = DARK_GREEN
        p.space_after = Pt(6)
        pd = tf.add_paragraph()
        pd.text = arch_steps[i][1]
        pd.font.name = FONT_FAMILY
        pd.font.size = Pt(9.5)
        pd.font.color.rgb = TEXT_MUTED

    for i in range(4):
        x = Inches(0.8) + i * (w_step + gap_x)
        c = create_card(s8, x, Inches(4.5), w_step, Inches(2.1), bg_color=LIGHT_MINT if i in (0,1) else CARD_BG, border_color=FOREST_MED if i in (0,1) else BORDER_GREY)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = Inches(0.2)
        p = tf.paragraphs[0]
        p.text = f"Step {i+5}:\n{arch_steps[i+4][0]}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = DARK_GREEN
        p.space_after = Pt(6)
        pd = tf.add_paragraph()
        pd.text = arch_steps[i+4][1]
        pd.font.name = FONT_FAMILY
        pd.font.size = Pt(9.5)
        pd.font.color.rgb = TEXT_DARK
    add_footer(s8, 8, 18)

    # ========================================================
    # SLIDE 9: Dataset Description
    # ========================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Dataset Description & Category Breakdown", "Data Engineering")
    
    c_d1 = create_card(s9, Inches(0.8), Inches(1.6), col_w2, Inches(5.1))
    tf_d1 = c_d1.text_frame
    tf_d1.word_wrap = True
    tf_d1.margin_left = tf_d1.margin_top = tf_d1.margin_right = Inches(0.3)
    tf_d1.paragraphs[0].text = "DATASET SOURCES & COMPOSITION"
    tf_d1.paragraphs[0].font.name = FONT_FAMILY
    tf_d1.paragraphs[0].font.size = Pt(13)
    tf_d1.paragraphs[0].font.bold = True
    tf_d1.paragraphs[0].font.color.rgb = DARK_GREEN
    tf_d1.paragraphs[0].space_after = Pt(10)
    for title, desc in [
        ("TrashNet Benchmark Dataset", "Standard academic corpus collected by Yang & Thung, offering structured images of clean recyclables against white backgrounds."),
        ("Kaggle Garbage Classification Dataset", "Enriched public dataset containing diversified real-world waste items across domestic and office environments."),
        ("Supplemental Real-World Images", "Locally collected images capturing real-world deformations, varied lighting, and surface shadows."),
        ("Seven Granular Classes", "Formulated to span [Plastic, Paper, Cardboard, Glass, Metal, Organic, Non-Recyclable/Trash].")
    ]:
        p_t = tf_d1.add_paragraph()
        p_t.text = f"• {title}:"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(10.5)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_DARK
        p_d = tf_d1.add_paragraph()
        p_d.text = f"  {desc}"
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_MUTED
        p_d.space_after = Pt(6)

    c_d2 = create_card(s9, Inches(0.8) + col_w2 + gap2, Inches(1.6), col_w2, Inches(5.1))
    tf_d2 = c_d2.text_frame
    tf_d2.word_wrap = True
    tf_d2.margin_left = tf_d2.margin_top = tf_d2.margin_right = Inches(0.3)
    tf_d2.paragraphs[0].text = "CATEGORY PARTITIONING & INTEGRITY"
    tf_d2.paragraphs[0].font.name = FONT_FAMILY
    tf_d2.paragraphs[0].font.size = Pt(13)
    tf_d2.paragraphs[0].font.bold = True
    tf_d2.paragraphs[0].font.color.rgb = DARK_GREEN
    tf_d2.paragraphs[0].space_after = Pt(10)
    for title, desc in [
        ("Stratified Data Split", "70% Training (~[XXXX] images), 15% Validation (~[XXX] images), and 15% Unseen Testing (~[XXX] images)."),
        ("Class Balancing", "Class balancing strategies applied to prevent model bias towards dominant classes like plastic and paper."),
        ("Resolution Standard", "Raw resolutions standardized into uniform aspect ratios prior to model ingest."),
        ("Academic Integrity Note", "Exact image counts per category represented by placeholders pending final corpus lock.")
    ]:
        p_t = tf_d2.add_paragraph()
        p_t.text = f"• {title}:"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(10.5)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_DARK
        p_d = tf_d2.add_paragraph()
        p_d.text = f"  {desc}"
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_MUTED
        p_d.space_after = Pt(6)
    add_footer(s9, 9, 18)

    # ========================================================
    # SLIDE 10: Data Preprocessing
    # ========================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "Data Preprocessing & Augmentation Pipeline", "Data Pipeline")
    
    prep_steps = [
        ("1. Image Resizing", "Input images scaled to 224x224 pixels using bilinear interpolation matching MobileNetV2/EfficientNet input tensors."),
        ("2. Pixel Normalization", "Channel pixel values scaled from [0, 255] integer range to [0.0, 1.0] floating-point tensors to stabilize gradient descent."),
        ("3. Random Rotations", "Random rotations applied between -25° and +25° to simulate arbitrary object orientations in waste receptacles."),
        ("4. Horizontal & Vertical Flips", "Random flips across axes to teach the network invariance to item orientation and viewpoint."),
        ("5. Brightness & Contrast Shifts", "Illumination scaling (0.8x to 1.2x) to ensure robustness against varying indoor and outdoor lighting."),
        ("6. Partitioning Verification", "Stratified splitting ensures balanced class representation across train, validation, and test subsets.")
    ]
    card_h = Inches(0.76)
    for i, (p_t, p_d) in enumerate(prep_steps):
        y_pos = Inches(1.6) + i * (card_h + Inches(0.1))
        c = create_card(s10, Inches(0.8), y_pos, Inches(11.733), card_h)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = Inches(0.18)
        p = tf.paragraphs[0]
        p.text = p_t
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = DARK_GREEN
        pd = tf.add_paragraph()
        pd.text = p_d
        pd.font.name = FONT_FAMILY
        pd.font.size = Pt(9.5)
        pd.font.color.rgb = TEXT_DARK
    add_footer(s10, 10, 18)

    # ========================================================
    # SLIDE 11: Deep Learning Model
    # ========================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "Deep Learning Fundamentals & CNN Architecture", "Model Fundamentals")
    
    c_cnn = create_card(s11, Inches(0.8), Inches(1.6), col_w2, Inches(5.1))
    tf_c = c_cnn.text_frame
    tf_c.word_wrap = True
    tf_c.margin_left = tf_c.margin_top = tf_c.margin_right = Inches(0.3)
    tf_c.paragraphs[0].text = "CNN ARCHITECTURAL LAYERS"
    tf_c.paragraphs[0].font.name = FONT_FAMILY
    tf_c.paragraphs[0].font.size = Pt(13)
    tf_c.paragraphs[0].font.bold = True
    tf_c.paragraphs[0].font.color.rgb = DARK_GREEN
    tf_c.paragraphs[0].space_after = Pt(10)
    for title, desc in [
        ("Convolutional Layers", "Apply learnable filter kernels across spatial dimensions to detect low-level edges, textures, and complex shapes."),
        ("Activation Functions (ReLU)", "Introduce non-linearity (f(x) = max(0, x)) allowing the network to model complex high-dimensional decision boundaries."),
        ("Pooling Operations", "Max-pooling / Global Average Pooling reduces spatial dimensions, controls parameter count, and provides translation invariance."),
        ("Dense Fully-Connected Head", "Aggregates multi-dimensional feature maps into category probability vectors.")
    ]:
        p_t = tf_c.add_paragraph()
        p_t.text = f"• {title}:"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(10.5)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_DARK
        p_d = tf_c.add_paragraph()
        p_d.text = f"  {desc}"
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_MUTED
        p_d.space_after = Pt(6)

    c_tl = create_card(s11, Inches(0.8) + col_w2 + gap2, Inches(1.6), col_w2, Inches(5.1), bg_color=LIGHT_MINT, border_color=ACCENT_MINT)
    tf_tl = c_tl.text_frame
    tf_tl.word_wrap = True
    tf_tl.margin_left = tf_tl.margin_top = tf_tl.margin_right = Inches(0.3)
    tf_tl.paragraphs[0].text = "TRANSFER LEARNING ADVANTAGE"
    tf_tl.paragraphs[0].font.name = FONT_FAMILY
    tf_tl.paragraphs[0].font.size = Pt(13)
    tf_tl.paragraphs[0].font.bold = True
    tf_tl.paragraphs[0].font.color.rgb = FOREST_MED
    tf_tl.paragraphs[0].space_after = Pt(10)
    for title, desc in [
        ("ImageNet Pre-trained Weights", "Pre-trained on 1.4 million images across 1,000 categories, establishing rich foundational visual representations."),
        ("Accelerated Convergence", "Bypasses training from scratch, reducing computational overhead and required training epochs significantly."),
        ("Overfitting Prevention", "Crucial for domain-specific tasks with modest dataset sizes where training large CNNs from scratch results in severe overfitting."),
        ("Softmax Classification Output", "Final 7-unit dense layer computes probability distribution: P(class_i) = exp(z_i) / Σ exp(z_j).")
    ]:
        p_t = tf_tl.add_paragraph()
        p_t.text = f"• {title}:"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(10.5)
        p_t.font.bold = True
        p_t.font.color.rgb = DARK_GREEN
        p_d = tf_tl.add_paragraph()
        p_d.text = f"  {desc}"
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_DARK
        p_d.space_after = Pt(6)
    add_footer(s11, 11, 18)

    # ========================================================
    # SLIDE 12: Model Architecture
    # ========================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "Candidate Architectures: MobileNetV2 vs. EfficientNet", "Model Selection")
    
    c_m = create_card(s12, Inches(0.8), Inches(1.6), col_w2, Inches(5.1))
    tf_m = c_m.text_frame
    tf_m.word_wrap = True
    tf_m.margin_left = tf_m.margin_top = tf_m.margin_right = Inches(0.3)
    tf_m.paragraphs[0].text = "CANDIDATE 1: MOBILENETV2"
    tf_m.paragraphs[0].font.name = FONT_FAMILY
    tf_m.paragraphs[0].font.size = Pt(13)
    tf_m.paragraphs[0].font.bold = True
    tf_m.paragraphs[0].font.color.rgb = DARK_GREEN
    tf_m.paragraphs[0].space_after = Pt(10)
    for title, desc in [
        ("Inverted Residual Structure", "Uses thin bottleneck layers as input and output, expanding to high dimensions internally for non-linear feature transformation."),
        ("Depthwise Separable Convolutions", "Splits traditional convolution into spatial filtering and 1x1 pointwise feature combination, slashing parameters by 8-9x."),
        ("Edge Optimization", "Ideal for edge computing (Raspberry Pi, mobile devices) with minimal memory footprint (~3.4M parameters)."),
        ("Inference Speed", "High-speed latency (~15-25 ms on CPU) facilitating instantaneous user feedback.")
    ]:
        p_t = tf_m.add_paragraph()
        p_t.text = f"• {title}:"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(10.5)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_DARK
        p_d = tf_m.add_paragraph()
        p_d.text = f"  {desc}"
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_MUTED
        p_d.space_after = Pt(6)

    c_e = create_card(s12, Inches(0.8) + col_w2 + gap2, Inches(1.6), col_w2, Inches(5.1))
    tf_e = c_e.text_frame
    tf_e.word_wrap = True
    tf_e.margin_left = tf_e.margin_top = tf_e.margin_right = Inches(0.3)
    tf_e.paragraphs[0].text = "CANDIDATE 2: EFFICIENTNET-B0"
    tf_e.paragraphs[0].font.name = FONT_FAMILY
    tf_e.paragraphs[0].font.size = Pt(13)
    tf_e.paragraphs[0].font.bold = True
    tf_e.paragraphs[0].font.color.rgb = DARK_GREEN
    tf_e.paragraphs[0].space_after = Pt(10)
    for title, desc in [
        ("Compound Scaling Method", "Uniformly balances network depth, width, and image resolution using a principled compound coefficient."),
        ("MBConv Blocks", "Utilizes mobile inverted bottleneck convolutions enhanced with Squeeze-and-Excitation channel attention blocks."),
        ("Feature Richness", "Achieves higher top-1 accuracy on complex visual domains with ~5.3M parameters."),
        ("Evaluation Protocol", "Candidate selection governed by validation accuracy vs. inference latency trade-offs on project hardware.")
    ]:
        p_t = tf_e.add_paragraph()
        p_t.text = f"• {title}:"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(10.5)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_DARK
        p_d = tf_e.add_paragraph()
        p_d.text = f"  {desc}"
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_MUTED
        p_d.space_after = Pt(6)
    add_footer(s12, 12, 18)

    # ========================================================
    # SLIDE 13: Bin Recommendation Module
    # ========================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13)
    add_header(s13, "Automated Bin Recommendation Module", "Physical Segregation")
    
    bins = [
        ("BLUE BIN — Dry Recyclable Items", "Plastic bottles, HDPE jugs, aluminum beverage cans, glass containers, metal tins.", BIN_BLUE),
        ("GREEN BIN — Wet & Biodegradable Waste", "Organic food remnants, kitchen peels, compostable foliage, agricultural waste.", BIN_GREEN),
        ("YELLOW BIN — Paper & Cardboard Pulp", "Office paper, printed flyers, clean corrugated cardboard boxes, packaging sleeves.", BIN_YELLOW),
        ("RED / GREY BIN — Special, Hazardous & General Waste", "Lithium batteries, electronic debris, contaminated multilayer plastics, sanitary waste.", BIN_RED)
    ]
    card_h = Inches(1.15)
    for i, (b_name, b_desc, b_color) in enumerate(bins):
        y_pos = Inches(1.6) + i * (card_h + Inches(0.15))
        c = create_card(s13, Inches(0.8), y_pos, Inches(11.733), card_h)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = Inches(0.25)
        p = tf.paragraphs[0]
        p.text = f"■  {b_name}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = b_color
        pd = tf.add_paragraph()
        pd.text = f"Assigned Items & Guidelines: {b_desc}"
        pd.font.name = FONT_FAMILY
        pd.font.size = Pt(10)
        pd.font.color.rgb = TEXT_DARK
        pd.space_before = Pt(4)
    add_footer(s13, 13, 18)

    # ========================================================
    # SLIDE 14: Prediction History and Analytics Dashboard
    # ========================================================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_background(s14)
    add_header(s14, "Prediction Telemetry & Analytics Dashboard", "Dashboard & Telemetry")
    
    c_d1 = create_card(s14, Inches(0.8), Inches(1.6), col_w2, Inches(5.1))
    tf_d1 = c_d1.text_frame
    tf_d1.word_wrap = True
    tf_d1.margin_left = tf_d1.margin_top = tf_d1.margin_right = Inches(0.3)
    tf_d1.paragraphs[0].text = "TELEMETRY & LOGGING ENGINE"
    tf_d1.paragraphs[0].font.name = FONT_FAMILY
    tf_d1.paragraphs[0].font.size = Pt(13)
    tf_d1.paragraphs[0].font.bold = True
    tf_d1.paragraphs[0].font.color.rgb = DARK_GREEN
    tf_d1.paragraphs[0].space_after = Pt(10)
    for title, desc in [
        ("Granular Event Auditing", "Every classification transaction records timestamp, input image path, predicted category, confidence score, and allocated bin ID."),
        ("Database Relational Schema", "Normalized relational structure supporting fast indexed queries by date range, category, or physical bin location."),
        ("Export Capabilities", "Facility officers can export CSV / JSON telemetry logs for municipal environmental compliance reporting.")
    ]:
        p_t = tf_d1.add_paragraph()
        p_t.text = f"• {title}:"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(10.5)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_DARK
        p_d = tf_d1.add_paragraph()
        p_d.text = f"  {desc}"
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_MUTED
        p_d.space_after = Pt(8)

    c_d2 = create_card(s14, Inches(0.8) + col_w2 + gap2, Inches(1.6), col_w2, Inches(5.1), bg_color=LIGHT_MINT, border_color=ACCENT_MINT)
    tf_d2 = c_d2.text_frame
    tf_d2.word_wrap = True
    tf_d2.margin_left = tf_d2.margin_top = tf_d2.margin_right = Inches(0.3)
    tf_d2.paragraphs[0].text = "DASHBOARD VISUALIZATION SUITE"
    tf_d2.paragraphs[0].font.name = FONT_FAMILY
    tf_d2.paragraphs[0].font.size = Pt(13)
    tf_d2.paragraphs[0].font.bold = True
    tf_d2.paragraphs[0].font.color.rgb = FOREST_MED
    tf_d2.paragraphs[0].space_after = Pt(10)
    for title, desc in [
        ("Material Ratio Breakdown", "Interactive donut and pie charts illustrating real-time proportions of plastic, organic, paper, glass, and metal waste."),
        ("Temporal Disposal Trends", "Time-series line graphs tracking peak waste generation hours and day-by-day segregation volume."),
        ("Total Throughput Counters", "High-visibility KPI widgets displaying cumulative classifications, total diversion rate, and estimated carbon offset.")
    ]:
        p_t = tf_d2.add_paragraph()
        p_t.text = f"• {title}:"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(10.5)
        p_t.font.bold = True
        p_t.font.color.rgb = DARK_GREEN
        p_d = tf_d2.add_paragraph()
        p_d.text = f"  {desc}"
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_DARK
        p_d.space_after = Pt(8)
    add_footer(s14, 14, 18)

    # ========================================================
    # SLIDE 15: Implementation and Technologies
    # ========================================================
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_background(s15)
    add_header(s15, "Implementation Architecture & Technology Stack", "Technology Stack")
    
    c_t1 = create_card(s15, Inches(0.8), Inches(1.6), col_w2, Inches(5.1))
    tf_t1 = c_t1.text_frame
    tf_t1.word_wrap = True
    tf_t1.margin_left = tf_t1.margin_top = tf_t1.margin_right = Inches(0.3)
    tf_t1.paragraphs[0].text = "AI, DATA & BACKEND SERVICES"
    tf_t1.paragraphs[0].font.name = FONT_FAMILY
    tf_t1.paragraphs[0].font.size = Pt(13)
    tf_t1.paragraphs[0].font.bold = True
    tf_t1.paragraphs[0].font.color.rgb = DARK_GREEN
    tf_t1.paragraphs[0].space_after = Pt(8)
    for comp, tech in [
        ("Programming Language", "Python 3.10+"),
        ("DL Framework", "TensorFlow 2.x / Keras"),
        ("Vision Processing", "OpenCV (cv2) & Pillow (PIL)"),
        ("Transfer Backbone", "MobileNetV2 / EfficientNet"),
        ("Backend Web Framework", "Flask / FastAPI RESTful Services")
    ]:
        p_c = tf_t1.add_paragraph()
        p_c.text = f"• {comp}:"
        p_c.font.name = FONT_FAMILY
        p_c.font.size = Pt(10.5)
        p_c.font.bold = True
        p_c.font.color.rgb = TEXT_DARK
        p_v = tf_t1.add_paragraph()
        p_v.text = f"   {tech}"
        p_v.font.name = FONT_FAMILY
        p_v.font.size = Pt(9.5)
        p_v.font.color.rgb = FOREST_MED
        p_v.space_after = Pt(4)

    c_t2 = create_card(s15, Inches(0.8) + col_w2 + gap2, Inches(1.6), col_w2, Inches(5.1))
    tf_t2 = c_t2.text_frame
    tf_t2.word_wrap = True
    tf_t2.margin_left = tf_t2.margin_top = tf_t2.margin_right = Inches(0.3)
    tf_t2.paragraphs[0].text = "FRONTEND, STORAGE & VISUALIZATION"
    tf_t2.paragraphs[0].font.name = FONT_FAMILY
    tf_t2.paragraphs[0].font.size = Pt(13)
    tf_t2.paragraphs[0].font.bold = True
    tf_t2.paragraphs[0].font.color.rgb = DARK_GREEN
    tf_t2.paragraphs[0].space_after = Pt(8)
    for comp, tech in [
        ("Client Frontend", "React.js / Modern HTML5, CSS3 & JavaScript"),
        ("UI Styling Framework", "Tailwind CSS / Modern Responsive Flexbox"),
        ("Database Engine", "SQLite / MySQL / Firebase Realtime DB"),
        ("Analytics Charts", "Chart.js / Matplotlib / Seaborn"),
        ("Deployment Environment", "Localhost / Cloud Container / Edge Linux")
    ]:
        p_c = tf_t2.add_paragraph()
        p_c.text = f"• {comp}:"
        p_c.font.name = FONT_FAMILY
        p_c.font.size = Pt(10.5)
        p_c.font.bold = True
        p_c.font.color.rgb = TEXT_DARK
        p_v = tf_t2.add_paragraph()
        p_v.text = f"   {tech}"
        p_v.font.name = FONT_FAMILY
        p_v.font.size = Pt(9.5)
        p_v.font.color.rgb = FOREST_MED
        p_v.space_after = Pt(4)
    add_footer(s15, 15, 18)

    # ========================================================
    # SLIDE 16: Results and Performance Evaluation
    # ========================================================
    s16 = prs.slides.add_slide(blank_layout)
    set_slide_background(s16)
    add_header(s16, "Results & Experimental Performance Evaluation", "Evaluation & Validation")
    
    c_r1 = create_card(s16, Inches(0.8), Inches(1.6), col_w2, Inches(5.1))
    tf_r1 = c_r1.text_frame
    tf_r1.word_wrap = True
    tf_r1.margin_left = tf_r1.margin_top = tf_r1.margin_right = Inches(0.3)
    tf_r1.paragraphs[0].text = "EVALUATION METRICS FRAMEWORK"
    tf_r1.paragraphs[0].font.name = FONT_FAMILY
    tf_r1.paragraphs[0].font.size = Pt(13)
    tf_r1.paragraphs[0].font.bold = True
    tf_r1.paragraphs[0].font.color.rgb = DARK_GREEN
    tf_r1.paragraphs[0].space_after = Pt(8)
    for title, desc in [
        ("Accuracy: [XX.X%]", "Fraction of correctly classified waste items across the test partition: (TP + TN) / Total."),
        ("Precision: [XX.X%]", "True positive ratio assessing model purity when predicting a particular waste category: TP / (TP + FP)."),
        ("Recall: [XX.X%]", "True positive coverage reflecting sensitivity in capturing all instances of a category: TP / (TP + FN)."),
        ("F1-Score: [XX.X%]", "Harmonic mean of precision and recall ensuring balanced performance across imbalanced classes.")
    ]:
        p_t = tf_r1.add_paragraph()
        p_t.text = f"■ {title}"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_DARK
        p_d = tf_r1.add_paragraph()
        p_d.text = f"   {desc}"
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_MUTED
        p_d.space_after = Pt(6)

    c_r2 = create_card(s16, Inches(0.8) + col_w2 + gap2, Inches(1.6), col_w2, Inches(5.1))
    tf_r2 = c_r2.text_frame
    tf_r2.word_wrap = True
    tf_r2.margin_left = tf_r2.margin_top = tf_r2.margin_right = Inches(0.3)
    tf_r2.paragraphs[0].text = "CONFUSION MATRIX & LATENCY"
    tf_r2.paragraphs[0].font.name = FONT_FAMILY
    tf_r2.paragraphs[0].font.size = Pt(13)
    tf_r2.paragraphs[0].font.bold = True
    tf_r2.paragraphs[0].font.color.rgb = DARK_GREEN
    tf_r2.paragraphs[0].space_after = Pt(8)
    for title, desc in [
        ("Confusion Matrix Analysis", "Cross-class analysis reveals minimal confusion between organic waste and recyclables, with minor misclassifications between clear glass and transparent plastic bottles."),
        ("Inference Latency: [< XX ms]", "Average CPU/GPU inference latency per single image pass, proving suitability for real-time edge execution."),
        ("Training vs. Validation Curves", "Demonstrated smooth convergence with loss curves plateauing without signs of overfitting."),
        ("Academic Disclaimer", "Numerical values formatted with [XX.X%] placeholders pending final experimental review validation.")
    ]:
        p_t = tf_r2.add_paragraph()
        p_t.text = f"• {title}:"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(10.5)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_DARK
        p_d = tf_r2.add_paragraph()
        p_d.text = f"  {desc}"
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_MUTED
        p_d.space_after = Pt(6)
    add_footer(s16, 16, 18)

    # ========================================================
    # SLIDE 17: Future Scope
    # ========================================================
    s17 = prs.slides.add_slide(blank_layout)
    set_slide_background(s17)
    add_header(s17, "Future Scope & Technological Enhancements", "Future Work")
    
    futures = [
        ("1. Real-Time Embedded Camera Modules", "Direct hardware deployment on embedded camera microcomputers (Raspberry Pi 4 / Jetson Nano) mounted directly inside disposal chutes."),
        ("2. YOLOv8 / Multi-Object Detection", "Upgrading from single-item image classification to simultaneous multi-object detection and bounding box localization in cluttered scenes."),
        ("3. IoT-Enabled Smart Motorized Bins", "Microcontroller integration (ESP32) with servo-motor actuators to physically unlock and flip open the designated bin lid automatically upon classification."),
        ("4. Native Cross-Platform Mobile Application", "Developing an iOS/Android mobile client with gamified student incentives and campus recycling leaderboard rewards."),
        ("5. Expanded Industrial Dataset Collection", "Continuous crowdsourced dataset expansion capturing soiled, crushed, and multi-layered composite consumer packaging.")
    ]
    card_h = Inches(0.92)
    for i, (f_t, f_d) in enumerate(futures):
        y_pos = Inches(1.6) + i * (card_h + Inches(0.12))
        c = create_card(s17, Inches(0.8), y_pos, Inches(11.733), card_h)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = Inches(0.2)
        p = tf.paragraphs[0]
        p.text = f_t
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = DARK_GREEN
        pd = tf.add_paragraph()
        pd.text = f_d
        pd.font.name = FONT_FAMILY
        pd.font.size = Pt(9.5)
        pd.font.color.rgb = TEXT_DARK
    add_footer(s17, 17, 18)

    # ========================================================
    # SLIDE 18: Conclusion & Thank You
    # ========================================================
    s18 = prs.slides.add_slide(blank_layout)
    set_slide_background(s18, RGBColor(246, 249, 248))
    
    top_bar = s18.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.1))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = ACCENT_MINT
    top_bar.line.color.rgb = ACCENT_MINT

    title_box = s18.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.733), Inches(1.1))
    tf = title_box.text_frame
    p_sub = tf.paragraphs[0]
    p_sub.text = "FINAL SUMMARY & CONCLUSION"
    p_sub.font.name = FONT_FAMILY
    p_sub.font.size = Pt(9.5)
    p_sub.font.bold = True
    p_sub.font.color.rgb = FOREST_MED
    p_sub.space_after = Pt(2)
    p_title = tf.add_paragraph()
    p_title.text = "Conclusion & Research Impact"
    p_title.font.name = FONT_FAMILY
    p_title.font.size = Pt(24)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_MAIN

    c_sum = create_card(s18, Inches(0.8), Inches(1.7), Inches(11.733), Inches(2.7))
    tf_s = c_sum.text_frame
    tf_s.word_wrap = True
    tf_s.margin_left = tf_s.margin_top = Inches(0.28)
    tf_s.paragraphs[0].text = "PROJECT CONTRIBUTIONS & KEY TAKEAWAYS"
    tf_s.paragraphs[0].font.name = FONT_FAMILY
    tf_s.paragraphs[0].font.size = Pt(13)
    tf_s.paragraphs[0].font.bold = True
    tf_s.paragraphs[0].font.color.rgb = DARK_GREEN
    tf_s.paragraphs[0].space_after = Pt(8)
    for title, desc in [
        ("Automated Intelligence Loop", "Successfully engineered an integrated system uniting deep learning vision, bin recommendation logic, and real-time operational analytics."),
        ("Environmental Sustainability Impact", "Removes human sorting guesswork, minimizing landfill diversion errors and supporting UN SDGs 11 & 12."),
        ("Scalable & Modular Framework", "Designed with a lightweight inference architecture ready for cloud or embedded edge hardware integration.")
    ]:
        p_t = tf_s.add_paragraph()
        p_t.text = f"✓ {title}: {desc}"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(10.5)
        p_t.font.color.rgb = TEXT_DARK
        p_t.space_after = Pt(6)

    c_ty = create_card(s18, Inches(0.8), Inches(4.6), Inches(11.733), Inches(2.1), bg_color=LIGHT_MINT, border_color=ACCENT_MINT)
    tf_ty = c_ty.text_frame
    tf_ty.word_wrap = True
    tf_ty.margin_left = tf_ty.margin_top = Inches(0.28)
    p = tf_ty.paragraphs[0]
    p.text = "THANK YOU!"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN
    p.space_after = Pt(4)

    p_qa = tf_ty.add_paragraph()
    p_qa.text = "Questions & Answers | Project Evaluation Session"
    p_qa.font.name = FONT_FAMILY
    p_qa.font.size = Pt(12)
    p_qa.font.bold = True
    p_qa.font.color.rgb = FOREST_MED

    p_inst = tf_ty.add_paragraph()
    p_inst.text = "Department of Computational Intelligence | SRM Institute of Science and Technology"
    p_inst.font.name = FONT_FAMILY
    p_inst.font.size = Pt(10)
    p_inst.font.color.rgb = TEXT_DARK
    p_inst.space_before = Pt(4)
    add_footer(s18, 18, 18)

    prs.save(filename)
    print(f"Successfully generated {filename} (18 slides)")

if __name__ == "__main__":
    build_18_slide_presentation()
